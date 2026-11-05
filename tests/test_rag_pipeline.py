import pytest

from src import rag_pipeline


def test_empty_question():

    with pytest.raises(ValueError):

        rag_pipeline.get_answer("")


def test_no_relevant_documents(monkeypatch):

    class FakeVectorStore:

        def similarity_search_with_relevance_scores(
            self,
            question,
            k
        ):
            return []

    monkeypatch.setattr(
        rag_pipeline,
        "load_vector_store",
        lambda: FakeVectorStore()
    )

    answer, sources = rag_pipeline.get_answer(
        "What is artificial intelligence?"
    )

    assert "couldn't find relevant information" in answer
    assert sources == []