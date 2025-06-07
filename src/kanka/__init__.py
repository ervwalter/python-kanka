"""Python client library for the Kanka API.

Kanka is a collaborative world-building and campaign management tool for
tabletop RPGs. This library provides a Python interface to interact with
the Kanka API, allowing you to programmatically manage your campaign data.

Key Features:
    - Full support for all Kanka entity types
    - Type-safe models using Pydantic v2
    - Comprehensive error handling
    - Filtering and search capabilities
    - Post/comment management

Quick Start:
    >>> from kanka import KankaClient
    >>> client = KankaClient("your-api-token", campaign_id=12345)
    >>> characters = client.characters.list()
    >>> dragon = client.search("dragon")

Main Classes:
    - KankaClient: Main client for API interaction
    - Entity models: Character, Location, Organisation, etc.
    - Exceptions: KankaException and specific error types
"""

# Version
from ._version import __version__

# Import the client
from .client import KankaClient
from .exceptions import (
    AuthenticationError,
    ForbiddenError,
    KankaException,
    NotFoundError,
    RateLimitError,
    ValidationError,
)

# Import models for easier access
from .models import (  # Base models; Entity models; Common models
    Calendar,
    Character,
    Creature,
    Entity,
    Event,
    Family,
    Journal,
    KankaModel,
    Location,
    Note,
    Organisation,
    Post,
    Quest,
    Race,
    SearchResult,
    Tag,
    Trait,
)

__all__ = [
    "KankaClient",
    "KankaException",
    "NotFoundError",
    "ValidationError",
    "AuthenticationError",
    "ForbiddenError",
    "RateLimitError",
    # Base models
    "KankaModel",
    "Entity",
    # Entity models
    "Calendar",
    "Character",
    "Creature",
    "Event",
    "Family",
    "Journal",
    "Location",
    "Note",
    "Organisation",
    "Quest",
    "Race",
    "Tag",
    # Common models
    "Post",
    "SearchResult",
    "Trait",
    "__version__",
]
