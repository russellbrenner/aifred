import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout

import alfred_action as action
from store import Store


class TestActionDryRun(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        os.environ["AIFRED_DB_PATH"] = os.path.join(self.tmp.name, "test.db")
        os.environ["AIFRED_DRY_RUN"] = "1"
        # Ensure clean store
        self.store = Store()

    def tearDown(self) -> None:
        self.tmp.cleanup()
        os.environ.pop("AIFRED_DB_PATH", None)
        os.environ.pop("AIFRED_DRY_RUN", None)

    def test_send_new_thread_openai(self):
        payload = {
            "query": "hello world",
            "directives": {"model": "gpt-4o", "temp": 0.6, "new": True},
            "provider": "openai",
            "model": "gpt-4o",
        }
        buf = io.StringIO()
        with redirect_stdout(buf):
            action.handle_action(json.dumps(payload))
        out = buf.getvalue()
        self.assertIn("openai gpt-4o", out)
        self.assertIn("hello world", out)

    def test_continue_latest_thread(self):
        # Seed a thread
        tid = self.store.create_thread("openai", "gpt-4o", "seed")
        self.store.add_message(tid, "user", "seed msg")
        payload = {
            "query": "continue please",
            "directives": {"cont": True},
        }
        buf = io.StringIO()
        with redirect_stdout(buf):
            action.handle_action(json.dumps(payload))
        out = buf.getvalue()
        self.assertIn("openai gpt-4o", out)  # default provider/model


if __name__ == "__main__":
    unittest.main()

