from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


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

    def test_sidebar_top_spacing_is_compact(self):
        source = (ROOT / "app" / "ui_styles.py").read_text(encoding="utf-8")

        self.assertIn('[data-testid="stSidebarHeader"]', source)
        self.assertIn('[data-testid="stLogoSpacer"]', source)
        self.assertIn('section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"]', source)
        self.assertIn("height: 2rem !important;", source)
        self.assertIn("height: 0 !important;", source)
        self.assertIn("padding-top: 0.2rem !important;", source)
        self.assertIn("padding-top: 0 !important;", source)
        self.assertIn(".studio-nav-card-title", source)
        self.assertIn(".st-key-lang-selector", source)
        self.assertIn('[class*="st-key-lang_selector_"] button', source)
        self.assertIn("margin-bottom: 0.25rem;", source)
        self.assertIn(".studio-sidebar-separator", source)
        self.assertIn("margin: 0.15rem 0 0.45rem;", source)

    def test_sidebar_navigation_groups_use_soft_cards(self):
        app_source = (ROOT / "app" / "app.py").read_text(encoding="utf-8")
        style_source = (ROOT / "app" / "ui_styles.py").read_text(encoding="utf-8")

        self.assertIn('NAV_ICON_TEXT_SPACER = "\\u00a0\\u00a0"', app_source)
        self.assertIn('with st.container(border=True, key=f"nav-card-{nav_key}"):', app_source)
        self.assertIn("studio-nav-card-title", app_source)
        self.assertIn('("nav.workspace", ["page.crews", "page.agents", "page.tasks", "page.tools", "page.knowledge", "page.kickoff", "page.results"])', app_source)
        self.assertNotIn('("nav.run", ["page.kickoff", "page.results"])', app_source)
        self.assertIn(".st-key-nav-card-workspace", style_source)
        self.assertIn(".st-key-nav-card-development", style_source)
        self.assertIn(".st-key-nav-card-system", style_source)
        self.assertNotIn(".st-key-nav-card-run", style_source)
        self.assertIn("background: linear-gradient(180deg, rgba(23, 32, 51, 0.58), rgba(12, 19, 32, 0.64));", style_source)
        self.assertIn("border: 1px solid rgba(148, 163, 184, 0.14);", style_source)

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
        self.assertIn("min-height: var(--dev-session-shell-height) !important;", source)
        self.assertIn("height: var(--dev-session-shell-height) !important;", source)
        self.assertIn("padding-top: 0.65rem !important;", source)
        self.assertIn("padding-left: 0.45rem !important;", source)
        self.assertIn("padding-right: 0.45rem !important;", source)
        self.assertIn("padding-bottom: 0.65rem !important;", source)
        self.assertIn("margin-top: 0 !important;", source)
        self.assertIn("margin-bottom: 0 !important;", source)
        self.assertIn("body:has(.st-key-dev-session-workbench) .st-key-dev-session-workbench", source)
        self.assertIn("--dev-session-shell-height: calc(100dvh - var(--studio-app-header-height) - 0.75rem);", source)
        self.assertIn("min-height: var(--dev-session-shell-height) !important;", source)
        self.assertIn("height: var(--dev-session-shell-height) !important;", source)
        self.assertIn(".st-key-dev-session-workbench > [data-testid=\"stLayoutWrapper\"]", source)
        self.assertIn(".st-key-dev-session-workbench > [data-testid=\"stLayoutWrapper\"] > [data-testid=\"stHorizontalBlock\"]", source)
        self.assertIn(".st-key-dev-session-workbench > [data-testid=\"stLayoutWrapper\"] > [data-testid=\"stHorizontalBlock\"] > [data-testid=\"stColumn\"]", source)
        self.assertIn("--dev-session-content-height: calc(var(--dev-session-shell-height) - 1.45rem);", source)
        self.assertIn("justify-content: flex-start;", source)
        self.assertIn("margin: clamp(1.4rem, 6vh, 4.4rem) auto 0;", source)
        self.assertIn("height: var(--dev-session-content-height) !important;", source)
        self.assertIn("height: 100%;", source)
        self.assertIn("height: 100% !important;", source)
        self.assertIn("align-self: stretch !important;", source)
        self.assertIn("overflow: hidden;", source)
        self.assertIn("padding: 1rem 0.35rem 0.35rem;", source)
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
        self.assertNotIn("position: absolute !important;", source)
        self.assertIn('[class*="st-key-dev-session-thread-"]', source)
        self.assertIn(".dev-session-message", source)
        self.assertIn(".dev-session-chat-message", source)
        self.assertIn(".dev-session-chat-message.is-user", source)
        self.assertIn(".dev-session-chat-message.is-assistant", source)
        self.assertIn('[class*="st-key-dev-session-followup-composer-"]', source)
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


if __name__ == "__main__":
    unittest.main()
