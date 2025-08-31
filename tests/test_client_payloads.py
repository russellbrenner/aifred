import os
import unittest

from providers.openai_client import OpenAIClient
from providers.anthropic_client import AnthropicClient


class TestClientPayloads(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["AIFRED_DRY_RUN"] = "1"  # ensure no network

    def tearDown(self) -> None:
        os.environ.pop("AIFRED_DRY_RUN", None)

    def test_openai_build_payload_with_tools(self):
        c = OpenAIClient()
        payload = c._build_payload(
            system="sys",
            messages=[{"role": "user", "content": "hi"}],
            model="gpt-4o",
            temperature=0.4,
            max_tokens=100,
            tools=["browse", "python"],
        )
        self.assertIn("tools", payload)
        self.assertEqual(payload.get("tool_choice"), "auto")
        self.assertGreaterEqual(len(payload["tools"]), 1)

    def test_anthropic_build_payload_with_tools(self):
        c = AnthropicClient()
        payload = c._build_payload(
            system="sys",
            messages=[{"role": "user", "content": "hi"}],
            model="claude-3-7-sonnet",
            temperature=0.4,
            max_tokens=100,
            tools=["browse", "code"],
        )
        self.assertIn("tools", payload)
        self.assertEqual(payload.get("tool_choice"), "auto")
        self.assertGreaterEqual(len(payload["tools"]), 1)


if __name__ == "__main__":
    unittest.main()

