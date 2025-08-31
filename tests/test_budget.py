import unittest

from utils.budget import estimate_tokens_text, estimate_tokens_messages, trim_history


class TestBudget(unittest.TestCase):
    def test_estimates(self):
        self.assertGreaterEqual(estimate_tokens_text("hello"), 1)
        msgs = [{"role": "user", "content": "hello"}, {"role": "assistant", "content": "world"}]
        self.assertGreater(estimate_tokens_messages(msgs, "sys"), 0)

    def test_trim(self):
        msgs = [
            {"role": "user", "content": "a" * 1000},
            {"role": "assistant", "content": "b" * 1000},
            {"role": "user", "content": "c" * 1000},
        ]
        trimmed, est = trim_history(msgs, system=None, max_input_tokens=300, reserve_for_completion=50)
        # Should trim at least one old message
        self.assertLess(len(trimmed), len(msgs))


if __name__ == "__main__":
    unittest.main()

