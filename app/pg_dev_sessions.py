from datetime import datetime
from html import escape
import time

import streamlit as st
from streamlit import session_state as ss

import db_utils
from dev_actions import DevActionError, apply_development_actions
from dev_chat import DevChatError, generate_development_reply
from dev_session import DevSession
from i18n import t
from llms import llm_providers_and_models


class PageDevSessions:
    def __init__(self):
        self.name = t("page.dev_sessions")

    def _sessions_for_workspace(self, workspace_id):
        return [session for session in ss.get("dev_sessions", []) if session.workspace_id == workspace_id]

    def _all_sessions(self):
        return list(ss.get("dev_sessions", []))

    def _search_query(self):
        return str(ss.get("dev_session_search_query") or "").strip().lower()

    def _matches_search(self, session):
        query = self._search_query()
        if not query:
            return True
        haystack = f"{self._session_title(session, limit=500)} {session.requirement}".lower()
        return query in haystack

    def _visible_sessions_for_workspace(self, workspace_id):
        return [session for session in self._sessions_for_workspace(workspace_id) if self._matches_search(session)]

    def _session_title(self, session, limit=42):
        title = session.requirement or ""
        if not title and session.messages:
            title = str(session.messages[0].get("content") or "")
        title = " ".join(str(title).split()) or t("dev_session.untitled_chat")
        if len(title) <= limit:
            return title
        return f"{title[:limit - 1]}..."

    def _relative_age(self, session):
        raw_time = getattr(session, "updated_at", None) or getattr(session, "created_at", None)
        try:
            timestamp = datetime.fromisoformat(raw_time)
        except (TypeError, ValueError):
            return ""

        delta = datetime.now() - timestamp
        minutes = max(1, int(delta.total_seconds() // 60))
        if minutes < 60:
            return f"{minutes}m"
        hours = minutes // 60
        if hours < 24:
            return f"{hours}h"
        return f"{hours // 24}d"

    def _workspace_label(self, workspace):
        return f"{workspace.name}  |  {workspace.path}"

    def _workspace_dropdown_label(self, workspace):
        name = str(workspace.name or "").strip() or t("dev_session.select_workspace")
        path = str(workspace.path or "").strip().rstrip("\\/")
        folder = path.replace("/", "\\").split("\\")[-1] if path else ""
        if folder and folder != name:
            return f"{name} · {folder}"
        return name

    def _selected_workspace(self, workspaces):
        workspaces_by_id = {workspace.id: workspace for workspace in workspaces}
        selected_workspace_id = ss.get("selected_dev_workspace_id")
        selected_session_id = ss.get("selected_dev_session_id")
        sessions_by_id = {session.id: session for session in self._all_sessions()}

        if selected_session_id in sessions_by_id:
            selected_workspace_id = sessions_by_id[selected_session_id].workspace_id
        if selected_workspace_id not in workspaces_by_id:
            selected_workspace_id = workspaces[0].id

        ss.selected_dev_workspace_id = selected_workspace_id
        return workspaces_by_id[selected_workspace_id]

    def _selected_session(self, workspace):
        sessions = self._sessions_for_workspace(workspace.id)
        session_ids = [session.id for session in sessions]
        selected_id = ss.get("selected_dev_session_id")
        if selected_id in session_ids:
            if "dev_session_new_chat" in ss:
                del ss["dev_session_new_chat"]
            return next(session for session in sessions if session.id == selected_id)
        if ss.get("dev_session_new_chat"):
            return None
        if sessions:
            ss.selected_dev_session_id = sessions[0].id
            return sessions[0]
        return None

    def _start_new_chat(self, workspace=None):
        if workspace is not None:
            ss.selected_dev_workspace_id = workspace.id
        ss.dev_session_new_chat = True
        if "selected_dev_session_id" in ss:
            del ss["selected_dev_session_id"]
        st.rerun()

    def _select_thread(self, workspace, session):
        ss.selected_dev_workspace_id = workspace.id
        ss.selected_dev_session_id = session.id
        if "dev_session_new_chat" in ss:
            del ss["dev_session_new_chat"]
        st.rerun()

    def _open_settings(self):
        ss.page = t("page.model_settings")
        st.rerun()

    def _create_session(self, workspace, requirement, selected_model):
        session = DevSession(
            workspace_id=workspace.id,
            requirement=requirement,
            llm_provider_model=selected_model,
            messages=[{"role": "user", "content": requirement}],
            status="thinking",
            logs=[t("dev_session.created_log")],
        )
        db_utils.save_dev_session(session)
        ss.dev_sessions = db_utils.load_dev_sessions()
        ss.selected_dev_session_id = session.id
        if "dev_session_new_chat" in ss:
            del ss["dev_session_new_chat"]
        return session

    def _attach_action_summary(self, session, workspace, reply):
        try:
            summary = apply_development_actions(session, workspace, reply)
        except DevActionError as exc:
            summary = f"开发动作执行失败: {exc}"
            session.status = "failed"
            session.logs = list(session.logs) + [summary]
        if not summary:
            return reply
        return f"{reply}\n\n---\n{summary}"

    def _pending_indicator_html(self):
        return (
            f'<div class="dev-session-thinking" role="status" aria-live="polite">'
            f'<span class="dev-session-thinking-dot"></span>'
            f'<span>{escape(t("dev_session.thinking"))}</span>'
            f'</div>'
        )

    def _draw_pending_indicator(self, slot=None):
        target = slot if slot is not None else st
        target.markdown(self._pending_indicator_html(), unsafe_allow_html=True)

    def _draw_working_status(self, slot, started_at):
        elapsed = max(1, int(time.perf_counter() - started_at))
        slot.markdown(
            f'<div class="dev-session-working">Working for {elapsed}s</div>',
            unsafe_allow_html=True,
        )

    def _assistant_message_html(self, content, streaming=False):
        role_label = escape(t("dev_session.assistant_message"))
        safe_content = escape(str(content or "")).replace("\n", "<br>")
        cursor = '<span class="dev-session-stream-cursor"></span>' if streaming else ""
        return (
            f'<div class="dev-session-chat-message is-assistant">'
            f'<div class="dev-session-chat-role">{role_label}</div>'
            f'<div class="dev-session-chat-content">{safe_content}{cursor}</div>'
            f"</div>"
        )

    def _stream_text_chunks(self, text):
        text = str(text or "")
        if not text:
            return []
        chunk_size = max(3, len(text) // 120)
        return [text[index:index + chunk_size] for index in range(0, len(text), chunk_size)]

    def _stream_assistant_reply(self, slot, reply):
        rendered = ""
        chunks = self._stream_text_chunks(reply)
        for chunk in chunks:
            rendered += chunk
            slot.markdown(self._assistant_message_html(rendered, streaming=True), unsafe_allow_html=True)
            if not ss.get("dev_session_disable_stream_delay"):
                time.sleep(0.012)
        slot.markdown(self._assistant_message_html(reply), unsafe_allow_html=True)

    def _queue_pending_session(self, session):
        ss.dev_session_pending_id = session.id
        ss.dev_sessions = db_utils.load_dev_sessions()
        st.rerun()

    def _complete_pending_reply(self, workspace, session, working_slot, stream_slot):
        started_at = time.perf_counter()
        self._draw_working_status(working_slot, started_at)
        try:
            reply = generate_development_reply(session, workspace)
        except DevChatError as exc:
            session.status = "failed"
            db_utils.save_dev_session(session)
            ss.dev_sessions = db_utils.load_dev_sessions()
            if ss.get("dev_session_pending_id") == session.id:
                del ss["dev_session_pending_id"]
            st.error(t("dev_session.message_failed", error=str(exc)))
            return

        self._draw_working_status(working_slot, started_at)
        reply = self._attach_action_summary(session, workspace, reply)
        self._stream_assistant_reply(stream_slot, reply)
        session.add_message("assistant", reply)
        session.status = "failed" if session.status == "failed" else "chatting"
        session.logs = list(session.logs) + [
            t("dev_session.message_sent_log", model=session.llm_provider_model)
        ]
        db_utils.save_dev_session(session)
        ss.dev_sessions = db_utils.load_dev_sessions()
        if ss.get("dev_session_pending_id") == session.id:
            del ss["dev_session_pending_id"]
        st.rerun()

    def _queue_new_session(self, workspace, message, selected_model):
        session = self._create_session(workspace, message, selected_model)
        self._queue_pending_session(session)

    def _create_thread_from_message(self, workspace, message, selected_model):
        message = str(message or "").strip()
        if not selected_model:
            st.warning(t("dev_session.no_models"))
            return
        if not message:
            st.warning(t("dev_session.empty_requirement_warning"))
            return

        self._queue_new_session(workspace, message, selected_model)

    def _delete_session(self, session):
        selected_session_id = ss.get("selected_dev_session_id")
        db_utils.delete_dev_session(session.id)
        ss.dev_sessions = db_utils.load_dev_sessions()
        remaining_sessions = self._sessions_for_workspace(session.workspace_id)
        remaining_session_ids = {remaining_session.id for remaining_session in remaining_sessions}
        if selected_session_id in remaining_session_ids:
            ss.selected_dev_session_id = selected_session_id
        elif remaining_sessions:
            ss.selected_dev_session_id = remaining_sessions[0].id
        elif "selected_dev_session_id" in ss:
            del ss["selected_dev_session_id"]
        ss.dev_session_flash = t("dev_session.deleted")
        st.rerun()

    def _send_chat_message(self, workspace, session, message):
        message = str(message or "").strip()
        if not message:
            st.warning(t("dev_session.empty_message_warning"))
            return

        session.add_message("user", message)
        session.status = "thinking"
        db_utils.save_dev_session(session)
        self._queue_pending_session(session)

    def _model_parts(self, provider_and_model):
        if provider_and_model and ": " in provider_and_model:
            return provider_and_model.split(": ", 1)
        return t("dev_session.no_model_selected"), ""

    def _model_badges_html(self, provider_and_model):
        provider, model = self._model_parts(provider_and_model)
        provider_label = escape(provider)
        model_label = escape(model)
        return (
            f'<span class="dev-session-model-provider">{provider_label}</span>'
            f'<span class="dev-session-model-name">{model_label}</span>'
        )

    def _draw_lane_summary(self, workspace):
        session_count = len(self._sessions_for_workspace(workspace.id))
        st.markdown(
            f'<div class="dev-session-lane-summary">'
            f'<div class="dev-session-lane-eyebrow">{escape(t("nav.development"))}</div>'
            f'<div class="dev-session-lane-title">{escape(workspace.name)}</div>'
            f'<div class="dev-session-lane-path">{escape(workspace.path)}</div>'
            f'<div class="dev-session-lane-stats">'
            f'<span>{session_count}</span>'
            f'<span>{escape(t("dev_session.sessions"))}</span>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    def _draw_click_only_dropdown(
        self,
        selected_label,
        options,
        key,
        on_select,
        help_text=None,
        selected_option=None,
    ):
        selected_option = selected_label if selected_option is None else selected_option
        with st.container(border=False, key=key):
            with st.popover(selected_label, help=help_text, use_container_width=True):
                for option_index, option_label in enumerate(options):
                    is_selected = option_label == selected_option
                    button_label = f"✓ {option_label}" if is_selected else option_label
                    if st.button(
                        button_label,
                        key=f"{key}-option-{option_index}",
                        use_container_width=True,
                        disabled=is_selected,
                    ):
                        on_select(option_label)
                        st.rerun()

    def _draw_workspace_selector(self, workspaces, selected_workspace):
        labels = [self._workspace_label(workspace) for workspace in workspaces]
        label_to_workspace = dict(zip(labels, workspaces))
        selected_option = self._workspace_label(selected_workspace)
        selected_label = self._workspace_dropdown_label(selected_workspace)
        st.markdown(
            f'<div class="dev-session-selector-label">{escape(t("dev_session.select_workspace"))}</div>',
            unsafe_allow_html=True,
        )

        def select_workspace(chosen_label):
            chosen_workspace = label_to_workspace[chosen_label]
            ss.selected_dev_workspace_id = chosen_workspace.id
            if "selected_dev_session_id" in ss:
                del ss["selected_dev_session_id"]

        self._draw_click_only_dropdown(
            selected_label,
            labels,
            key="dev-session-workspace-dropdown",
            on_select=select_workspace,
            help_text=t("dev_session.select_workspace"),
            selected_option=selected_option,
        )

    def _sidebar_thread_button(self, workspace, session):
        active = ss.get("selected_dev_session_id") == session.id
        title = self._session_title(session, limit=30)
        age = self._relative_age(session)
        button_label = f"{title}  {age}" if age else title
        if st.button(
            button_label,
            key=f"dev-session-session-{session.id}",
            use_container_width=True,
            type="primary" if active else "secondary",
            disabled=active,
        ):
            self._select_thread(workspace, session)

    def _draw_sidebar_session_row(self, workspace, session):
        with st.container(border=False, key=f"dev-session-session-row-{session.id}"):
            session_col, delete_col = st.columns([0.84, 0.16], gap="small")
            with session_col:
                self._sidebar_thread_button(workspace, session)
            with delete_col:
                with st.container(border=False, key=f"dev-session-session-delete-{session.id}"):
                    if st.button(
                        "×",
                        key=f"delete-dev-session-sidebar-{session.id}",
                        help=t("dev_session.delete_session"),
                        use_container_width=True,
                    ):
                        self._delete_session(session)

    def _draw_session_list(self, workspace):
        sessions = self._visible_sessions_for_workspace(workspace.id)
        st.markdown(
            f'<div class="dev-session-section-header">'
            f'<span class="dev-session-section-label">{escape(t("dev_session.sessions"))}</span>'
            f"</div>",
            unsafe_allow_html=True,
        )
        with st.container(border=False, key="dev-session-session-list"):
            st.markdown('<div class="dev-session-session-list"></div>', unsafe_allow_html=True)
            if not sessions:
                empty_message = (
                    t("dev_session.no_session_matches")
                    if self._search_query()
                    else t("dev_session.no_sessions")
                )
                st.markdown(
                    f'<div class="dev-session-empty-state">'
                    f'<div class="dev-session-empty-title">{escape(t("dev_session.sessions"))}</div>'
                    f'<div class="dev-session-empty-copy">{escape(empty_message)}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                return
            for session in sessions:
                self._draw_sidebar_session_row(workspace, session)

    def _draw_flash_message(self):
        message = ss.get("dev_session_flash")
        if not message:
            return
        st.markdown(
            f'<div class="dev-session-inline-notice">{escape(str(message))}</div>',
            unsafe_allow_html=True,
        )
        del ss["dev_session_flash"]

    def _draw_session_lane(self, workspaces, selected_workspace):
        with st.container(border=False, key="dev-session-lane"):
            st.markdown('<div class="dev-session-lane-card"></div>', unsafe_allow_html=True)
            self._draw_lane_summary(selected_workspace)

            with st.container(border=False, key="dev-session-lane-controls"):
                self._draw_workspace_selector(workspaces, selected_workspace)

                action_col, settings_col = st.columns([0.58, 0.42], gap="small")
                with action_col:
                    if st.button(
                        f"+ {t('dev_session.new_chat')}",
                        key="dev-session-new-chat-sidebar",
                        use_container_width=True,
                        type="primary",
                    ):
                        self._start_new_chat(selected_workspace)
                with settings_col:
                    if st.button(
                        t("dev_session.settings"),
                        key="dev-session-settings-button",
                        use_container_width=True,
                    ):
                        self._open_settings()

                st.text_input(
                    t("dev_session.search"),
                    key="dev_session_search_query",
                    placeholder=t("dev_session.search"),
                    label_visibility="collapsed",
                )
            self._draw_flash_message()
            self._draw_session_list(selected_workspace)

    def _message_html(self, message):
        role = message.get("role", "assistant")
        content = escape(str(message.get("content") or "")).replace("\n", "<br>")
        if role == "user":
            return (
                f'<div class="dev-session-user-message-row">'
                f'<div class="dev-session-current-user-bubble">{content}</div>'
                f'<div class="dev-session-copy-icon" title="{escape(t("dev_session.copy_message"))}">copy</div>'
                f"</div>"
            )

        return self._assistant_message_html(message.get("content") or "")

    def _draw_message_thread(self, session):
        messages = session.messages or [
            {"role": "user", "content": session.requirement or t("dev_session.empty_requirement")}
        ]
        rendered_messages = "".join(self._message_html(message) for message in messages)
        if session.status == "thinking":
            rendered_messages += self._pending_indicator_html()
        st.markdown(
            f'<div class="dev-session-message dev-session-chat-thread">{rendered_messages}</div>',
            unsafe_allow_html=True,
        )

    def _draw_thread_header(self, workspace, session):
        title = self._session_title(session) if session else workspace.name
        status = getattr(session, "status", "") or t("dev_session.current_chat")
        title_col, delete_col = st.columns([0.78, 0.22], gap="small")
        with title_col:
            st.markdown(
                f'<div class="dev-session-topbar">'
                f'<div>'
                f'<div class="dev-session-topbar-title">{escape(title)}</div>'
                f'<div class="dev-session-topbar-subtitle">{escape(workspace.path)}</div>'
                f'</div>'
                f'<div class="dev-session-topbar-actions">'
                f'<span>{escape(status)}</span>'
                f'{self._model_badges_html(session.llm_provider_model)}'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        with delete_col:
            if st.button(t("dev_session.delete_session"), key=f"delete-dev-session-{session.id}"):
                self._delete_session(session)

    def _draw_chat_composer(self, workspace, session):
        is_new_thread = session is None
        message_key = (
            f"new-dev-session-requirement-{workspace.id}"
            if is_new_thread
            else f"dev-session-message-input-{session.id}"
        )

        if not is_new_thread:
            with st.container(border=False, key="dev-session-bottom-composer"):
                with st.container(border=False, key=f"dev-session-followup-composer-{session.id}"):
                    message = st.text_area(
                        t("dev_session.message_placeholder"),
                        placeholder=t("dev_session.message_placeholder"),
                        height=78,
                        label_visibility="collapsed",
                        key=message_key,
                    )
                    button_key = f"dev-session-send-arrow-{session.id}"
                    if st.button("↑", key=button_key, help=t("dev_session.send_message")):
                        st.markdown('<div class="dev-session-send-button"></div>', unsafe_allow_html=True)
                        self._send_chat_message(workspace, session, ss.get(message_key, message))
            return

        available_models = llm_providers_and_models()
        with st.container(border=False, key="dev-session-home-composer-card"):
            with st.container(border=False, key=f"dev-session-composer-{workspace.id}"):
                with st.container(border=False, key=f"dev-session-new-chat-composer-{workspace.id}"):
                    message = st.text_area(
                        t("dev_session.requirement"),
                        placeholder=t("dev_session.requirement_placeholder"),
                        height=82,
                        label_visibility="collapsed",
                        key=message_key,
                    )

                    with st.container(border=False, key=f"dev-session-composer-toolbar-{workspace.id}"):
                        _, model_col, action_col = st.columns([0.64, 0.28, 0.08], gap="small")
                        with model_col:
                            if available_models:
                                model_key = f"new-dev-session-model-{workspace.id}"
                                selected_model = ss.get(model_key)
                                if selected_model not in available_models:
                                    selected_model = available_models[0]
                                    ss[model_key] = selected_model
                                with st.container(
                                    border=False,
                                    key=f"new-dev-session-model-dropdown-{workspace.id}",
                                ):
                                    with st.popover(
                                        selected_model,
                                        help=t("dev_session.llm_provider_model"),
                                        use_container_width=True,
                                    ):
                                        for model_index, model_label in enumerate(available_models):
                                            is_selected = model_label == selected_model
                                            option_label = f"✓ {model_label}" if is_selected else model_label
                                            if st.button(
                                                option_label,
                                                key=f"new-dev-session-model-option-{workspace.id}-{model_index}",
                                                use_container_width=True,
                                                disabled=is_selected,
                                            ):
                                                ss[model_key] = model_label
                                                st.rerun()
                            else:
                                selected_model = None
                                st.warning(t("dev_session.no_models"))
                        with action_col:
                            if st.button("↑", key=f"dev-session-create-arrow-{workspace.id}", help=t("dev_session.send_message")):
                                st.markdown('<div class="dev-session-send-button"></div>', unsafe_allow_html=True)
                                self._create_thread_from_message(workspace, ss.get(message_key, message), selected_model)

    def _draw_empty_home(self, workspace):
        with st.container(border=False, key="dev-session-home"):
            with st.container(border=False, key="dev-session-home-shell"):
                st.markdown(
                    f'<div class="dev-session-home-card dev-session-layout">'
                    f'<div class="dev-session-home-kicker">{escape(t("page.dev_sessions"))}</div>'
                    f'<div class="dev-session-home-context">{escape(workspace.name)}</div>'
                    f'<div class="dev-session-hero-title">{escape(t("dev_session.hero_title"))}</div>'
                    f'<div class="dev-session-home-subtitle">{escape(t("dev_session.empty_thread_hint"))}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                with st.container(border=False, key="dev-session-home-spacer-wrap"):
                    st.markdown('<div class="dev-session-home-spacer" aria-hidden="true"></div>', unsafe_allow_html=True)
                self._draw_chat_composer(workspace, None)

    def _draw_session_editor(self, session):
        with st.container(border=False, key="dev-session-codex-prose"):
            self._draw_message_thread(session)

    def _draw_main_thread(self, workspace, session):
        with st.container(border=False, key="dev-session-conversation"):
            if session is None:
                self._draw_empty_home(workspace)
                return

            self._draw_thread_header(workspace, session)
            with st.container(border=False, key=f"dev-session-thread-{session.id}"):
                with st.container(border=False, key="dev-session-chat-canvas"):
                    st.markdown('<div class="dev-session-codex-stream"></div>', unsafe_allow_html=True)
                    self._draw_session_editor(session)
                    if session.status == "thinking" and ss.get("dev_session_pending_id") == session.id:
                        working_slot = st.empty()
                        stream_slot = st.empty()
                        self._complete_pending_reply(workspace, session, working_slot, stream_slot)
            self._draw_chat_composer(workspace, session)

    def draw(self):
        if "workspaces" not in ss:
            ss.workspaces = db_utils.load_workspaces()
        if "dev_sessions" not in ss:
            ss.dev_sessions = db_utils.load_dev_sessions()

        if not ss.workspaces:
            st.info(t("dev_session.no_workspaces"))
            return

        workspaces = ss.workspaces
        selected_workspace = self._selected_workspace(workspaces)
        selected_session = self._selected_session(selected_workspace)

        with st.container(border=False, key="dev-session-workbench"):
            lane_col, main_col = st.columns([0.23, 0.77], gap="medium")
            with lane_col:
                self._draw_session_lane(workspaces, selected_workspace)
            with main_col:
                self._draw_main_thread(selected_workspace, selected_session)
