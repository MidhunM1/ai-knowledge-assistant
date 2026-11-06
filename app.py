
import streamlit as st
import os
import hashlib

from src.document_loader import load_multiple_pdfs
from src.text_splitter import split_documents
from src.vector_store import create_vector_store, clear_vector_store
from src.rag_pipeline import get_answer
from src.error_handling import safe_api_error_message


MAX_FILE_SIZE = 10 * 1024 * 1024
UPLOAD_FOLDER = "data/uploaded_pdfs"


# ---------------- PAGE CONFIGURATION ----------------

st.set_page_config(
    page_title="AI Knowledge Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ---------------- CUSTOM CSS ----------------

st.markdown("""
<style>

/* Main page */

.stApp {
    background-color: #ffffff;
    color: #202123;
}

header[data-testid="stHeader"] {
    background-color: #ffffff;
}

.block-container {
    max-width: 900px;
    padding-top: 2rem;
    padding-bottom: 7rem;
}

/* Sidebar */

[data-testid="stSidebar"] {
    background-color: #f7f7f8;
    border-right: 1px solid #e5e5e5;
}

[data-testid="stSidebar"] * {
    color: #202123;
}

/* Headings */

h1, h2, h3, p, label {
    color: #202123;
}

.main-title {
    font-size: 28px;
    font-weight: 600;
    text-align: center;
    margin-top: 100px;
    margin-bottom: 12px;
    color: #202123;
}

.subtitle {
    text-align: center;
    color: #666666;
    font-size: 15px;
    margin-bottom: 35px;
}

/* Buttons */

.stButton > button {
    border-radius: 8px;
    border: 1px solid #dddddd;
    background: #ffffff;
    color: #202123 !important;
    min-height: 38px;
}

.stButton > button:hover {
    background: #eeeeee;
    color: #202123 !important;
    border-color: #cccccc;
}

/* PDF uploader */

[data-testid="stFileUploader"] {
    background: #ffffff !important;
    border: 1px dashed #b8b8b8 !important;
    border-radius: 10px;
    padding: 12px;
    color: #202123 !important;
}

[data-testid="stFileUploader"] * {
    color: #202123 !important;
}

[data-testid="stFileUploader"] section {
    background: #ffffff !important;
}

[data-testid="stFileUploader"] button {
    background: #f5f5f5 !important;
    color: #202123 !important;
    border: 1px solid #cccccc !important;
}

/* Chat messages */

[data-testid="stChatMessage"] {
    background: transparent;
    border: none;
    padding: 12px 0;
    color: #202123;
}

/* Bottom chat area */

[data-testid="stBottom"] {
    background: #0e0e0e !important;
}

/* Chat input container */

[data-testid="stChatInput"] {
    background: #000000 !important;
    border: 1.5px solid #ff3b3b !important;
    border-radius: 12px !important;
    box-shadow: none !important;
}

[data-testid="stChatInput"] > div {
    background: #000000 !important;
}

/* Typed text */

[data-testid="stChatInput"] textarea {
    background: #000000 !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    caret-color: #ffffff !important;
}

/* Placeholder */

[data-testid="stChatInput"] textarea::placeholder {
    color: #cccccc !important;
    -webkit-text-fill-color: #cccccc !important;
    opacity: 1 !important;
}

/* Send button */

[data-testid="stChatInput"] button {
    background: #ff3b3b !important;
    color: #ffffff !important;
    border: none !important;
}

/* Separators */

hr {
    border-color: #e5e5e5;
}

.small-text {
    color: #666666;
    font-size: 12px;
}

</style>
""", unsafe_allow_html=True)


# ---------------- SESSION STATE ----------------

defaults = {
    "messages": [],
    "documents_processed": False,
    "document_names": [],
    "total_pages": 0,
    "total_chunks": 0
}

for key, value in defaults.items():

    if key not in st.session_state:
        st.session_state[key] = value


# ---------------- SIDEBAR ----------------

with st.sidebar:

    st.markdown("## 📚 AI Knowledge Assistant")

    st.caption("Chat with your PDF documents")

    st.divider()

    # New chat

    if st.button("＋ New Chat", use_container_width=True):

        st.session_state.messages = []

        st.rerun()

    st.divider()

    # Upload documents

    st.markdown("### Upload documents")

    uploaded_files = st.file_uploader(
        "Choose PDF files",
        type=["pdf"],
        accept_multiple_files=True
    )

    # Process documents

    if st.button("Process Documents", use_container_width=True):

        if not uploaded_files:

            st.warning("Please upload at least one PDF.")

        else:

            try:

                os.makedirs(UPLOAD_FOLDER, exist_ok=True)

                file_paths = []
                document_names = []
                uploaded_hashes = set()

                for uploaded_file in uploaded_files:

                    if uploaded_file.size > MAX_FILE_SIZE:

                        raise ValueError(
                            f"{uploaded_file.name} exceeds the 10 MB limit."
                        )

                    if not uploaded_file.name.lower().endswith(".pdf"):

                        raise ValueError(
                            f"{uploaded_file.name} is not a PDF."
                        )

                    file_hash = hashlib.sha256(
                        uploaded_file.getvalue()
                    ).hexdigest()

                    if file_hash in uploaded_hashes:

                        raise ValueError(
                            f"Duplicate PDF: {uploaded_file.name}"
                        )

                    uploaded_hashes.add(file_hash)

                    safe_name = os.path.basename(
                        uploaded_file.name
                    )

                    file_path = os.path.join(
                        UPLOAD_FOLDER,
                        safe_name
                    )

                    with open(file_path, "wb") as file:

                        file.write(
                            uploaded_file.getbuffer()
                        )

                    file_paths.append(file_path)

                    document_names.append(safe_name)

                with st.spinner(
                    "Reading and processing documents..."
                ):

                    documents = load_multiple_pdfs(
                        file_paths
                    )

                    chunks = split_documents(
                        documents
                    )

                    if not chunks:

                        raise ValueError(
                            "No readable text found in the PDFs."
                        )

                    create_vector_store(chunks)

                st.session_state.documents_processed = True

                st.session_state.document_names = document_names

                st.session_state.total_pages = len(documents)

                st.session_state.total_chunks = len(chunks)

                st.session_state.messages = []

                st.success(
                    "Documents processed successfully!"
                )

                st.rerun()

            except Exception as error:

                st.error(
                    safe_api_error_message(
                        error,
                        "Document processing"
                    )
                )

    st.divider()

    # Uploaded document list

    st.markdown("### Your documents")

    if st.session_state.document_names:

        for document in st.session_state.document_names:

            st.caption(f"📄 {document}")

        st.caption(
            f"{st.session_state.total_pages} pages • "
            f"{st.session_state.total_chunks} chunks"
        )

    else:

        st.caption("No documents uploaded yet.")

    # Knowledge base status

    if st.session_state.documents_processed:

        st.success("Knowledge base ready")

    else:

        st.info("Upload PDFs to get started")

    st.divider()

    # Clear knowledge base

    if st.button(
        "🗑️ Clear Knowledge Base",
        use_container_width=True
    ):

        try:

            clear_vector_store()

            if os.path.exists(UPLOAD_FOLDER):

                for filename in os.listdir(UPLOAD_FOLDER):

                    file_path = os.path.join(
                        UPLOAD_FOLDER,
                        filename
                    )

                    if os.path.isfile(file_path):

                        os.remove(file_path)

            st.session_state.documents_processed = False

            st.session_state.messages = []

            st.session_state.document_names = []

            st.session_state.total_pages = 0

            st.session_state.total_chunks = 0

            st.success("Knowledge base cleared.")

            st.rerun()

        except Exception as error:

            st.error(str(error))


# ---------------- MAIN CHAT AREA ----------------

if not st.session_state.messages:

    st.markdown(
        '<div class="main-title">'
        'What would you like to know?'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        'Upload your PDFs and ask anything about their content.'
        '</div>',
        unsafe_allow_html=True
    )

else:

    st.markdown("### AI Knowledge Assistant")


# ---------------- DISPLAY CHAT HISTORY ----------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])


# ---------------- CHAT INPUT ----------------

question = st.chat_input(
    "Ask anything about your documents..."
)


# ---------------- GENERATE ANSWER ----------------

if question:

    if not st.session_state.documents_processed:

        st.warning(
            "Please upload and process your PDF documents first."
        )

    else:

        st.session_state.messages.append(
            {
                "role": "user",
                "content": question
            }
        )

        with st.chat_message("user"):

            st.markdown(question)

        try:

            with st.chat_message("assistant"):

                with st.spinner("Thinking..."):

                    answer, sources = get_answer(
                        question,
                        st.session_state.messages[:-1]
                    )

                st.markdown(answer)

                if sources:

                    st.markdown("**Sources**")

                    for source in sources:

                        st.caption(
                            f"📄 {source['file']} "
                            f"· Page {source['page']}"
                        )

            answer_text = answer

            if sources:

                answer_text += "\n\n**Sources:**\n"

                for source in sources:

                    answer_text += (
                        f"- {source['file']} "
                        f"(Page {source['page']})\n"
                    )

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer_text
                }
            )

        except Exception as error:

            st.session_state.messages.pop()

            st.error(
                safe_api_error_message(
                    error,
                    "Answer generation"
                )
            )
