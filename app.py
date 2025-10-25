import streamlit as st
import requests

st.set_page_config(
    page_title="RAG Document Q&A System",
    layout="wide"
)

API_URL = "http://localhost:8000"

if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []

st.title("RAG Document Q&A System")
st.markdown("Upload your documents and ask questions about them!")

with st.sidebar:
    st.header(" Upload Documents")

    try:
        response = requests.get(f"{API_URL}/supported-formats", timeout=2)
        if response.status_code == 200:
            supported_formats = response.json()["formats"]
            format_display = ", ".join([f.upper() for f in supported_formats])
            st.markdown(f"**Supported formats:** {format_display}")
        else:
            supported_formats = ["pdf", "docx"]
            st.markdown("**Supported formats:** PDF, DOCX")
    except:
        supported_formats = ["pdf", "docx"]
        st.markdown("**Supported formats:** PDF, DOCX")

    uploaded_file = st.file_uploader(
        "Choose a file",
        type=supported_formats,
        help="Upload documents to add to the knowledge base"
    )

    if uploaded_file is not None:
        if st.button("Process Document", type="primary"):
            with st.spinner("Processing document..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}

                    response = requests.post(f"{API_URL}/upload", files=files)

                    if response.status_code == 200:
                        result = response.json()
                        st.success(f" Successfully processed {result['filename']}")
                        st.info(f" Total chunks created: {result['total_chunks']}")

                        if uploaded_file.name not in st.session_state.uploaded_files:
                            st.session_state.uploaded_files.append(uploaded_file.name)
                    else:
                        error_data = response.json()
                        st.error(f" Error: {error_data.get('detail', 'Unknown error')}")
                except Exception as e:
                    st.error(f" Error uploading file: {str(e)}")

    if st.session_state.uploaded_files:
        st.markdown("---")
        st.subheader("Uploaded Files")
        for file in st.session_state.uploaded_files:
            st.text(f"✓ {file}")

    st.markdown("---")
    st.subheader("🔌 API Status")
    try:
        response = requests.get(f"{API_URL}/health", timeout=2)
        if response.status_code == 200:
            st.success("Connected")
        else:
            st.error("API Error")
    except:
        st.error("Disconnected")
        st.caption("Make sure the API is running on port 8000")
        st.caption("Run: python main.py")


st.markdown("---")
st.header("💬 Ask Questions")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask a question about your documents..."):

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    f"{API_URL}/query",
                    json={"question": prompt}
                )

                if response.status_code == 200:
                    answer = response.json()["answer"]
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    error_msg = f"Error: {response.text}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
            except Exception as e:
                error_msg = f"Error connecting to API: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})


if st.session_state.messages:
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()


st.markdown("---")
st.caption("Built with Streamlit, FastAPI, ChromaDB, and Mistral AI")
st.caption(
    "⚠️ Python 3.13: Image and advanced PPTX processing not available. Use Python 3.12 or lower for full features.")