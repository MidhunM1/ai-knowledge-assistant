import re
import time


TRANSIENT_HTTP_STATUSES = {408, 500, 502, 503, 504}
STATUS_PATTERN = re.compile(r"\b(?:HTTP\s*)?(408|429|500|502|503|504)\b", re.IGNORECASE)


def get_gemini_http_status(error):
    """Find an HTTP status on an error or its wrapped provider exception."""
    current = error
    visited = set()

    while current is not None and id(current) not in visited:
        visited.add(id(current))

        for attribute in ("status_code", "status", "code"):
            status = getattr(current, attribute, None)
            try:
                status = int(status)
            except (TypeError, ValueError):
                continue
            if status in TRANSIENT_HTTP_STATUSES | {429}:
                return status

        message = str(current)
        match = STATUS_PATTERN.search(message)
        if match:
            return int(match.group(1))
        if "RESOURCE_EXHAUSTED" in message.upper():
            return 429

        current = current.__cause__ or current.__context__

    return None


def is_temporary_gemini_failure(error):
    """Recognize temporary server and transport failures, excluding HTTP 429."""
    return get_gemini_http_status(error) in TRANSIENT_HTTP_STATUSES


def invoke_with_503_retries(invoke, max_attempts=3, sleep=time.sleep):
    """Retry only 503 responses with short exponential backoff.

    The Google SDK retry layer is disabled for chat calls so quota errors (429)
    are surfaced immediately instead of being retried against a long reset time.
    """
    for attempt in range(max_attempts):
        try:
            return invoke()
        except Exception as error:
            if get_gemini_http_status(error) != 503 or attempt + 1 >= max_attempts:
                raise
            sleep(min(2 ** attempt, 8))


def safe_api_error_message(error, operation):
    """Return a user-safe message; never echo provider exception contents."""
    status = get_gemini_http_status(error)
    if status == 429:
        return (
            "Gemini's daily generate_content quota for gemini-3.8-flash has been "
            "exceeded (HTTP 429). No retry was made. Wait for the daily quota "
            "reset or check your Google AI Studio quota."
        )

    if status in TRANSIENT_HTTP_STATUSES:
        return (
            "Gemini is temporarily busy or unavailable. The request was retried; "
            "please try again shortly."
        )

    if operation == "Document processing":
        return (
            "Document processing failed. Check that the PDFs are readable and "
            "Gemini API access is configured, then try again."
        )

    return (
        f"{operation} failed. Check the Gemini API configuration and access, "
        "then try again."
    )
