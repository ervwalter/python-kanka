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
    - Backward compatibility with legacy API

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

# Import the new client
# Keep backward compatibility imports
from .api import KankaClient as LegacyKankaClient
from .client import KankaClient
from .exceptions import (
    AuthenticationError,
    ForbiddenError,
    KankaError,
    KankaException,
    NotFoundError,
    RateLimitError,
    ValidationError,
)

# Import models for easier access
from .models import (  # Base models; Entity models; Common models
    Ability,
    AttributeTemplate,
    Bookmark,
    Calendar,
    Character,
    Conversation,
    Creature,
    DiceRoll,
    Entity,
    Event,
    Family,
    Item,
    Journal,
    KankaModel,
    Location,
    Map,
    Note,
    Organisation,
    Post,
    Quest,
    Race,
    SearchResult,
    Tag,
    Timeline,
    Trait,
)

__all__ = [
    "KankaClient",
    "LegacyKankaClient",
    "KankaError",
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
    "Ability",
    "AttributeTemplate",
    "Bookmark",
    "Calendar",
    "Character",
    "Conversation",
    "Creature",
    "DiceRoll",
    "Event",
    "Family",
    "Item",
    "Journal",
    "Location",
    "Map",
    "Note",
    "Organisation",
    "Quest",
    "Race",
    "Tag",
    "Timeline",
    # Common models
    "Post",
    "SearchResult",
    "Trait",
]
