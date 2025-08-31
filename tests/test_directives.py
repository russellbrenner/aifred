import unittest

from utils.directives import parse_directives, summarise_directives


class TestDirectives(unittest.TestCase):
    def test_basic_model_and_temp(self):
        text = "Summarise this @gpt-4o @temp:0.5"
        cleaned, d = parse_directives(text)
        self.assertEqual(cleaned, "Summarise this")
        self.assertEqual(d.model, "gpt-4o")
        self.assertEqual(d.temp, 0.5)

    def test_quoted_sys_and_tools(self):
        text = 'Help me @sys:"You are helpful." @tools:browse,code'
        cleaned, d = parse_directives(text)
        self.assertEqual(cleaned, "Help me")
        self.assertEqual(d.sys, "You are helpful.")
        self.assertEqual(d.tools, ["browse", "code"])

    def test_duplicates_override(self):
        text = "@temp:0.2 plan @temp:0.7"
        cleaned, d = parse_directives(text)
        self.assertEqual(cleaned, "plan")
        self.assertEqual(d.temp, 0.7)

    def test_bare_flags(self):
        text = "continue please @cont"  # cont only
        cleaned, d = parse_directives(text)
        self.assertEqual(cleaned, "continue please")
        self.assertTrue(d.cont)
        self.assertFalse(d.new)

    def test_unknown_tokens_remain(self):
        text = "Ask @weird:token to stay"
        cleaned, d = parse_directives(text)
        self.assertEqual(cleaned, text)
        self.assertIsNone(d.model)

    def test_provider_and_name(self):
        text = "draft @provider:openai @name:notes"
        cleaned, d = parse_directives(text)
        self.assertEqual(cleaned, "draft")
        self.assertEqual(d.provider, "openai")
        self.assertEqual(d.name, "notes")

    def test_summary(self):
        text = '@gpt-4o @temp:0.4 @max:800 @tools:browse'
        _, d = parse_directives(text)
        summary = summarise_directives(d)
        self.assertIn("gpt-4o", summary)
        self.assertIn("temp 0.4", summary)
        self.assertIn("max 800", summary)
        self.assertIn("tools: browse", summary)


if __name__ == "__main__":
    unittest.main()

