class LinkedInErrorType:
    AUTH = "auth_error"
    RATE_LIMIT = "rate_limit"
    VALIDATION = "validation_error"
    UNKNOWN = "unknown"


def classify_linkedin_error(status_code: int, payload: str) -> str:
    if status_code == 401:
        return LinkedInErrorType.AUTH
    if status_code == 429:
        return LinkedInErrorType.RATE_LIMIT
    if status_code == 400:
        return LinkedInErrorType.VALIDATION
    return LinkedInErrorType.UNKNOWN

class LinkedInAuthError(Exception):
    """
    Raised when LinkedIn authentication is invalid or expired.
    Requires user re-authorization.
    """
    pass
