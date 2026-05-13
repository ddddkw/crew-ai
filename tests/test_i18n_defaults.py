import importlib
import os
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "app"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))


class I18nDefaultTests(unittest.TestCase):
    def test_default_language_is_chinese_when_not_configured(self):
        original_value = os.environ.pop("DEFAULT_LANGUAGE", None)
        try:
            import i18n

            importlib.reload(i18n)

            self.assertEqual(i18n.get_default_language(), "zh")
        finally:
            if original_value is not None:
                os.environ["DEFAULT_LANGUAGE"] = original_value


if __name__ == "__main__":
    unittest.main()
