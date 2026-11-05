import pytest
from langchain_core.documents import Document
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda

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


def test_successful_answer_uses_supported_model_and_explicit_retries(monkeypatch):
    class FakeVectorStore:
        def similarity_search_with_relevance_scores(self, question, k):
            return [
                (
                    Document(
                        page_content="AI systems perform tasks that usually need human intelligence.",
                        metadata={"source": "guide.pdf", "page": 2},
                    ),
                    0.9,
                )
            ]

    model_options = {}

    def fake_chat_model(**options):
        model_options.update(options)
        return RunnableLambda(lambda _prompt: AIMessage(content="AI enables intelligent tasks."))

    monkeypatch.setattr(rag_pipeline, "load_vector_store", lambda: FakeVectorStore())
    monkeypatch.setattr(rag_pipeline, "ChatGoogleGenerativeAI", fake_chat_model)

    answer, sources = rag_pipeline.get_answer("What is AI?")

    assert answer == "AI enables intelligent tasks."
    assert sources == [{"file": "guide.pdf", "page": 2}]
    assert model_options["model"] == rag_pipeline.GEMINI_CHAT_MODEL
    assert model_options["max_retries"] == 1
    assert model_options["request_timeout"] == rag_pipeline.GEMINI_REQUEST_TIMEOUT_SECONDS
    assert model_options["max_tokens"] == 512
    assert model_options["temperature"] is None
