import os
import sys
import unittest
import json
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "app"
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))


class LlmConfigTests(unittest.TestCase):
    def test_model_list_uses_custom_model_configs(self):
        import llms

        original_value = os.environ.get("MODEL_CONFIGS")
        try:
            os.environ["MODEL_CONFIGS"] = json.dumps(
                [
                    {
                        "provider": "小米 MiMo",
                        "model": "mimo-v2.5-pro",
                        "api_base": "https://api.xiaomimimo.com/v1",
                        "api_key": "secret-key",
                    }
                ],
                ensure_ascii=False,
            )

            models = llms.llm_providers_and_models()

            self.assertEqual(models, ["小米 MiMo: mimo-v2.5-pro"])
        finally:
            if original_value is None:
                os.environ.pop("MODEL_CONFIGS", None)
            else:
                os.environ["MODEL_CONFIGS"] = original_value

    def test_model_list_does_not_include_hardcoded_defaults_when_custom_configs_are_empty(self):
        import llms

        original_value = os.environ.get("MODEL_CONFIGS")
        try:
            os.environ["MODEL_CONFIGS"] = "[]"

            models = llms.llm_providers_and_models()

            self.assertEqual(models, [])
        finally:
            if original_value is None:
                os.environ.pop("MODEL_CONFIGS", None)
            else:
                os.environ["MODEL_CONFIGS"] = original_value

    def test_create_llm_applies_default_request_timeout(self):
        import llms

        class FakeLLM:
            calls = []

            def __init__(self, **kwargs):
                self.kwargs = kwargs
                FakeLLM.calls.append(kwargs)

        original_model_configs = os.environ.get("MODEL_CONFIGS")
        original_crewai = sys.modules.get("crewai")
        try:
            os.environ["MODEL_CONFIGS"] = json.dumps(
                [
                    {
                        "provider": "deepseek",
                        "model": "deepseek-v4-flash",
                        "api_base": "https://api.deepseek.example/v1",
                        "api_key": "secret-key",
                    }
                ]
            )
            sys.modules["crewai"] = SimpleNamespace(LLM=FakeLLM)

            llm = llms.create_llm("deepseek: deepseek-v4-flash")

            self.assertIsInstance(llm, FakeLLM)
            self.assertEqual(FakeLLM.calls[0]["timeout"], llms.DEFAULT_LLM_TIMEOUT_SECONDS)
        finally:
            if original_model_configs is None:
                os.environ.pop("MODEL_CONFIGS", None)
            else:
                os.environ["MODEL_CONFIGS"] = original_model_configs
            if original_crewai is None:
                sys.modules.pop("crewai", None)
            else:
                sys.modules["crewai"] = original_crewai


if __name__ == "__main__":
    unittest.main()
