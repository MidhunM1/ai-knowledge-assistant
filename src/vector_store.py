
from langchain_chroma import Chroma
from src.embeddings import get_embeddings

DB_PATH = "chroma_db"
COLLECTION_NAME = "knowledge_assistant"


def create_vector_store(chunks):

    embeddings = get_embeddings()

    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=DB_PATH
    )

    vector_store.reset_collection()

    vector_store.add_documents(chunks)

    return vector_store


def load_vector_store():

    embeddings = get_embeddings()

    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=DB_PATH
    )

    return vector_store


def clear_vector_store():

    embeddings = get_embeddings()

    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=DB_PATH
    )

    vector_store.reset_collection()
