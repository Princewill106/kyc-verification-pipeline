# KYC Verification Pipeline

> Verified, rejected with a fixable reason, or referred to a human: verification in minutes, not days.

![Python](https://img.shields.io/badge/python-3.10%2B-blue) ![License](https://img.shields.io/badge/license-MIT-green) ![Offline demo](https://img.shields.io/badge/demo-runs%20offline-brightgreen) ![n8n](https://img.shields.io/badge/n8n-importable%20workflow-EA4B71) ![n8n](https://img.shields.io/badge/n8n-importable%20workflow-EA4B71) ![Series](https://img.shields.io/badge/AI%20Automation-3%2F50-purple)

**Sector:** Fintech & Compliance  ·  **Project 3 of 50** in my [AI Automation Projects series](https://github.com/Princewill106/Princewill106)

## The problem

Onboarding drop-off is usually a KYC problem. Every hour a customer waits for verification is a customer deciding they don't need the product. Worse, the lazy version rejects with 'document not accepted', which generates most of the support tickets and most of the churn.

## How it works

```mermaid
flowchart LR
    S0["Upload"]
    S1["Classify doc"]
    S2["Cross-check"]
    S3["3 outcomes"]
    S4["Audit trail"]
    S0 --> S1
    S1 --> S2
    S2 --> S3
    S3 --> S4
```

1. **Capture** — Documents arrive with the signup form. The demo uses OCR text in `sample_submissions.json`.
2. **Classify** — Each document is classified (national ID, passport, driver's licence, utility bill, unknown) from keywords, so wrong uploads are caught immediately.
3. **Cross-check** — Name on the ID is fuzzy-matched to the form, date of birth must agree, and the expiry date must be in the future.
4. **Decide** — Three outcomes only: VERIFIED, REJECTED with a specific fixable reason, or REFERRED to a human with the exact field highlighted.
5. **Audit** — Every check, result and reason is written to `output/kyc_audit.json`.

## Features

- Keyword-based document classification
- Fuzzy name matching (handles initials and order swaps)
- DOB and expiry checks
- Fixable rejection messages customers understand
- Human referral with the exact field in question
- Per-check audit trail

## Quick start

```bash
git clone https://github.com/Princewill106/kyc-verification-pipeline.git
cd kyc-verification-pipeline
python main.py --demo
```

No installs needed: it uses only the Python standard library. The demo runs fully offline using the sample data in this repo.

**Optional: plug in an LLM.** Copy `.env.example` to `.env` and add an Anthropic or OpenAI key. The project will then use the model for the language-heavy steps and fall back to its rule-based logic if a call fails.

Run the tests:

```bash
python -m unittest -v
```

## Sample output

```text
CUS-101  VERIFIED  all checks passed
      [ok ] document_type  national_id
      [ok ] name_match     NWOSU ADAEZE vs Adaeze Nwosu (1.00)
      [ok ] dob_match      1995-04-12 vs 1995-04-12
      [ok ] not_expired    2030-01-01
      [ok ] face_match     0.93
CUS-102  REJECTED  We received a utility bill. Please upload a national ID, passport or driver's licence.
      [FAIL] document_type  utility_bill
CUS-103  REJECTED  Your ID expired on 2025-06-30. Please upload a valid, unexpired ID.
      [ok ] document_type  passport
      [ok ] name_match     FATIMA SULE vs Fatima Sule (1.00)
      [ok ] dob_match      1990-02-02 vs 1990-02-02
      [FAIL] not_expired    2025-06-30
      [ok ] face_match     0.88
CUS-104  REFERRED  name partially matches
      [ok ] document_type  drivers_licence
      [FAIL] name_match     EMEKA OBI vs Emeka John Obi (0.78)
      [ok ] dob_match      1992-11-15 vs 1992-11-15
      [ok ] not_expired    2028-03-01
      [ok ] face_match     0.91
CUS-105  REFERRED  date_of_birth differs between ID and form
      [ok ] document_type  national_id
      [ok ] name_match     BLESSING UDO vs Blessing Udo (1.00)
      [FAIL] dob_match      1997-07-21 vs 1998-07-21
      [ok ] not_expired    2031-05-05
      [ok ] face_match     0.95

Audit trail -> output/kyc_audit.json
```

## Use it in n8n (no code needed)

[`n8n-workflow.json`](n8n-workflow.json) is a ready-to-import n8n version of this project, built for n8n 1.x.

1. In n8n, open **Workflows → Import from File** and choose `n8n-workflow.json`.
2. Click **Test workflow**. It runs the full logic on the sample data built into the *Sample data* node, so you can see the results before connecting anything.
3. Open each output node and connect your accounts: Slack. For Google Sheets, pick your spreadsheet and sheet.
4. Adjust the settings at the top of the **Logic** node (thresholds, templates, contacts), then **Activate**.

**Flow:** **Webhook** (`POST /webhook/kyc`) → **Logic** (Code node) → **Route** (Switch)

**Outputs:**
- Activate account (your API)
- Tell customer what to resend (your API)
- Send to compliance (Slack)

The Logic node is a JavaScript port of the rules in `main.py`, so you can run the project in n8n without Python.

## Use it on your own data

Feed OCR text from your document capture step into the shape of `sample_submissions.json` and run `python main.py --input submissions.json`. Face-match and liveness are left as a hook (`face_match_score`) for your vendor's API.

## Project structure

```text
n8n-workflow.json            Importable n8n workflow
.env.example                 Optional API key settings
.gitignore                   Git ignore rules
LICENSE                      MIT license
README.md                    This file
llm.py                       Optional LLM helper (offline fallback)
main.py                      Entry point and core logic
requirements.txt             Dependencies (stdlib only)
sample_submissions.json      Sample input data for the demo
test_main.py                 Unit tests
```

## Who this is for

- Fintech and wallet onboarding teams
- Microfinance account opening
- Compliance teams designing an audit-ready flow

## Ideas to extend it

- [ ] Integrate a face-match/liveness API
- [ ] On-device glare and blur checks before upload
- [ ] NIN/BVN lookup integration
- [ ] Weekly report of top rejection reasons

## About

Built by **Ogbu Ugochukwu Princewill**, AI Automation Lead and robotics engineer. I teach people and businesses to build with AI, not just talk about it. [LinkedIn](https://www.linkedin.com/in/ugochukwu-ogbu-653a0816a)

If this helped you, give it a ⭐ and share what you built with it.

## License

MIT — see [LICENSE](LICENSE).
