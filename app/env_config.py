"""Helpers for reading and updating model settings in .env files."""

import json
import os
import re
from pathlib import Path


ENV_PATH = Path(".env")
MODEL_CONFIGS_ENV_KEY = "MODEL_CONFIGS"

MODEL_CONFIG_FIELDS = [
    {
        "key": "provider",
        "label_key": "model_settings.fields.provider.label",
        "help_key": "model_settings.fields.provider.help",
        "secret": False,
    },
    {
        "key": "model",
        "label_key": "model_settings.fields.model.label",
        "help_key": "model_settings.fields.model.help",
        "secret": False,
    },
    {
        "key": "api_base",
        "label_key": "model_settings.fields.api_base.label",
        "help_key": "model_settings.fields.api_base.help",
        "secret": False,
    },
    {
        "key": "api_key",
        "label_key": "model_settings.fields.api_key.label",
        "help_key": "model_settings.fields.api_key.help",
        "secret": True,
    },
]

LEGACY_MODEL_ENV_KEYS = [
    "OPENAI_API_KEY",
    "OPENAI_API_BASE",
    "OPENAI_MODEL_NAME",
    "OPENAI_PROXY_MODELS",
    "GROQ_API_KEY",
    "LMSTUDIO_API_BASE",
    "ANTHROPIC_API_KEY",
    "OLLAMA_HOST",
    "OLLAMA_MODELS",
    "XAI_API_KEY",
]
MODEL_ENV_KEYS = [MODEL_CONFIGS_ENV_KEY] + LEGACY_MODEL_ENV_KEYS
_ENV_LINE_RE = re.compile(r"^(\s*)([A-Za-z_][A-Za-z0-9_]*)(\s*)=(.*)$")


def _strip_inline_comment(value: str) -> str:
    in_single = False
    in_double = False
    escaped = False

    for index, char in enumerate(value):
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char == "'" and not in_double:
            in_single = not in_single
            continue
        if char == '"' and not in_single:
            in_double = not in_double
            continue
        if char == "#" and not in_single and not in_double:
            if index == 0 or value[index - 1].isspace():
                return value[:index].rstrip()
    return value


def _strip_env_quotes(value: str) -> str:
    value = _strip_inline_comment(value).strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        quote = value[0]
        value = value[1:-1]
        if quote == '"':
            value = value.replace("\\n", "\n").replace('\\"', '"').replace("\\\\", "\\")
    return value


def _quote_env_value(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return f'"{escaped}"'


def read_env_file(env_path: str | Path = ENV_PATH) -> dict[str, str]:
    path = Path(env_path)
    if not path.exists():
        return {}

    values = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = _ENV_LINE_RE.match(line)
        if match:
            values[match.group(2)] = _strip_env_quotes(match.group(4))
    return values


def read_model_env_values(env_path: str | Path = ENV_PATH) -> dict[str, str]:
    file_values = read_env_file(env_path)
    return {key: file_values.get(key, os.getenv(key, "") or "") for key in MODEL_ENV_KEYS}


def split_model_list(value: str | None) -> list[str]:
    if not value:
        return []
    return [model.strip() for model in value.split(",") if model.strip()]


def infer_provider_name(api_base: str | None) -> str:
    base = (api_base or "").lower()
    if "xiaomimimo" in base or "mimo" in base:
        return "小米 MiMo"
    return "OpenAI"


def normalize_model_config(config: dict) -> dict[str, str] | None:
    normalized = {
        "provider": str(config.get("provider", "") or "").strip(),
        "model": str(config.get("model", "") or "").strip(),
        "api_base": str(config.get("api_base", "") or "").strip(),
        "api_key": str(config.get("api_key", "") or "").strip(),
    }
    if not normalized["provider"] or not normalized["model"]:
        return None
    return normalized


def _read_model_configs_json(raw_value: str | None) -> list[dict[str, str]] | None:
    if raw_value is None:
        return None
    raw_value = raw_value.strip()
    if raw_value == "":
        return []
    try:
        parsed = json.loads(raw_value)
    except json.JSONDecodeError:
        return []
    if not isinstance(parsed, list):
        return []
    configs = []
    for item in parsed:
        if isinstance(item, dict):
            normalized = normalize_model_config(item)
            if normalized:
                configs.append(normalized)
    return configs


def _legacy_model_configs(values: dict[str, str]) -> list[dict[str, str]]:
    api_key = values.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY", "")
    api_base = values.get("OPENAI_API_BASE") or os.getenv("OPENAI_API_BASE", "")
    proxy_models = values.get("OPENAI_PROXY_MODELS") or os.getenv("OPENAI_PROXY_MODELS", "")
    model_name = values.get("OPENAI_MODEL_NAME") or os.getenv("OPENAI_MODEL_NAME", "")
    models = split_model_list(proxy_models) or split_model_list(model_name)
    if not models:
        return []

    provider = infer_provider_name(api_base)
    return [
        {
            "provider": provider,
            "model": model,
            "api_base": api_base,
            "api_key": api_key,
        }
        for model in models
    ]


def read_model_configs(env_path: str | Path = ENV_PATH) -> list[dict[str, str]]:
    values = read_env_file(env_path)
    raw_configs = os.getenv(MODEL_CONFIGS_ENV_KEY)
    if raw_configs is None:
        raw_configs = values.get(MODEL_CONFIGS_ENV_KEY)

    configs = _read_model_configs_json(raw_configs)
    if configs is not None:
        return configs
    return _legacy_model_configs(values)


def write_model_configs(env_path: str | Path, configs: list[dict[str, str]]) -> None:
    normalized_configs = []
    for config in configs:
        normalized = normalize_model_config(config)
        if normalized:
            normalized_configs.append(normalized)
    raw_value = json.dumps(normalized_configs, ensure_ascii=False, separators=(",", ":"))
    update_env_file(env_path, {MODEL_CONFIGS_ENV_KEY: raw_value})


def apply_model_configs(configs: list[dict[str, str]]) -> None:
    normalized_configs = []
    for config in configs:
        normalized = normalize_model_config(config)
        if normalized:
            normalized_configs.append(normalized)
    os.environ[MODEL_CONFIGS_ENV_KEY] = json.dumps(normalized_configs, ensure_ascii=False, separators=(",", ":"))


def update_env_file(env_path: str | Path, values: dict[str, str]) -> None:
    path = Path(env_path)
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True) if path.exists() else []
    remaining = dict(values)
    updated_lines = []

    for line in lines:
        match = _ENV_LINE_RE.match(line.rstrip("\r\n"))
        if not match:
            updated_lines.append(line)
            continue

        key = match.group(2)
        if key not in remaining:
            updated_lines.append(line)
            continue

        newline = "\r\n" if line.endswith("\r\n") else "\n"
        updated_lines.append(f"{match.group(1)}{key}{match.group(3)}={_quote_env_value(remaining.pop(key) or '')}{newline}")

    if updated_lines and not updated_lines[-1].endswith(("\n", "\r\n")):
        updated_lines[-1] += "\n"

    for key, value in remaining.items():
        updated_lines.append(f"{key}={_quote_env_value(value or '')}\n")

    path.write_text("".join(updated_lines), encoding="utf-8")


def apply_env_values(values: dict[str, str]) -> None:
    for key, value in values.items():
        if value:
            os.environ[key] = value
        else:
            os.environ.pop(key, None)
