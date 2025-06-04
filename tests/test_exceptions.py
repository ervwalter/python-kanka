"""Tests for exception handling."""

import pytest

from kanka.exceptions import (
    AuthenticationError,
    ForbiddenError,
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

    def test_specific_exceptions(self):
        """Test specific exception types."""
        # NotFoundError
        exc1 = NotFoundError("Entity not found")
        assert isinstance(exc1, KankaException)
        assert str(exc1) == "Entity not found"

        # ValidationError
        exc2 = ValidationError("Invalid data")
        assert isinstance(exc2, KankaException)
        assert str(exc2) == "Invalid data"

        # RateLimitError
        exc3 = RateLimitError("Too many requests")
        assert isinstance(exc3, KankaException)
        assert str(exc3) == "Too many requests"

        # AuthenticationError
        exc4 = AuthenticationError("Invalid token")
        assert isinstance(exc4, KankaException)
        assert str(exc4) == "Invalid token"

        # ForbiddenError
        exc5 = ForbiddenError("Access denied")
        assert isinstance(exc5, KankaException)
        assert str(exc5) == "Access denied"

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
