import os
import tempfile
import unittest

from store import Store


class TestStore(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        os.environ["AIFRED_DB_PATH"] = os.path.join(self.tmp.name, "test.db")
        self.store = Store()

    def tearDown(self) -> None:
        self.tmp.cleanup()
        os.environ.pop("AIFRED_DB_PATH", None)

    def test_thread_and_messages(self):
        tid = self.store.create_thread("openai", "gpt-4o", "notes")
        self.assertTrue(tid > 0)
        self.store.add_message(tid, "user", "hello")
        self.store.add_message(tid, "assistant", "world", meta={"usage": {"prompt_tokens": 1}})
        msgs = self.store.get_thread_messages(tid)
        self.assertEqual(len(msgs), 2)
        self.assertEqual(msgs[0].content, "hello")
        self.assertEqual(msgs[1].role, "assistant")

    def test_recent_threads(self):
        t1 = self.store.create_thread("openai", "gpt-4o", None)
        t2 = self.store.create_thread("anthropic", "claude-3-7-sonnet", None)
        threads = self.store.get_recent_threads()
        self.assertGreaterEqual(len(threads), 2)


if __name__ == "__main__":
    unittest.main()

