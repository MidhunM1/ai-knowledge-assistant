from src.error_handling import is_temporary_gemini_failure, safe_api_error_message


def test_recognizes_transient_gemini_503():
    error = RuntimeError("Error embedding content (503): service unavailable")

    assert is_temporary_gemini_failure(error)
    message = safe_api_error_message(error, "Answer generation")
    assert "temporarily busy or unavailable" in message
    assert "503" not in message


def test_does_not_echo_provider_error_details():
    error = RuntimeError("invalid API configuration; sensitive-value")

    message = safe_api_error_message(error, "Answer generation")

    assert "sensitive-value" not in message
    assert "API configuration" in message


def test_recognizes_status_on_wrapped_cause():
    cause = RuntimeError("temporary failure")
    cause.status_code = 503
    error = RuntimeError("provider request failed")
    error.__cause__ = cause

    assert is_temporary_gemini_failure(error)
