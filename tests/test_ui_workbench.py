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

        self.assertIn("st.selectbox(", source)
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

    def test_sidebar_navigation_groups_use_soft_cards(self):
        app_source = (ROOT / "app" / "app.py").read_text(encoding="utf-8")
        style_source = (ROOT / "app" / "ui_styles.py").read_text(encoding="utf-8")

        self.assertIn('with st.container(border=True, key=f"nav-card-{nav_key}"):', app_source)
        self.assertIn("studio-nav-card-title", app_source)
        self.assertIn(".st-key-nav-card-workspace", style_source)
        self.assertIn(".st-key-nav-card-run", style_source)
        self.assertIn(".st-key-nav-card-system", style_source)
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

    def test_sidebar_collapse_button_is_persistent_lower_and_larger(self):
        source = (ROOT / "app" / "ui_styles.py").read_text(encoding="utf-8")

        self.assertIn('[data-testid="stSidebarCollapseButton"]', source)
        self.assertIn("visibility: visible !important;", source)
        self.assertIn("transform: translateY(0.75rem);", source)
        self.assertIn("width: 2.45rem !important;", source)
        self.assertIn("height: 2.45rem !important;", source)
        self.assertIn("width: 1.75rem !important;", source)
        self.assertIn("height: 1.75rem !important;", source)


if __name__ == "__main__":
    unittest.main()
