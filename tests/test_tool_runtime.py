import os
import unittest

from utils.tool_runtime import run_citation_extract, run_web_search, run_fetch_url, run_case_search


class TestToolRuntime(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["AIFRED_DRY_RUN"] = "1"

    def tearDown(self) -> None:
        os.environ.pop("AIFRED_DRY_RUN", None)

    def test_citation_extract(self):
        text = "Roe v. Wade, 410 U.S. 113 (1973) and 42 U.S.C. § 1983"
        res = run_citation_extract({"text": text})
        self.assertTrue(any("410 U.S. 113 (1973)" in c for c in res["cases"]))
        self.assertTrue(any("42 U.S.C. § 1983" in s for s in res["statutes"]))

    def test_web_search_stub(self):
        res = run_web_search({"query": "constitutional law"})
        self.assertIn("results", res)

    def test_fetch_url_stub(self):
        res = run_fetch_url({"url": "https://example.com"})
        self.assertIn("text", res)

    def test_case_search_stub(self):
        res = run_case_search({"query": "Miranda"})
        self.assertIn("results", res)


if __name__ == "__main__":
    unittest.main()

