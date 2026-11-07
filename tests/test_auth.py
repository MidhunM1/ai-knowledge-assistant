from unittest.mock import MagicMock

import src.auth as auth_module


def test_sign_up(monkeypatch):
    mock_client = MagicMock()
    mock_response = MagicMock()

    mock_client.auth.sign_up.return_value = mock_response

    monkeypatch.setattr(
        auth_module,
        "get_supabase_client",
        lambda: mock_client
    )

    result = auth_module.sign_up(
        "test@example.com",
        "password123",
        "Test User"
    )

    assert result is mock_response

    mock_client.auth.sign_up.assert_called_once_with({
        "email": "test@example.com",
        "password": "password123",
        "options": {
            "data": {
                "display_name": "Test User"
            }
        }
    })


def test_sign_in(monkeypatch):
    mock_client = MagicMock()
    mock_response = MagicMock()

    mock_client.auth.sign_in_with_password.return_value = mock_response

    monkeypatch.setattr(
        auth_module,
        "get_supabase_client",
        lambda: mock_client
    )

    result = auth_module.sign_in(
        "test@example.com",
        "password123"
    )

    assert result is mock_response

    mock_client.auth.sign_in_with_password.assert_called_once_with({
        "email": "test@example.com",
        "password": "password123"
    })


def test_sign_out(monkeypatch):
    mock_client = MagicMock()

    monkeypatch.setattr(
        auth_module,
        "get_supabase_client",
        lambda access_token, refresh_token: mock_client
    )

    auth_module.sign_out(
        "access-token",
        "refresh-token"
    )

    mock_client.auth.sign_out.assert_called_once()