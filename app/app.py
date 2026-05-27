import streamlit as st
from streamlit import session_state as ss
import db_utils
from dotenv import load_dotenv
from llms import load_secrets_fron_env
from i18n import t, setup_language_selector
from ui_styles import apply_global_styles
import importlib
import os

DEFAULT_PAGE_KEY = "page.crews"

NAV_GROUPS = [
    ("nav.workspace", ["page.crews", "page.agents", "page.tasks", "page.tools", "page.knowledge", "page.kickoff", "page.results"]),
    ("nav.development", ["page.workspaces", "page.dev_sessions"]),
    ("nav.system", ["page.model_settings", "page.import_export"]),
]

PAGE_ICONS = {
    "page.crews": "▦",
    "page.agents": "◎",
    "page.tasks": "☑",
    "page.tools": "⚙",
    "page.knowledge": "◇",
    "page.workspaces": "▣",
    "page.dev_sessions": "⌁",
    "page.kickoff": "▶",
    "page.results": "▤",
    "page.model_settings": "◉",
    "page.import_export": "⇄",
}

NAV_ICON_TEXT_SPACER = "\u00a0\u00a0"


def _build_page(module_name, class_name):
    page_class = getattr(importlib.import_module(module_name), class_name)
    return page_class()


def _build_crews_page():
    return _build_page("pg_crews", "PageCrews")


def _build_tools_page():
    return _build_page("pg_tools", "PageTools")


def _build_agents_page():
    return _build_page("pg_agents", "PageAgents")


def _build_tasks_page():
    return _build_page("pg_tasks", "PageTasks")


def _build_knowledge_page():
    return _build_page("pg_knowledge", "PageKnowledge")


def _build_workspaces_page():
    from pg_workspaces import PageWorkspaces

    return PageWorkspaces()


def _build_dev_sessions_page():
    from pg_dev_sessions import PageDevSessions

    return PageDevSessions()


def _build_kickoff_page():
    return _build_page("pg_crew_run", "PageCrewRun")


def _build_results_page():
    return _build_page("pg_results", "PageResults")


def _build_model_settings_page():
    return _build_page("pg_model_settings", "PageModelSettings")


def _build_import_export_page():
    return _build_page("pg_export_crew", "PageExportCrew")


PAGE_BUILDERS = {
    "page.crews": _build_crews_page,
    "page.tools": _build_tools_page,
    "page.agents": _build_agents_page,
    "page.tasks": _build_tasks_page,
    "page.knowledge": _build_knowledge_page,
    "page.workspaces": _build_workspaces_page,
    "page.dev_sessions": _build_dev_sessions_page,
    "page.kickoff": _build_kickoff_page,
    "page.results": _build_results_page,
    "page.model_settings": _build_model_settings_page,
    "page.import_export": _build_import_export_page,
}

PAGE_DATA_LOADERS = {
    "page.crews": ("crews", db_utils.load_crews),
    "page.tools": ("tools", db_utils.load_tools),
    "page.agents": ("agents", db_utils.load_agents),
    "page.tasks": ("tasks", db_utils.load_tasks),
    "page.knowledge": ("knowledge_sources", db_utils.load_knowledge_sources),
    "page.workspaces": ("workspaces", db_utils.load_workspaces),
    "page.dev_sessions": ("dev_sessions", db_utils.load_dev_sessions),
    "page.kickoff": ("crews", db_utils.load_crews),
    "page.results": ("results", db_utils.load_results),
    "page.import_export": ("crews", db_utils.load_crews),
}

PAGE_EXTRA_DATA_LOADERS = {
    "page.crews": (("tools", db_utils.load_tools), ("knowledge_sources", db_utils.load_knowledge_sources), ("agents", db_utils.load_agents), ("tasks", db_utils.load_tasks)),
    "page.agents": (("tools", db_utils.load_tools), ("knowledge_sources", db_utils.load_knowledge_sources), ("agents", db_utils.load_agents), ("tasks", db_utils.load_tasks), ("crews", db_utils.load_crews)),
    "page.tasks": (("tools", db_utils.load_tools), ("knowledge_sources", db_utils.load_knowledge_sources), ("agents", db_utils.load_agents), ("tasks", db_utils.load_tasks), ("crews", db_utils.load_crews)),
    "page.kickoff": (("tools", db_utils.load_tools), ("knowledge_sources", db_utils.load_knowledge_sources), ("agents", db_utils.load_agents), ("tasks", db_utils.load_tasks), ("results", db_utils.load_results)),
    "page.import_export": (("tools", db_utils.load_tools), ("agents", db_utils.load_agents), ("tasks", db_utils.load_tasks)),
    "page.dev_sessions": (("workspaces", db_utils.load_workspaces),),
}


