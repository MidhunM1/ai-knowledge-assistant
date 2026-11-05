from langchain_core.documents import Document

from src import vector_store


class FakeEmbeddings:

    def embed_documents(self, texts):

        return [
            [float(len(text)), float(text.count(" ") + 1), 0.1]
            for text in texts
        ]

    def embed_query(self, text):

        return [
            float(len(text)),
            float(text.count(" ") + 1),
            0.1
        ]


def test_create_and_clear_vector_store(tmp_path, monkeypatch):

    monkeypatch.setattr(
        vector_store,
        "get_embeddings",
        lambda: FakeEmbeddings()
    )

    monkeypatch.setattr(
        vector_store,
        "DB_PATH",
        str(tmp_path / "chroma_db")
    )

    monkeypatch.setattr(
        vector_store,
        "COLLECTION_NAME",
        "test_knowledge_assistant"
    )

    documents = [
        Document(
            page_content="Artificial Intelligence is a technology.",
            metadata={
                "source": "sample.pdf",
                "page": 1
            }
        )
    ]

    # Store documents

    database = vector_store.create_vector_store(documents)

    assert database._collection.count() == 1

    # Retrieve documents

    results = database.similarity_search(
        "Artificial Intelligence",
        k=1
    )

    assert len(results) == 1
    assert results[0].metadata["source"] == "sample.pdf"

    # Clear the database

    vector_store.clear_vector_store()

    empty_database = vector_store.load_vector_store()

    assert empty_database._collection.count() == 0
    