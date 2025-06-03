"""Kanka API exceptions."""


class KankaException(Exception):
    """Base exception for all Kanka errors."""
    pass


class KankaError(KankaException):
    """Legacy exception name for backward compatibility."""
    pass


class KankaAPIError(KankaException):
    """Legacy exception name for backward compatibility."""
    pass


class NotFoundError(KankaException):
    """Entity not found (404)."""
    pass


class ValidationError(KankaException):
    """Invalid data (422)."""
    pass


class RateLimitError(KankaException):
    """Rate limit exceeded (429)."""
    pass


class AuthenticationError(KankaException):
    """Invalid token (401)."""
    pass


class ForbiddenError(KankaException):
    """Access forbidden (403)."""
    pass
