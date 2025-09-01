import os
import tempfile
import unittest

from utils.config import get_defaults, DEFAULT_LEGAL_PROMPT
from utils.user_config import load_config, save_config


class TestPersona(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        os.environ["alfred_workflow_data"] = self.tmp.name

    def tearDown(self) -> None:
        os.environ.pop("alfred_workflow_data", None)
        self.tmp.cleanup()

    def test_legal_persona_defaults(self):
        cfg = load_config()
        cfg["active_persona"] = "legal"
        save_config(cfg)
        d = get_defaults()
        self.assertTrue(d.legal_mode)
        self.assertEqual(d.persona_name, "legal")
        self.assertEqual(d.persona_prompt, DEFAULT_LEGAL_PROMPT)


if __name__ == "__main__":
    unittest.main()
