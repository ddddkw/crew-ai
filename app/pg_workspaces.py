import os

import streamlit as st
from streamlit import session_state as ss

import db_utils
from i18n import t
from my_workspace import MyWorkspace
from page_chrome import draw_page_header
from workspace_fs import WorkspacePathError, get_parent_directory, list_selectable_directories, normalize_workspace_path


class PageWorkspaces:
    def __init__(self):
        self.name = t("page.workspaces")

    def create_workspace(self):
        workspace = MyWorkspace(
            name=t("workspace.default_name"),
            path=os.getcwd(),
        )
        workspace.path = normalize_workspace_path(workspace.path)
        ss.workspaces.append(workspace)
        ss.workspace_edit_id = workspace.id
        db_utils.save_workspace(workspace)

    def _is_editing(self, workspace):
        return ss.get("workspace_edit_id") == workspace.id

    def _path_key(self, workspace):
        return f"workspace-path-{workspace.id}"

    def _browse_key(self, workspace):
        return f"workspace-browse-path-{workspace.id}"

    def _init_directory_picker(self, workspace):
        path_key = self._path_key(workspace)
        browse_key = self._browse_key(workspace)
        if path_key not in ss:
            ss[path_key] = workspace.path
        if browse_key not in ss:
            try:
                ss[browse_key] = normalize_workspace_path(ss[path_key] or os.getcwd())
            except WorkspacePathError:
                ss[browse_key] = normalize_workspace_path(os.getcwd())
        return path_key, browse_key

    def _draw_directory_picker(self, workspace):
        path_key, browse_key = self._init_directory_picker(workspace)
        selected_path = ss.get(path_key, workspace.path)

        st.markdown(f"**{t('workspace.current_path')}**")
        st.code(selected_path or t("workspace.empty"), language=None)

        with st.container(border=True, key=f"workspace-directory-picker-{workspace.id}"):
            st.caption(t("workspace.directory_picker_help"))
            try:
                browse_path = normalize_workspace_path(ss.get(browse_key) or selected_path or os.getcwd())
            except WorkspacePathError:
                browse_path = normalize_workspace_path(os.getcwd())
                ss[browse_key] = browse_path

            st.markdown(f"**{t('workspace.browse_path')}:** `{browse_path}`")
            col_parent, col_select = st.columns([1, 1])
            with col_parent:
                if st.button(t("workspace.open_parent"), key=f"workspace-parent-{workspace.id}", use_container_width=True):
                    ss[browse_key] = get_parent_directory(browse_path)
                    st.rerun()
            with col_select:
                if st.button(t("button.use_current_directory"), key=f"workspace-use-current-{workspace.id}", type="primary", use_container_width=True):
                    ss[path_key] = browse_path
                    st.rerun()

            directories = list_selectable_directories(browse_path)
            if not directories:
                st.caption(t("workspace.no_subdirectories"))
                return

            for row_start in range(0, len(directories), 3):
                cols = st.columns(3)
                for index, directory in enumerate(directories[row_start:row_start + 3]):
                    with cols[index]:
                        if st.button(directory["name"], key=f"workspace-dir-{workspace.id}-{row_start}-{index}", use_container_width=True):
                            ss[browse_key] = directory["path"]
                            st.rerun()

    def _draw_workspace_form(self, workspace):
        self._draw_directory_picker(workspace)

        with st.form(f"workspace-form-{workspace.id}"):
            name = st.text_input(t("workspace.name"), value=workspace.name)
            tech_stack = st.text_area(t("workspace.tech_stack"), value=workspace.tech_stack, height=90)
            col_start, col_test = st.columns(2)
            with col_start:
                start_command = st.text_input(t("workspace.start_command"), value=workspace.start_command)
            with col_test:
                test_command = st.text_input(t("workspace.test_command"), value=workspace.test_command)

            st.markdown(f"#### {t('workspace.permissions')}")
            col_read, col_write, col_command = st.columns(3)
            with col_read:
                allow_read = st.checkbox(t("workspace.allow_read"), value=workspace.allow_read)
            with col_write:
                allow_write = st.checkbox(t("workspace.allow_write"), value=workspace.allow_write)
            with col_command:
                allow_command = st.checkbox(t("workspace.allow_command"), value=workspace.allow_command)

            col_save, col_cancel = st.columns(2)
            with col_save:
                submitted = st.form_submit_button(t("button.save"), type="primary")
            with col_cancel:
                cancelled = st.form_submit_button(t("button.cancel"))

        if cancelled:
            ss.workspace_edit_id = None
            st.rerun()

        if submitted:
            try:
                workspace.path = normalize_workspace_path(ss.get(self._path_key(workspace), workspace.path))
            except WorkspacePathError as exc:
                st.error(str(exc))
                return

            workspace.name = name.strip() or t("workspace.default_name")
            workspace.tech_stack = tech_stack
            workspace.start_command = start_command
            workspace.test_command = test_command
            workspace.allow_read = allow_read
            workspace.allow_write = allow_write
            workspace.allow_command = allow_command
            db_utils.save_workspace(workspace)
            ss.workspaces = db_utils.load_workspaces()
            ss.workspace_edit_id = None
            st.success(t("workspace.saved"))
            st.rerun()

    def _permission_summary(self, workspace):
        enabled = []
        if workspace.allow_read:
            enabled.append(t("workspace.allow_read_short"))
        if workspace.allow_write:
            enabled.append(t("workspace.allow_write_short"))
        if workspace.allow_command:
            enabled.append(t("workspace.allow_command_short"))
        return " / ".join(enabled) if enabled else t("workspace.no_permissions")

    def _draw_workspace(self, workspace):
        title = f"{workspace.name} - {workspace.path}"
        with st.expander(title, expanded=self._is_editing(workspace)):
            if self._is_editing(workspace):
                self._draw_workspace_form(workspace)
                return

            st.markdown(f"**{t('workspace.path')}:** `{workspace.path}`")
            st.markdown(f"**{t('workspace.tech_stack')}:** {workspace.tech_stack or t('workspace.empty')}")
            st.markdown(f"**{t('workspace.start_command')}:** `{workspace.start_command or '-'}`")
            st.markdown(f"**{t('workspace.test_command')}:** `{workspace.test_command or '-'}`")
            st.markdown(f"**{t('workspace.permissions')}:** {self._permission_summary(workspace)}")

            col_edit, col_delete = st.columns(2)
            with col_edit:
                if st.button(t("button.edit"), key=f"edit-workspace-{workspace.id}"):
                    ss.workspace_edit_id = workspace.id
                    st.rerun()
            with col_delete:
                if st.button(t("button.delete"), key=f"delete-workspace-{workspace.id}"):
                    db_utils.delete_workspace(workspace.id)
                    ss.workspaces = db_utils.load_workspaces()
                    st.rerun()

    def draw(self):
        if "workspaces" not in ss:
            ss.workspaces = db_utils.load_workspaces()
        if "workspace_edit_id" not in ss:
            ss.workspace_edit_id = None

        draw_page_header(
            self.name,
            section=t("nav.development"),
            subtitle=t("workspace.subtitle"),
            count=len(ss.workspaces),
        )

        with st.container(border=True, key="workspaces-list-card"):
            if not ss.workspaces:
                st.info(t("workspace.none_defined"))

            for workspace in ss.workspaces:
                self._draw_workspace(workspace)

            st.button(
                t("button.create_workspace"),
                on_click=self.create_workspace,
                disabled=ss.workspace_edit_id is not None,
            )
