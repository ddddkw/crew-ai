import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "app"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))


class ModelSettingsI18nTests(unittest.TestCase):
    def test_chinese_model_settings_translations_are_defined(self):
        zh = json.loads((APP_DIR / "i18n" / "zh.json").read_text(encoding="utf-8"))

        self.assertEqual(zh["page"]["model_settings"], "模型配置")
        self.assertEqual(zh["model_settings"]["title"], "模型配置")
        self.assertIn(".env", zh["model_settings"]["description"])
        self.assertEqual(zh["model_settings"]["add_model"], "新增模型")
        self.assertEqual(zh["model_settings"]["fields"]["provider"]["label"], "显示名称")
        self.assertEqual(zh["model_settings"]["fields"]["model"]["label"], "模型名称")
        self.assertEqual(zh["model_settings"]["fields"]["api_base"]["label"], "接口地址")

    def test_model_config_fields_reference_translation_keys(self):
        from env_config import MODEL_CONFIG_FIELDS

        for field in MODEL_CONFIG_FIELDS:
            self.assertIn("label_key", field)
            self.assertIn("help_key", field)


if __name__ == "__main__":
    unittest.main()
