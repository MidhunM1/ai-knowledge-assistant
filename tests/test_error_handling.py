import pytest

from src.error_handling import (
    get_gemini_http_status,
    invoke_with_503_retries,
    is_temporary_gemini_failure,
    safe_api_error_message,
)


def provider_error(status, message):
    error = RuntimeError(message)
    error.code = status
    return error


def test_429_daily_quota_is_reported_and_not_retried():
    error = provider_error(
        429,
        "RESOURCE_EXHAUSTED: daily generate_content quota; retry after 86400s",
    )
    calls = []
    sleeps = []

    def invoke():
        calls.append("called")
        raise error

    with pytest.raises(RuntimeError):
        invoke_with_503_retries(invoke, max_attempts=3, sleep=sleeps.append)

    message = safe_api_error_message(error, "Answer generation")
    assert get_gemini_http_status(error) == 429
    assert "daily generate_content quota" in message
    assert "No retry was made" in message
    assert "86400" not in message
    assert len(calls) == 1
    assert sleeps == []


def test_503_is_retried_with_backoff_and_reported_as_temporary():
    error = provider_error(503, "UNAVAILABLE: service temporarily unavailable")
    calls = []
    sleeps = []

    def invoke():
        calls.append("called")
        if len(calls) < 3:
            raise error
        return "answer"

    result = invoke_with_503_retries(invoke, max_attempts=3, sleep=sleeps.append)

    assert result == "answer"
    assert len(calls) == 3
    assert sleeps == [1, 2]
    assert get_gemini_http_status(error) == 503
    assert is_temporary_gemini_failure(error)
    assert "temporarily busy or unavailable" in safe_api_error_message(
        error, "Answer generation"
    )


def test_does_not_echo_provider_error_details():
    error = RuntimeError("invalid API configuration; sensitive-value")

    message = safe_api_error_message(error, "Answer generation")

    assert "sensitive-value" not in message
    assert "API configuration" in message


def test_recognizes_status_on_wrapped_cause():
    cause = provider_error(503, "temporary failure")
    error = RuntimeError("provider request failed")
    error.__cause__ = cause

    assert get_gemini_http_status(error) == 503
