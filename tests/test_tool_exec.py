import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout

import alfred_action as action
from store import Store


class TestToolExec(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        os.environ["AIFRED_DB_PATH"] = os.path.join(self.tmp.name, "test.db")
        os.environ["AIFRED_DRY_RUN"] = "1"
        os.environ["AIFRED_TOOL_EXEC"] = "1"
        self.store = Store()

    def tearDown(self) -> None:
        self.tmp.cleanup()
        os.environ.pop("AIFRED_DB_PATH", None)
        os.environ.pop("AIFRED_DRY_RUN", None)
        os.environ.pop("AIFRED_TOOL_EXEC", None)

    def test_tool_call_and_persist(self):
        payload = {
            "query": "research something",
            "directives": {"model": "gpt-4o", "tools": ["browse"], "new": True},
            "provider": "openai",
            "model": "gpt-4o",
        }
        buf = io.StringIO()
        with redirect_stdout(buf):
            action.handle_action(json.dumps(payload))
        # Verify a tool message exists
        threads = self.store.get_recent_threads()
        self.assertGreaterEqual(len(threads), 1)
        msgs = self.store.get_thread_messages(threads[0].id)
        roles = [m.role for m in msgs]
        self.assertIn("tool", roles)


if __name__ == "__main__":
    unittest.main()

