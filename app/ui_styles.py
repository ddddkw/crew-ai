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
          background:
            radial-gradient(circle at 22% 0%, rgba(59, 130, 246, 0.18), transparent 28rem),
            linear-gradient(135deg, rgba(16, 24, 39, 0.96), rgba(24, 34, 53, 0.94) 58%, rgba(16, 24, 39, 0.96));
          border-bottom: 1px solid rgba(148, 163, 184, 0.08);
          box-shadow:
            inset 0 -1px 0 rgba(255, 255, 255, 0.02),
            0 16px 48px rgba(15, 23, 42, 0.20);
          backdrop-filter: blur(12px);
        }

        header[data-testid="stHeader"]::before {
          background: linear-gradient(90deg, transparent, rgba(96, 165, 250, 0.10), transparent);
          height: 1px;
          top: auto;
          bottom: 0;
        }

        header[data-testid="stHeader"] [data-testid="stToolbar"] {
          color: var(--studio-text);
        }

        header[data-testid="stHeader"] button:hover,
        header[data-testid="stHeader"] a:hover {
          background: rgba(96, 165, 250, 0.10) !important;
          border-radius: 7px;
        }

        section[data-testid="stSidebar"] {
          background:
            radial-gradient(circle at 85% 8%, rgba(59, 130, 246, 0.13), transparent 16rem),
            linear-gradient(180deg, rgba(15, 23, 42, 0.98), rgba(11, 18, 30, 0.98) 54%, rgba(8, 13, 22, 0.98));
          border-right: 1px solid rgba(96, 165, 250, 0.10);
          box-shadow:
            inset -1px 0 0 rgba(255, 255, 255, 0.025),
            16px 0 42px rgba(0, 0, 0, 0.14);
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
          margin-bottom: 0.25rem;
        }

        .studio-sidebar-separator {
          height: 1px;
          margin: 0.15rem 0 0.45rem;
          background: rgba(148, 163, 184, 0.13);
          border-radius: 999px;
        }

        section[data-testid="stSidebar"] .st-key-lang-selector {
          margin-top: 0.1rem;
        }

        section[data-testid="stSidebar"] .st-key-lang-selector button,
        [class*="st-key-lang_selector_"] button {
          width: 100%;
          min-height: 2.28rem;
          justify-content: space-between;
          border-radius: 8px;
          border: 1px solid rgba(148, 163, 184, 0.22);
          background: rgba(17, 28, 46, 0.86);
          color: var(--studio-text);
          font-weight: 650;
        }

        section[data-testid="stSidebar"] .st-key-lang-selector button:hover,
        [class*="st-key-lang_selector_"] button:hover {
          border-color: rgba(147, 197, 253, 0.34);
          background: rgba(30, 41, 59, 0.92);
          color: white;
        }

        [class*="st-key-lang_selector_"] button:disabled {
          color: #bfdbfe !important;
          border-color: rgba(96, 165, 250, 0.34) !important;
          background: rgba(37, 99, 235, 0.18) !important;
          opacity: 1 !important;
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
        section[data-testid="stSidebar"] .st-key-nav-card-development,
        section[data-testid="stSidebar"] .st-key-nav-card-system {
          background: linear-gradient(180deg, rgba(23, 32, 51, 0.58), rgba(12, 19, 32, 0.64));
          border: 1px solid rgba(148, 163, 184, 0.14);
          border-radius: 10px;
          box-shadow:
            inset 0 1px 0 rgba(255, 255, 255, 0.035),
            0 12px 30px rgba(0, 0, 0, 0.10);
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
          background: rgba(96, 165, 250, 0.12);
          border-color: rgba(96, 165, 250, 0.26);
          color: white;
        }

        section[data-testid="stSidebar"] .stButton > button[kind="primary"],
        section[data-testid="stSidebar"] .stButton > button:disabled {
          background: linear-gradient(135deg, rgba(37, 99, 235, 0.24), rgba(14, 53, 112, 0.30));
          border-color: rgba(96, 165, 250, 0.42);
          color: white;
          opacity: 1;
          box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04);
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

        body:has(.st-key-dev-session-workbench) .main .block-container,
        .main .block-container:has(.st-key-dev-session-workbench),
        body:has(.st-key-dev-session-workbench) [data-testid="stMain"] .block-container,
        [data-testid="stMain"] .block-container:has(.st-key-dev-session-workbench),
        body:has(.st-key-dev-session-workbench) [data-testid="stMainBlockContainer"],
        [data-testid="stMainBlockContainer"]:has(.st-key-dev-session-workbench) {
          --dev-session-shell-height: calc(100dvh - 0.35rem);
          min-height: var(--dev-session-shell-height) !important;
          height: var(--dev-session-shell-height) !important;
          overflow: hidden;
          padding-top: 0.65rem !important;
          padding-left: 0.45rem !important;
          padding-right: 0.45rem !important;
          padding-bottom: 0.65rem !important;
          margin-top: 0 !important;
          margin-bottom: 0 !important;
        }

        body:has(.st-key-dev-session-workbench) .st-key-dev-session-workbench {
          margin-bottom: 0 !important;
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
        .st-key-workspaces-list-card,
        .st-key-dev-sessions-card,
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

        .st-key-tools-palette-card .stButton,
        .st-key-tools-palette-card [data-testid="stElementContainer"],
        [class*="st-key-enable"] {
          width: 100%;
        }

        .st-key-tools-palette-card .stButton > button,
        .st-key-tools-palette-card button,
        [class*="st-key-enable"] button {
          width: 100%;
          display: flex;
          justify-content: flex-start;
          align-items: center;
          min-height: 2.45rem;
          padding: 0.58rem 0.72rem;
          border-radius: 8px;
          border: 1px solid rgba(148, 163, 184, 0.18);
          background: linear-gradient(180deg, rgba(30, 41, 59, 0.72), rgba(15, 23, 42, 0.76));
          color: var(--studio-text);
          white-space: normal;
          text-align: left;
          line-height: 1.25;
          box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.035);
        }

        .st-key-tools-palette-card button p,
        [class*="st-key-enable"] button p {
          width: 100%;
          text-align: left;
          line-height: 1.25;
        }

        .st-key-tools-palette-card .stButton > button:hover,
        .st-key-tools-palette-card button:hover,
        [class*="st-key-enable"] button:hover {
          border-color: rgba(96, 165, 250, 0.38);
          background: linear-gradient(180deg, rgba(37, 50, 72, 0.88), rgba(16, 32, 57, 0.86));
          color: white;
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

        [class*="st-key-agent-list-"] div[data-testid="stExpander"],
        [class*="st-key-task-list-"] div[data-testid="stExpander"],
        [class*="st-key-crew-list-"] div[data-testid="stExpander"] {
          margin-bottom: 0 !important;
          box-shadow: 0 6px 18px rgba(0, 0, 0, 0.12);
        }

        [class*="st-key-agent-list-"] div[data-testid="stExpander"] summary,
        [class*="st-key-task-list-"] div[data-testid="stExpander"] summary,
        [class*="st-key-crew-list-"] div[data-testid="stExpander"] summary {
          min-height: 2.05rem;
          padding: 0.42rem 0.72rem !important;
        }

        [class*="st-key-agent-list-"][data-testid="stVerticalBlock"],
        [class*="st-key-agent-list-"] [data-testid="stVerticalBlock"],
        [class*="st-key-task-list-"][data-testid="stVerticalBlock"],
        [class*="st-key-task-list-"] [data-testid="stVerticalBlock"],
        [class*="st-key-crew-list-"][data-testid="stVerticalBlock"],
        [class*="st-key-crew-list-"] [data-testid="stVerticalBlock"] {
          gap: 0.45rem !important;
        }

        [class*="st-key-agent-list-"].st-emotion-cache-1n6tfoc,
        [class*="st-key-agent-list-"] .st-emotion-cache-1n6tfoc,
        [class*="st-key-task-list-"].st-emotion-cache-1n6tfoc,
        [class*="st-key-task-list-"] .st-emotion-cache-1n6tfoc,
        [class*="st-key-crew-list-"].st-emotion-cache-1n6tfoc,
        [class*="st-key-crew-list-"] .st-emotion-cache-1n6tfoc {
          gap: 0.45rem !important;
        }

        [class*="st-key-agent-list-"] [data-testid="element-container"],
        [class*="st-key-task-list-"] [data-testid="element-container"],
        [class*="st-key-crew-list-"] [data-testid="element-container"] {
          margin-top: 0 !important;
          margin-bottom: 0.12rem !important;
        }

        [class*="st-key-agent-list-"] [data-testid="stExpander"] details,
        [class*="st-key-task-list-"] [data-testid="stExpander"] details,
        [class*="st-key-crew-list-"] [data-testid="stExpander"] details {
          margin-bottom: 0 !important;
        }

        [class*="st-key-agent-list-"] + .stButton,
        [class*="st-key-task-list-"] + .stButton,
        [class*="st-key-crew-list-"] + .stButton {
          margin-top: 0.24rem;
        }

        div[data-testid="stDialog"] {
          color: var(--studio-text);
        }

        div[data-testid="stDialog"] div[role="dialog"] {
          background:
            radial-gradient(circle at 18% 0%, rgba(239, 68, 68, 0.14), transparent 18rem),
            linear-gradient(180deg, rgba(23, 32, 51, 0.98), rgba(10, 16, 27, 0.98));
          border: 1px solid rgba(148, 163, 184, 0.18);
          border-radius: 14px;
          box-shadow:
            0 30px 90px rgba(0, 0, 0, 0.46),
            inset 0 1px 0 rgba(255, 255, 255, 0.04);
          overflow: hidden;
        }

        div[data-testid="stDialog"] div[role="dialog"] > div {
          padding: 1.05rem 1.35rem 1.2rem;
        }

        div[data-testid="stDialog"] h2,
        div[data-testid="stDialog"] h3,
        div[data-testid="stDialog"] p {
          color: var(--studio-text);
        }

        div[data-testid="stDialog"] button[aria-label="Close"] {
          color: var(--studio-muted);
          border-radius: 7px;
        }

        div[data-testid="stDialog"] button[aria-label="Close"]:hover {
          color: white;
          background: rgba(239, 68, 68, 0.12);
        }

        .studio-delete-hero {
          display: grid;
          grid-template-columns: 2.35rem minmax(0, 1fr);
          gap: 0.85rem;
          align-items: flex-start;
          padding: 0.95rem;
          border: 1px solid rgba(248, 113, 113, 0.24);
          border-radius: 10px;
          background:
            linear-gradient(135deg, rgba(127, 29, 29, 0.28), rgba(30, 41, 59, 0.44));
          margin-bottom: 0.85rem;
        }

        .studio-delete-warning {
          width: 2.2rem;
          height: 2.2rem;
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: 10px;
          border: 1px solid rgba(248, 113, 113, 0.42);
          background: rgba(239, 68, 68, 0.16);
          color: #fecaca;
          font-size: 1.2rem;
          font-weight: 840;
          line-height: 1;
        }

        .studio-delete-title {
          color: #fff7ed;
          font-size: 1.05rem;
          font-weight: 780;
          line-height: 1.25;
          margin-bottom: 0.3rem;
        }

        .studio-delete-copy,
        .studio-delete-note {
          color: #cbd5e1;
          font-size: 0.88rem;
          line-height: 1.55;
        }

        .studio-delete-note {
          padding: 0.75rem 0.85rem;
          border: 1px solid rgba(148, 163, 184, 0.14);
          border-radius: 9px;
          background: rgba(15, 23, 42, 0.42);
          margin-bottom: 0.85rem;
        }

        .studio-delete-scope {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 1rem;
          padding: 0.72rem 0.85rem;
          border: 1px solid rgba(96, 165, 250, 0.20);
          border-radius: 9px;
          background: rgba(37, 99, 235, 0.10);
          margin-bottom: 0.75rem;
        }

        .studio-delete-scope-label {
          color: var(--studio-muted);
          font-size: 0.78rem;
          font-weight: 720;
        }

        .studio-delete-scope-name {
          color: #dbeafe;
          font-weight: 760;
          overflow-wrap: anywhere;
          text-align: right;
        }

        .st-key-delete-dialog-agents,
        .st-key-delete-dialog-tasks {
          background: rgba(15, 23, 42, 0.46);
          border: 1px solid rgba(148, 163, 184, 0.14);
          border-radius: 10px;
          padding: 0.72rem 0.72rem 0.98rem;
          margin-bottom: 0.7rem;
          box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03);
        }

        .studio-delete-group-head {
          display: flex;
          justify-content: space-between;
          gap: 1rem;
          color: #f8fafc;
          font-size: 0.92rem;
          font-weight: 760;
          padding-bottom: 0.55rem;
          margin-bottom: 0.4rem;
          border-bottom: 1px solid rgba(148, 163, 184, 0.12);
        }

        .studio-delete-group-head span:last-child {
          min-width: 1.65rem;
          height: 1.45rem;
          display: inline-flex;
          align-items: center;
          justify-content: center;
          border-radius: 999px;
          border: 1px solid rgba(96, 165, 250, 0.25);
          color: #bfdbfe;
          background: rgba(37, 99, 235, 0.12);
          font-size: 0.76rem;
        }

        .studio-delete-empty {
          color: var(--studio-muted);
          font-size: 0.84rem;
          padding: 0.58rem 0.1rem 0.32rem;
        }

        .st-key-delete-dialog-agents label,
        .st-key-delete-dialog-tasks label {
          padding: 0.42rem 0.5rem;
          border: 1px solid rgba(148, 163, 184, 0.10);
          border-radius: 8px;
          background: rgba(30, 41, 59, 0.30);
          margin-bottom: 0.32rem;
        }

        .st-key-delete-dialog-agents label p,
        .st-key-delete-dialog-tasks label p {
          color: #e5e7eb;
          font-size: 0.84rem;
          line-height: 1.35;
        }

        .studio-delete-actions {
          margin-top: 0.95rem;
          padding-top: 0.95rem;
          border-top: 1px solid rgba(148, 163, 184, 0.14);
        }

        div[data-testid="stDialog"] .studio-delete-actions + div .stButton > button,
        div[data-testid="stDialog"] .stButton > button {
          width: 100%;
          min-height: 2.55rem;
          border-radius: 8px;
          font-weight: 740;
        }

        div[data-testid="stDialog"] .stButton > button[kind="primary"] {
          background: linear-gradient(180deg, #f87171, #dc2626);
          border-color: #fca5a5;
          color: white;
        }

        div[data-testid="stDialog"] .stButton > button[kind="primary"]:hover {
          background: linear-gradient(180deg, #fb7185, #b91c1c);
          border-color: #fecaca;
        }

        [class*="st-key-agent-editor-shell"],
        [class*="st-key-task-editor-shell"],
        [class*="st-key-crew-editor-shell"] {
          background:
            linear-gradient(180deg, rgba(30, 41, 59, 0.74), rgba(15, 23, 42, 0.82));
          border: 1px solid rgba(96, 165, 250, 0.24);
          border-radius: 8px;
          padding: 1rem 1rem 0.9rem;
          box-shadow:
            inset 0 1px 0 rgba(255, 255, 255, 0.04),
            0 18px 44px rgba(0, 0, 0, 0.18);
        }

        .studio-editor-header {
          display: flex;
          align-items: flex-start;
          justify-content: space-between;
          gap: 1rem;
          padding: 0.2rem 0.1rem 0.9rem;
          margin-bottom: 0.8rem;
          border-bottom: 1px solid rgba(148, 163, 184, 0.13);
        }

        .studio-editor-kicker {
          color: #93c5fd;
          font-size: 0.72rem;
          font-weight: 760;
          letter-spacing: 0.08em;
          text-transform: uppercase;
          margin-bottom: 0.28rem;
        }

        .studio-editor-title {
          color: #f8fafc;
          font-size: 1.1rem;
          font-weight: 760;
          line-height: 1.2;
        }

        .studio-editor-subtitle {
          color: var(--studio-muted);
          font-size: 0.86rem;
          margin-top: 0.28rem;
          line-height: 1.35;
        }

        .studio-editor-meta {
          flex: 0 0 auto;
          max-width: 34%;
          border: 1px solid rgba(96, 165, 250, 0.25);
          border-radius: 999px;
          padding: 0.38rem 0.62rem;
          color: #dbeafe;
          background: rgba(37, 99, 235, 0.14);
          font-size: 0.78rem;
          font-weight: 700;
          line-height: 1.2;
          overflow-wrap: anywhere;
        }

        .studio-form-section {
          margin: 0.9rem 0 0.5rem;
          padding-left: 0.65rem;
          border-left: 3px solid rgba(96, 165, 250, 0.54);
        }

        .studio-form-section-title {
          color: #f8fafc;
          font-size: 0.94rem;
          font-weight: 730;
          line-height: 1.2;
        }

        .studio-form-section-desc {
          color: var(--studio-muted);
          font-size: 0.8rem;
          margin-top: 0.18rem;
          line-height: 1.35;
        }

        [class*="st-key-agent-editor-shell"] div[data-testid="stForm"],
        [class*="st-key-task-editor-shell"] div[data-testid="stForm"] {
          background: rgba(7, 12, 22, 0.22);
          border-color: rgba(148, 163, 184, 0.10);
          box-shadow: none;
        }

        [class*="st-key-agent-editor-shell"] label p,
        [class*="st-key-task-editor-shell"] label p,
        [class*="st-key-crew-editor-shell"] label p {
          color: #dbeafe;
          font-weight: 680;
        }

        [class*="st-key-agent-editor-shell"] textarea,
        [class*="st-key-task-editor-shell"] textarea {
          min-height: 7.5rem;
        }

        .studio-editor-actions {
          margin-top: 1rem;
          padding-top: 0.9rem;
          border-top: 1px solid rgba(148, 163, 184, 0.12);
        }

        [class*="st-key-agent-editor-shell"] .stButton > button,
        [class*="st-key-task-editor-shell"] .stButton > button,
        [class*="st-key-crew-editor-shell"] .stButton > button {
          min-height: 2.45rem;
          font-weight: 720;
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

        div[data-testid="stTabs"] [aria-selected="true"]::after,
        div[data-testid="stTabs"] [data-baseweb="tab-highlight"] {
          background-color: #60a5fa !important;
        }

        div[data-testid="stTabs"] [data-baseweb="tab-border"] {
          background-color: rgba(148, 163, 184, 0.14) !important;
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

        .dev-session-workbench {
          display: none;
          grid-template-columns: minmax(14rem, 0.25fr) minmax(0, 1fr);
        }

        .st-key-dev-session-workbench {
          --dev-session-surface: rgba(15, 23, 42, 0.52);
          --dev-session-surface-strong: rgba(23, 32, 51, 0.78);
          --dev-session-outline: rgba(148, 163, 184, 0.14);
          --dev-session-control: rgba(17, 28, 46, 0.86);
          --dev-session-control-hover: rgba(22, 36, 58, 0.94);
          --dev-session-shell-height: calc(100dvh - 0.35rem);
          --dev-session-content-height: calc(var(--dev-session-shell-height) - 1.45rem);
          min-height: var(--dev-session-shell-height) !important;
          height: var(--dev-session-shell-height) !important;
          overflow: hidden;
          border: 0;
          border-radius: 14px;
          background: transparent;
          box-shadow: none;
          padding: 1rem 0.35rem 0.35rem;
          box-sizing: border-box;
        }

        .st-key-dev-session-workbench > [data-testid="stLayoutWrapper"] {
          min-height: var(--dev-session-content-height) !important;
          height: var(--dev-session-content-height) !important;
          display: flex !important;
          flex: 1 1 auto !important;
        }

        .st-key-dev-session-workbench > [data-testid="stLayoutWrapper"] > [data-testid="stHorizontalBlock"] {
          min-height: var(--dev-session-content-height) !important;
          height: var(--dev-session-content-height) !important;
          align-items: stretch !important;
          gap: 0.55rem !important;
        }

        .st-key-dev-session-workbench [data-testid="stHorizontalBlock"] {
          align-items: stretch;
          gap: 0.65rem;
        }

        .st-key-dev-session-workbench > [data-testid="stLayoutWrapper"] > [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
          min-height: var(--dev-session-content-height) !important;
          height: var(--dev-session-content-height) !important;
          align-self: stretch !important;
          display: flex !important;
          flex-direction: column;
        }

        .st-key-dev-session-workbench > [data-testid="stLayoutWrapper"] > [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] > [data-testid="stVerticalBlock"],
        .st-key-dev-session-workbench > [data-testid="stLayoutWrapper"] > [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] > [data-testid="stVerticalBlock"] > [data-testid="stLayoutWrapper"] {
          min-height: var(--dev-session-content-height) !important;
          height: var(--dev-session-content-height) !important;
          display: flex !important;
          flex: 1 1 auto !important;
        }

        .st-key-dev-session-lane,
        .dev-session-lane {
          min-height: var(--dev-session-content-height) !important;
          height: var(--dev-session-content-height) !important;
          flex: 1 1 auto !important;
          overflow-x: hidden;
          overflow-y: auto;
          scrollbar-gutter: stable;
          border: 1px solid var(--dev-session-outline);
          border-radius: 14px;
          background:
            linear-gradient(180deg, var(--dev-session-surface-strong), rgba(10, 17, 29, 0.68));
          padding: 0.7rem;
          box-shadow:
            inset 0 1px 0 rgba(255, 255, 255, 0.035),
            0 14px 38px rgba(0, 0, 0, 0.12);
        }

        .dev-session-lane-card {
          display: none;
        }

        .st-key-dev-session-lane [data-testid="stVerticalBlock"] {
          min-height: 100%;
          gap: 0.5rem !important;
        }

        .dev-session-lane-summary {
          display: grid;
          gap: 0.35rem;
          border: 1px solid rgba(96, 165, 250, 0.18);
          border-radius: 12px;
          background:
            linear-gradient(135deg, rgba(37, 99, 235, 0.16), rgba(15, 23, 42, 0.34));
          padding: 0.76rem 0.82rem;
          box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04);
        }

        .dev-session-lane-eyebrow {
          color: #93c5fd;
          font-size: 0.68rem;
          font-weight: 780;
          letter-spacing: 0.08em;
          line-height: 1;
          text-transform: uppercase;
        }

        .dev-session-lane-title {
          color: #f8fafc;
          font-size: 0.98rem;
          font-weight: 780;
          line-height: 1.2;
          overflow-wrap: anywhere;
        }

        .dev-session-lane-path {
          color: var(--studio-muted);
          font-size: 0.74rem;
          line-height: 1.35;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        .dev-session-lane-stats {
          width: fit-content;
          display: inline-flex;
          align-items: center;
          gap: 0.36rem;
          min-height: 1.55rem;
          border: 1px solid rgba(148, 163, 184, 0.13);
          border-radius: 999px;
          background: rgba(15, 23, 42, 0.42);
          color: #bfdbfe;
          padding: 0 0.5rem;
          font-size: 0.72rem;
          font-weight: 720;
        }

        .st-key-dev-session-lane-controls {
          border: 1px solid rgba(148, 163, 184, 0.12);
          border-radius: 12px;
          background: rgba(8, 13, 22, 0.22);
          padding: 0.58rem;
        }

        .st-key-dev-session-lane-controls > [data-testid="stVerticalBlock"] {
          gap: 0.54rem !important;
        }

        .st-key-dev-session-lane-controls [data-testid="stHorizontalBlock"] {
          gap: 0.48rem;
        }

        .st-key-dev-session-lane-controls label p {
          color: #cbd5e1;
          font-size: 0.76rem;
          font-weight: 720;
          margin-bottom: 0.24rem;
        }

        .st-key-dev-session-lane .stButton > button {
          justify-content: flex-start;
          min-height: 2.36rem;
          border-radius: 8px;
          color: var(--studio-text);
          background: rgba(30, 41, 59, 0.46);
          border-color: rgba(148, 163, 184, 0.13);
          box-shadow: none;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
          font-weight: 700;
        }

        .st-key-dev-session-lane .stButton > button:hover {
          background: rgba(37, 50, 72, 0.78);
          border-color: rgba(96, 165, 250, 0.32);
        }

        .st-key-dev-session-lane .stButton > button[kind="primary"],
        .st-key-dev-session-lane .stButton > button:disabled {
          background: linear-gradient(135deg, rgba(37, 99, 235, 0.34), rgba(29, 78, 216, 0.24));
          border-color: rgba(147, 197, 253, 0.38);
          color: #f8fafc;
          opacity: 1;
          box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.05);
        }

        .st-key-dev-session-lane div[data-baseweb="select"] > div,
        .st-key-dev-session-lane input {
          min-height: 2.36rem;
          border-radius: 8px !important;
          background: var(--dev-session-control) !important;
          border-color: rgba(148, 163, 184, 0.18) !important;
          color: var(--studio-text) !important;
          box-shadow: none !important;
        }

        .st-key-dev-session-lane div[data-baseweb="select"] > div:hover,
        .st-key-dev-session-lane input:hover,
        .st-key-dev-session-lane input:focus {
          border-color: rgba(147, 197, 253, 0.34) !important;
          background: var(--dev-session-control-hover) !important;
        }

        .dev-session-section-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-top: 0.75rem;
        }

        .dev-session-section-label {
          display: block;
          color: #93c5fd;
          font-size: 0.74rem;
          font-weight: 760;
          letter-spacing: 0.06em;
          text-transform: uppercase;
          margin: 0.75rem 0 0.28rem;
        }

        .dev-session-inline-notice {
          border: 1px solid rgba(34, 197, 94, 0.22);
          border-radius: 8px;
          background: rgba(22, 101, 52, 0.14);
          color: #bbf7d0;
          padding: 0.58rem 0.72rem;
          font-size: 0.83rem;
          font-weight: 650;
          line-height: 1.42;
          box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03);
        }

        .st-key-dev-session-session-list,
        .dev-session-session-list {
          width: 100%;
        }

        .st-key-dev-session-session-list [data-testid="stVerticalBlock"] {
          gap: 0.44rem !important;
        }

        [class*="st-key-dev-session-session-row-"] [data-testid="stHorizontalBlock"] {
          align-items: center;
          gap: 0.35rem;
        }

        [class*="st-key-dev-session-session-"] button {
          width: 100%;
          min-height: 2.38rem;
          justify-content: flex-start;
          overflow: hidden;
          text-overflow: ellipsis;
        }

        .dev-session-session-delete,
        [class*="st-key-dev-session-session-delete-"] button,
        [class*="st-key-delete-dev-session-sidebar-"] button {
          min-height: 2.38rem;
          justify-content: center !important;
          padding: 0 !important;
          color: #fca5a5;
          border-color: rgba(248, 113, 113, 0.24);
          background: rgba(127, 29, 29, 0.16);
          font-size: 1rem;
          font-weight: 800;
        }

        [class*="st-key-delete-dev-session-sidebar-"] button:hover {
          color: #fecaca;
          border-color: rgba(248, 113, 113, 0.44);
          background: rgba(127, 29, 29, 0.28);
        }

        .dev-session-empty-state {
          border: 1px solid rgba(148, 163, 184, 0.12);
          border-radius: 10px;
          color: var(--studio-muted);
          background: rgba(15, 23, 42, 0.30);
          padding: 0.74rem 0.82rem;
          font-size: 0.84rem;
          line-height: 1.42;
          box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.025);
        }

        .dev-session-empty-title {
          color: #dbeafe;
          font-size: 0.78rem;
          font-weight: 760;
          margin-bottom: 0.22rem;
        }

        .dev-session-empty-copy {
          color: var(--studio-muted);
          font-size: 0.8rem;
          line-height: 1.42;
        }

        .st-key-dev-session-conversation,
        .dev-session-conversation {
          min-height: var(--dev-session-content-height) !important;
          height: var(--dev-session-content-height) !important;
          flex: 1 1 auto !important;
          overflow: hidden;
          border: 1px solid var(--dev-session-outline);
          border-radius: 14px;
          background: linear-gradient(180deg, var(--dev-session-surface), rgba(8, 13, 22, 0.36));
          padding: 0.95rem;
          box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03);
        }

        .st-key-dev-session-conversation:has(.st-key-dev-session-home),
        .dev-session-conversation:has(.dev-session-home) {
          border: 0;
          background: transparent;
          box-shadow: none;
          padding: 0.2rem 0.35rem 0;
        }

        .st-key-dev-session-conversation > [data-testid="stLayoutWrapper"],
        .st-key-dev-session-conversation > [data-testid="stLayoutWrapper"] > [data-testid="stVerticalBlock"] {
          min-height: 100% !important;
          height: 100% !important;
          display: flex !important;
          flex: 1 1 auto !important;
          gap: 0.75rem !important;
        }

        .st-key-dev-session-conversation:not(:has(.st-key-dev-session-home)) > [data-testid="stLayoutWrapper"] > [data-testid="stVerticalBlock"] {
          flex-direction: column !important;
          align-items: stretch !important;
          min-height: 0 !important;
        }

        .dev-session-main {
          min-height: auto;
          height: fit-content;
        }

        .dev-session-topbar {
          display: flex;
          align-items: flex-start;
          justify-content: space-between;
          gap: 1rem;
          border-bottom: 1px solid rgba(148, 163, 184, 0.12);
          padding: 0.25rem 0 0.85rem;
        }

        .dev-session-topbar-title {
          color: #f8fafc;
          font-size: 1.1rem;
          font-weight: 760;
          line-height: 1.25;
          overflow-wrap: anywhere;
        }

        .dev-session-topbar-subtitle {
          color: var(--studio-muted);
          font-size: 0.8rem;
          margin-top: 0.26rem;
          overflow-wrap: anywhere;
        }

        .dev-session-topbar-actions {
          display: inline-flex;
          align-items: center;
          flex-wrap: wrap;
          gap: 0.48rem;
          color: var(--studio-muted);
          font-size: 0.82rem;
        }

        .dev-session-model-provider,
        .dev-session-model-name,
        .dev-session-topbar-actions span {
          display: inline-flex;
          align-items: center;
          min-height: 1.85rem;
          border: 1px solid rgba(148, 163, 184, 0.16);
          border-radius: 999px;
          padding: 0 0.62rem;
          color: #dbeafe;
          background: rgba(30, 41, 59, 0.58);
          font-size: 0.78rem;
          font-weight: 640;
        }

        .st-key-dev-session-conversation:not(:has(.st-key-dev-session-home)) [class*="st-key-dev-session-thread-"] {
          flex: 1 1 auto !important;
          min-height: 0 !important;
          overflow: hidden;
        }

        .st-key-dev-session-conversation:not(:has(.st-key-dev-session-home)) .st-key-dev-session-chat-canvas,
        .st-key-dev-session-conversation:not(:has(.st-key-dev-session-home)) .dev-session-chat-canvas {
          height: 100% !important;
          min-height: 0 !important;
          max-height: none !important;
        }

        .st-key-dev-session-conversation:not(:has(.st-key-dev-session-home)) [class*="st-key-dev-session-chat-canvas"] > [data-testid="stVerticalBlock"] {
          height: 100% !important;
          min-height: 0 !important;
          max-height: none !important;
        }

        .st-key-dev-session-conversation:not(:has(.st-key-dev-session-home)) .st-key-dev-session-bottom-composer,
        .st-key-dev-session-conversation:not(:has(.st-key-dev-session-home)) .dev-session-bottom-composer {
          flex: 0 0 auto !important;
          margin-top: 0 !important;
          margin-bottom: 0 !important;
        }

        .dev-session-layout {
          margin: 0;
        }

        .st-key-dev-session-home,
        .dev-session-home {
          min-height: 100% !important;
          height: 100% !important;
          display: flex !important;
          flex: 1 1 auto !important;
          flex-direction: column;
          justify-content: stretch;
          padding-top: 0;
        }

        .st-key-dev-session-home > [data-testid="stLayoutWrapper"],
        .st-key-dev-session-home > [data-testid="stLayoutWrapper"] > [data-testid="stVerticalBlock"] {
          min-height: 100% !important;
          height: 100% !important;
          display: flex !important;
          flex: 1 1 auto !important;
          align-items: center;
          gap: 0.95rem !important;
        }

        .st-key-dev-session-home-shell {
          width: min(100%, 76rem);
          margin: 0 auto;
          border: 1px solid var(--dev-session-outline);
          border-radius: 16px;
          background:
            linear-gradient(180deg, var(--dev-session-surface-strong), rgba(10, 16, 27, 0.48));
          padding: clamp(1rem, 2vw, 1.55rem);
          min-height: 100% !important;
          height: 100% !important;
          display: flex !important;
          flex: 1 1 auto !important;
          flex-direction: column;
          justify-content: stretch;
          box-shadow:
            inset 0 1px 0 rgba(255, 255, 255, 0.04),
            0 22px 60px rgba(0, 0, 0, 0.18);
        }

        .st-key-dev-session-home-shell > [data-testid="stLayoutWrapper"],
        .st-key-dev-session-home-shell > [data-testid="stLayoutWrapper"] > [data-testid="stVerticalBlock"] {
          min-height: 100% !important;
          height: 100% !important;
          display: flex !important;
          flex: 1 1 auto !important;
          justify-content: flex-start;
          gap: 1.15rem !important;
        }

        .st-key-dev-session-home-shell > [data-testid="stLayoutWrapper"] > [data-testid="stVerticalBlock"] {
          flex-direction: column !important;
        }

        .dev-session-home-card {
          max-width: 48rem;
          margin: 0.35rem auto 0;
          text-align: center;
        }

        .dev-session-home-kicker,
        .dev-session-home-context {
          width: fit-content;
          margin: 0 auto 0.55rem;
          border: 1px solid rgba(96, 165, 250, 0.22);
          border-radius: 999px;
          background: rgba(37, 99, 235, 0.12);
          color: #bfdbfe;
          padding: 0.24rem 0.64rem;
          font-size: 0.74rem;
          font-weight: 720;
          line-height: 1.2;
        }

        .dev-session-home-context {
          max-width: min(34rem, 92%);
          margin-bottom: 1rem;
          border-color: rgba(148, 163, 184, 0.14);
          background: rgba(15, 23, 42, 0.44);
          color: var(--studio-muted);
          overflow-wrap: anywhere;
        }

        .dev-session-hero-title {
          color: #f8fafc;
          font-size: clamp(1.7rem, 2.4vw, 2.15rem);
          font-weight: 700;
          line-height: 1.16;
          letter-spacing: 0;
          margin-bottom: 0.55rem;
        }

        .dev-session-home-subtitle {
          color: var(--studio-muted);
          font-size: 0.94rem;
          line-height: 1.55;
          max-width: 38rem;
          margin: 0 auto;
        }

        .dev-session-home-spacer {
          width: 100%;
          flex: 1 1 100%;
          min-height: clamp(12rem, 34vh, 28rem);
        }

        .st-key-dev-session-home-composer-card,
        .st-key-dev-session-bottom-composer,
        .dev-session-home-composer-card,
        .dev-session-bottom-composer {
          max-width: 64rem;
          width: 100%;
          margin: 0 auto;
        }

        .st-key-dev-session-home-composer-card,
        .dev-session-home-composer-card {
          margin-top: auto !important;
          margin-bottom: 0 !important;
          flex: 0 0 auto !important;
          align-self: stretch;
        }

        [class*="st-key-dev-session-composer-"] {
          border: 0;
          background: transparent;
          padding: 0;
          margin: 0;
          box-shadow: none;
        }

        [class*="st-key-dev-session-new-chat-composer-"],
        [class*="st-key-dev-session-followup-composer-"] {
          border: 1px solid rgba(148, 163, 184, 0.18);
          border-radius: 14px;
          background: rgba(17, 24, 39, 0.82);
          padding: 0.85rem 0.9rem 0.78rem;
          box-shadow: 0 14px 34px rgba(0, 0, 0, 0.16), inset 0 1px 0 rgba(255, 255, 255, 0.035);
        }

        [class*="st-key-dev-session-new-chat-composer-"] [data-testid="stVerticalBlock"],
        [class*="st-key-dev-session-followup-composer-"] [data-testid="stVerticalBlock"] {
          gap: 0.58rem !important;
        }

        [class*="st-key-dev-session-new-chat-composer-"] textarea,
        [class*="st-key-dev-session-followup-composer-"] textarea {
          min-height: 5rem !important;
          border: 0 !important;
          background: transparent !important;
          box-shadow: none !important;
          color: var(--studio-text) !important;
          font-size: 0.98rem;
          line-height: 1.5;
        }

        [class*="st-key-dev-session-new-chat-composer-"] textarea:focus,
        [class*="st-key-dev-session-followup-composer-"] textarea:focus {
          border: 0 !important;
          box-shadow: none !important;
        }

        [class*="st-key-dev-session-new-chat-composer-"] div[data-baseweb="select"] > div,
        [class*="st-key-dev-session-composer-"] div[data-baseweb="select"] > div {
          min-height: 2.25rem;
          border-radius: 8px;
          background: rgba(30, 41, 59, 0.72);
          border-color: rgba(148, 163, 184, 0.18);
        }

        [class*="st-key-dev-session-composer-toolbar-"] {
          margin-top: -0.2rem;
        }

        [class*="st-key-dev-session-composer-toolbar-"] > [data-testid="stVerticalBlock"] {
          gap: 0 !important;
        }

        [class*="st-key-dev-session-composer-toolbar-"] [data-testid="stHorizontalBlock"] {
          align-items: center;
          gap: 0.48rem;
        }

        [class*="st-key-dev-session-composer-toolbar-"] [data-testid="stElementContainer"] {
          margin-bottom: 0 !important;
        }

        .dev-session-toolbar-right {
          display: inline-flex;
          align-items: center;
          gap: 0.45rem;
          color: var(--studio-muted);
          font-size: 0.82rem;
          min-height: 2.25rem;
        }

        .dev-session-send-arrow,
        .dev-session-create-arrow,
        [class*="st-key-dev-session-send-arrow-"] button,
        [class*="st-key-dev-session-create-arrow-"] button {
          width: 2.45rem !important;
          min-width: 2.45rem !important;
          height: 2.45rem !important;
          min-height: 2.45rem !important;
          padding: 0 !important;
          border-radius: 999px;
          justify-content: center;
          align-items: center;
          font-size: 1.1rem;
          font-weight: 740;
          line-height: 1;
        }

        [class*="st-key-dev-session-send-arrow-"] button,
        [class*="st-key-dev-session-create-arrow-"] button {
          background: linear-gradient(180deg, rgba(15, 23, 42, 0.98), rgba(17, 24, 39, 0.96)) !important;
          border-color: rgba(148, 163, 184, 0.24) !important;
          color: #f8fafc !important;
          box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.06), 0 10px 20px rgba(0, 0, 0, 0.22) !important;
        }

        [class*="st-key-dev-session-send-arrow-"] button:hover,
        [class*="st-key-dev-session-create-arrow-"] button:hover {
          background: linear-gradient(180deg, rgba(30, 41, 59, 0.98), rgba(23, 32, 51, 0.98)) !important;
          border-color: rgba(226, 232, 240, 0.34) !important;
          color: white !important;
          box-shadow: 0 12px 24px rgba(0, 0, 0, 0.24), inset 0 1px 0 rgba(255, 255, 255, 0.10) !important;
        }

        .dev-session-send-button {
          display: none;
        }

        .st-key-dev-session-chat-canvas,
        .dev-session-chat-canvas {
          height: clamp(24rem, 56vh, 44rem);
          min-height: 24rem;
          max-height: 44rem;
          max-width: 68rem;
          width: 100%;
          margin: 0 auto;
          padding: 0.8rem 0 0.2rem;
          overflow-x: hidden;
          overflow-y: auto;
          overscroll-behavior: contain;
          scrollbar-gutter: stable;
        }

        [class*="st-key-dev-session-chat-canvas"] > [data-testid="stVerticalBlock"] {
          height: clamp(24rem, 56vh, 44rem);
          min-height: 24rem;
          max-height: 44rem;
          overflow-x: hidden;
          overflow-y: auto;
          overscroll-behavior: contain;
          scrollbar-gutter: stable;
        }

        .st-key-dev-session-chat-canvas::-webkit-scrollbar,
        .dev-session-chat-canvas::-webkit-scrollbar,
        [class*="st-key-dev-session-chat-canvas"] > [data-testid="stVerticalBlock"]::-webkit-scrollbar {
          width: 0.55rem;
        }

        .st-key-dev-session-chat-canvas::-webkit-scrollbar-thumb,
        .dev-session-chat-canvas::-webkit-scrollbar-thumb,
        [class*="st-key-dev-session-chat-canvas"] > [data-testid="stVerticalBlock"]::-webkit-scrollbar-thumb {
          border-radius: 999px;
          background: rgba(148, 163, 184, 0.24);
        }

        .st-key-dev-session-chat-canvas::-webkit-scrollbar-track,
        .dev-session-chat-canvas::-webkit-scrollbar-track,
        [class*="st-key-dev-session-chat-canvas"] > [data-testid="stVerticalBlock"]::-webkit-scrollbar-track {
          background: transparent;
        }

        .dev-session-codex-stream {
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
        }

        .dev-session-message {
          border: 0;
          border-radius: 0;
          background: transparent;
          padding: 0;
          margin-bottom: 0;
        }

        .dev-session-chat-thread {
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
          min-height: 100%;
          overflow: visible;
        }

        [class*="st-key-dev-session-thread-"] {
          width: 100%;
        }

        [class*="st-key-dev-session-thread-"] [data-testid="stVerticalBlock"] {
          gap: 0.75rem !important;
        }

        .dev-session-user-message-row {
          display: flex;
          flex-direction: column;
          align-items: flex-end;
          gap: 0.28rem;
          margin-left: auto;
        }

        .dev-session-current-user-bubble,
        .dev-session-chat-message {
          width: fit-content;
          max-width: min(58rem, 88%);
          border: 1px solid rgba(148, 163, 184, 0.14);
          border-radius: 14px;
          padding: 0.72rem 0.82rem;
          background: rgba(15, 23, 42, 0.56);
          color: var(--studio-text);
          box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03);
        }

        .dev-session-current-user-bubble,
        .dev-session-chat-message.is-user {
          margin-left: auto;
          border-color: rgba(96, 165, 250, 0.34);
          background: rgba(37, 99, 235, 0.18);
        }

        .dev-session-chat-message.is-assistant {
          margin-right: auto;
        }

        .dev-session-chat-role {
          color: #93c5fd;
          font-size: 0.72rem;
          font-weight: 760;
          margin-bottom: 0.26rem;
        }

        .dev-session-chat-content {
          color: inherit;
          font-size: 0.95rem;
          line-height: 1.56;
          overflow-wrap: anywhere;
        }

        .dev-session-copy-icon {
          color: var(--studio-subtle);
          font-size: 0.72rem;
          padding-right: 0.4rem;
        }

        .dev-session-working {
          color: var(--studio-muted);
          font-size: 0.9rem;
          font-weight: 560;
          line-height: 1.35;
          margin: 0.72rem 0 0.38rem;
          padding-bottom: 0.72rem;
          border-bottom: 1px solid rgba(148, 163, 184, 0.13);
        }

        .dev-session-stream-cursor {
          display: inline-block;
          width: 0.48rem;
          height: 1em;
          margin-left: 0.12rem;
          transform: translateY(0.12em);
          border-radius: 999px;
          background: rgba(147, 197, 253, 0.9);
          animation: dev-session-stream-caret 0.9s ease-in-out infinite;
        }

        .dev-session-thinking {
          width: fit-content;
          max-width: 100%;
          display: inline-flex;
          align-items: center;
          gap: 0.48rem;
          color: #cbd5e1;
          font-size: 0.84rem;
          font-weight: 650;
          line-height: 1;
          margin: 0.65rem 0 0.1rem;
          padding: 0.5rem 0.68rem;
          border: 1px solid rgba(148, 163, 184, 0.16);
          border-radius: 999px;
          background: rgba(15, 23, 42, 0.58);
          box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.035);
          white-space: nowrap;
        }

        .dev-session-thinking-dot {
          width: 0.55rem;
          height: 0.55rem;
          flex: 0 0 auto;
          border-radius: 999px;
          background: #93c5fd;
          box-shadow: 0 0 0 0 rgba(147, 197, 253, 0.45);
          animation: dev-session-thinking-pulse 1.35s ease-out infinite;
        }

        @keyframes dev-session-thinking-pulse {
          0% {
            transform: scale(0.78);
            opacity: 0.72;
            box-shadow: 0 0 0 0 rgba(147, 197, 253, 0.36);
          }

          70% {
            transform: scale(1);
            opacity: 1;
            box-shadow: 0 0 0 0.42rem rgba(147, 197, 253, 0);
          }

          100% {
            transform: scale(0.78);
            opacity: 0.72;
            box-shadow: 0 0 0 0 rgba(147, 197, 253, 0);
          }
        }

        @keyframes dev-session-stream-caret {
          0%, 100% {
            opacity: 0.24;
          }

          50% {
            opacity: 1;
          }
        }

        [class*="st-key-workspace-directory-picker-"] {
          background: rgba(15, 23, 42, 0.32);
          border: 1px solid rgba(96, 165, 250, 0.16);
          border-radius: 10px;
          padding: 0.85rem;
          margin: 0.55rem 0 1rem;
        }

        [class*="st-key-workspace-directory-picker-"] .stButton > button {
          min-height: 2.25rem;
          width: 100%;
          justify-content: flex-start;
          overflow-wrap: anywhere;
        }

        @media (max-width: 1100px) {
          .st-key-dev-session-workbench {
            min-height: auto !important;
            height: auto !important;
            overflow: visible;
          }

          .st-key-dev-session-workbench > [data-testid="stLayoutWrapper"],
          .st-key-dev-session-workbench > [data-testid="stLayoutWrapper"] > [data-testid="stHorizontalBlock"],
          .st-key-dev-session-workbench > [data-testid="stLayoutWrapper"] > [data-testid="stHorizontalBlock"] > [data-testid="stColumn"],
          .st-key-dev-session-workbench > [data-testid="stLayoutWrapper"] > [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] > [data-testid="stVerticalBlock"],
          .st-key-dev-session-workbench > [data-testid="stLayoutWrapper"] > [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] > [data-testid="stVerticalBlock"] > [data-testid="stLayoutWrapper"] {
            min-height: auto !important;
            height: auto !important;
          }

          .st-key-dev-session-workbench [data-testid="stHorizontalBlock"] {
            flex-direction: column;
          }

          .st-key-dev-session-lane,
          .dev-session-lane,
          .st-key-dev-session-conversation,
          .dev-session-conversation {
            width: 100%;
            min-height: auto !important;
            height: auto !important;
            overflow: visible;
          }

          .st-key-dev-session-lane-controls [data-testid="stHorizontalBlock"],
          [class*="st-key-dev-session-session-row-"] [data-testid="stHorizontalBlock"],
          [class*="st-key-dev-session-composer-toolbar-"] [data-testid="stHorizontalBlock"] {
            flex-direction: row;
          }

          .st-key-dev-session-home,
          .dev-session-home {
            min-height: auto !important;
            height: auto !important;
            padding-top: 0.75rem;
          }

          .st-key-dev-session-home > [data-testid="stLayoutWrapper"],
          .st-key-dev-session-home > [data-testid="stLayoutWrapper"] > [data-testid="stVerticalBlock"],
          .st-key-dev-session-home-shell,
          .st-key-dev-session-home-shell > [data-testid="stLayoutWrapper"],
          .st-key-dev-session-home-shell > [data-testid="stLayoutWrapper"] > [data-testid="stVerticalBlock"] {
            min-height: auto !important;
            height: auto !important;
          }

          .st-key-dev-session-home-shell {
            padding: 0.95rem;
          }

          .dev-session-home-spacer {
            height: 1.5rem;
            min-height: 1.5rem;
            flex: 0 0 auto;
          }
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
