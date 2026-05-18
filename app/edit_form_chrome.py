from html import escape

import streamlit as st


def draw_editor_header(title, subtitle=None, meta=None):
    subtitle_html = f'<div class="studio-editor-subtitle">{escape(str(subtitle))}</div>' if subtitle else ""
    meta_html = f'<div class="studio-editor-meta">{escape(str(meta))}</div>' if meta else ""
    st.markdown(
        f"""
        <div class="studio-editor-header">
          <div>
            <div class="studio-editor-kicker">CONFIGURATION</div>
            <div class="studio-editor-title">{escape(str(title))}</div>
            {subtitle_html}
          </div>
          {meta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def draw_form_section(title, description=None):
    description_html = f'<div class="studio-form-section-desc">{escape(str(description))}</div>' if description else ""
    st.markdown(
        f"""
        <div class="studio-form-section">
          <div class="studio-form-section-title">{escape(str(title))}</div>
          {description_html}
        </div>
        """,
        unsafe_allow_html=True,
    )
