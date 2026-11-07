import streamlit as st

from config import SUPABASE_URL, SUPABASE_KEY

st.write("Supabase URL loaded:", bool(SUPABASE_URL))
st.write("Supabase KEY loaded:", bool(SUPABASE_KEY))

import os
import hashlib
import shutil

from src.document_loader import load_multiple_pdfs
from src.text_splitter import split_documents

from src.vector_store import (
    create_vector_store,
    clear_vector_store,
    vector_store_exists,
    close_vector_store
)

from src.rag_pipeline import get_answer
from src.error_handling import safe_api_error_message

from src.chat_history import (
    create_conversation,
    get_conversations,
    get_messages,
    save_message,
    rename_conversation,
    delete_conversation
)

from src.auth import sign_up, sign_in, sign_out


MAX_FILE_SIZE = 10 * 1024 * 1024

UPLOAD_FOLDER = "data/uploaded_pdfs"

DB_FOLDER = "chroma_db"


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

/* ==============================
   MAIN APPLICATION
============================== */

.stApp {
    background-color: var(--background-color);
    color: var(--text-color);
}

.block-container {
    max-width: 900px;
    padding-top: 2rem;
    padding-bottom: 7rem;
}

/* ==============================
   HEADER
============================== */

header[data-testid="stHeader"] {
    background-color: var(--background-color);
}

/* ==============================
   SIDEBAR
============================== */

[data-testid="stSidebar"] {
    background-color: var(--secondary-background-color);
    border-right: 1px solid var(--border-color, rgba(128,128,128,0.2));
}

/* ==============================
   TEXT
============================== */

h1, h2, h3, h4, p, label {
    color: var(--text-color);
}

.stMarkdown {
    color: var(--text-color);
}

.main-title {
    font-size: 28px;
    font-weight: 600;
    text-align: center;
    margin-top: 100px;
    margin-bottom: 12px;
    color: var(--text-color);
}

.subtitle {
    text-align: center;
    color: var(--text-color);
    opacity: 0.65;
    font-size: 15px;
    margin-bottom: 35px;
}

.small-text {
    color: var(--text-color);
    opacity: 0.65;
    font-size: 12px;
}

/* ==============================
   TEXT INPUTS
============================== */

.stTextInput input {
    background-color: var(--secondary-background-color) !important;
    color: var(--text-color) !important;
    -webkit-text-fill-color: var(--text-color) !important;
    border: 1px solid var(--border-color, rgba(128,128,128,0.3)) !important;
    border-radius: 8px !important;
}

.stTextInput input::placeholder {
    color: var(--text-color) !important;
    -webkit-text-fill-color: var(--text-color) !important;
    opacity: 0.55 !important;
}

.stTextInput input:focus {
    border-color: var(--primary-color) !important;
    box-shadow: 0 0 0 1px var(--primary-color) !important;
}

/* ==============================
   BUTTONS
============================== */

.stButton > button {
    background-color: var(--secondary-background-color);
    color: var(--text-color) !important;
    border: 1px solid var(--border-color, rgba(128,128,128,0.3));
    border-radius: 8px;
    min-height: 38px;
}

.stButton > button:hover {
    border-color: var(--primary-color);
    color: var(--primary-color) !important;
}

/* ==============================
   FORM BUTTONS
============================== */

.stFormSubmitButton > button {
    background-color: var(--primary-color);
    color: white !important;
    border: 1px solid var(--primary-color);
    border-radius: 8px;
    min-height: 40px;
}

.stFormSubmitButton > button:hover {
    opacity: 0.85;
    color: white !important;
}

/* ==============================
   FILE UPLOADER
============================== */

[data-testid="stFileUploader"] {
    background-color: var(--secondary-background-color);
    border: 1px dashed var(--border-color, rgba(128,128,128,0.3));
    border-radius: 10px;
    padding: 12px;
}

[data-testid="stFileUploader"] * {
    color: var(--text-color);
}

[data-testid="stFileUploader"] section {
    background-color: transparent !important;
}

[data-testid="stFileUploader"] button {
    background-color: var(--background-color);
    color: var(--text-color) !important;
    border: 1px solid var(--border-color, rgba(128,128,128,0.3));
}

/* ==============================
   CHAT MESSAGES
============================== */

[data-testid="stChatMessage"] {
    background-color: transparent;
    border: none;
    padding: 12px 0;
    color: var(--text-color);
}

/* ==============================
   CHAT INPUT
============================== */

[data-testid="stBottom"] {
    background-color: var(--background-color);
}

[data-testid="stChatInput"] {
    background-color: var(--secondary-background-color);
    border: 1px solid var(--border-color, rgba(128,128,128,0.3));
    border-radius: 12px;
    box-shadow: none;
}

