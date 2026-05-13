import os

import streamlit as st
from streamlit import session_state as ss
from dotenv import load_dotenv

from env_config import ENV_PATH, MODEL_CONFIG_FIELDS, apply_model_configs, read_model_configs, write_model_configs
from i18n import t
from page_chrome import draw_page_header


class PageModelSettings:
    def __init__(self):
        self.name = t("page.model_settings")

    def _empty_config(self):
        return {
            "provider": "",
            "model": "",
            "api_base": "",
            "api_key": "",
        }

    def _row_count(self, configs):
        if "model_settings_row_count" not in ss:
            ss.model_settings_row_count = max(1, len(configs))
        if len(configs) > ss.model_settings_row_count:
            ss.model_settings_row_count = len(configs)
        return ss.model_settings_row_count

    def _field_widget(self, row_index, field, value):
        field_key = f"model_settings_{row_index}_{field['key']}"
        label = t(field["label_key"])
        help_text = t(field["help_key"])
        if field["secret"]:
            return st.text_input(
                label,
                value=value,
                type="password",
                key=field_key,
                help=help_text,
            )
        return st.text_input(
            label,
            value=value,
            key=field_key,
            help=help_text,
        )

    def _draw_config_row(self, row_index, config):
        st.markdown(f"#### {t('model_settings.model_row', number=row_index + 1)}")
        collected = {}
        col1, col2 = st.columns(2)
        with col1:
            collected["provider"] = self._field_widget(
                row_index,
                MODEL_CONFIG_FIELDS[0],
                config.get("provider", ""),
            )
            collected["api_base"] = self._field_widget(
                row_index,
                MODEL_CONFIG_FIELDS[2],
                config.get("api_base", ""),
            )
        with col2:
            collected["model"] = self._field_widget(
                row_index,
                MODEL_CONFIG_FIELDS[1],
                config.get("model", ""),
            )
            collected["api_key"] = self._field_widget(
                row_index,
                MODEL_CONFIG_FIELDS[3],
                config.get("api_key", ""),
            )
        remove = st.checkbox(t("model_settings.remove_model"), key=f"model_settings_remove_{row_index}")
        return collected, remove

    def draw(self):
        configs = read_model_configs(ENV_PATH)
        row_count = self._row_count(configs)

        draw_page_header(
            self.name,
            section=t("nav.system"),
            subtitle=t("model_settings.description"),
            count=len(configs),
        )

        with st.container(border=True, key="model-settings-card"):
            if st.button(t("model_settings.add_model")):
                ss.model_settings_row_count = row_count + 1
                st.rerun()

            submitted_rows = []
            with st.form("model_settings_form"):
                for index in range(row_count):
                    config = configs[index] if index < len(configs) else self._empty_config()
                    row, remove = self._draw_config_row(index, config)
                    submitted_rows.append((row, remove))
                    if index < row_count - 1:
                        st.divider()

                submitted = st.form_submit_button(t("button.save"))

        if submitted:
            normalized_configs = [
                row
                for row, remove in submitted_rows
                if not remove and (row.get("provider") or row.get("model") or row.get("api_base") or row.get("api_key"))
            ]
            write_model_configs(ENV_PATH, normalized_configs)
            apply_model_configs(normalized_configs)
            load_dotenv(override=True)
            ss.env_vars = {"MODEL_CONFIGS": os.getenv("MODEL_CONFIGS")}
            ss.model_settings_row_count = max(1, len(read_model_configs(ENV_PATH)))
            st.success(t("model_settings.saved"))
