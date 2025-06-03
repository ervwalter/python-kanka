"""Tests for exception handling."""

import pytest

from kanka.exceptions import (
    AuthenticationError,
    ForbiddenError,
    KankaAPIError,
    KankaError,
    KankaException,
    NotFoundError,
    RateLimitError,
    ValidationError,
)


class TestExceptions:
    """Test exception classes."""

    def test_base_exception(self):
        """Test base KankaException."""
        exc = KankaException("Test error")
        assert str(exc) == "Test error"
        assert isinstance(exc, Exception)

    def test_legacy_exceptions(self):
        """Test legacy exception names for backward compatibility."""
        # KankaError should be same as KankaException
        exc1 = KankaError("Legacy error")
        assert isinstance(exc1, KankaException)
        assert str(exc1) == "Legacy error"

        # KankaAPIError should also be same as KankaException
        exc2 = KankaAPIError("API error")
        assert isinstance(exc2, KankaException)
        assert str(exc2) == "API error"

    def test_specific_exceptions(self):
        """Test specific exception types."""
        # NotFoundError
        exc = NotFoundError("Entity not found")
        assert isinstance(exc, KankaException)
        assert str(exc) == "Entity not found"

        # ValidationError
        exc = ValidationError("Invalid data")
        assert isinstance(exc, KankaException)
        assert str(exc) == "Invalid data"

        # RateLimitError
        exc = RateLimitError("Too many requests")
        assert isinstance(exc, KankaException)
        assert str(exc) == "Too many requests"

        # AuthenticationError
        exc = AuthenticationError("Invalid token")
        assert isinstance(exc, KankaException)
        assert str(exc) == "Invalid token"

        # ForbiddenError
        exc = ForbiddenError("Access denied")
        assert isinstance(exc, KankaException)
        assert str(exc) == "Access denied"

    def test_exception_inheritance(self):
        """Test that all exceptions inherit from KankaException."""
        exceptions = [
            NotFoundError,
            ValidationError,
            RateLimitError,
            AuthenticationError,
            ForbiddenError,
        ]

        for exc_class in exceptions:
            exc = exc_class("Test")
            assert isinstance(exc, KankaException)
            assert isinstance(exc, Exception)

    def test_exception_raising(self):
        """Test raising and catching exceptions."""
        # Test catching specific exception
        with pytest.raises(NotFoundError) as exc_info:
            raise NotFoundError("Character not found")

        assert "Character not found" in str(exc_info.value)

        # Test catching base exception
        with pytest.raises(KankaException):
            raise ValidationError("Invalid input")

        # Test that we can catch as KankaException base class
        with pytest.raises(KankaException):
            raise AuthenticationError("Bad token")

    def test_exception_with_extra_data(self):
        """Test exceptions can carry extra data."""
        # Python exceptions can have arbitrary attributes
        exc = ValidationError("Field validation failed")
        exc.errors = {"name": ["Required field"]}  # type: ignore
        exc.field = "name"  # type: ignore

        assert str(exc) == "Field validation failed"
        assert exc.errors == {"name": ["Required field"]}  # type: ignore
        assert exc.field == "name"  # type: ignore
