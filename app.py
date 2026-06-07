import streamlit as st
import requests
import os

st.set_page_config(
    page_title="RAG Document Q&A System",
    layout="wide"
)

API_URL = os.getenv("FASTAPI_URL", "https://mistral-rag-system.onrender.com")
if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []


st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&family=Syne:wght@400;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Syne', sans-serif;
        background-color: #080a0c;
        color: #c9d1d9;
    }

    /* ── Main background ── */
    .stApp {
        background-color: #080a0c;
        background-image:
            radial-gradient(ellipse 80% 40% at 50% -10%, rgba(0, 200, 120, 0.06) 0%, transparent 70%),
            linear-gradient(180deg, #080a0c 0%, #0d1117 100%);
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background-color: #0d1117 !important;
        border-right: 1px solid #1c2128;
    }
    section[data-testid="stSidebar"] * {
        color: #8b949e !important;
    }
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] .stSubheader {
        color: #e6edf3 !important;
        font-weight: 700;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        font-size: 0.72rem !important;
    }

    /* ── App header ── */
    .app-header {
        background: #0d1117;
        border: 1px solid #1c2128;
        border-left: 3px solid #00c878;
        padding: 28px 32px;
        border-radius: 8px;
        margin-bottom: 28px;
    }
    .app-header h1 {
        font-family: 'Syne', sans-serif;
        font-size: 1.8rem;
        font-weight: 800;
        color: #e6edf3;
        letter-spacing: -0.02em;
        margin: 0 0 6px 0;
    }
    .app-header p {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.78rem;
        color: #6e7681;
        margin: 0;
        letter-spacing: 0.02em;
    }

    /* ── Cards ── */
    .card {
        background-color: #0d1117;
        padding: 18px 20px;
        border-radius: 8px;
        margin-bottom: 12px;
        border: 1px solid #1c2128;
    }

    /* ── Chat messages ── */
    .user-msg {
        background-color: #161b22;
        border: 1px solid #1c2128;
        border-left: 3px solid #00c878;
        padding: 14px 18px;
        border-radius: 6px;
        color: #e6edf3;
        margin-bottom: 10px;
        max-width: 82%;
        margin-left: auto;
        font-size: 0.9rem;
        line-height: 1.6;
    }
    .assistant-msg {
        background-color: #0d1117;
        border: 1px solid #1c2128;
        padding: 14px 18px;
        border-radius: 6px;
        color: #c9d1d9;
        margin-bottom: 10px;
        max-width: 82%;
        font-size: 0.9rem;
        line-height: 1.6;
        font-family: 'JetBrains Mono', monospace;
    }

    /* ── Section heading ── */
    h2 {
        font-family: 'Syne', sans-serif !important;
        font-weight: 800 !important;
        color: #e6edf3 !important;
        font-size: 1.1rem !important;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        border-bottom: 1px solid #1c2128;
        padding-bottom: 10px;
        margin-bottom: 18px;
    }

    /* ── Buttons ── */
    .stButton > button {
        background-color: #161b22 !important;
        color: #00c878 !important;
        border: 1px solid #00c878 !important;
        border-radius: 6px !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.78rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.06em !important;
        text-transform: uppercase !important;
        padding: 8px 18px !important;
        transition: all 0.15s ease !important;
    }
    .stButton > button:hover {
        background-color: #00c878 !important;
        color: #080a0c !important;
    }
    button[kind="primary"] {
        background-color: #00c878 !important;
        color: #080a0c !important;
        border: 1px solid #00c878 !important;
        border-radius: 6px !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.78rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.06em !important;
        text-transform: uppercase !important;
    }

    /* ── File uploader ── */
    [data-testid="stFileUploader"] {
        background-color: #0d1117 !important;
        border: 1px dashed #2d3748 !important;
        border-radius: 8px !important;
        padding: 12px !important;
    }

    /* ── Chat input ── */
    [data-testid="stChatInput"] textarea {
        background-color: #0d1117 !important;
        border: 1px solid #1c2128 !important;
        border-radius: 6px !important;
        color: #e6edf3 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.85rem !important;
    }
    [data-testid="stChatInput"] textarea:focus {
        border-color: #00c878 !important;
        box-shadow: 0 0 0 2px rgba(0, 200, 120, 0.08) !important;
    }

    /* ── Success / Info / Error ── */
    .stSuccess {
        background-color: rgba(0, 200, 120, 0.07) !important;
        border: 1px solid rgba(0, 200, 120, 0.3) !important;
        border-radius: 6px !important;
        color: #00c878 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.8rem !important;
    }
    .stError {
        background-color: rgba(248, 81, 73, 0.07) !important;
        border: 1px solid rgba(248, 81, 73, 0.3) !important;
        border-radius: 6px !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.8rem !important;
    }
    .stInfo {
        background-color: rgba(58, 118, 220, 0.07) !important;
        border: 1px solid rgba(58, 118, 220, 0.2) !important;
        border-radius: 6px !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.8rem !important;
    }

    /* ── Divider ── */
    hr {
        border-color: #1c2128 !important;
    }

    /* ── Spinner ── */
    .stSpinner > div {
        border-top-color: #00c878 !important;
    }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width: 4px; height: 4px; }
    ::-webkit-scrollbar-track { background: #0d1117; }
    ::-webkit-scrollbar-thumb { background: #2d3748; border-radius: 2px; }
    ::-webkit-scrollbar-thumb:hover { background: #4a5568; }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="app-header">
        <h1>RAG Document Q&amp;A System</h1>
        <p>// Upload documents and query them using Retrieval-Augmented Generation</p>
    </div>
""", unsafe_allow_html=True)


with st.sidebar:
    st.markdown("<h2>Upload Documents</h2>", unsafe_allow_html=True)

    try:
        response = requests.get(f"{API_URL}/supported-formats", timeout=2)
        supported_formats = response.json()["formats"] if response.status_code == 200 else ["pdf"]
    except:
        supported_formats = ["pdf"]

    uploaded_file = st.file_uploader("Choose a file", type=supported_formats)

    if uploaded_file and st.button("Process Document", type="primary"):
        with st.spinner("Processing document..."):
            files = {
                "file": (
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                    uploaded_file.type
                )
            }
            try:
                response = requests.post(f"{API_URL}/upload", files=files)
                if response.status_code == 200:
                    result = response.json()
                    st.success(f"Processed {result['filename']}")
                    st.info(f"Total chunks: {result['total_chunks']}")
                    if uploaded_file.name not in st.session_state.uploaded_files:
                        st.session_state.uploaded_files.append(uploaded_file.name)
                else:
                    try:
                        err = response.json()
                        st.error(err.get("detail", response.text))
                    except:
                        st.error(response.text)
            except Exception as e:
                st.error(str(e))

    if st.session_state.uploaded_files:
        st.markdown("---")
        st.subheader("Uploaded Files")
        for f in st.session_state.uploaded_files:
            st.write(f"✓ {f}")

    st.markdown("---")
    st.subheader("API Status")
    try:
        if requests.get(f"{API_URL}/health", timeout=2).status_code == 200:
            st.success("Connected")
        else:
            st.error("API error")
    except:
        st.error("Disconnected")

# 💬 Chat Interface
st.markdown("<h2>Ask Questions</h2>", unsafe_allow_html=True)

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"<div class='user-msg'>{msg['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='assistant-msg'>{msg['content']}</div>", unsafe_allow_html=True)

if prompt := st.chat_input("Ask a question about your documents..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.spinner("Thinking..."):
        try:
            response = requests.post(f"{API_URL}/query", json={"question": prompt})
            if response.status_code == 200:
                answer = response.json().get("answer", "No answer returned.")
            else:
                try:
                    err = response.json()
                    answer = err.get("detail", response.text)
                except:
                    answer = response.text

            st.session_state.messages.append({"role": "assistant", "content": answer})
            st.rerun()
        except Exception as e:
            st.error(str(e))

if st.session_state.messages and st.button("Clear Chat"):
    st.session_state.messages = []
    st.rerun()