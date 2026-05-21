import os

import streamlit as st
from dotenv import load_dotenv

from env_config import MODEL_ENV_KEYS, read_model_configs


DEFAULT_LLM_TIMEOUT_SECONDS = 60


def load_secrets_fron_env():
    load_dotenv(override=True)
    if "env_vars" not in st.session_state:
        st.session_state.env_vars = {key: os.getenv(key) for key in MODEL_ENV_KEYS}
    else:
        st.session_state.env_vars = st.session_state.env_vars


def get_model_label(config):
    return f"{config['provider']}: {config['model']}"


def get_model_config(provider, model):
    for config in read_model_configs():
        if config["provider"] == provider and config["model"] == model:
            return config
    return None


def llm_providers_and_models():
    return [get_model_label(config) for config in read_model_configs()]


def create_llm(provider_and_model, temperature=0.15, timeout=DEFAULT_LLM_TIMEOUT_SECONDS):
    if ": " not in provider_and_model:
        raise ValueError("Input string must be in format 'Provider: Model'")

    provider, model = provider_and_model.split(": ", 1)
    config = get_model_config(provider, model)
    if not config:
        raise ValueError(f"LLM provider/model {provider_and_model} is not configured")
    if not config.get("api_key"):
        raise ValueError(f"API key is not set for {provider_and_model}")
    if not config.get("api_base"):
        raise ValueError(f"API base URL is not set for {provider_and_model}")

    os.environ["OPENAI_API_KEY"] = config["api_key"]
    os.environ["OPENAI_API_BASE"] = config["api_base"]
    from crewai import LLM

    return LLM(
        model=model,
        temperature=temperature,
        timeout=timeout,
        api_key=config["api_key"],
        base_url=config["api_base"],
    )
