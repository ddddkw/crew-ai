import streamlit as st
from streamlit import session_state as ss
import db_utils
from pg_agents import PageAgents
from pg_tasks import PageTasks
from pg_crews import PageCrews
from pg_tools import PageTools
from pg_crew_run import PageCrewRun
from pg_export_crew import PageExportCrew
from pg_results import PageResults
from pg_knowledge import PageKnowledge
from pg_model_settings import PageModelSettings
from dotenv import load_dotenv
from llms import load_secrets_fron_env
from i18n import t, setup_language_selector
from ui_styles import apply_global_styles
import os

NAV_GROUPS = [
    ("nav.workspace", ["page.crews", "page.agents", "page.tasks", "page.tools", "page.knowledge"]),
    ("nav.run", ["page.kickoff", "page.results"]),
    ("nav.system", ["page.model_settings", "page.import_export"]),
]

PAGE_ICONS = {
    "page.crews": "▦",
    "page.agents": "◎",
    "page.tasks": "☑",
    "page.tools": "⚙",
    "page.knowledge": "◇",
    "page.kickoff": "▶",
    "page.results": "▤",
    "page.model_settings": "◉",
    "page.import_export": "⇄",
}

def pages():
    return {
        t('page.crews'): PageCrews(),
        t('page.tools'): PageTools(),
        t('page.agents'): PageAgents(),
        t('page.tasks'): PageTasks(),
        t('page.knowledge'): PageKnowledge(),
        t('page.kickoff'): PageCrewRun(),
        t('page.results'): PageResults(),
        t('page.model_settings'): PageModelSettings(),
        t('page.import_export'): PageExportCrew()
    }

def load_data():
    ss.agents = db_utils.load_agents()
    ss.tasks = db_utils.load_tasks()
    ss.crews = db_utils.load_crews()
    ss.tools = db_utils.load_tools()
    ss.enabled_tools = db_utils.load_tools_state()
    ss.knowledge_sources = db_utils.load_knowledge_sources()


def page_key_to_label(page_key):
    return t(page_key)


def draw_navigation():
    available_pages = pages()
    if 'page' not in ss:
        ss.page = t('page.crews')
    if ss.page not in available_pages:
        ss.page = t('page.crews')

    st.markdown('<div class="studio-nav-shell">', unsafe_allow_html=True)
    for group_key, page_keys in NAV_GROUPS:
        nav_key = group_key.split(".")[-1]
        with st.container(border=True, key=f"nav-card-{nav_key}"):
            st.markdown(f'<div class="studio-nav-card-title">{t(group_key)}</div>', unsafe_allow_html=True)
            for page_key in page_keys:
                label = page_key_to_label(page_key)
                selected = ss.page == label
                icon = PAGE_ICONS.get(page_key, "•")
                button_label = f"{icon}  {label}"
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
    load_data()
    draw_sidebar()
    PageCrewRun.maintain_session_state() #this will persist the session state for the crew run page so crew run can be run in a separate thread
    pages()[ss.page].draw()
    
if __name__ == '__main__':
    main()
