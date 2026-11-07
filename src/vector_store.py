
import os
import gc

from langchain_chroma import Chroma
from src.embeddings import get_embeddings


DB_PATH = "chroma_db"
COLLECTION_NAME = "knowledge_assistant"


def get_conversation_path(conversation_id):

    if not conversation_id:
        raise ValueError("No active conversation found.")

    return os.path.join(
        DB_PATH,
        str(conversation_id)
    )


def close_vector_store(vector_store):

    if vector_store is None:
        return

    client = getattr(
        vector_store,
        "_client",
        None
    )

    if client is not None:

        close_method = getattr(
            client,
            "close",
            None
        )

        if callable(close_method):

            try:
                close_method()

            except Exception:
                pass

    gc.collect()


def create_vector_store(chunks, conversation_id):

    if not chunks:
        raise ValueError("No document chunks were provided.")

    conversation_path = get_conversation_path(
        conversation_id
    )

    os.makedirs(
        conversation_path,
        exist_ok=True
    )

    # Clear the previous collection before adding new documents.
    if os.path.isdir(conversation_path):

        clear_vector_store(conversation_id)

    embeddings = get_embeddings()

    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=conversation_path
    )

    try:

        vector_store.add_documents(chunks)

        return vector_store

    except Exception:

        close_vector_store(vector_store)

        raise


def load_vector_store(conversation_id):

    conversation_path = get_conversation_path(
        conversation_id
    )

    if not os.path.isdir(conversation_path):

        raise ValueError(
            "No knowledge base found for this conversation. "
            "Please upload and process your PDFs."
        )

    embeddings = get_embeddings()

    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=conversation_path
    )

    return vector_store


def clear_vector_store(conversation_id):

    conversation_path = get_conversation_path(
        conversation_id
    )

    if not os.path.isdir(conversation_path):
        return

    vector_store = None

    try:

        vector_store = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=None,
            persist_directory=conversation_path
        )

        # Delete the collection and its documents.
        vector_store.delete_collection()

    finally:

        close_vector_store(vector_store)


def vector_store_exists(conversation_id):

    if not conversation_id:
        return False

    conversation_path = get_conversation_path(
        conversation_id
    )

    if not os.path.isdir(conversation_path):
        return False

    vector_store = None

    try:

        vector_store = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=None,
            persist_directory=conversation_path
        )

        stored_data = vector_store.get(limit=1)

        return bool(stored_data.get("ids"))

    except Exception:

        return False

    finally:

        close_vector_store(vector_store)
