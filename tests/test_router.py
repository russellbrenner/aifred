import unittest

from providers.router import route, validate_tools


class TestRouter(unittest.TestCase):
    def test_route_by_hint(self):
        self.assertEqual(route(None, "openai"), "openai")
        self.assertEqual(route(None, "anthropic"), "anthropic")

    def test_route_by_model(self):
        self.assertEqual(route("gpt-4o", None), "openai")
        self.assertEqual(route("claude-3-7-sonnet", None), "anthropic")

    def test_default_openai(self):
        self.assertEqual(route(None, None), "openai")

    def test_tool_validation(self):
        supported, dropped = validate_tools("openai", ["browse", "python", "foo"])
        self.assertEqual(set(supported), {"browse", "python"})
        self.assertEqual(dropped, ["foo"])


if __name__ == "__main__":
    unittest.main()

