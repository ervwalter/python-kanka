"""Kanka API exception classes.

This module defines all custom exceptions that can be raised by the
Kanka API client. These exceptions provide specific error handling for
different API error scenarios.

Exception Hierarchy:
    KankaException: Base exception for all Kanka errors
    ├── NotFoundError: Resource not found (404)
    ├── ValidationError: Invalid request data (422)
    ├── RateLimitError: Rate limit exceeded (429)
    ├── AuthenticationError: Invalid authentication (401)
    └── ForbiddenError: Access forbidden (403)

Example:
    >>> try:
    ...     character = client.characters.get(999999)
    ... except NotFoundError:
    ...     print("Character not found")
    ... except KankaException as e:
    ...     print(f"API error: {e}")
"""


class KankaException(Exception):
    """Base exception for all Kanka API errors.

    This is the base class for all exceptions raised by the Kanka API client.
    Catching this exception will catch any Kanka-specific error.

    Example:
        >>> try:
        ...     result = client.search("dragon")
        ... except KankaException as e:
        ...     print(f"Kanka API error: {e}")
    """

    pass


class NotFoundError(KankaException):
    """Raised when a requested resource is not found (HTTP 404).

    This exception is raised when attempting to access an entity
    that doesn't exist or has been deleted.

    Example:
        >>> try:
        ...     character = client.characters.get(99999)
        ... except NotFoundError:
        ...     print("Character does not exist")
    """

    pass


class ValidationError(KankaException):
    """Raised when request data fails validation (HTTP 422).

    This exception is raised when the API rejects the provided data
    due to validation errors, such as missing required fields or
    invalid field values.

    The error message typically contains details about which fields
    failed validation and why.

    Example:
        >>> try:
        ...     character = client.characters.create(name="")  # Empty name
        ... except ValidationError as e:
        ...     print(f"Validation failed: {e}")
    """

    pass


class RateLimitError(KankaException):
    """Raised when API rate limit is exceeded (HTTP 429).

    Kanka API has rate limits to prevent abuse. This exception
    is raised when you've made too many requests in a short period.

    The API allows:
    - 30 requests per minute for regular users
    - 90 requests per minute for subscribers

    Example:
        >>> try:
        ...     for i in range(100):
        ...         client.characters.list()
        ... except RateLimitError:
        ...     print("Slow down! Rate limit hit.")
        ...     time.sleep(60)  # Wait a minute
    """

    pass


class AuthenticationError(KankaException):
    """Raised when authentication fails (HTTP 401).

    This exception indicates that the provided API token is
    invalid, expired, or missing required permissions.

    Example:
        >>> try:
        ...     client = KankaClient("invalid-token", campaign_id=123)
        ...     client.characters.list()
        ... except AuthenticationError:
        ...     print("Invalid API token")
    """

    pass


class ForbiddenError(KankaException):
    """Raised when access to a resource is forbidden (HTTP 403).

    This exception occurs when you try to access a resource that
    you don't have permission to view or modify, such as:
    - Private entities in campaigns you're not a member of
    - Entities in campaigns where you lack proper permissions
    - Admin-only operations without admin rights

    Example:
        >>> try:
        ...     private_note = client.notes.get(123)  # Private note
        ... except ForbiddenError:
        ...     print("You don't have permission to view this note")
    """

    pass
