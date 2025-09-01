import os
import unittest

from providers.perplexity_client import PerplexityClient
from providers.gemini_client import GeminiClient
from providers.openrouter_client import OpenRouterClient


class TestExtraClients(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["AIFRED_DRY_RUN"] = "1"

    def tearDown(self) -> None:
        os.environ.pop("AIFRED_DRY_RUN", None)

    def test_perplexity_dry(self):
        c = PerplexityClient()
        r = c.send("sys", [{"role": "user", "content": "hi"}], "llama-3.1-70b-instruct", 0.4, None, [])
        self.assertIn("dry-run", r["text"]) 

    def test_gemini_dry(self):
        c = GeminiClient()
        r = c.send("sys", [{"role": "user", "content": "hi"}], "gemini-1.5-pro", 0.4, None, [])
        self.assertIn("dry-run", r["text"]) 

    def test_openrouter_dry(self):
        c = OpenRouterClient()
        r = c.send("sys", [{"role": "user", "content": "hi"}], "openrouter/anthropic/claude-3.5-sonnet", 0.4, None, [])
        self.assertIn("dry-run", r["text"]) 


if __name__ == "__main__":
    unittest.main()
