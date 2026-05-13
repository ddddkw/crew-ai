import streamlit as st
from streamlit import session_state as ss

import db_utils
from i18n import t
from my_tools import TOOL_CLASSES
from page_chrome import draw_page_header
from utils import rnd_id


class PageTools:
    def __init__(self):
        self.name = t("page.tools")
        self.available_tools = TOOL_CLASSES

    def create_tool(self, tool_name):
        tool_class = self.available_tools[tool_name]
        tool_instance = tool_class(rnd_id())
        if "tools" not in ss:
            ss.tools = []
        ss.tools.append(tool_instance)
        db_utils.save_tool(tool_instance)

    def remove_tool(self, tool_id):
        ss.tools = [tool for tool in ss.tools if tool.tool_id != tool_id]
        db_utils.delete_tool(tool_id)
        st.rerun()

    def set_tool_parameter(self, tool_id, param_name, value):
        if value == "":
            value = None
        for tool in ss.tools:
            if tool.tool_id == tool_id:
                tool.set_parameters(**{param_name: value})
                db_utils.save_tool(tool)
                break

    def get_tool_display_name(self, tool):
        first_param_name = tool.get_parameter_names()[0] if tool.get_parameter_names() else None
        first_param_value = tool.parameters.get(first_param_name, "") if first_param_name else ""
        return f"{tool.name} ({first_param_value if first_param_value else tool.tool_id})"

    def draw_tools(self):
        c1, c2 = st.columns([1, 3])
        with c1:
            with st.container(border=True, key="tools-palette-card"):
                for tool_name in self.available_tools.keys():
                    tool_class = self.available_tools[tool_name]
                    tool_instance = tool_class()
                    tool_description = tool_instance.description
                    if st.button(
                        tool_name,
                        key=f"enable_{tool_name}",
                        help=tool_description,
                        use_container_width=True,
                    ):
                        self.create_tool(tool_name)
        with c2:
            with st.container(border=True, key="tools-enabled-card"):
                if "tools" in ss:
                    st.write(f"##### {t('tools.enabled_tools')}")
                    for tool in ss.tools:
                        display_name = self.get_tool_display_name(tool)
                        is_complete = tool.is_valid()
                        expander_title = display_name if is_complete else f"! {display_name}"
                        with st.expander(expander_title):
                            st.write(tool.description)
                            for param_name in tool.get_parameter_names():
                                param_value = tool.parameters.get(param_name, "")
                                placeholder = t("tools.required") if tool.is_parameter_mandatory(param_name) else t("tools.optional")
                                new_value = st.text_input(
                                    param_name,
                                    value=param_value,
                                    key=f"{tool.tool_id}_{param_name}",
                                    placeholder=placeholder,
                                )
                                if new_value != param_value:
                                    self.set_tool_parameter(tool.tool_id, param_name, new_value)
                            if st.button("Remove", key=f"remove_{tool.tool_id}"):
                                self.remove_tool(tool.tool_id)

    def draw(self):
        enabled_count = len(ss.tools) if "tools" in ss else 0
        draw_page_header(
            self.name,
            section=t("nav.workspace"),
            subtitle=t("tools.enabled_tools"),
            count=enabled_count,
        )
        self.draw_tools()
