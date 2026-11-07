from unittest.mock import MagicMock

import pytest

import src.rag_pipeline as rag_module


class FakePrompt:
    def __or__(self, model):
        return FakeChain()


class FakeChain:
    def invoke(self, inputs):
        assert "question" in inputs
        assert "context" in inputs
        return MagicMock(content="This is a generated answer.")


def test_get_answer_empty_question():
    with pytest.raises(ValueError, match="valid question"):
        rag_module.get_answer("", "chat123")


def test_get_answer_missing_conversation():
    with pytest.raises(ValueError, match="No active conversation"):
        rag_module.get_answer("What is AI?", None)


def test_get_answer_no_relevant_documents(monkeypatch):
    mock_store = MagicMock()
    mock_store.similarity_search_with_relevance_scores.return_value = [
        (MagicMock(), 0.10)
    ]

    monkeypatch.setattr(
        rag_module,
        "load_vector_store",
        lambda conversation_id: mock_store
    )

    monkeypatch.setattr(
        rag_module,
        "close_vector_store",
        lambda store: None
    )

    answer, sources = rag_module.get_answer(
        "What is AI?",
        "chat123"
    )

    assert "couldn't find relevant information" in answer
    assert sources == []


def test_get_answer_generates_answer(monkeypatch):
    document = MagicMock()
    document.page_content = "Artificial Intelligence is a field of computer science."
    document.metadata = {"source": "AI.pdf", "page": 2}

    mock_store = MagicMock()
    mock_store.similarity_search_with_relevance_scores.return_value = [
        (document, 0.85)
    ]

    monkeypatch.setattr(
        rag_module,
        "load_vector_store",
        lambda conversation_id: mock_store
    )

    monkeypatch.setattr(
        rag_module,
        "close_vector_store",
        lambda store: None
    )

    monkeypatch.setattr(
        rag_module.ChatPromptTemplate,
        "from_template",
        lambda template: FakePrompt()
    )

    monkeypatch.setattr(
        rag_module,
        "ChatGroq",
        lambda **kwargs: MagicMock()
    )

    answer, sources = rag_module.get_answer(
        "What is AI?",
        "chat123"
    )

    assert answer == "This is a generated answer."
    assert sources == [{"file": "AI.pdf", "page": 2}]


def test_get_answer_closes_vector_store(monkeypatch):
    document = MagicMock()
    document.page_content = "Sample content"
    document.metadata = {"source": "sample.pdf", "page": 1}

    mock_store = MagicMock()
    mock_store.similarity_search_with_relevance_scores.return_value = [
        (document, 0.90)
    ]

    close_mock = MagicMock()

    monkeypatch.setattr(
        rag_module,
        "load_vector_store",
        lambda conversation_id: mock_store
    )

    monkeypatch.setattr(
        rag_module,
        "close_vector_store",
        close_mock
    )

    monkeypatch.setattr(
        rag_module.ChatPromptTemplate,
        "from_template",
        lambda template: FakePrompt()
    )

    monkeypatch.setattr(
        rag_module,
        "ChatGroq",
        lambda **kwargs: MagicMock()
    )

    rag_module.get_answer("Explain this", "chat123")

    close_mock.assert_called_once_with(mock_store)