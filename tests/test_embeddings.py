from unittest.mock import MagicMock

import src.embeddings as embeddings_module


def test_get_embeddings(monkeypatch):
    mock_embeddings = MagicMock()

    def fake_embeddings(**kwargs):
        assert kwargs["model"] == embeddings_module.GEMINI_EMBEDDING_MODEL
        assert kwargs["api_key"] == embeddings_module.GOOGLE_API_KEY
        return mock_embeddings

    monkeypatch.setattr(
        embeddings_module,
        "GoogleGenerativeAIEmbeddings",
        fake_embeddings
    )

    result = embeddings_module.get_embeddings()

    assert result is mock_embeddings