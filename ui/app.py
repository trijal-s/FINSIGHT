import streamlit as st
import requests
import json
import os

# ── Page Config ───────────────────────────────────────
st.set_page_config(
    page_title="FinSight",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background-color: #0d1117;
    color: #e6edf3;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: #161b22;
    border-right: 1px solid #21262d;
}

[data-testid="stSidebar"] .stMarkdown p {
    color: #8b949e;
    font-size: 12px;
    letter-spacing: 0.04em;
}

/* ── Header ── */
.finsight-header {
    padding: 2rem 0 1.5rem 0;
    border-bottom: 1px solid #21262d;
    margin-bottom: 2rem;
}

.finsight-logo {
    font-size: 1.5rem;
    font-weight: 600;
    color: #e6edf3;
    letter-spacing: -0.02em;
}

.finsight-logo span {
    color: #3fb950;
}

.finsight-tagline {
    font-size: 0.8rem;
    color: #8b949e;
    margin-top: 0.25rem;
    font-weight: 400;
}

/* ── Chat messages ── */
.msg-row {
    display: flex;
    width: 100%;
    margin: 0.75rem 0;
}
.msg-row.human { justify-content: flex-end; }
.msg-row.ai    { justify-content: flex-start; }

.msg-human, .msg-ai {
    max-width: 75%;
    padding: 0.8rem 1.1rem;
    font-size: 0.9rem;
    color: #e6edf3;
    line-height: 1.6;
}
.msg-human {
    background: #1f3a5c;
    border: 1px solid #2d4f7c;
    border-radius: 14px 14px 2px 14px;
}
.msg-ai {
    background: #161b22;
    border: 1px solid #21262d;
    border-radius: 14px 14px 14px 2px;
}
.msg-human p, .msg-ai p { margin: 0 0 0.4rem 0; }

.msg-label {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    margin-bottom: 0.5rem;
    text-transform: uppercase;
}

