from datetime import datetime
import os
from pathlib import Path

import streamlit as st
from streamlit import session_state as ss

import db_utils
from i18n import t
from utils import fix_columns_width, rnd_id


class MyKnowledgeSource:
    def __init__(
        self,
        id=None,
        name=None,
        source_type=None,
        source_path=None,
        content=None,
        metadata=None,
        chunk_size=None,
        chunk_overlap=None,
        created_at=None,
        type=None,
        file_path=None,
        description=None,
        workspace_id=None,
    ):
        self.id = id or "KS_" + rnd_id()
        self.name = name or "Knowledge Source 1"
        self.source_type = source_type or type or "string"
        self.source_path = source_path if source_path is not None else (file_path or "")
        self.content = content or ""
        self.metadata = metadata or {}
        self.chunk_size = chunk_size or 4000
        self.chunk_overlap = chunk_overlap or 200
        self.created_at = created_at or datetime.now().isoformat()
        self.description = description or ""
        self.workspace_id = workspace_id
        self.edit_key = f"edit_{self.id}"
        if self.edit_key not in ss:
            ss[self.edit_key] = False

    @property
    def edit(self):
        return ss[self.edit_key]

    @edit.setter
    def edit(self, value):
        ss[self.edit_key] = value

    def find_file(self, file_path):
        if not file_path:
            return None
        if Path("knowledge", file_path).exists():
            return file_path
        return None

    def get_crewai_knowledge_source(self):
        if self.source_type == "string":
            from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource

            return StringKnowledgeSource(
                content=self.content,
                metadata=self.metadata,
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
            )
        if self.source_type == "docling":
            from crewai.knowledge.source.crew_docling_source import CrewDoclingSource

            return CrewDoclingSource(
                file_paths=[self.source_path],
                metadata=self.metadata,
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
            )

        actual_path = self.find_file(self.source_path)
        if not actual_path:
            raise FileNotFoundError(f"File not found: {self.source_path}")

        if self.source_type == "text_file":
            from crewai.knowledge.source.text_file_knowledge_source import TextFileKnowledgeSource

            return TextFileKnowledgeSource(
                file_paths=[actual_path],
                metadata=self.metadata,
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
            )
        if self.source_type == "pdf":
            from crewai.knowledge.source.pdf_knowledge_source import PDFKnowledgeSource

            return PDFKnowledgeSource(
                file_paths=[actual_path],
                metadata=self.metadata,
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
            )
        if self.source_type == "csv":
            from crewai.knowledge.source.csv_knowledge_source import CSVKnowledgeSource

            return CSVKnowledgeSource(
                file_paths=[actual_path],
                metadata=self.metadata,
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
            )
        if self.source_type == "excel":
            from crewai.knowledge.source.excel_knowledge_source import ExcelKnowledgeSource

            return ExcelKnowledgeSource(
                file_paths=[actual_path],
                metadata=self.metadata,
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
            )
        if self.source_type == "json":
            from crewai.knowledge.source.json_knowledge_source import JSONKnowledgeSource

            return JSONKnowledgeSource(
                file_paths=[actual_path],
                metadata=self.metadata,
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
            )
        raise ValueError(f"Unsupported knowledge source type: {self.source_type}")

    def is_valid(self, show_warning=False):
        if self.source_type == "string" and not self.content:
            if show_warning:
                st.warning(f"Knowledge source {self.name} has no content")
            return False

        if self.source_type not in ("string", "docling") and not self.source_path:
            if show_warning:
                st.warning(f"Knowledge source {self.name} has no source path")
            return False

        if self.source_type not in ("string", "docling") and not self.find_file(self.source_path):
            if show_warning:
                st.warning(f"File not found: {self.source_path}")
            return False

        return True

    def delete(self):
        ss.knowledge_sources = [ks for ks in ss.knowledge_sources if ks.id != self.id]
        db_utils.delete_knowledge_source(self.id)

    def draw(self, key=None):
        source_types = {
            "string": t("knowledge.source_types.string"),
            "text_file": t("knowledge.source_types.text_file"),
            "pdf": t("knowledge.source_types.pdf"),
            "csv": t("knowledge.source_types.csv"),
            "excel": t("knowledge.source_types.excel"),
            "json": t("knowledge.source_types.json"),
            "docling": t("knowledge.source_types.docling"),
        }

        if self.edit:
            with st.container():
                st.subheader(f"{t('knowledge.title')}: {self.name}")
                self.name = st.text_input(t("knowledge.name"), value=self.name, key=f"name_{self.id}")

                previous_type = self.source_type
                self.source_type = st.selectbox(
                    t("knowledge.source_type"),
                    options=list(source_types.keys()),
                    format_func=lambda option: source_types[option],
                    index=list(source_types.keys()).index(self.source_type),
                    key=f"type_{self.id}",
                )
                if previous_type != self.source_type:
                    db_utils.save_knowledge_source(self)
                    st.rerun()

                with st.form(key=f"form_{self.id}" if key is None else key):
                    if self.source_type == "string":
                        self.content = st.text_area(t("knowledge.content_preview"), value=self.content, height=200)
                    else:
                        self.source_path = st.text_input(
                            t("knowledge.source_path"),
                            value=self.source_path,
                            help=t("knowledge.source_path_hint"),
                        )
                        if self.source_type != "docling":
                            upload_types = {
                                "text_file": "txt",
                                "pdf": "pdf",
                                "csv": "csv",
                                "excel": ["xlsx", "xls"],
                                "json": "json",
                            }
                            file_type = upload_types.get(self.source_type)
                            if file_type:
                                uploaded_file = st.file_uploader(
                                    t("knowledge.upload_file", type=source_types[self.source_type]),
                                    type=file_type,
                                    key=f"uploader_{self.id}_{self.source_type}",
                                )
                                if uploaded_file is not None:
                                    os.makedirs("knowledge", exist_ok=True)
                                    file_path = os.path.join("knowledge", uploaded_file.name)
                                    with open(file_path, "wb") as file:
                                        file.write(uploaded_file.getbuffer())
                                    self.source_path = uploaded_file.name

                    st.subheader(t("knowledge.advanced_settings"))
                    col1, col2 = st.columns(2)
                    with col1:
                        self.chunk_size = st.number_input(
                            t("knowledge.chunk_size"),
                            value=self.chunk_size,
                            min_value=100,
                            max_value=8000,
                            help=t("knowledge.chunk_size_hint"),
                        )
                    with col2:
                        self.chunk_overlap = st.number_input(
                            t("knowledge.chunk_overlap"),
                            value=self.chunk_overlap,
                            min_value=0,
                            max_value=1000,
                            help=t("knowledge.chunk_overlap_hint"),
                        )

                    col_save, col_cancel = st.columns(2)
                    with col_save:
                        submitted = st.form_submit_button(t("button.save"))
                    with col_cancel:
                        cancelled = st.form_submit_button(t("button.cancel"))
                    if cancelled:
                        self.cancel_edit()
                    elif submitted:
                        db_utils.save_knowledge_source(self)
                        self.set_editable(False)
            return

        fix_columns_width()
        source_name = self.name if self.is_valid() else f"! {self.name}"
        with st.expander(source_name, expanded=False):
            st.markdown(f"**{t('knowledge.name')}:** {self.name}")
            st.markdown(f"**{t('knowledge.source_type')}:** {source_types[self.source_type]}")
            if self.source_type == "string":
                preview = self.content[:100] + "..." if len(self.content) > 100 else self.content
                st.markdown(f"**{t('knowledge.content_preview')}:** {preview}")
            else:
                st.markdown(f"**{t('knowledge.source_path')}:** {self.source_path}")
            st.markdown(f"**{t('knowledge.chunk_size')}:** {self.chunk_size}")
            st.markdown(f"**{t('knowledge.chunk_overlap')}:** {self.chunk_overlap}")

            col1, col2 = st.columns(2)
            with col1:
                st.button(t("button.edit"), on_click=self.set_editable, args=(True,), key=rnd_id())
            with col2:
                st.button(t("button.delete"), on_click=self.delete, key=rnd_id())

            self.is_valid(show_warning=True)

    def set_editable(self, edit):
        self.edit = edit
        self.is_new = False
        db_utils.save_knowledge_source(self)
        if not edit:
            st.rerun()

    def cancel_edit(self):
        if getattr(self, "is_new", False):
            self.delete()
        else:
            self.edit = False
        st.rerun()


KnowledgeSource = MyKnowledgeSource
