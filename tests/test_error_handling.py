import pytest

from src.error_handling import (
    get_gemini_http_status,
    is_temporary_gemini_failure,
    invoke_with_503_retries,
    safe_api_error_message
)


def test_get_status_from_error_attribute():
    error = Exception("Server error")
    error.status_code = 503

    assert get_gemini_http_status(error) == 503


def test_get_status_from_error_message():
    error = Exception("HTTP 429 RESOURCE_EXHAUSTED")

    assert get_gemini_http_status(error) == 429


def test_get_status_from_resource_exhausted():
    error = Exception("RESOURCE_EXHAUSTED")

    assert get_gemini_http_status(error) == 429


def test_temporary_failure():
    error = Exception("HTTP 503")

    assert is_temporary_gemini_failure(error) is True


def test_quota_error_is_not_temporary():
    error = Exception("HTTP 429")

    assert is_temporary_gemini_failure(error) is False


def test_retry_success():
    calls = []
    sleeps = []

    def operation():
        calls.append(1)

        if len(calls) < 3:
            raise Exception("HTTP 503")

        return "Success"

    result = invoke_with_503_retries(
        operation,
        max_attempts=3,
        sleep=lambda seconds: sleeps.append(seconds)
    )

    assert result == "Success"
    assert len(calls) == 3
    assert sleeps == [1, 2]


def test_retry_does_not_retry_429():
    calls = []

    def operation():
        calls.append(1)
        raise Exception("HTTP 429")

    with pytest.raises(Exception):
        invoke_with_503_retries(
            operation,
            max_attempts=3,
            sleep=lambda seconds: None
        )

    assert len(calls) == 1


def test_safe_message_for_quota_error():
    message = safe_api_error_message(
        Exception("HTTP 429"),
        "Embedding"
    )

    assert "429" in message
    assert "quota" in message.lower()


def test_safe_message_for_document_processing():
    message = safe_api_error_message(
        Exception("Unknown error"),
        "Document processing"
    )

    assert "Document processing failed" in message