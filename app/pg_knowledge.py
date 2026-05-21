import os
from pathlib import Path
import shutil

import streamlit as st
from streamlit import session_state as ss

import db_utils
from i18n import t
from my_knowledge_source import MyKnowledgeSource
from page_chrome import draw_page_header


class PageKnowledge:
    def __init__(self):
        self.name = t("page.knowledge")

    def create_knowledge_source(self):
        knowledge_source = MyKnowledgeSource()
        if "knowledge_sources" not in ss:
            ss.knowledge_sources = []
        ss.knowledge_sources.append(knowledge_source)
        knowledge_source.is_new = True
        knowledge_source.edit = True
        db_utils.save_knowledge_source(knowledge_source)
        return knowledge_source

    def clear_knowledge(self):
        knowledge_dir = Path.home() / ".crewai" / "knowledge"
        if knowledge_dir.exists():
            shutil.rmtree(knowledge_dir)
            st.success("Knowledge stores cleared successfully!")
        else:
            st.info("No knowledge stores found to clear.")

    def draw(self):
        os.makedirs("knowledge", exist_ok=True)

        editing = False
        if "knowledge_sources" not in ss:
            ss.knowledge_sources = db_utils.load_knowledge_sources()

        draw_page_header(
            self.name,
            section=t("nav.workspace"),
            subtitle=t("knowledge.description"),
            count=len(ss.knowledge_sources),
        )

        with st.container(border=True, key="knowledge-workspace-card"):
            st.button(
                t("button.clear_knowledge"),
                on_click=self.clear_knowledge,
                help=t("knowledge.clear_help"),
            )

            for knowledge_source in ss.knowledge_sources:
                knowledge_source.draw()
                if knowledge_source.edit:
                    editing = True

            if not ss.knowledge_sources:
                st.write(t("knowledge.none_defined"))

            st.button(t("button.create_knowledge"), on_click=self.create_knowledge_source, disabled=editing)
