import pytest
from unittest.mock import MagicMock

import src.supabase_client as supabase_module


def test_supabase_client_creation(monkeypatch):
    monkeypatch.setattr(
        supabase_module,
        "SUPABASE_URL",
        "https://example.supabase.co"
    )

    monkeypatch.setattr(
        supabase_module,
        "SUPABASE_KEY",
        "test-key"
    )

    mock_client = MagicMock()

    monkeypatch.setattr(
        supabase_module,
        "create_client",
        lambda url, key: mock_client
    )

    client = supabase_module.get_supabase_client()

    assert client is mock_client


def test_supabase_client_with_session(monkeypatch):
    monkeypatch.setattr(
        supabase_module,
        "SUPABASE_URL",
        "https://example.supabase.co"
    )

    monkeypatch.setattr(
        supabase_module,
        "SUPABASE_KEY",
        "test-key"
    )

    mock_client = MagicMock()

    monkeypatch.setattr(
        supabase_module,
        "create_client",
        lambda url, key: mock_client
    )

    client = supabase_module.get_supabase_client(
        "test-access-token",
        "test-refresh-token"
    )

    assert client is mock_client

    mock_client.auth.set_session.assert_called_once_with(
        "test-access-token",
        "test-refresh-token"
    )


def test_supabase_client_missing_credentials(monkeypatch):
    monkeypatch.setattr(
        supabase_module,
        "SUPABASE_URL",
        None
    )

    monkeypatch.setattr(
        supabase_module,
        "SUPABASE_KEY",
        None
    )

    with pytest.raises(ValueError):
        supabase_module.get_supabase_client()