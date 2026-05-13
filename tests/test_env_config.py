import os
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "app"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))


class EnvConfigTests(unittest.TestCase):
    def test_update_env_file_preserves_existing_lines_and_appends_new_keys(self):
        from env_config import update_env_file

        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = Path(temp_dir) / ".env"
            env_path.write_text(
                "# existing comment\n"
                "OPENAI_API_KEY=old-key\n"
                "UNRELATED=value\n",
                encoding="utf-8",
            )

            update_env_file(
                env_path,
                {
                    "OPENAI_API_KEY": "new-key",
                    "OPENAI_API_BASE": "https://example.test/v1",
                },
            )

            content = env_path.read_text(encoding="utf-8")

        self.assertIn("# existing comment\n", content)
        self.assertIn("UNRELATED=value\n", content)
        self.assertIn('OPENAI_API_KEY="new-key"\n', content)
        self.assertTrue(content.endswith('OPENAI_API_BASE="https://example.test/v1"\n'))

    def test_apply_env_values_updates_process_environment_and_removes_blank_values(self):
        from env_config import apply_env_values

        os.environ["OPENAI_API_KEY"] = "old-key"
        os.environ["GROQ_API_KEY"] = "old-groq"

        apply_env_values(
            {
                "OPENAI_API_KEY": "new-key",
                "GROQ_API_KEY": "",
            }
        )

        self.assertEqual(os.environ["OPENAI_API_KEY"], "new-key")
        self.assertNotIn("GROQ_API_KEY", os.environ)

    def test_read_model_configs_reads_custom_model_json(self):
        from env_config import read_model_configs, write_model_configs

        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = Path(temp_dir) / ".env"
            write_model_configs(
                env_path,
                [
                    {
                        "provider": "小米 MiMo",
                        "model": "mimo-v2.5-pro",
                        "api_base": "https://api.xiaomimimo.com/v1",
                        "api_key": "secret-key",
                    }
                ],
            )

            configs = read_model_configs(env_path)

        self.assertEqual(
            configs,
            [
                {
                    "provider": "小米 MiMo",
                    "model": "mimo-v2.5-pro",
                    "api_base": "https://api.xiaomimimo.com/v1",
                    "api_key": "secret-key",
                }
            ],
        )

    def test_read_model_configs_can_migrate_legacy_xiaomi_openai_settings(self):
        from env_config import read_model_configs

        with tempfile.TemporaryDirectory() as temp_dir:
            env_path = Path(temp_dir) / ".env"
            env_path.write_text(
                'OPENAI_API_KEY="secret-key"\n'
                'OPENAI_API_BASE="https://api.xiaomimimo.com/v1"\n'
                "OPENAI_MODEL_NAME=mimo-v2.5-pro                      # 推荐使用最新的旗舰模型\n",
                encoding="utf-8",
            )

            configs = read_model_configs(env_path)

        self.assertEqual(configs[0]["provider"], "小米 MiMo")
        self.assertEqual(configs[0]["model"], "mimo-v2.5-pro")
        self.assertEqual(configs[0]["api_base"], "https://api.xiaomimimo.com/v1")


if __name__ == "__main__":
    unittest.main()
