from pathlib import Path
import sys
from types import SimpleNamespace
import unittest


ROOT = Path(__file__).resolve().parents[1]


class FakeSessionState(dict):
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError as exc:
            raise AttributeError(key) from exc

    def __setattr__(self, key, value):
        self[key] = value


class WorkbenchUiTests(unittest.TestCase):
    def test_app_applies_global_workbench_styles(self):
        source = (ROOT / "app" / "app.py").read_text(encoding="utf-8")

        self.assertIn("from ui_styles import apply_global_styles", source)
        self.assertIn("apply_global_styles()", source)

    def test_frontend_design_system_has_shared_page_chrome(self):
        source = (ROOT / "app" / "page_chrome.py").read_text(encoding="utf-8")
        style_source = (ROOT / "app" / "ui_styles.py").read_text(encoding="utf-8")

        self.assertIn("def draw_page_header", source)
        self.assertIn("studio-page-header", source)
        self.assertIn("studio-page-actions", source)
        self.assertIn(".studio-surface-card", style_source)
        self.assertIn(".studio-muted-panel", style_source)

    def test_core_pages_use_shared_page_header(self):
        pages = [
            "pg_agents.py",
            "pg_tasks.py",
            "pg_tools.py",
            "pg_knowledge.py",
            "pg_model_settings.py",
            "pg_results.py",
            "pg_export_crew.py",
        ]

        for page in pages:
            source = (ROOT / "app" / page).read_text(encoding="utf-8")
            self.assertIn("from page_chrome import draw_page_header", source, page)
            self.assertIn("draw_page_header(", source, page)

    def test_knowledge_source_exports_legacy_model_contract(self):
        app_path = str(ROOT / "app")
        if app_path not in sys.path:
            sys.path.insert(0, app_path)
        from my_knowledge_source import MyKnowledgeSource

        source = MyKnowledgeSource(name="Docs", source_type="string", content="hello")

        self.assertEqual(source.name, "Docs")
        self.assertEqual(source.source_type, "string")
        self.assertEqual(source.content, "hello")
        self.assertTrue(callable(source.get_crewai_knowledge_source))
        self.assertTrue(callable(source.draw))

    def test_knowledge_page_exposes_page_class(self):
        app_path = str(ROOT / "app")
        if app_path not in sys.path:
            sys.path.insert(0, app_path)
        import pg_knowledge

        self.assertTrue(hasattr(pg_knowledge, "PageKnowledge"))
        self.assertTrue(callable(pg_knowledge.PageKnowledge))

    def test_model_settings_rows_are_collapsed_expandable_details(self):
        source = (ROOT / "app" / "pg_model_settings.py").read_text(encoding="utf-8")

        self.assertIn("def _row_title(self, row_index, config):", source)
        self.assertIn("with st.expander(self._row_title(row_index, config), expanded=False):", source)
        self.assertNotIn("st.markdown(f\"#### {t('model_settings.model_row'", source)

    def test_model_settings_row_title_includes_configured_model_identity(self):
        app_path = str(ROOT / "app")
        if app_path not in sys.path:
            sys.path.insert(0, app_path)
        import pg_model_settings

        page = pg_model_settings.PageModelSettings.__new__(pg_model_settings.PageModelSettings)
        title = page._row_title(
            0,
            {
                "provider": "deepseek",
                "model": "deepseek-v4-flash",
                "api_base": "https://api.deepseek.com",
                "api_key": "secret",
            },
        )

        self.assertIn("deepseek", title)
        self.assertIn("deepseek-v4-flash", title)

    def test_model_settings_save_reruns_after_row_count_changes(self):
        source = (ROOT / "app" / "pg_model_settings.py").read_text(encoding="utf-8")
        save_block = source[source.index("        if submitted:"):]

        self.assertIn('ss.model_settings_saved = True', save_block)
        self.assertIn("st.rerun()", save_block)
        self.assertLess(
            save_block.index("ss.model_settings_row_count = max(1, len(read_model_configs(ENV_PATH)))"),
            save_block.index("st.rerun()"),
        )
        self.assertNotIn("st.success(t(\"model_settings.saved\"))", save_block)

    def test_frontend_design_skill_restyles_default_streamlit_surfaces(self):
        source = (ROOT / "app" / "ui_styles.py").read_text(encoding="utf-8")

        self.assertIn('div[data-testid="stTabs"]', source)
        self.assertIn('[data-baseweb="tab-list"]', source)
        self.assertIn('div[data-testid="stForm"]', source)
        self.assertIn('div[data-testid="stFileUploader"]', source)
        self.assertIn('.st-key-tools-palette-card', source)
        self.assertIn('.st-key-model-settings-card', source)

    def test_tools_palette_buttons_use_full_width_workbench_cards(self):
        tools_source = (ROOT / "app" / "pg_tools.py").read_text(encoding="utf-8")
        source = (ROOT / "app" / "ui_styles.py").read_text(encoding="utf-8")

        self.assertIn("use_container_width=True", tools_source)
        self.assertIn('.st-key-tools-palette-card button', source)
        self.assertIn('[class*="st-key-enable"] button', source)
        self.assertIn('.st-key-tools-palette-card button p', source)
        self.assertIn("width: 100%;", source)
        self.assertIn("display: flex;", source)
        self.assertIn("justify-content: flex-start;", source)
        self.assertIn("white-space: normal;", source)

    def test_execution_page_has_cockpit_sections(self):
        source = (ROOT / "app" / "pg_crew_run.py").read_text(encoding="utf-8")

        self.assertIn("def draw_cockpit_header", source)
        self.assertIn("crew-run-cockpit", source)
        self.assertIn("crew-run-log-panel", source)

    def test_crew_run_page_exposes_loop_controls(self):
        source = (ROOT / "app" / "pg_crew_run.py").read_text(encoding="utf-8")
        zh = (ROOT / "app" / "i18n" / "zh.json").read_text(encoding="utf-8")
        en = (ROOT / "app" / "i18n" / "en.json").read_text(encoding="utf-8")

        self.assertIn("from crew_run_loop import LoopConfig, run_crew_loop", source)
        self.assertIn("'loop_enabled': False", source)
        self.assertIn("'loop_count': 2", source)
        self.assertIn("'loop_target_placeholder': None", source)
        self.assertIn("def draw_loop_controls(self, selected_crew):", source)
        self.assertIn('st.checkbox(t("crew_run.loop_enabled")', source)
        self.assertIn('st.number_input(t("crew_run.loop_count")', source)
        self.assertIn('st.selectbox(t("crew_run.loop_target_placeholder")', source)
        self.assertIn('"loop_panel": "Loop 设置"', zh)
        self.assertIn('"loop_panel_caption": "将上一轮最终输出自动作为下一轮输入。"', zh)
        self.assertIn('"loop_enabled": "启用 Loop"', zh)
        self.assertIn('"loop_count": "循环次数"', zh)
        self.assertIn('"loop_target_placeholder": "上一轮结果注入到"', zh)
        self.assertIn('"loop_no_placeholders": "当前团队没有可注入的占位符，无法启用 Loop。"', zh)
        self.assertIn('"loop_select_placeholder": "请选择上一轮结果要注入的占位符。"', zh)
        self.assertIn('"loop_progress": "Loop 进度"', zh)
        self.assertIn('"loop_round_status": "第 {index}/{total} 轮：{status}"', zh)
        self.assertIn('"loop_status_waiting": "等待中"', zh)
        self.assertIn('"loop_status_running": "运行中"', zh)
        self.assertIn('"loop_status_success": "成功"', zh)
        self.assertIn('"loop_status_failed": "失败"', zh)
        self.assertIn('"loop_status_stopped": "已停止"', zh)
        self.assertIn('"loop_panel": "Loop settings"', en)
        self.assertIn('"loop_panel_caption": "Use each round\'s final output as the next round\'s input."', en)
        self.assertIn('"loop_enabled": "Enable loop"', en)
        self.assertIn('"loop_count": "Loop count"', en)
        self.assertIn('"loop_target_placeholder": "Inject previous result into"', en)
        self.assertIn('"loop_no_placeholders": "This crew has no injectable placeholders, so loop mode cannot be enabled."', en)
        self.assertIn('"loop_select_placeholder": "Select the placeholder that receives the previous round result."', en)
        self.assertIn('"loop_progress": "Loop progress"', en)
        self.assertIn('"loop_round_status": "Round {index}/{total}: {status}"', en)
        self.assertIn('"loop_status_waiting": "Waiting"', en)
        self.assertIn('"loop_status_running": "Running"', en)
        self.assertIn('"loop_status_success": "Success"', en)
        self.assertIn('"loop_status_failed": "Failed"', en)
        self.assertIn('"loop_status_stopped": "Stopped"', en)

    def test_sidebar_uses_custom_navigation_instead_of_radio(self):
        source = (ROOT / "app" / "app.py").read_text(encoding="utf-8")

        self.assertIn("def draw_navigation", source)
        self.assertNotIn("st.radio(", source)

    def test_sidebar_logo_is_not_rendered(self):
        source = (ROOT / "app" / "app.py").read_text(encoding="utf-8")

        self.assertNotIn("st.image(\"img/crewai_logo.png\")", source)

    def test_language_selector_uses_dropdown_instead_of_radio(self):
        source = (ROOT / "app" / "i18n.py").read_text(encoding="utf-8")

        self.assertIn("st.popover(", source)
        self.assertIn("lang-selector", source)
        self.assertIn("set_language(lang_code)", source)
        self.assertIn("studio-sidebar-separator", source)
        self.assertNotIn("st.selectbox(", source)
        self.assertNotIn("st.divider()", source)
        self.assertNotIn("st.radio(", source)

    def test_dev_session_selectors_are_click_only_dropdowns(self):
        source = (ROOT / "app" / "pg_dev_sessions.py").read_text(encoding="utf-8")

        self.assertIn("def _draw_click_only_dropdown(", source)
        self.assertIn("def _workspace_dropdown_label(", source)
        self.assertIn('key="dev-session-workspace-dropdown"', source)
        self.assertIn('key=f"new-dev-session-model-dropdown-{workspace.id}"', source)
        self.assertIn("st.columns([0.64, 0.28, 0.08], gap=\"small\")", source)
        self.assertNotIn("st.columns([0.50, 0.42, 0.08], gap=\"small\")", source)
        self.assertIn("with st.popover(selected_label, help=help_text, use_container_width=True):", source)
        self.assertIn('help_text=t("dev_session.select_workspace")', source)
        self.assertIn("selected_option = selected_label if selected_option is None else selected_option", source)
        self.assertIn("selected_label = self._workspace_dropdown_label(selected_workspace)", source)
        self.assertIn("selected_option=selected_option", source)
        self.assertIn("with st.popover(", source)
        self.assertIn("selected_model,", source)
        self.assertIn('help=t("dev_session.llm_provider_model")', source)
        self.assertNotIn("st.selectbox(", source)

    def test_dev_session_workspace_dropdown_labels_hide_paths(self):
        app_path = str(ROOT / "app")
        if app_path not in sys.path:
            sys.path.insert(0, app_path)
        import pg_dev_sessions

        page = pg_dev_sessions.PageDevSessions.__new__(pg_dev_sessions.PageDevSessions)
        workspace = SimpleNamespace(
            id="W_1",
            name="crewAi",
            path=r"C:\codeProjects\CrewAI-Studio\CrewAI-Studio-main",
        )

        self.assertEqual(page._workspace_label(workspace), "crewAi")
        self.assertEqual(page._workspace_dropdown_label(workspace), "crewAi")
        self.assertNotIn("CrewAI-Studio-main", page._workspace_dropdown_label(workspace))
        self.assertNotIn(workspace.path, page._workspace_label(workspace))

    def test_dev_session_defaults_to_latest_thread_unless_starting_new_chat(self):
        app_path = str(ROOT / "app")
        if app_path not in sys.path:
            sys.path.insert(0, app_path)
        import pg_dev_sessions

        original_state = pg_dev_sessions.ss
        fake_state = FakeSessionState()
        sessions = [
            SimpleNamespace(id="D_latest", workspace_id="W_1"),
            SimpleNamespace(id="D_old", workspace_id="W_1"),
        ]
        fake_state.dev_sessions = sessions
        page = pg_dev_sessions.PageDevSessions.__new__(pg_dev_sessions.PageDevSessions)

        try:
            pg_dev_sessions.ss = fake_state
            selected = page._selected_session(SimpleNamespace(id="W_1"))
            self.assertIs(selected, sessions[0])
            self.assertEqual(fake_state.selected_dev_session_id, "D_latest")

            del fake_state["selected_dev_session_id"]
            fake_state.dev_session_new_chat = True
            self.assertIsNone(page._selected_session(SimpleNamespace(id="W_1")))
            self.assertNotIn("selected_dev_session_id", fake_state)
        finally:
            pg_dev_sessions.ss = original_state

    def test_dev_session_existing_thread_model_selection_is_saved(self):
        app_path = str(ROOT / "app")
        if app_path not in sys.path:
            sys.path.insert(0, app_path)
        import pg_dev_sessions

        original_state = pg_dev_sessions.ss
        original_save = pg_dev_sessions.db_utils.save_dev_session
        original_load = pg_dev_sessions.db_utils.load_dev_sessions
        fake_state = FakeSessionState()
        session = SimpleNamespace(id="D_1", llm_provider_model="deepseek: old-model")
        saved_sessions = []
        page = pg_dev_sessions.PageDevSessions.__new__(pg_dev_sessions.PageDevSessions)

        try:
            pg_dev_sessions.ss = fake_state
            pg_dev_sessions.db_utils.save_dev_session = saved_sessions.append
            pg_dev_sessions.db_utils.load_dev_sessions = lambda: ["reloaded"]

            page._set_session_model(session, "deepseek: new-model")

            self.assertEqual(session.llm_provider_model, "deepseek: new-model")
            self.assertEqual(saved_sessions, [session])
            self.assertEqual(fake_state.dev_sessions, ["reloaded"])
        finally:
            pg_dev_sessions.ss = original_state
            pg_dev_sessions.db_utils.save_dev_session = original_save
            pg_dev_sessions.db_utils.load_dev_sessions = original_load

    def test_dev_session_send_clears_followup_input_on_next_render(self):
        app_path = str(ROOT / "app")
        if app_path not in sys.path:
            sys.path.insert(0, app_path)
        import pg_dev_sessions

        class FakeDevSession:
            id = "D_1"
            status = "chatting"

            def __init__(self):
                self.messages = []

            def add_message(self, role, content):
                self.messages.append({"role": role, "content": content})

        original_state = pg_dev_sessions.ss
        original_save = pg_dev_sessions.db_utils.save_dev_session
        fake_state = FakeSessionState()
        message_key = "dev-session-message-input-D_1"
        clear_key = f"{message_key}__clear_after_send"
        fake_state[message_key] = "知识库的数据会存放在哪里"
        session = FakeDevSession()
        saved_sessions = []
        queued_sessions = []
        page = pg_dev_sessions.PageDevSessions.__new__(pg_dev_sessions.PageDevSessions)
        page._queue_pending_session = queued_sessions.append

        try:
            pg_dev_sessions.ss = fake_state
            pg_dev_sessions.db_utils.save_dev_session = saved_sessions.append

            page._send_chat_message(SimpleNamespace(id="W_1"), session, fake_state[message_key])

            self.assertEqual(session.messages, [{"role": "user", "content": "知识库的数据会存放在哪里"}])
            self.assertEqual(saved_sessions, [session])
            self.assertEqual(queued_sessions, [session])
            self.assertTrue(fake_state.get(clear_key))
            page._apply_pending_message_input_clear(message_key)
            self.assertEqual(fake_state[message_key], "")
            self.assertNotIn(clear_key, fake_state)
        finally:
            pg_dev_sessions.ss = original_state
            pg_dev_sessions.db_utils.save_dev_session = original_save

    def test_dev_session_send_requests_thread_scroll_to_bottom(self):
        app_path = str(ROOT / "app")
        if app_path not in sys.path:
            sys.path.insert(0, app_path)
        import pg_dev_sessions

        class FakeDevSession:
            id = "D_1"
            status = "chatting"

            def add_message(self, role, content):
                self.last_message = {"role": role, "content": content}

        original_state = pg_dev_sessions.ss
        original_save = pg_dev_sessions.db_utils.save_dev_session
        fake_state = FakeSessionState()
        session = FakeDevSession()
        page = pg_dev_sessions.PageDevSessions.__new__(pg_dev_sessions.PageDevSessions)
        page._queue_pending_session = lambda _session: None

        try:
            pg_dev_sessions.ss = fake_state
            pg_dev_sessions.db_utils.save_dev_session = lambda _session: None

            page._send_chat_message(SimpleNamespace(id="W_1"), session, "不支持html吗")

            self.assertEqual(fake_state.dev_session_scroll_to_bottom_session_id, "D_1")
            self.assertEqual(fake_state.dev_session_scroll_to_bottom_nonce, 1)
        finally:
            pg_dev_sessions.ss = original_state
            pg_dev_sessions.db_utils.save_dev_session = original_save

    def test_dev_session_scroll_script_targets_chat_canvas_bottom(self):
        app_path = str(ROOT / "app")
        if app_path not in sys.path:
            sys.path.insert(0, app_path)
        import pg_dev_sessions

        page = pg_dev_sessions.PageDevSessions.__new__(pg_dev_sessions.PageDevSessions)
        script = page._chat_scroll_to_bottom_script(3)

        self.assertIn("dev-session-scroll-request-3", script)
        self.assertIn("window.parent.document", script)
        self.assertIn(".st-key-dev-session-chat-canvas", script)
        self.assertIn('[class*="st-key-dev-session-chat-canvas"] > [data-testid="stVerticalBlock"]', script)
        self.assertIn("target.scrollTop = target.scrollHeight", script)

    def test_dev_session_renders_cleared_composer_before_pending_reply_blocks(self):
        source = (ROOT / "app" / "pg_dev_sessions.py").read_text(encoding="utf-8")
        start = source.index("    def _draw_main_thread")
        end = source.index("    def draw", start)
        main_thread = source[start:end]

        self.assertLess(
            main_thread.index("self._draw_chat_composer(workspace, session)"),
            main_thread.index("self._complete_pending_reply("),
        )

    def test_dev_session_scrolls_thread_before_pending_reply_blocks(self):
        source = (ROOT / "app" / "pg_dev_sessions.py").read_text(encoding="utf-8")
        start = source.index("    def _draw_main_thread")
        end = source.index("    def draw", start)
        main_thread = source[start:end]

        self.assertIn("self._draw_chat_scroll_to_bottom(session)", main_thread)
        self.assertLess(
            main_thread.index("stream_slot = st.empty()"),
            main_thread.index("self._draw_chat_scroll_to_bottom(session)"),
        )
        self.assertLess(
            main_thread.index("self._draw_chat_scroll_to_bottom(session)"),
            main_thread.index("self._complete_pending_reply("),
        )

    def test_sidebar_top_spacing_is_compact(self):
        source = (ROOT / "app" / "ui_styles.py").read_text(encoding="utf-8")

        self.assertIn('[data-testid="stSidebarHeader"]', source)
        self.assertIn('[data-testid="stLogoSpacer"]', source)
        self.assertIn('section[data-testid="stSidebar"] [data-testid="stSidebarContent"]', source)
        self.assertIn('section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"]', source)
        self.assertIn("height: 2rem !important;", source)
        self.assertIn("height: 0 !important;", source)
        self.assertIn("padding-top: 0.2rem !important;", source)
        self.assertIn("padding-top: 0 !important;", source)
        self.assertIn("padding-left: 0.25rem !important;", source)
        self.assertIn("padding-right: 0.25rem !important;", source)
        self.assertIn("padding-left: 0.26rem !important;", source)
        self.assertIn("padding-right: 0.28rem !important;", source)
        self.assertIn("width: calc(100% + 1rem) !important;", source)
        self.assertIn("max-width: none !important;", source)
        self.assertIn("margin-left: -0.55rem !important;", source)
        self.assertIn("margin-right: -0.45rem !important;", source)
        self.assertIn(".studio-nav-card-title", source)
        self.assertIn(".st-key-lang-selector", source)
        self.assertIn('[class*="st-key-lang_selector_"] button', source)
        self.assertIn("margin-bottom: 0.25rem;", source)
        self.assertIn(".studio-sidebar-separator", source)
        self.assertIn("margin: 0.15rem 0 0.45rem;", source)

    def test_sidebar_navigation_groups_use_lightweight_rail_sections(self):
        app_source = (ROOT / "app" / "app.py").read_text(encoding="utf-8")
        style_source = (ROOT / "app" / "ui_styles.py").read_text(encoding="utf-8")

        self.assertIn('NAV_ICON_TEXT_SPACER = "\\u00a0\\u00a0"', app_source)
        self.assertIn('with st.container(border=False, key=f"nav-card-{nav_key}"):', app_source)
        self.assertNotIn('with st.container(border=True, key=f"nav-card-{nav_key}"):', app_source)
        self.assertIn("studio-nav-card-title", app_source)
        self.assertIn('("nav.workspace", ["page.crews", "page.agents", "page.tasks", "page.tools", "page.knowledge", "page.kickoff", "page.results"])', app_source)
        self.assertNotIn('("nav.run", ["page.kickoff", "page.results"])', app_source)
        self.assertIn(".st-key-nav-card-workspace", style_source)
        self.assertIn(".st-key-nav-card-development", style_source)
        self.assertIn(".st-key-nav-card-system", style_source)
        self.assertNotIn(".st-key-nav-card-run", style_source)
        self.assertIn("background: transparent !important;", style_source)
        self.assertIn("border: 0 !important;", style_source)
        self.assertIn("box-shadow: none !important;", style_source)
        self.assertIn(".st-key-nav-card-workspace::before", style_source)
        self.assertIn("padding-left: 0.42rem;", style_source)
        self.assertIn("padding: 0.05rem 0 0.18rem 0.24rem !important;", style_source)
        self.assertIn("left: 0.02rem;", style_source)
        self.assertIn("width: 1px;", style_source)
        self.assertIn("width: calc(100% - 0.58rem) !important;", style_source)
        self.assertIn("margin-left: 0.58rem !important;", style_source)
        self.assertIn("padding-left: 0.44rem !important;", style_source)
        self.assertIn("padding-right: 0.38rem !important;", style_source)
        hover_start = style_source.index(
            'section[data-testid="stSidebar"] .st-key-nav-card-workspace .stButton > button:hover'
        )
        selected_start = style_source.index(
            'section[data-testid="stSidebar"] .st-key-nav-card-workspace .stButton > button[kind="primary"]',
            hover_start,
        )
        hover_block = style_source[hover_start:selected_start]
        self.assertIn("min-height: 2.48rem !important;", hover_block)
        self.assertIn("padding-top: 0.28rem !important;", hover_block)
        self.assertIn("padding-bottom: 0.28rem !important;", hover_block)
        self.assertIn("min-height: 2.72rem !important;", style_source)
        self.assertIn("height: 2.72rem !important;", style_source)
        self.assertIn("padding-top: 0.38rem !important;", style_source)
        self.assertIn("padding-bottom: 0.38rem !important;", style_source)
        self.assertIn("background: linear-gradient(90deg, rgba(37, 99, 235, 0.22), rgba(37, 99, 235, 0.06)) !important;", style_source)
        self.assertIn("box-shadow: inset 2px 0 0 rgba(96, 165, 250, 0.92) !important;", style_source)
        self.assertNotIn("background: linear-gradient(180deg, rgba(23, 32, 51, 0.58), rgba(12, 19, 32, 0.64));", style_source)

    def test_streamlit_header_uses_workbench_palette(self):
        source = (ROOT / "app" / "ui_styles.py").read_text(encoding="utf-8")

        self.assertIn('header[data-testid="stHeader"]', source)
        self.assertIn("radial-gradient(circle at 22% 0%, rgba(59, 130, 246, 0.18), transparent 28rem)", source)
        self.assertIn("linear-gradient(135deg, rgba(16, 24, 39, 0.96), rgba(24, 34, 53, 0.94) 58%, rgba(16, 24, 39, 0.96));", source)
        self.assertIn("border-bottom: 1px solid rgba(148, 163, 184, 0.08);", source)

    def test_main_content_uses_soft_panel_surface(self):
        source = (ROOT / "app" / "ui_styles.py").read_text(encoding="utf-8")

        self.assertIn(".main .block-container", source)
        self.assertIn("background: rgba(30, 41, 59, 0.34);", source)
        self.assertIn("border: 1px solid rgba(148, 163, 184, 0.16);", source)
        self.assertIn("border-radius: 10px;", source)

    def test_overall_workbench_palette_is_slightly_brighter(self):
        source = (ROOT / "app" / "ui_styles.py").read_text(encoding="utf-8")

        self.assertIn("--studio-bg: #101827;", source)
        self.assertIn("--studio-panel: #172033;", source)
        self.assertIn("--studio-app-header-height: 2.35rem;", source)
        self.assertNotIn("--studio-app-header-height: 4.75rem;", source)
        self.assertIn("linear-gradient(135deg, #101827 0%, #182235 52%, #101827 100%)", source)

    def test_crews_page_uses_workspace_header_and_card(self):
        source = (ROOT / "app" / "pg_crews.py").read_text(encoding="utf-8")

        self.assertIn("from page_chrome import draw_page_header", source)
        self.assertIn("draw_page_header(", source)
        self.assertIn('with st.container(border=True, key="crews-list-card"):', source)

    def test_expanders_and_primary_actions_use_polished_cards(self):
        source = (ROOT / "app" / "ui_styles.py").read_text(encoding="utf-8")

        self.assertIn('div[data-testid="stExpander"]', source)
        self.assertIn("background: linear-gradient(180deg, rgba(30, 41, 59, 0.72), rgba(15, 23, 42, 0.82));", source)
        self.assertIn('div[data-testid="stExpander"] summary', source)
        self.assertIn("box-shadow: 0 12px 34px rgba(0, 0, 0, 0.18);", source)

    def test_agent_lists_use_compact_expander_spacing(self):
        app_source = (ROOT / "app" / "pg_agents.py").read_text(encoding="utf-8")
        style_source = (ROOT / "app" / "ui_styles.py").read_text(encoding="utf-8")

        self.assertIn('key="agent-list-all"', app_source)
        self.assertIn('key="agent-list-unassigned"', app_source)
        self.assertIn('key=f"agent-list-crew-{i}"', app_source)
        self.assertIn('[class*="st-key-agent-list-"] div[data-testid="stExpander"]', style_source)
        self.assertIn("margin-bottom: 0 !important;", style_source)
        self.assertIn("min-height: 2.05rem;", style_source)
        self.assertIn("padding: 0.42rem 0.72rem !important;", style_source)
        self.assertIn("gap: 0.45rem !important;", style_source)

    def test_task_and_crew_lists_use_compact_expander_spacing(self):
        task_source = (ROOT / "app" / "pg_tasks.py").read_text(encoding="utf-8")
        crew_source = (ROOT / "app" / "pg_crews.py").read_text(encoding="utf-8")
        style_source = (ROOT / "app" / "ui_styles.py").read_text(encoding="utf-8")

        self.assertIn('key="task-list-all"', task_source)
        self.assertIn('key="task-list-unassigned"', task_source)
        self.assertIn('key=f"task-list-crew-{i}"', task_source)
        self.assertIn('key="crew-list-all"', crew_source)
        self.assertIn('[class*="st-key-task-list-"] div[data-testid="stExpander"]', style_source)
        self.assertIn('[class*="st-key-crew-list-"] div[data-testid="stExpander"]', style_source)
        self.assertIn('[class*="st-key-task-list-"] [data-testid="stVerticalBlock"]', style_source)
        self.assertIn('[class*="st-key-crew-list-"] [data-testid="stVerticalBlock"]', style_source)
        self.assertIn('[class*="st-key-task-list-"] div[data-testid="stExpander"] summary {', style_source)
        self.assertIn("height: 2.35rem !important;", style_source)
        self.assertIn("max-height: 2.35rem !important;", style_source)
        self.assertIn('[class*="st-key-task-list-"] div[data-testid="stExpander"] summary p', style_source)
        self.assertIn("white-space: nowrap !important;", style_source)
        self.assertIn("overflow: hidden !important;", style_source)
        self.assertIn("text-overflow: ellipsis !important;", style_source)

    def test_sidebar_collapse_button_is_persistent_lower_and_larger(self):
        source = (ROOT / "app" / "ui_styles.py").read_text(encoding="utf-8")

        self.assertIn('[data-testid="stSidebarCollapseButton"]', source)
        self.assertIn("visibility: visible !important;", source)
        self.assertIn("transform: translateY(0.75rem);", source)
        self.assertIn("width: 2.45rem !important;", source)
        self.assertIn("height: 2.45rem !important;", source)
        self.assertIn("width: 1.75rem !important;", source)
        self.assertIn("height: 1.75rem !important;", source)

    def test_development_workbench_pages_have_polished_surfaces(self):
        source = (ROOT / "app" / "ui_styles.py").read_text(encoding="utf-8")

        self.assertIn(".st-key-workspaces-list-card", source)
        self.assertIn(".dev-session-workbench", source)
        self.assertIn(".st-key-dev-session-workbench", source)
        self.assertIn("--dev-session-surface:", source)
        self.assertIn("--dev-session-outline:", source)
        self.assertIn("--dev-session-control:", source)
        self.assertIn("body:has(.st-key-dev-session-workbench) .main .block-container", source)
        self.assertIn(".main .block-container:has(.st-key-dev-session-workbench)", source)
        self.assertIn('body:has(.st-key-dev-session-workbench) [data-testid="stMain"] .block-container', source)
        self.assertIn('[data-testid="stMain"] .block-container:has(.st-key-dev-session-workbench)', source)
        self.assertIn('[data-testid="stMainBlockContainer"]:has(.st-key-dev-session-workbench)', source)
        self.assertIn("min-height: 100dvh !important;", source)
        self.assertIn("height: 100dvh !important;", source)
        self.assertIn("padding: calc(var(--studio-app-header-height) + 0.32rem) 0.35rem 0.35rem !important;", source)
        self.assertNotIn("padding: 0.55rem 0.35rem 0.35rem !important;", source)
        self.assertNotIn("padding: calc(var(--studio-app-header-height) + 0.35rem) 0.35rem 0.35rem !important;", source)
        self.assertIn("margin-top: 0 !important;", source)
        self.assertIn("margin-bottom: 0 !important;", source)
        self.assertIn("box-sizing: border-box !important;", source)
        self.assertIn("body:has(.st-key-dev-session-workbench) .st-key-dev-session-workbench", source)
        self.assertIn("--dev-session-shell-height: calc(100dvh - var(--studio-app-header-height) - 0.75rem);", source)
        self.assertIn("min-height: var(--dev-session-shell-height) !important;", source)
        self.assertIn("height: var(--dev-session-shell-height) !important;", source)
        self.assertNotIn("--dev-session-shell-height: calc(100dvh - var(--studio-app-header-height) + 2.45rem);", source)
        self.assertNotIn("--dev-session-shell-height: calc(100dvh - var(--studio-app-header-height) - 0.8rem);", source)
        self.assertIn(".st-key-dev-session-workbench > [data-testid=\"stLayoutWrapper\"]", source)
        self.assertIn(".st-key-dev-session-workbench > [data-testid=\"stLayoutWrapper\"] > [data-testid=\"stHorizontalBlock\"]", source)
        self.assertIn(".st-key-dev-session-workbench > [data-testid=\"stLayoutWrapper\"] > [data-testid=\"stHorizontalBlock\"] > [data-testid=\"stColumn\"]", source)
        self.assertIn("--dev-session-content-height: calc(var(--dev-session-shell-height) - 0.52rem);", source)
        self.assertIn("justify-content: flex-start;", source)
        self.assertIn("margin: clamp(1.4rem, 6vh, 4.4rem) auto 0;", source)
        self.assertIn("height: var(--dev-session-content-height) !important;", source)
        self.assertIn("height: 100%;", source)
        self.assertIn("height: 100% !important;", source)
        self.assertIn("align-self: stretch !important;", source)
        self.assertIn("overflow: hidden;", source)
        self.assertIn("padding: 0.22rem 0.25rem 0.3rem;", source)
        self.assertIn("box-sizing: border-box;", source)
        self.assertIn("gap: 0.55rem !important;", source)
        self.assertNotIn("min-height: calc(100vh - 8rem);", source)
        self.assertNotIn("min-height: calc(100vh - 10rem);", source)
        self.assertIn(".dev-session-lane", source)
        self.assertIn(".st-key-dev-session-lane", source)
        self.assertIn(".dev-session-lane-card", source)
        self.assertIn(".dev-session-lane-summary", source)
        self.assertIn(".dev-session-lane-eyebrow", source)
        self.assertIn(".dev-session-lane-title", source)
        self.assertIn(".dev-session-lane-path", source)
        self.assertIn(".dev-session-lane-stats", source)
        self.assertIn(".st-key-dev-session-lane-controls", source)
        self.assertIn(".dev-session-empty-title", source)
        self.assertIn(".dev-session-empty-copy", source)
        self.assertIn("text-transform: uppercase;", source)
        self.assertIn(".dev-session-conversation", source)
        self.assertIn(".st-key-dev-session-conversation", source)
        self.assertIn(".dev-session-section-label", source)
        self.assertIn(".dev-session-inline-notice", source)
        self.assertIn(".dev-session-session-list", source)
        self.assertIn(".st-key-dev-session-session-list", source)
        self.assertIn(".dev-session-empty-state", source)
        self.assertIn(".dev-session-session-delete", source)
        self.assertIn('[class*="st-key-dev-session-session-"] button', source)
        self.assertIn('[class*="st-key-delete-dev-session-sidebar-"] button', source)
        self.assertNotIn(".dev-session-meta-chip", source)
        self.assertIn(".dev-session-main", source)
        self.assertIn(".dev-session-topbar", source)
        self.assertIn(".dev-session-layout", source)
        self.assertIn(".dev-session-codex-stream", source)
        self.assertIn(".dev-session-home", source)
        self.assertIn(".st-key-dev-session-home-shell", source)
        self.assertIn(".dev-session-home-kicker", source)
        self.assertIn(".dev-session-home-context", source)
        self.assertIn(".dev-session-home-card", source)
        self.assertIn(".dev-session-hero-title", source)
        self.assertIn(".dev-session-home-spacer", source)
        self.assertIn(".dev-session-home-composer-card", source)
        self.assertIn(".st-key-dev-session-conversation:has(.st-key-dev-session-home)", source)
        self.assertIn("background: transparent;", source)
        self.assertIn("box-shadow: none;", source)
        self.assertIn(".dev-session-chat-canvas", source)
        self.assertIn("height: clamp(24rem, 56vh, 44rem);", source)
        self.assertIn("min-height: 24rem;", source)
        self.assertIn("max-height: 44rem;", source)
        self.assertIn("max-width: 68rem;", source)
        self.assertIn("overflow-y: auto;", source)
        self.assertIn("scrollbar-gutter: stable;", source)
        self.assertIn("overscroll-behavior: contain;", source)
        self.assertIn('[class*="st-key-dev-session-chat-canvas"] > [data-testid="stVerticalBlock"]', source)
        self.assertIn(".dev-session-current-user-bubble", source)
        self.assertIn(".dev-session-copy-icon", source)
        self.assertIn(".st-key-dev-session-conversation:not(:has(.st-key-dev-session-home))", source)
        self.assertIn("align-items: stretch !important;", source)
        self.assertIn("max-height: none !important;", source)
        self.assertIn(".dev-session-thinking", source)
        self.assertIn(".dev-session-thinking-dot", source)
        self.assertIn("@keyframes dev-session-thinking-pulse", source)
        self.assertIn("white-space: nowrap;", source)
        self.assertIn(".dev-session-working", source)
        self.assertIn(".dev-session-stream-cursor", source)
        self.assertIn("@keyframes dev-session-stream-caret", source)
        self.assertIn(".dev-session-bottom-composer", source)
        self.assertIn(".dev-session-send-button", source)
        self.assertIn(".dev-session-send-arrow", source)
        self.assertIn(".dev-session-create-arrow", source)
        self.assertIn('[class*="st-key-dev-session-composer-toolbar-"]', source)
        self.assertIn("margin-top: -0.2rem;", source)
        self.assertIn("width: 2.45rem !important;", source)
        self.assertIn("min-width: 2.45rem !important;", source)
        self.assertIn('[class*="st-key-dev-session-create-arrow-"] button {', source)
        self.assertIn("background: linear-gradient(180deg, rgba(15, 23, 42, 0.98), rgba(17, 24, 39, 0.96)) !important;", source)
        self.assertIn("border-color: rgba(148, 163, 184, 0.24) !important;", source)
        self.assertIn("border-color: rgba(226, 232, 240, 0.34) !important;", source)
        self.assertNotIn("border-color: rgba(96, 165, 250, 0.30) !important;", source)
        self.assertNotIn("border-color: rgba(147, 197, 253, 0.72) !important;", source)
        self.assertIn('[class*="st-key-dev-session-create-arrow-"] button:hover', source)
        self.assertIn("box-shadow: 0 12px 24px rgba(0, 0, 0, 0.24)", source)
        self.assertIn(".st-key-dev-session-home", source)
        self.assertIn(".st-key-dev-session-home-composer-card", source)
        self.assertIn(".st-key-dev-session-bottom-composer", source)
        self.assertIn(".st-key-dev-session-chat-canvas", source)
        self.assertIn('[class*="st-key-dev-session-composer-"]', source)
        self.assertIn('<div class="dev-session-home-spacer" aria-hidden="true"></div>', (ROOT / "app" / "pg_dev_sessions.py").read_text(encoding="utf-8"))
        self.assertIn(".st-key-dev-session-workspace-dropdown [data-testid=\"stPopoverButton\"]", source)
        self.assertIn('[class*="st-key-new-dev-session-model-dropdown-"] [data-testid="stPopoverButton"]', source)
        self.assertIn('[class*="st-key-new-dev-session-model-dropdown-"] {', source)
        self.assertIn("max-width: 17.5rem;", source)
        self.assertIn("margin-left: auto;", source)
        self.assertIn('[class*="st-key-dev-session-workspace-dropdown-option-"] button', source)
        self.assertIn('[class*="st-key-new-dev-session-model-option-"] button', source)
        self.assertIn("min-height: 2.05rem !important;", source)
        self.assertIn("text-overflow: ellipsis;", source)
        self.assertIn('[data-testid="stPopoverBody"]:has([class*="st-key-dev-session-workspace-dropdown-option-"])', source)
        self.assertIn('[data-testid="stPopoverBody"]:has([class*="st-key-new-dev-session-model-option-"])', source)
        self.assertIn("padding: 0.46rem !important;", source)
        self.assertIn("width: min(13rem, calc(100vw - 1rem)) !important;", source)
        self.assertIn("min-width: min(11rem, calc(100vw - 1rem)) !important;", source)
        self.assertNotIn("width: min(24rem, calc(100vw - 1rem)) !important;", source)
        self.assertIn("width: min(19rem, calc(100vw - 1rem)) !important;", source)
        self.assertIn("backdrop-filter: blur(16px);", source)
        self.assertIn("--dev-session-lane-height: calc(var(--dev-session-shell-height) - 0.52rem);", source)
        self.assertIn("--dev-session-shell-height: calc(100dvh - var(--studio-app-header-height) - 0.75rem);", source)
        self.assertIn("--dev-session-content-height: var(--dev-session-lane-height);", source)
        self.assertIn(".st-key-dev-session-workbench > [data-testid=\"stLayoutWrapper\"] > [data-testid=\"stHorizontalBlock\"] > [data-testid=\"stColumn\"] > [data-testid=\"stVerticalBlock\"]", source)
        self.assertIn(".st-key-dev-session-lane,", source)
        self.assertIn("height: var(--dev-session-lane-height) !important;", source)
        self.assertIn("padding: 0.22rem 0.2rem 0.3rem !important;", source)
        self.assertIn("max-height: var(--dev-session-content-height) !important;", source)
        self.assertIn("max-height: var(--dev-session-lane-height) !important;", source)
        self.assertIn('.st-key-dev-session-lane > [data-testid="stLayoutWrapper"] > [data-testid="stVerticalBlock"]', source)
        self.assertIn("gap: 0.64rem !important;", source)
        self.assertNotIn(".dev-session-lane-top-spacer", source)
        self.assertNotIn('<div class="dev-session-lane-top-spacer" aria-hidden="true"></div>', (ROOT / "app" / "pg_dev_sessions.py").read_text(encoding="utf-8"))
        self.assertIn("gap: 0.44rem !important;", source)
        self.assertIn("margin-top: 0.12rem;", source)
        self.assertIn("margin-top: 0.42rem !important;", source)
        self.assertIn("margin-bottom: 0.38rem;", source)
        self.assertIn('[data-testid="stLayoutWrapper"]:has(.st-key-dev-session-workspace-dropdown)', source)
        self.assertIn("margin-top: 0.18rem !important;", source)
        self.assertIn("flex-direction: column !important;", source)
        self.assertIn("min-height: clamp(4rem, 12vh, 8rem);", source)
        self.assertIn("margin-top: auto !important;", source)
        self.assertIn("margin-bottom: 0 !important;", source)
        self.assertIn("width: min(100%, 62rem);", source)
        self.assertIn("border: 0;", source)
        self.assertIn('.st-key-dev-session-home > [data-testid="stLayoutWrapper"] > [data-testid="stVerticalBlock"].st-key-dev-session-home-shell', source)
        self.assertIn("grid-template-rows: auto minmax(0, 1fr) auto;", source)
        self.assertIn("grid-template-columns: minmax(0, 1fr);", source)
        self.assertIn("justify-items: stretch;", source)
        self.assertIn("grid-row: 2;", source)
        self.assertIn("grid-row: 3;", source)
        self.assertIn("align-self: end !important;", source)
        self.assertIn('.st-key-dev-session-home-shell > [data-testid="stLayoutWrapper"]:has(.st-key-dev-session-home-spacer-wrap)', source)
        self.assertIn('.st-key-dev-session-home-shell > [data-testid="stLayoutWrapper"]:has(.st-key-dev-session-home-composer-card)', source)
        self.assertIn("height: auto !important;", source)
        self.assertIn("justify-self: stretch;", source)
        self.assertNotIn(".st-key-dev-session-home-composer-card {\n          position: absolute", source)
        self.assertIn("padding-bottom: 0.34rem !important;", source)
        self.assertIn("padding-bottom: 0.48rem !important;", source)
        self.assertIn('[class*="st-key-dev-session-thread-"]', source)
        self.assertIn(".dev-session-message", source)
        self.assertIn(".dev-session-chat-message", source)
        self.assertIn(".dev-session-chat-message.is-user", source)
        self.assertIn(".dev-session-chat-message.is-assistant", source)
        self.assertIn('[class*="st-key-dev-session-followup-composer-"]', source)
        self.assertIn("grid-template-rows: auto minmax(0, 1fr) auto !important;", source)
        self.assertIn('[data-testid="stLayoutWrapper"]:has([class*="st-key-dev-session-thread-"])', source)
        self.assertIn('[data-testid="stLayoutWrapper"]:has(.st-key-dev-session-bottom-composer)', source)
        self.assertIn("justify-content: flex-start;", source)
        self.assertIn("padding: 0.35rem 0.15rem 0.25rem !important;", source)
        self.assertIn("width: min(58rem, calc(100% - 1.5rem)) !important;", source)
        self.assertIn("position: relative;", source)
        self.assertIn("position: absolute;", source)
        self.assertIn("right: 0.68rem;", source)
        self.assertIn("bottom: 0.58rem;", source)
        self.assertIn('[data-testid="stElementContainer"]:has([class*="st-key-dev-session-send-arrow-"])', source)
        self.assertIn('[data-testid="stLayoutWrapper"]:has([class*="st-key-dev-session-followup-composer-"])', source)
        self.assertNotIn("grid-template-columns: minmax(0, 1fr) 2.25rem !important;", source)
        self.assertIn("padding-bottom: 0.48rem !important;", source)
        self.assertNotIn('_, action_col = st.columns([0.92, 0.08], gap="small")', (ROOT / "app" / "pg_dev_sessions.py").read_text(encoding="utf-8"))
        self.assertIn('key=f"dev-session-followup-composer-{session.id}"', (ROOT / "app" / "pg_dev_sessions.py").read_text(encoding="utf-8"))
        self.assertIn('button_key = f"dev-session-send-arrow-{session.id}"', (ROOT / "app" / "pg_dev_sessions.py").read_text(encoding="utf-8"))
        self.assertIn('key=f"dev-session-model-dropdown-{session.id}"', (ROOT / "app" / "pg_dev_sessions.py").read_text(encoding="utf-8"))
        self.assertIn('key=f"dev-session-model-option-{session.id}-{model_index}"', (ROOT / "app" / "pg_dev_sessions.py").read_text(encoding="utf-8"))
        self.assertIn('self._set_session_model(session, model_label)', (ROOT / "app" / "pg_dev_sessions.py").read_text(encoding="utf-8"))
        self.assertIn('[class*="st-key-dev-session-model-dropdown-"]', source)
        self.assertIn('[class*="st-key-dev-session-model-option-"] button', source)
        self.assertIn('[class*="st-key-dev-session-followup-composer-"] [class*="st-key-dev-session-model-dropdown-"]', source)
        self.assertIn("width: min(13.75rem, calc(100% - 4.45rem)) !important;", source)
        self.assertNotIn('key=f"dev-session-composer-toolbar-{session.id}"', (ROOT / "app" / "pg_dev_sessions.py").read_text(encoding="utf-8"))
        self.assertIn("grid-template-columns: minmax(16rem, clamp(17rem, 21vw, 21rem)) minmax(0, 1fr);", source)
        self.assertNotIn("grid-template-columns: minmax(15rem, 0.32fr) minmax(0, 1fr);", source)
        self.assertIn("@media (max-width: 1100px)", source)
        self.assertIn("flex-direction: column;", source)
        self.assertIn("border-radius: 14px;", source)
        self.assertIn('[class*="st-key-workspace-directory-picker-"]', source)
        self.assertNotIn(".dev-session-page-reset", source)
        self.assertNotIn("body:has(.dev-session-page-reset)", source)
        self.assertNotIn("#f7f0ed", source)
        self.assertNotIn(".dev-session-shell", source)
        self.assertNotIn(".dev-session-window-toolbar", source)
        self.assertNotIn(".dev-session-web-preview-card", source)
        self.assertNotIn(".dev-session-changes-card", source)
        self.assertNotIn(".dev-session-panel", source)
        self.assertNotIn(".dev-session-tree", source)
        self.assertNotIn(".dev-session-diff", source)
        self.assertNotIn(".dev-session-artifact-card", source)
        self.assertNotIn(".dev-session-artifact-title", source)
        self.assertNotIn(".dev-session-rail", source)
        self.assertNotIn(".dev-session-rail-action", source)
        self.assertNotIn(".dev-session-thread-list", source)
        self.assertNotIn(".dev-session-bottom-bar", source)
        self.assertNotIn(".dev-session-context-row", source)
        self.assertNotIn(".dev-session-suggestions", source)
        self.assertNotIn(".dev-session-suggestion-row", source)
        self.assertNotIn(".dev-session-sidebar-action", source)
        self.assertNotIn(".dev-session-project-row", source)
        self.assertNotIn(".dev-session-sidebar-thread", source)
        self.assertNotIn(".dev-session-thread-age", source)
        self.assertNotIn(".dev-session-composer-toolbar", source)

    def test_dev_session_thread_layout_uses_direct_streamlit_rows(self):
        source = (ROOT / "app" / "ui_styles.py").read_text(encoding="utf-8")

        self.assertIn(
            ".st-key-dev-session-conversation:not(:has(.st-key-dev-session-home)) {\n"
            "          display: grid !important;\n"
            "          grid-template-rows: auto minmax(0, 1fr) auto !important;",
            source,
        )
        self.assertIn(
            '.st-key-dev-session-conversation:not(:has(.st-key-dev-session-home)) > '
            '[data-testid="stLayoutWrapper"]:has([class*="st-key-dev-session-thread-"])',
            source,
        )
        self.assertIn(
            '.st-key-dev-session-conversation:not(:has(.st-key-dev-session-home)) > '
            '[data-testid="stLayoutWrapper"]:has(.st-key-dev-session-bottom-composer)',
            source,
        )
        self.assertIn(
            '.st-key-dev-session-bottom-composer > [data-testid="stLayoutWrapper"]:has('
            '[class*="st-key-dev-session-followup-composer-"])',
            source,
        )


if __name__ == "__main__":
    unittest.main()
