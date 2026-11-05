
import streamlit as st
import os
import hashlib

from src.document_loader import load_multiple_pdfs
from src.text_splitter import split_documents
from src.vector_store import create_vector_store, clear_vector_store
from src.rag_pipeline import get_answer


MAX_FILE_SIZE = 10 * 1024 * 1024
UPLOAD_FOLDER = "data/uploaded_pdfs"


st.set_page_config(
    page_title="AI Knowledge Assistant",
    page_icon="📚",
    layout="wide"
)


# Initialize session state

if "messages" not in st.session_state:
    st.session_state.messages = []

if "documents_processed" not in st.session_state:
    st.session_state.documents_processed = False

if "document_names" not in st.session_state:
    st.session_state.document_names = []

if "total_pages" not in st.session_state:
    st.session_state.total_pages = 0

if "total_chunks" not in st.session_state:
    st.session_state.total_chunks = 0


# Sidebar dashboard

with st.sidebar:

    st.title("📚 Knowledge Assistant")

    st.write("Your personal AI document assistant.")

    st.divider()

    st.subheader("Project Status")

    if st.session_state.documents_processed:
        st.success("Documents ready")
    else:
        st.info("Waiting for documents")

    st.divider()

    st.subheader("Document Statistics")

    st.metric("PDF Files", len(st.session_state.document_names))
    st.metric("Pages Extracted", st.session_state.total_pages)
    st.metric("Text Chunks", st.session_state.total_chunks)

    st.divider()

    st.subheader("Uploaded Documents")

    if st.session_state.document_names:

        for document in st.session_state.document_names:
            st.write("📄", document)

    else:
        st.caption("No documents processed yet.")


# Main application

st.title("📚 AI Knowledge Assistant")

st.write(
    "Upload your PDF documents and ask questions "
    "about their content."
)


# PDF upload

st.subheader("Upload Documents")

uploaded_files = st.file_uploader(
    "Choose PDF documents",
    type=["pdf"],
    accept_multiple_files=True
)


# Process documents

if st.button("Process Documents"):

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
                        f"Duplicate PDF uploaded: {uploaded_file.name}"
                    )

                uploaded_hashes.add(file_hash)

                safe_name = os.path.basename(uploaded_file.name)

                file_path = os.path.join(
                    UPLOAD_FOLDER,
                    safe_name
                )

                with open(file_path, "wb") as file:
                    file.write(uploaded_file.getbuffer())

                file_paths.append(file_path)
                document_names.append(safe_name)

            with st.spinner("Processing your documents..."):

                documents = load_multiple_pdfs(file_paths)

                chunks = split_documents(documents)

                if not chunks:
                    raise ValueError(
                        "No readable text was found in the PDFs."
                    )

                create_vector_store(chunks)

            st.session_state.documents_processed = True
            st.session_state.messages = []

            st.session_state.document_names = document_names
            st.session_state.total_pages = len(documents)
            st.session_state.total_chunks = len(chunks)

            st.success(
                f"Successfully processed {len(document_names)} PDF(s)!"
            )

            st.rerun()

        except Exception as error:

            st.session_state.documents_processed = False

            st.error(
                f"Document processing failed: {error}"
            )


st.divider()


# Document management

st.subheader("Document Management")

if st.button("Clear Knowledge Base"):

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

        st.success("Knowledge base cleared successfully!")

        st.rerun()

    except Exception as error:

        st.error(
            f"Unable to clear knowledge base: {error}"
        )


st.divider()


# Chat section

st.subheader("Ask Your Documents")


if st.button("Clear Chat"):

    st.session_state.messages = []
    st.rerun()


# Display chat history

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Question input

question = st.chat_input(
    "Ask a question about your PDFs..."
)


# Generate answer

if question:

    if not st.session_state.documents_processed:

        st.warning(
            "Please upload and process your documents first."
        )

    else:

        try:

            with st.chat_message("user"):
                st.markdown(question)

            with st.spinner("Finding your answer..."):

                answer, sources = get_answer(
                    question,
                    st.session_state.messages
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
                {"role": "user", "content": question}
            )

            st.session_state.messages.append(
                {"role": "assistant", "content": answer_text}
            )

            st.rerun()

        except Exception as error:

            st.error(
                f"Unable to generate answer: {error}"
            )
