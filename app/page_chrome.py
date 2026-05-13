import html

import streamlit as st


def draw_page_header(title, section="", subtitle="", count=None):
    safe_title = html.escape(str(title))
    safe_section = html.escape(str(section)) if section else ""
    safe_subtitle = html.escape(str(subtitle)) if subtitle else ""
    count_markup = ""
    if count is not None:
        count_markup = f'<div class="studio-page-count">{html.escape(str(count))}</div>'

    st.markdown(
        f"""
        <div class="studio-page-header">
          <div>
            <div class="studio-page-kicker">{safe_section}</div>
            <div class="studio-page-title">{safe_title}</div>
            <div class="studio-page-subtitle">{safe_subtitle}</div>
          </div>
          <div class="studio-page-actions">{count_markup}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
