from unittest.mock import MagicMock

import pytest

import src.vector_store as vector_module


def test_get_conversation_path():
    path = vector_module.get_conversation_path("chat123")

    assert path.endswith("chat123")


def test_get_conversation_path_without_id():
    with pytest.raises(ValueError):
        vector_module.get_conversation_path(None)


def test_create_vector_store(tmp_path, monkeypatch):
    monkeypatch.setattr(vector_module, "DB_PATH", str(tmp_path))
    monkeypatch.setattr(vector_module, "get_embeddings", MagicMock())

    mock_store = MagicMock()

    monkeypatch.setattr(
        vector_module,
        "clear_vector_store",
        lambda conversation_id: None
    )

    monkeypatch.setattr(
        vector_module,
        "Chroma",
        lambda **kwargs: mock_store
    )

    chunks = [MagicMock()]

    result = vector_module.create_vector_store(chunks, "chat123")

    assert result is mock_store
    mock_store.add_documents.assert_called_once_with(chunks)


def test_create_vector_store_without_chunks():
    with pytest.raises(ValueError, match="No document chunks"):
        vector_module.create_vector_store([], "chat123")


def test_load_vector_store_missing_directory(tmp_path, monkeypatch):
    monkeypatch.setattr(vector_module, "DB_PATH", str(tmp_path))

    with pytest.raises(ValueError, match="No knowledge base found"):
        vector_module.load_vector_store("missing-chat")


def test_load_vector_store(tmp_path, monkeypatch):
    monkeypatch.setattr(vector_module, "DB_PATH", str(tmp_path))
    monkeypatch.setattr(vector_module, "get_embeddings", MagicMock())

    conversation_path = tmp_path / "chat123"
    conversation_path.mkdir()

    mock_store = MagicMock()

    monkeypatch.setattr(
        vector_module,
        "Chroma",
        lambda **kwargs: mock_store
    )

    result = vector_module.load_vector_store("chat123")

    assert result is mock_store


def test_clear_vector_store(tmp_path, monkeypatch):
    monkeypatch.setattr(vector_module, "DB_PATH", str(tmp_path))

    conversation_path = tmp_path / "chat123"
    conversation_path.mkdir()

    mock_store = MagicMock()

    monkeypatch.setattr(
        vector_module,
        "Chroma",
        lambda **kwargs: mock_store
    )

    vector_module.clear_vector_store("chat123")

    mock_store.delete_collection.assert_called_once()


def test_vector_store_exists(tmp_path, monkeypatch):
    monkeypatch.setattr(vector_module, "DB_PATH", str(tmp_path))

    conversation_path = tmp_path / "chat123"
    conversation_path.mkdir()

    mock_store = MagicMock()
    mock_store.get.return_value = {"ids": ["document1"]}

    monkeypatch.setattr(
        vector_module,
        "Chroma",
        lambda **kwargs: mock_store
    )

    assert vector_module.vector_store_exists("chat123") is True


def test_vector_store_does_not_exist(tmp_path, monkeypatch):
    monkeypatch.setattr(vector_module, "DB_PATH", str(tmp_path))

    assert vector_module.vector_store_exists("missing-chat") is False


def test_close_vector_store_without_store():
    vector_module.close_vector_store(None)