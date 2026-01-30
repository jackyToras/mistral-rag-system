import streamlit as st
import requests
import os


st.set_page_config(
    page_title="RAG Document Q&A System",
    layout="wide"
)

API_URL = os.getenv("FASTAPI_URL", "http://localhost:8000")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []

st.markdown(
    """
    <style>
    body { background-color: #0e1117; color: #e6e6e6; }
    .app-header { background: linear-gradient(90deg, #4f46e5, #9333ea); padding: 20px; border-radius: 12px; margin-bottom: 20px; color: white; }
    .card { background-color: #161b22; padding: 16px; border-radius: 12px; margin-bottom: 12px; border: 1px solid #262730; }
    section[data-testid="stSidebar"] { background-color: #0b0f14; }
    .user-msg { background-color: #2563eb; padding: 12px; border-radius: 12px; color: white; margin-bottom: 8px; max-width: 80%; }
    .assistant-msg { background-color: #1f2937; padding: 12px; border-radius: 12px; margin-bottom: 8px; max-width: 80%; border: 1px solid #374151; }
    button[kind="primary"] { background-color: #4f46e5 !important; border-radius: 8px !important; }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="app-header">
        <h1>📄 RAG Document Q&A System</h1>
        <p>Upload documents and ask intelligent questions using Retrieval-Augmented Generation.</p>
    </div>
    """,
    unsafe_allow_html=True
)

with st.sidebar:
    st.markdown("<h2>📤 Upload Documents</h2>", unsafe_allow_html=True)

    try:
        response = requests.get(f"{API_URL}/supported-formats", timeout=2)
        if response.status_code == 200:
            supported_formats = response.json()["formats"]
            st.markdown(
                f"**Supported formats:** {', '.join([f.upper() for f in supported_formats])}"
            )
        else:
            supported_formats = ["pdf"]
    except:
        supported_formats = ["pdf"]

    uploaded_file = st.file_uploader(
        "Choose a file",
        type=supported_formats
    )

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
                    # Show concise backend error message
                    try:
                        err = response.json()
                        st.error(err.get("detail", response.text))
                    except:
                        st.error(response.text)
            except Exception as e:
                st.error(str(e))

    if st.session_state.uploaded_files:
        st.markdown("---")
        st.subheader("📚 Uploaded Files")
        for f in st.session_state.uploaded_files:
            st.write(f"✓ {f}")

    st.markdown("---")
    st.subheader("🔌 API Status")
    try:
        if requests.get(f"{API_URL}/health", timeout=2).status_code == 200:
            st.success("Connected")
        else:
            st.error("API error")
    except:
        st.error("Disconnected")

st.markdown("<h2>💬 Ask Questions</h2>", unsafe_allow_html=True)

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(
            f"<div class='user-msg'>{msg['content']}</div>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"<div class='assistant-msg'>{msg['content']}</div>",
            unsafe_allow_html=True
        )

if prompt := st.chat_input("Ask a question about your documents..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.spinner("Thinking..."):
        try:
            response = requests.post(
                f"{API_URL}/query",
                json={"question": prompt}
            )
            if response.status_code == 200:
                data = response.json()
                answer = data.get("answer", "No answer returned.")
            else:
                try:
                    err = response.json()
                    answer = err.get("detail", response.text)
                except:
                    answer = response.text

            st.session_state.messages.append(
                {"role": "assistant", "content": answer}
            )
            st.rerun()
        except Exception as e:
            st.error(str(e))

if st.session_state.messages and st.button("🗑️ Clear Chat"):
    st.session_state.messages = []
    st.rerun()
