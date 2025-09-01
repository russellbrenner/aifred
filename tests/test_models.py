import os
import tempfile
import unittest

from utils.models import get_caps
from utils.user_config import save_config


class TestModels(unittest.TestCase):
    def test_builtin_caps(self):
        c = get_caps("openai", "gpt-4o")
        self.assertGreaterEqual(c["context"], 100000)
        self.assertGreaterEqual(c["max_output_tokens"], 1000)

    def test_user_override_via_config(self):
        tmp = tempfile.TemporaryDirectory()
        os.environ["alfred_workflow_data"] = tmp.name
        try:
            save_config({"model_caps": {"openai:gpt-4o": {"context": 9999, "max_output_tokens": 123}}})
            c = get_caps("openai", "gpt-4o")
            self.assertEqual(c["context"], 9999)
            self.assertEqual(c["max_output_tokens"], 123)
        finally:
            os.environ.pop("alfred_workflow_data", None)
            tmp.cleanup()


if __name__ == "__main__":
    unittest.main()
