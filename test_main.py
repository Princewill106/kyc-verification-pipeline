import json
import unittest
from datetime import date

import main


class KycTests(unittest.TestCase):
    def test_outcomes(self):
        subs = json.load(open("sample_submissions.json"))
        got = {s["customer_id"]: main.verify(s, date(2026, 10, 9))["status"] for s in subs}
        self.assertEqual(got, {"CUS-101": "VERIFIED", "CUS-102": "REJECTED",
                               "CUS-103": "REJECTED", "CUS-104": "REFERRED",
                               "CUS-105": "REFERRED"})

    def test_classify(self):
        self.assertEqual(main.classify("PASSPORT Nationality: NGA"), "passport")


if __name__ == "__main__":
    unittest.main()
