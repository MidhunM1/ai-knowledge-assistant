import re


TRANSIENT_HTTP_STATUSES = {408, 429, 500, 502, 503, 504}


def is_temporary_gemini_failure(error):
    """Recognize transient Google API errors without exposing their details."""
    current = error
    visited = set()

    while current is not None and id(current) not in visited:
        visited.add(id(current))

        for attribute in ("status_code", "status", "code"):
            status = getattr(current, attribute, None)
            try:
                if int(status) in TRANSIENT_HTTP_STATUSES:
                    return True
            except (TypeError, ValueError):
                pass

        if re.search(r"\b(?:408|429|500|502|503|504)\b", str(current)):
            return True

        current = current.__cause__ or current.__context__

    return False


def safe_api_error_message(error, operation):
    """Return a user-safe message; never echo provider exception contents."""
    if is_temporary_gemini_failure(error):
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
