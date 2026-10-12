"""KYC Verification Pipeline: classify -> cross-check -> decide -> audit."""
import argparse
import json
import re
from datetime import date
from difflib import SequenceMatcher
from pathlib import Path

DOC_KEYWORDS = {
    "national_id": ["national identification", "nin", "national identity"],
    "passport": ["passport", "nationality", "passport no"],
    "drivers_licence": ["driver", "licence", "license no"],
    "utility_bill": ["electricity", "meter", "bill", "disco"],
}
ACCEPTED_ID = {"national_id", "passport", "drivers_licence"}


def classify(text: str) -> str:
    t = text.lower()
    scores = {k: sum(w in t for w in words) for k, words in DOC_KEYWORDS.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] else "unknown"


def field(text, label):
    m = re.search(label + r"\s*:\s*(.+)", text, re.I)
    return m.group(1).strip() if m else None


def name_similarity(a: str, b: str) -> float:
    norm = lambda s: sorted(re.sub(r"[^a-z ]", "", s.lower()).split())
    return SequenceMatcher(None, " ".join(norm(a)), " ".join(norm(b))).ratio()


def verify(sub: dict, today: date) -> dict:
    checks, form, doc = [], sub["form"], sub["document_text"]
    kind = classify(doc)
    checks.append(("document_type", kind in ACCEPTED_ID, kind))
    if kind not in ACCEPTED_ID:
        return outcome(sub, checks, "REJECTED",
                       f"We received a {kind.replace('_', ' ')}. Please upload a national ID, "
                       "passport or driver's licence.")
    id_name, dob, expiry = field(doc, "name"), field(doc, "date of birth"), field(doc, "expiry")
    sim = name_similarity(id_name or "", form["full_name"])
    checks.append(("name_match", sim >= 0.85, f"{id_name} vs {form['full_name']} ({sim:.2f})"))
    checks.append(("dob_match", dob == form["date_of_birth"], f"{dob} vs {form['date_of_birth']}"))
    expired = expiry and date.fromisoformat(expiry) < today
    checks.append(("not_expired", not expired, expiry))
    face = sub.get("face_match_score")
    checks.append(("face_match", face is None or face >= 0.8, face))
    if expired:
        return outcome(sub, checks, "REJECTED",
                       f"Your ID expired on {expiry}. Please upload a valid, unexpired ID.")
    if dob != form["date_of_birth"]:
        return outcome(sub, checks, "REFERRED", "date_of_birth differs between ID and form")
    if sim < 0.6:
        return outcome(sub, checks, "REJECTED",
                       "The name on your ID doesn't match the name you signed up with. "
                       "Please check the spelling or upload your own ID.")
    if sim < 0.85 or (face is not None and face < 0.8):
        return outcome(sub, checks, "REFERRED",
                       "name partially matches" if sim < 0.85 else "low face-match score")
    return outcome(sub, checks, "VERIFIED", "all checks passed")


def outcome(sub, checks, status, reason):
    return {"customer_id": sub["customer_id"], "status": status, "reason": reason,
            "checks": [{"check": c, "passed": p, "detail": d} for c, p, d in checks]}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", default="sample_submissions.json")
    ap.add_argument("--today", default="2026-10-09")
    ap.add_argument("--demo", action="store_true")
    a = ap.parse_args()
    subs = json.loads(Path(a.input).read_text())
    results = [verify(s, date.fromisoformat(a.today)) for s in subs]
    Path("output").mkdir(exist_ok=True)
    Path("output/kyc_audit.json").write_text(json.dumps(results, indent=2))
    for r in results:
        print(f"{r['customer_id']}  {r['status']:<9} {r['reason']}")
        for c in r["checks"]:
            mark = "ok " if c["passed"] else "FAIL"
            print(f"      [{mark}] {c['check']:<14} {c['detail']}")
    print("\nAudit trail -> output/kyc_audit.json")


if __name__ == "__main__":
    main()