[data-testid="stBottom"], [data-testid="stBottom"] > div {
    background-color: #0d1117 !important;
}
[data-testid="stChatInput"] {
    background-color: #161b22 !important;
    border: 1px solid #30363d !important;
    border-radius: 10px !important;
}
[data-testid="stChatInput"] textarea {
    color: #e6edf3 !important;
}
.msg-label-human { color: #79b8ff; }
.msg-label-ai    { color: #3fb950; }

/* ── Citation badge ── */
.citation {
    display: inline-block;
    background: #1c2128;
    border: 1px solid #30363d;
    border-radius: 4px;
    padding: 0.1rem 0.5rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    color: #8b949e;
    margin: 0 2px;
}

/* ── Input area ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background-color: #161b22 !important;
    border: 1px solid #30363d !important;
    border-radius: 6px !important;
    color: #e6edf3 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.9rem !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #388bfd !important;
    box-shadow: 0 0 0 3px rgba(56, 139, 253, 0.1) !important;
}

/* ── Buttons ── */
.stButton > button {
    background-color: #238636 !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 6px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.875rem !important;
    padding: 0.5rem 1.25rem !important;
    transition: background-color 0.15s ease !important;
}

.stButton > button:hover {
    background-color: #2ea043 !important;
}

/* Secondary button */
.btn-secondary > button {
    background-color: #21262d !important;
    color: #e6edf3 !important;
    border: 1px solid #30363d !important;
}

.btn-secondary > button:hover {
    background-color: #30363d !important;
}

/* ── Selectbox ── */
.stSelectbox > div > div {
    background-color: #161b22 !important;
    border: 1px solid #30363d !important;
    border-radius: 6px !important;
    color: #e6edf3 !important;
}

/* ── Metrics ── */
.metric-card {
    background: #161b22;
    border: 1px solid #21262d;
    border-radius: 8px;
    padding: 1.25rem;
    text-align: center;
}

.metric-value {
    font-size: 1.5rem;
    font-weight: 600;
    color: #3fb950;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: -0.02em;
}

.metric-label {
    font-size: 0.75rem;
    color: #8b949e;
    margin-top: 0.25rem;
    font-weight: 400;
}

/* ── Company badge ── */
.company-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: #1c2128;
    border: 1px solid #30363d;
    border-radius: 20px;
    padding: 0.3rem 0.75rem;
    font-size: 0.8rem;
    color: #8b949e;
    margin: 0.2rem;
    cursor: pointer;
    transition: all 0.15s ease;
}

.company-badge:hover {
    border-color: #388bfd;
    color: #388bfd;
}

.company-badge.active {
    background: #1f3a5c;
    border-color: #388bfd;
    color: #388bfd;
}

/* ── Divider ── */
.finsight-divider {
    border: none;
    border-top: 1px solid #21262d;
    margin: 1.5rem 0;
}

/* ── Empty state ── */
.empty-state {
    text-align: center;
    padding: 4rem 2rem;
    color: #8b949e;
}

.empty-state-icon {
    font-size: 2.5rem;
    margin-bottom: 1rem;
    opacity: 0.5;
}

.empty-state-title {
    font-size: 1rem;
    font-weight: 500;
    color: #e6edf3;
    margin-bottom: 0.5rem;
}

.empty-state-sub {
    font-size: 0.85rem;
    color: #8b949e;
}

/* ── Suggested questions ── */
.suggestion {
    background: #161b22;
    border: 1px solid #21262d;
    border-radius: 6px;
    padding: 0.6rem 1rem;
    font-size: 0.82rem;
    color: #8b949e;
    cursor: pointer;
    transition: all 0.15s ease;
    margin: 0.25rem 0;
}

.suggestion:hover {
    border-color: #388bfd;
    color: #e6edf3;
}

/* ── Status indicator ── */
.status-dot {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #3fb950;
    margin-right: 6px;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%   { opacity: 1; }
    50%  { opacity: 0.4; }
    100% { opacity: 1; }
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0d1117; }
::-webkit-scrollbar-thumb { background: #30363d; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #484f58; }

/* ── Hide Streamlit defaults ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1rem !important; }
</style>
""", unsafe_allow_html=True)

API_BASE = os.environ.get("API_BASE", "http://localhost:8000")

# ── Session State ──────────────────────────────────────
if "messages"        not in st.session_state:
    st.session_state.messages = []
if "selected_company" not in st.session_state:
    st.session_state.selected_company = None
if "companies"       not in st.session_state:
    st.session_state.companies = []
if "chunk_count"     not in st.session_state:
    st.session_state.chunk_count = 0

# ── Fetch companies on load ────────────────────────────
def fetch_companies():
    try:
        r = requests.get(f"{API_BASE}/companies", timeout=5)
        if r.status_code == 200:
            data = r.json()
            st.session_state.companies   = data.get("companies", [])
            st.session_state.chunk_count = data.get("total_chunks", 0)
    except:
        st.session_state.companies   = []
        st.session_state.chunk_count = 0

if not st.session_state.companies:
    fetch_companies()

# ── Sidebar ────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding: 0.5rem 0 1.5rem 0;">
        <div style="font-size:1.1rem;font-weight:600;color:#e6edf3;letter-spacing:-0.01em;">
            Fin<span style="color:#3fb950;">Sight</span>
        </div>
        <div style="font-size:0.72rem;color:#8b949e;margin-top:0.2rem;">
            Annual Report Intelligence
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<p style="font-size:0.7rem;color:#8b949e;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:0.5rem;">Filter by Company</p>', unsafe_allow_html=True)

    # All companies option
    all_selected = st.session_state.selected_company is None
    if st.button(
        f"{'● ' if all_selected else '○ '}All Companies",
        key="btn_all",
        use_container_width=True,
    ):
        st.session_state.selected_company = None
        st.rerun()

    # Individual company buttons
    for company in st.session_state.companies:
        is_selected = st.session_state.selected_company == company
        if st.button(
            f"{'● ' if is_selected else '○ '}{company}",
            key=f"btn_{company}",
            use_container_width=True,
        ):
            st.session_state.selected_company = company
            st.rerun()

    st.markdown('<hr style="border-color:#21262d;margin:1.5rem 0;">', unsafe_allow_html=True)

    # Stats
    st.markdown(f"""
    <div class="metric-card" style="margin-bottom:0.75rem;">
        <div class="metric-value">{st.session_state.chunk_count:,}</div>
        <div class="metric-label">Chunks indexed</div>
    </div>
    <div class="metric-card">
        <div class="metric-value">{len(st.session_state.companies)}</div>
        <div class="metric-label">Companies loaded</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr style="border-color:#21262d;margin:1.5rem 0;">', unsafe_allow_html=True)

    # Clear chat
    with st.container():
        st.markdown('<div class="btn-secondary">', unsafe_allow_html=True)
        if st.button("Clear conversation", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # API status
    try:
        r = requests.get(f"{API_BASE}/health", timeout=2)
        api_ok = r.status_code == 200
    except:
        api_ok = False

    status_color = "#3fb950" if api_ok else "#f85149"
    status_text  = "API connected" if api_ok else "API offline"
    st.markdown(f"""
    <div style="margin-top:1rem;font-size:0.75rem;color:#8b949e;display:flex;align-items:center;gap:0.4rem;">
        <span style="width:7px;height:7px;border-radius:50%;background:{status_color};display:inline-block;"></span>
        {status_text}
    </div>
    """, unsafe_allow_html=True)

# ── Main Area ──────────────────────────────────────────
# Header
company_label = st.session_state.selected_company or "All Companies"
st.markdown(f"""
<div class="finsight-header">
    <div style="display:flex;align-items:baseline;justify-content:space-between;">
        <div>
            <span class="finsight-logo">Fin<span>Sight</span></span>
            <div class="finsight-tagline">Ask questions across annual reports — get cited, accurate answers</div>
        </div>
        <div style="font-size:0.78rem;color:#8b949e;background:#161b22;border:1px solid #21262d;
                    border-radius:20px;padding:0.3rem 0.9rem;font-family:'JetBrains Mono',monospace;">
            {company_label}
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Suggested questions ────────────────────────────────
SUGGESTIONS = [
    "What was the net profit and revenue growth?",
    "What are the key risk factors?",
    "How much dividend was paid per share?",
    "What is the EBITDA margin?",
    "How many employees does the company have?",
]

# ── Pick up a new question (suggestion click or chat box) ──
new_q = st.chat_input("Ask about revenue, profit, risks, dividends...")
if not new_q:
    new_q = st.session_state.pop("pending_question", None)

history = []
if new_q:
    # history = previous turns only (last 3 turns), before adding this question
    history = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages[-6:]
    ]
    st.session_state.messages.append({"role": "human", "content": new_q})


def bubble(role: str, content: str) -> str:
    label = "You" if role == "human" else "FinSight"
    return (
        f'<div class="msg-row {role}"><div class="msg-{role}">'
        f'<div class="msg-label msg-label-{role}">{label}</div>\n\n'
        f'{content}</div></div>'
    )


# ── Chat history ───────────────────────────────────────
if not st.session_state.messages:
    st.markdown("""
<div class="empty-state">
<div class="empty-state-icon">📊</div>
<div class="empty-state-title">Ask anything about the annual reports</div>
<div class="empty-state-sub">Revenue, profit, risk factors, dividends, headcount — all cited with page numbers</div>
</div>
""", unsafe_allow_html=True)

    st.markdown('<p style="text-align:center;font-size:0.78rem;color:#8b949e;margin:1rem 0 0.5rem;">Try asking</p>', unsafe_allow_html=True)
    cols = st.columns(len(SUGGESTIONS))
    for i, suggestion in enumerate(SUGGESTIONS):
        with cols[i]:
            if st.button(suggestion, key=f"sug_{i}", use_container_width=True):
                st.session_state.pending_question = suggestion
                st.rerun()
else:
    for msg in st.session_state.messages:
        st.markdown(bubble(msg["role"], msg["content"]), unsafe_allow_html=True)

# ── Stream the answer for a new question ───────────────
if new_q:
    placeholder = st.empty()
    full_answer = ""
    placeholder.markdown(bubble("ai", "Thinking…"), unsafe_allow_html=True)
    try:
        with requests.post(
            f"{API_BASE}/ask_stream",
            json={
                "query":   new_q,
                "company": st.session_state.selected_company,
                "history": history,
            },
            stream=True,
            timeout=120,
        ) as response:
            if response.status_code != 200:
                placeholder.empty()
                st.error(f"API error: {response.status_code}")
            else:
                for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
                    if chunk:
                        full_answer += chunk
                        placeholder.markdown(bubble("ai", full_answer + " ▌"), unsafe_allow_html=True)
                placeholder.markdown(bubble("ai", full_answer), unsafe_allow_html=True)
                st.session_state.messages.append({"role": "ai", "content": full_answer})
    except requests.exceptions.ConnectionError:
        placeholder.empty()
        st.error("Cannot connect to API. Run: cd src && python api.py")
    except Exception as e:
        placeholder.empty()
        st.error(f"Error: {str(e)}")
