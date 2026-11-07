from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

import src.chat_history as history_module


def create_mock_client(data=None, execute_results=None):
    mock_client = MagicMock()
    mock_query = MagicMock()

    mock_client.table.return_value = mock_query

    mock_query.insert.return_value = mock_query
    mock_query.select.return_value = mock_query
    mock_query.single.return_value = mock_query
    mock_query.order.return_value = mock_query
    mock_query.eq.return_value = mock_query
    mock_query.update.return_value = mock_query
    mock_query.delete.return_value = mock_query

    if execute_results is not None:
        mock_query.execute.side_effect = [
            SimpleNamespace(data=result)
            for result in execute_results
        ]
    else:
        mock_query.execute.return_value = SimpleNamespace(data=data)

    return mock_client, mock_query


def patch_client(monkeypatch, mock_client):
    monkeypatch.setattr(
        history_module,
        "get_supabase_client",
        lambda access_token, refresh_token: mock_client
    )


def test_missing_session():
    with pytest.raises(ValueError, match="session has expired"):
        history_module._client(None, None)


def test_create_conversation(monkeypatch):
    mock_client, mock_query = create_mock_client(
        data={"id": "chat123", "title": "My Chat"}
    )

    patch_client(monkeypatch, mock_client)

    result = history_module.create_conversation(
        "access",
        "refresh",
        "user123",
        "My Chat"
    )

    assert result["id"] == "chat123"

    mock_client.table.assert_called_with("conversations")
    mock_query.insert.assert_called_once_with({
        "user_id": "user123",
        "title": "My Chat"
    })


def test_get_conversations(monkeypatch):
    conversations = [{"id": "chat123"}]

    mock_client, mock_query = create_mock_client(
        data=conversations
    )

    patch_client(monkeypatch, mock_client)

    result = history_module.get_conversations(
        "access",
        "refresh"
    )

    assert result == conversations
    mock_client.table.assert_called_with("conversations")


def test_get_conversations_empty(monkeypatch):
    mock_client, mock_query = create_mock_client(data=None)

    patch_client(monkeypatch, mock_client)

    result = history_module.get_conversations(
        "access",
        "refresh"
    )

    assert result == []


def test_get_messages(monkeypatch):
    messages = [{"role": "user", "content": "Hello"}]

    mock_client, mock_query = create_mock_client(data=messages)

    patch_client(monkeypatch, mock_client)

    result = history_module.get_messages(
        "access",
        "refresh",
        "chat123"
    )

    assert result == messages
    mock_client.table.assert_called_with("messages")


def test_save_message(monkeypatch):
    saved_message = {
        "role": "user",
        "content": "Hello"
    }

    mock_client, mock_query = create_mock_client(
        execute_results=[saved_message, None]
    )

    patch_client(monkeypatch, mock_client)

    result = history_module.save_message(
        "access",
        "refresh",
        "chat123",
        "user",
        "Hello",
        "test-model"
    )

    assert result == saved_message
    mock_client.table.assert_any_call("messages")
    mock_client.table.assert_any_call("conversations")


def test_save_message_invalid_role():
    with pytest.raises(ValueError, match="Message role"):
        history_module.save_message(
            "access",
            "refresh",
            "chat123",
            "invalid",
            "Hello"
        )


def test_save_message_empty_content():
    with pytest.raises(ValueError, match="cannot be empty"):
        history_module.save_message(
            "access",
            "refresh",
            "chat123",
            "user",
            "   "
        )


def test_rename_conversation(monkeypatch):
    updated = {"id": "chat123", "title": "New Title"}

    mock_client, mock_query = create_mock_client(data=updated)

    patch_client(monkeypatch, mock_client)

    result = history_module.rename_conversation(
        "access",
        "refresh",
        "chat123",
        "New Title"
    )

    assert result == updated
    mock_client.table.assert_called_with("conversations")


def test_rename_conversation_empty_title():
    with pytest.raises(ValueError, match="title cannot be empty"):
        history_module.rename_conversation(
            "access",
            "refresh",
            "chat123",
            "   "
        )


def test_delete_conversation(monkeypatch):
    mock_client, mock_query = create_mock_client(data=None)

    patch_client(monkeypatch, mock_client)

    result = history_module.delete_conversation(
        "access",
        "refresh",
        "chat123"
    )

    assert result is None
    mock_client.table.assert_called_with("conversations")
    mock_query.delete.assert_called_once()