import streamlit as st


def apply_global_styles():
    st.markdown(
        """
        <style>
        :root {
          --studio-bg: #101827;
          --studio-panel: #172033;
          --studio-panel-soft: #1e293b;
          --studio-panel-deep: #0f172a;
          --studio-border: #334155;
          --studio-border-strong: #475569;
          --studio-text: #e5e7eb;
          --studio-muted: #94a3b8;
          --studio-subtle: #64748b;
          --studio-accent: #3b82f6;
          --studio-accent-strong: #2563eb;
          --studio-danger: #ef4444;
          --studio-success: #22c55e;
          --studio-radius: 8px;
        }

        .stApp {
          background:
            radial-gradient(circle at top left, rgba(59, 130, 246, 0.16), transparent 34rem),
            linear-gradient(135deg, #101827 0%, #182235 52%, #101827 100%);
          color: var(--studio-text);
        }

        header[data-testid="stHeader"] {
          background: rgba(8, 12, 19, 0.72);
          border-bottom: 1px solid rgba(148, 163, 184, 0.10);
          box-shadow: none;
          backdrop-filter: blur(10px);
        }

        header[data-testid="stHeader"]::before {
          background: transparent;
        }

        section[data-testid="stSidebar"] {
          background: linear-gradient(180deg, rgba(9, 13, 20, 0.98), rgba(8, 12, 19, 0.96));
          border-right: 1px solid rgba(148, 163, 184, 0.10);
          box-shadow: 16px 0 42px rgba(0, 0, 0, 0.16);
        }

        section[data-testid="stSidebar"] > div {
          padding-top: 0 !important;
        }

        section[data-testid="stSidebar"] [data-testid="stSidebarHeader"] {
          height: 2rem !important;
          min-height: 2rem !important;
          margin-bottom: 0.15rem !important;
        }

        section[data-testid="stSidebar"] [data-testid="stLogoSpacer"] {
          height: 0 !important;
          min-height: 0 !important;
          margin: 0 !important;
        }

        section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] {
          margin-left: auto !important;
          visibility: visible !important;
          opacity: 1 !important;
          transform: translateY(0.75rem);
        }

        section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] button {
          width: 2.45rem !important;
          height: 2.45rem !important;
          min-width: 2.45rem !important;
          min-height: 2.45rem !important;
          padding: 0 !important;
          color: var(--studio-muted) !important;
        }

        section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] svg {
          width: 1.75rem !important;
          height: 1.75rem !important;
        }

        section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"]:hover button {
          color: white !important;
          background: rgba(59, 130, 246, 0.12) !important;
        }

        section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {
          padding-top: 0.2rem !important;
        }

        section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] > div:first-child {
          padding-top: 0 !important;
        }

        .studio-nav-shell {
          margin-top: 0;
          margin-bottom: 0.9rem;
        }

        .studio-nav-card-title {
          color: var(--studio-subtle);
          font-size: 0.72rem;
          font-weight: 700;
          letter-spacing: 0.08em;
          text-transform: uppercase;
          margin: 0 0 0.35rem;
        }

        section[data-testid="stSidebar"] .st-key-nav-card-workspace,
        section[data-testid="stSidebar"] .st-key-nav-card-run,
        section[data-testid="stSidebar"] .st-key-nav-card-system {
          background: rgba(15, 23, 42, 0.34);
          border: 1px solid rgba(148, 163, 184, 0.12);
          border-radius: 10px;
          box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03);
          margin-bottom: 0.75rem;
          padding: 0.55rem 0.45rem 0.45rem;
        }

        section[data-testid="stSidebar"] .stButton > button {
          justify-content: flex-start;
          min-height: 2.35rem;
          border-radius: 7px;
          border: 1px solid transparent;
          background: transparent;
          color: var(--studio-muted);
          font-weight: 560;
          padding-left: 0.75rem;
        }

        section[data-testid="stSidebar"] .stButton > button:hover {
          background: rgba(59, 130, 246, 0.11);
          border-color: rgba(59, 130, 246, 0.28);
          color: white;
        }

        section[data-testid="stSidebar"] .stButton > button[kind="primary"],
        section[data-testid="stSidebar"] .stButton > button:disabled {
          background: rgba(37, 99, 235, 0.17);
          border-color: rgba(96, 165, 250, 0.34);
          color: white;
          opacity: 1;
        }

        .main .block-container {
          padding: 2rem 2.1rem 3rem;
          max-width: 1500px;
          margin-top: 0.9rem;
          margin-bottom: 1.2rem;
          background: rgba(30, 41, 59, 0.34);
          border: 1px solid rgba(148, 163, 184, 0.16);
          border-radius: 10px;
          box-shadow: 0 20px 70px rgba(0, 0, 0, 0.20);
        }

        h1, h2, h3 {
          letter-spacing: 0;
        }

        .studio-page-header {
          display: flex;
          align-items: flex-end;
          justify-content: space-between;
          gap: 16px;
          border: 1px solid rgba(148, 163, 184, 0.14);
          border-radius: 10px;
          background: linear-gradient(135deg, rgba(30, 41, 59, 0.72), rgba(15, 23, 42, 0.58));
          padding: 18px 20px;
          margin-bottom: 16px;
          box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04), 0 16px 42px rgba(0, 0, 0, 0.18);
        }

        .studio-page-kicker {
          color: #93c5fd;
          font-size: 0.78rem;
          font-weight: 700;
          letter-spacing: 0.08em;
          text-transform: uppercase;
          margin-bottom: 5px;
        }

        .studio-page-title {
          color: white;
          font-size: 1.65rem;
          font-weight: 760;
          line-height: 1.15;
        }

        .studio-page-subtitle {
          color: var(--studio-muted);
          font-size: 0.9rem;
          margin-top: 6px;
        }

        .studio-page-count {
          min-width: 2.6rem;
          height: 2.2rem;
          border-radius: 999px;
          border: 1px solid rgba(96, 165, 250, 0.36);
          background: rgba(37, 99, 235, 0.16);
          color: white;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: 740;
        }

        .studio-page-actions {
          display: flex;
          align-items: center;
          gap: 0.6rem;
        }

        .studio-surface-card,
        .st-key-agents-workspace-card,
        .st-key-tasks-workspace-card,
        .st-key-tools-palette-card,
        .st-key-tools-enabled-card,
        .st-key-knowledge-workspace-card,
        .st-key-model-settings-card,
        .st-key-results-filter-card,
        .st-key-results-list-card,
        .st-key-export-workspace-card {
          background: rgba(15, 23, 42, 0.38);
          border: 1px solid rgba(148, 163, 184, 0.14);
          border-radius: 10px;
          padding: 14px;
          box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.035);
        }

        .studio-muted-panel {
          background: rgba(30, 41, 59, 0.32);
          border: 1px solid rgba(148, 163, 184, 0.12);
          border-radius: 8px;
        }

        .st-key-crews-list-card {
          background: rgba(15, 23, 42, 0.38);
          border: 1px solid rgba(148, 163, 184, 0.14);
          border-radius: 10px;
          padding: 14px;
          box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.035);
        }

        div[data-testid="stExpander"] {
          border: 1px solid rgba(148, 163, 184, 0.18);
          border-radius: 9px;
          background: linear-gradient(180deg, rgba(30, 41, 59, 0.72), rgba(15, 23, 42, 0.82));
          box-shadow: 0 12px 34px rgba(0, 0, 0, 0.18);
          overflow: hidden;
          margin-bottom: 0.8rem;
        }

        div[data-testid="stExpander"] summary {
          min-height: 2.65rem;
          padding: 0.72rem 0.9rem !important;
          color: white;
          background: rgba(30, 41, 59, 0.38);
          border-radius: 9px;
        }

        div[data-testid="stExpander"]:hover {
          border-color: rgba(96, 165, 250, 0.36);
          background: linear-gradient(180deg, rgba(37, 50, 72, 0.78), rgba(15, 23, 42, 0.86));
        }

        [class*="st-key-agent-list-"] div[data-testid="stExpander"] {
          margin-bottom: 0.38rem;
          box-shadow: 0 8px 22px rgba(0, 0, 0, 0.14);
        }

        [class*="st-key-agent-list-"] div[data-testid="stExpander"] summary {
          min-height: 2.25rem;
          padding: 0.5rem 0.78rem !important;
        }

        div[data-testid="stForm"] {
          border: 1px solid rgba(148, 163, 184, 0.14);
          border-radius: 10px;
          background: rgba(15, 23, 42, 0.46);
          padding: 1rem;
        }

        div[data-testid="stTabs"] [data-baseweb="tab-list"] {
          gap: 0.35rem;
          border-bottom: 1px solid rgba(148, 163, 184, 0.14);
          margin-bottom: 1rem;
        }

        div[data-testid="stTabs"] [data-baseweb="tab"] {
          border-radius: 7px 7px 0 0;
          color: var(--studio-muted);
          font-weight: 650;
          padding: 0.7rem 0.85rem;
        }

        div[data-testid="stTabs"] [aria-selected="true"] {
          color: white;
          background: rgba(37, 99, 235, 0.14);
        }

        div[data-testid="stFileUploader"] {
          border: 1px dashed rgba(147, 197, 253, 0.28);
          border-radius: 10px;
          background: rgba(15, 23, 42, 0.38);
          padding: 0.65rem;
        }

        .stButton > button {
          border-radius: 7px;
          border: 1px solid var(--studio-border-strong);
          background: #182235;
          color: var(--studio-text);
          min-height: 2.35rem;
        }

        .stButton > button:hover {
          border-color: var(--studio-accent);
          color: white;
          background: #172033;
        }

        .stButton > button[kind="primary"] {
          background: linear-gradient(180deg, #60a5fa, #2563eb);
          border-color: #60a5fa;
          color: white;
        }

        .stTextInput input,
        .stTextArea textarea,
        .stNumberInput input,
        div[data-baseweb="select"] > div {
          border-radius: 7px;
          border-color: rgba(148, 163, 184, 0.22);
          background-color: #111c2e;
        }

        .crew-run-cockpit {
          border: 1px solid var(--studio-border);
          background: linear-gradient(135deg, rgba(17, 24, 39, 0.94), rgba(8, 12, 19, 0.92));
          border-radius: 8px;
          padding: 18px 20px;
          margin-bottom: 16px;
          box-shadow: 0 18px 45px rgba(0, 0, 0, 0.28);
        }

        .crew-run-title-row {
          display: flex;
          align-items: flex-start;
          justify-content: space-between;
          gap: 16px;
          margin-bottom: 16px;
        }

        .crew-run-eyebrow {
          color: var(--studio-muted);
          font-size: 0.78rem;
          text-transform: uppercase;
          letter-spacing: 0.08em;
          margin-bottom: 4px;
        }

        .crew-run-title {
          color: white;
          font-size: 1.75rem;
          font-weight: 760;
          line-height: 1.15;
        }

        .crew-run-subtitle {
          color: var(--studio-muted);
          margin-top: 6px;
          font-size: 0.92rem;
        }

        .crew-run-status {
          display: inline-flex;
          align-items: center;
          gap: 8px;
          border: 1px solid var(--studio-border-strong);
          border-radius: 999px;
          padding: 7px 11px;
          color: var(--studio-text);
          background: #0f172a;
          white-space: nowrap;
        }

        .crew-run-status-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background: var(--studio-subtle);
        }

        .crew-run-status.is-running .crew-run-status-dot {
          background: var(--studio-success);
          box-shadow: 0 0 0 5px rgba(34, 197, 94, 0.14);
        }

        .crew-run-metrics {
          display: grid;
          grid-template-columns: repeat(4, minmax(0, 1fr));
          gap: 10px;
        }

        .crew-run-metric {
          border: 1px solid var(--studio-border);
          border-radius: 8px;
          background: rgba(15, 23, 42, 0.88);
          padding: 12px;
        }

        .crew-run-metric-label {
          color: var(--studio-muted);
          font-size: 0.76rem;
          margin-bottom: 5px;
        }

        .crew-run-metric-value {
          color: white;
          font-size: 1.28rem;
          font-weight: 760;
          line-height: 1.1;
        }

        .crew-run-panel {
          border: 1px solid var(--studio-border);
          border-radius: 8px;
          background: rgba(17, 24, 39, 0.78);
          padding: 15px;
          margin-bottom: 14px;
        }

        .crew-run-panel-title {
          color: white;
          font-size: 1rem;
          font-weight: 700;
          margin-bottom: 4px;
        }

        .crew-run-panel-caption {
          color: var(--studio-muted);
          font-size: 0.86rem;
          margin-bottom: 12px;
        }

        .crew-run-log-panel {
          border: 1px solid var(--studio-border);
          border-radius: 8px;
          background: #060a10;
          padding: 12px;
          min-height: 220px;
        }

        .crew-run-log-panel pre {
          background: transparent !important;
        }

        @media (max-width: 900px) {
          .crew-run-title-row {
            display: block;
          }
          .crew-run-status {
            margin-top: 12px;
          }
          .crew-run-metrics {
            grid-template-columns: repeat(2, minmax(0, 1fr));
          }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
