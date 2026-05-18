import streamlit as st
from streamlit import session_state as ss
from my_crew import MyCrew
import db_utils
from i18n import t
from page_chrome import draw_page_header

class PageCrews:
    def __init__(self):
        self.name = t("page.crews")

    def create_crew(self):
        crew = MyCrew()
        if 'crews' not in ss:
            ss.crews = [MyCrew]
        ss.crews.append(crew)
        crew.is_new = True
        crew.edit = True
        db_utils.save_crew(crew)  # Save crew to database
        return crew

    def draw(self):
        if 'crews' not in ss:
            ss.crews = db_utils.load_crews()  # Load crews from database

        draw_page_header(
            self.name,
            section=t("nav.workspace"),
            subtitle=t("crew.all_crews"),
            count=len(ss.crews),
        )

        with st.container(border=True, key="crews-list-card"):
            editing = False
            with st.container(key="crew-list-all"):
                for crew in ss.crews:
                    crew.draw()
                    if crew.edit:
                        editing = True
            if len(ss.crews) == 0:
                st.write(t("crew.none_defined"))
            st.button(t("button.create_crew"), on_click=self.create_crew, disabled=editing)