[data-testid="stChatInput"] > div {
    background-color: transparent;
}

[data-testid="stChatInput"] textarea {
    background-color: transparent;
    color: var(--text-color) !important;
    -webkit-text-fill-color: var(--text-color) !important;
    caret-color: var(--text-color);
}

[data-testid="stChatInput"] textarea::placeholder {
    color: var(--text-color) !important;
    -webkit-text-fill-color: var(--text-color) !important;
    opacity: 0.55;
}

[data-testid="stChatInput"] button {
    background-color: var(--primary-color);
    color: white !important;
    border: none;
    border-radius: 8px;
}

/* ==============================
   TABS
============================== */

.stTabs [data-baseweb="tab"] {
    color: var(--text-color);
}

.stTabs [aria-selected="true"] {
    color: var(--primary-color) !important;
}

/* ==============================
   DIVIDERS
============================== */

hr {
    border-color: var(--border-color, rgba(128,128,128,0.2));
}

/* ==============================
   SCROLLBAR
============================== */

* {
    scrollbar-color: var(--text-color) var(--background-color);
}

</style>
""", unsafe_allow_html=True)


# ---------------- SESSION STATE ----------------

defaults = {
    "messages": [],
    "documents_processed": False,
    "document_names": [],
    "total_pages": 0,
    "total_chunks": 0,
    "current_conversation_id": None,
    "uploader_key": 0,
    "access_token": None,
    "refresh_token": None,
    "user": None
}

for key, value in defaults.items():

    if key not in st.session_state:
        st.session_state[key] = value


# ---------------- HELPER FUNCTIONS ----------------

def reset_current_chat():

    st.session_state.messages = []

    st.session_state.documents_processed = False

    st.session_state.document_names = []

    st.session_state.total_pages = 0

    st.session_state.total_chunks = 0

    st.session_state.uploader_key += 1


def get_conversation_upload_folder(conversation_id):

    return os.path.join(
        UPLOAD_FOLDER,
        str(conversation_id)
    )


def get_conversation_vector_folder(conversation_id):

    return os.path.join(
        DB_FOLDER,
        str(conversation_id)
    )


def create_new_conversation():

    conversation = create_conversation(
        st.session_state.access_token,
        st.session_state.refresh_token,
        st.session_state.user.id
    )

    st.session_state.current_conversation_id = conversation["id"]

    reset_current_chat()


def cleanup_conversation_files(conversation_id):

    warnings = []

    # Try to clear the ChromaDB collection.
    # Do not manually delete an open ChromaDB database folder.

    try:

        clear_vector_store(conversation_id)

    except Exception as error:

        warnings.append(
            f"ChromaDB cleanup could not be completed: {error}"
        )

    # Delete uploaded PDFs.

    upload_folder = get_conversation_upload_folder(
        conversation_id
    )

    try:

        if os.path.exists(upload_folder):

            shutil.rmtree(upload_folder)

    except Exception as error:

        warnings.append(
            f"Uploaded PDF cleanup failed: {error}"
        )

    return warnings


# ---------------- AUTHENTICATION ----------------

if not st.session_state.user:

    st.markdown(
        "<h1 style='text-align:center;'>📚 AI Knowledge Assistant</h1>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<p style='text-align:center;'>Login or create an account to continue.</p>",
        unsafe_allow_html=True
    )

    login_tab, signup_tab = st.tabs(["Login", "Sign Up"])

    with login_tab:

        with st.form("login_form"):

            email = st.text_input(
                "Email",
                placeholder="Enter your email address"
            )

            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password"
            )

            login_button = st.form_submit_button(
                "Login",
                use_container_width=True
            )

            if login_button:

                if not email.strip() or not password:

                    st.warning(
                        "Please enter both your email and password."
                    )

                else:

                    try:

                        response = sign_in(
                            email.strip(),
                            password
                        )

                        if response.session is None or response.user is None:

                            st.error(
                                "Login did not return an active session. "
                                "If email confirmation is enabled, verify "
                                "your email before logging in."
                            )

                        else:

                            st.session_state.access_token = (
                                response.session.access_token
                            )

                            st.session_state.refresh_token = (
                                response.session.refresh_token
                            )

                            st.session_state.user = response.user

                            st.success("Login successful!")

                            st.rerun()

                    except Exception as error:

                        st.error(f"Login failed: {str(error)}")

    with signup_tab:

        with st.form("signup_form"):

            display_name = st.text_input(
                "Your name",
                placeholder="Enter your name"
            )

            signup_email = st.text_input(
                "Email address",
                placeholder="Enter your email address"
            )

            signup_password = st.text_input(
                "Password",
                type="password",
                placeholder="Create a password (at least 6 characters)"
            )

            signup_button = st.form_submit_button(
                "Create Account",
                use_container_width=True
            )

            if signup_button:

                try:

                    response = sign_up(
                        signup_email,
                        signup_password,
                        display_name
                    )

                    if response.session:

                        st.session_state.access_token = (
                            response.session.access_token
                        )

                        st.session_state.refresh_token = (
                            response.session.refresh_token
                        )

                        st.session_state.user = response.user

                        st.success("Account created!")

                        st.rerun()

                    else:

                        st.success(
                            "Account created! Please verify your email, "
                            "then log in."
                        )

                except Exception as error:

                    st.error(f"Sign up failed: {str(error)}")

    st.stop()


# ---------------- SIDEBAR ----------------

with st.sidebar:

    user_name = (
        st.session_state.user.user_metadata.get("display_name")
        or st.session_state.user.email
    )

    st.markdown("## 📚 AI Knowledge Assistant")

    st.caption(f"Logged in as: {user_name}")


    # ---------------- LOGOUT ----------------

    if st.button("Logout", use_container_width=True):

        try:

            sign_out(
                st.session_state.access_token,
                st.session_state.refresh_token
            )

        except Exception:
            pass

        st.session_state.access_token = None
        st.session_state.refresh_token = None
        st.session_state.user = None
        st.session_state.current_conversation_id = None

        reset_current_chat()

        st.rerun()


    # ---------------- CHAT HISTORY ----------------

    st.subheader("Chat History")

    try:

        conversations = get_conversations(
            st.session_state.access_token,
            st.session_state.refresh_token
        )

        if conversations:

            for conversation in conversations:

                conversation_id = conversation["id"]

                col1, col2 = st.columns([0.80, 0.20])

                with col1:

                    if st.button(
                        conversation["title"],
                        key=f"chat_{conversation_id}",
                        use_container_width=True
                    ):

                        messages = get_messages(
                            st.session_state.access_token,
                            st.session_state.refresh_token,
                            conversation_id
                        )

                        st.session_state.current_conversation_id = (
                            conversation_id
                        )

                        st.session_state.messages = [
                            {
                                "role": message["role"],
                                "content": message["content"]
                            }
                            for message in messages
                        ]

                        # Restore this conversation's document status.

                        upload_folder = get_conversation_upload_folder(
                            conversation_id
                        )

                        if os.path.isdir(upload_folder):

                            document_names = [
                                filename
                                for filename in os.listdir(upload_folder)
                                if os.path.isfile(
                                    os.path.join(upload_folder, filename)
                                )
                            ]

                        else:

                            document_names = []

                        has_knowledge_base = (
                            vector_store_exists(conversation_id)
                            and bool(document_names)
                        )

                        st.session_state.documents_processed = (
                            has_knowledge_base
                        )

                        st.session_state.document_names = (
                            document_names if has_knowledge_base else []
                        )

                        st.session_state.total_pages = 0

                        st.session_state.total_chunks = 0

                        st.session_state.uploader_key += 1

                        st.rerun()

                with col2:

                    # ---------------- DELETE CONVERSATION ----------------

                    if st.button(
                        "🗑️",
                        key=f"delete_{conversation_id}",
                        help="Delete conversation",
                        use_container_width=True
                    ):

                        try:

                            # First clean local files.
                            # A local cleanup error should not prevent
                            # deletion of the Supabase conversation.

                            cleanup_warnings = cleanup_conversation_files(
                                conversation_id
                            )

                            # Delete conversation and messages from Supabase.

                            delete_conversation(
                                st.session_state.access_token,
                                st.session_state.refresh_token,
                                conversation_id
                            )

                            # Reset active chat if it was deleted.

                            if (
                                st.session_state.current_conversation_id
                                == conversation_id
                            ):

                                st.session_state.current_conversation_id = None

                                reset_current_chat()

                            st.success("Conversation deleted!")

                            for warning in cleanup_warnings:

                                st.warning(warning)

                            st.rerun()

                        except Exception as error:

                            st.error(
                                f"Could not delete conversation: {error}"
                            )

        else:

            st.caption("No previous conversations yet.")

    except Exception as error:

        st.error(f"Could not load chat history: {error}")


    st.divider()

    st.caption("Chat with your PDF documents")

    st.divider()


    # ---------------- NEW CHAT ----------------

    if st.button(
        "➕ New Chat",
        use_container_width=True
    ):

        try:

            create_new_conversation()

            st.rerun()

        except Exception as error:

            st.error(f"Could not create a new chat: {error}")


    st.divider()


    # ---------------- UPLOAD DOCUMENTS ----------------

    st.markdown("### Upload documents")

    uploaded_files = st.file_uploader(
        "Choose PDF files",
        type=["pdf"],
        accept_multiple_files=True,
        key=f"pdf_uploader_{st.session_state.uploader_key}"
    )


    # ---------------- PROCESS DOCUMENTS ----------------

    if st.button(
        "Process Documents",
        use_container_width=True
    ):

        if not uploaded_files:

            st.warning("Please upload at least one PDF.")

        else:

            try:

                # Create a conversation if one is not active.

                if not st.session_state.current_conversation_id:

                    create_new_conversation()

                conversation_id = (
                    st.session_state.current_conversation_id
                )

                conversation_folder = (
                    get_conversation_upload_folder(conversation_id)
                )

                # Replace only this conversation's previous PDFs.

                if os.path.exists(conversation_folder):

                    shutil.rmtree(conversation_folder)

                os.makedirs(
                    conversation_folder,
                    exist_ok=True
                )

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
                        conversation_folder,
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

                    documents = load_multiple_pdfs(file_paths)

                    chunks = split_documents(documents)

                    if not chunks:

                        raise ValueError(
                            "No readable text found in the PDFs."
                        )

                    # Create the vector store.

                    vector_store = create_vector_store(
                        chunks,
                        conversation_id
                    )

                    try:

                        st.session_state.documents_processed = True

                        st.session_state.document_names = document_names

                        st.session_state.total_pages = len(documents)

                        st.session_state.total_chunks = len(chunks)

                        st.session_state.messages = []

                    finally:

                        close_vector_store(vector_store)

                        del vector_store

                st.success(
                    "Documents processed successfully!"
                )

                st.rerun()

            except Exception as error:

                st.session_state.documents_processed = False

                st.error(
                    safe_api_error_message(
                        error,
                        "Document processing"
                    )
                )


    st.divider()


    # ---------------- UPLOADED DOCUMENT LIST ----------------

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


    # ---------------- KNOWLEDGE BASE STATUS ----------------

    if st.session_state.documents_processed:

        st.success("Knowledge base ready")

    else:

        st.info("Upload PDFs to get started")


    st.divider()



# ---------------- CLEAR KNOWLEDGE BASE ----------------

with st.sidebar:

    if st.button(
        "🗑️ Clear Knowledge Base",
        use_container_width=True
    ):

        conversation_id = (
            st.session_state.current_conversation_id
        )

        if not conversation_id:

            st.warning("No active conversation found.")

        else:

            try:

                # Clear ChromaDB and uploaded PDFs.

                cleanup_warnings = cleanup_conversation_files(
                    conversation_id
                )

                # Reset document and chat state.

                reset_current_chat()

                if cleanup_warnings:

                    st.warning(
                        "Chat was reset, but some local files "
                        "could not be cleaned up."
                    )

                    for warning in cleanup_warnings:
                        st.warning(warning)

                else:

                    st.success(
                        "Knowledge base cleared successfully."
                    )

                st.rerun()

            except Exception as error:

                st.error(
                    f"Could not clear knowledge base: {error}"
                )


# ---------------- MAIN CHAT AREA ----------------


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

        try:

            # Create a conversation if one is not active.

            if not st.session_state.current_conversation_id:

                create_new_conversation()

            conversation_id = (
                st.session_state.current_conversation_id
            )

            # Show user question.

            with st.chat_message("user"):

                st.markdown(question)

            # Generate answer.

            with st.chat_message("assistant"):

                with st.spinner("Thinking..."):

                    answer, sources = get_answer(
                        question,
                        conversation_id,
                        st.session_state.messages
                    )

                st.markdown(answer)

                if sources:

                    st.markdown("**Sources**")

                    for source in sources:

                        st.caption(
                            f"📄 {source['file']} "
                            f"· Page {source['page']}"
                        )

            # Prepare answer with sources.

            answer_text = answer

            if sources:

                answer_text += "\n\n**Sources:**\n"

                for source in sources:

                    answer_text += (
                        f"- {source['file']} "
                        f"(Page {source['page']})\n"
                    )

            # Set conversation title using first question.

            if not st.session_state.messages:

                chat_title = question.strip()[:50]

                rename_conversation(
                    st.session_state.access_token,
                    st.session_state.refresh_token,
                    conversation_id,
                    chat_title
                )

            # Save user message.

            save_message(
                st.session_state.access_token,
                st.session_state.refresh_token,
                conversation_id,
                "user",
                question
            )

            # Save assistant message.

            save_message(
                st.session_state.access_token,
                st.session_state.refresh_token,
                conversation_id,
                "assistant",
                answer_text
            )

            # Update local chat history.

            st.session_state.messages.append({
                "role": "user",
                "content": question
            })

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer_text
            })

            st.rerun()

        except Exception as error:

            st.error(
                safe_api_error_message(
                    error,
                    "Answer generation or chat saving"
                )
            )