def _page_keys():
    return [page_key for _group_key, page_keys in NAV_GROUPS for page_key in page_keys]


def pages():
    return {t(page_key): PAGE_BUILDERS[page_key] for page_key in _page_keys()}


def _page_label_to_key():
    return {t(page_key): page_key for page_key in _page_keys()}


def _load_state_value(state_key, loader):
    if state_key not in ss:
        ss[state_key] = loader()


def ensure_page_data(page_key):
    for state_key, loader in PAGE_EXTRA_DATA_LOADERS.get(page_key, ()):
        _load_state_value(state_key, loader)

    loader_entry = PAGE_DATA_LOADERS.get(page_key)
    if loader_entry is not None:
        state_key, loader = loader_entry
        _load_state_value(state_key, loader)


def maintain_crew_run_session_state():
    import queue
    import time

    defaults = {
        'crew_thread': None,
        'result': None,
        'running': False,
        'message_queue': queue.Queue(),
        'crew_runs': {},
        'crew_run_order': [],
        'selected_crew_name': None,
        'placeholders': {},
        'console_output': [],
        'last_update': time.time(),
        'console_expanded': True,
    }
    for key, value in defaults.items():
        if key not in ss:
            ss[key] = value


def page_key_to_label(page_key):
    return t(page_key)


def selected_page_key():
    available_pages = _page_label_to_key()
    if 'page' not in ss:
        ss.page = t(DEFAULT_PAGE_KEY)
    if ss.page not in available_pages:
        ss.page = t(DEFAULT_PAGE_KEY)
    return available_pages[ss.page]


def redirect_to_kickoff_if_running(page_key):
    if isinstance(ss.get("crew_runs"), dict):
        return
    if ss.get("running") and page_key != "page.kickoff":
        ss.page = t("page.kickoff")
        st.rerun()


def draw_navigation():
    selected_page_key()

    st.markdown('<div class="studio-nav-shell">', unsafe_allow_html=True)
    for group_key, page_keys in NAV_GROUPS:
        nav_key = group_key.split(".")[-1]
        with st.container(border=False, key=f"nav-card-{nav_key}"):
            st.markdown(f'<div class="studio-nav-card-title">{t(group_key)}</div>', unsafe_allow_html=True)
            for page_key in page_keys:
                label = page_key_to_label(page_key)
                selected = ss.page == label
                icon = PAGE_ICONS.get(page_key, "•")
                button_label = f"{icon}{NAV_ICON_TEXT_SPACER}{label}"
                if st.button(
                    button_label,
                    key=f"nav_{page_key}",
                    use_container_width=True,
                    type="primary" if selected else "secondary",
                    disabled=selected,
                ):
                    ss.page = label
                    st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


def draw_sidebar():
    with st.sidebar:
        draw_navigation()
        setup_language_selector()

def main():
    st.set_page_config(page_title=t('page.title'), page_icon="img/favicon.ico", layout="wide")
    apply_global_styles()
    load_dotenv()
    load_secrets_fron_env()
    if (str(os.getenv('AGENTOPS_ENABLED')).lower() in ['true', '1']) and not ss.get('agentops_failed', False):
        try:
            import agentops
            agentops.init(api_key=os.getenv('AGENTOPS_API_KEY'),auto_start_session=False)    
        except ModuleNotFoundError as e:
            ss.agentops_failed = True
            print(f"Error initializing AgentOps: {str(e)}")            
        
    db_utils.initialize_db()
    maintain_crew_run_session_state()
    draw_sidebar()
    page_key = selected_page_key()
    redirect_to_kickoff_if_running(page_key)
    ensure_page_data(page_key)
    pages()[ss.page]().draw()
    
if __name__ == '__main__':
    main()
