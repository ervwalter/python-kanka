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
    Character,
    Conversation,
    Creature,
    Entity,
    Event,
    Family,
    Item,
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
    "Character",
    "Location",
    "Organisation",
    "Note",
    "Race",
    "Quest",
    "Journal",
    "Family",
    "Item",
    "Event",
    "Ability",
    "Conversation",
    "Creature",
    "Tag",
    # Common models
    "Post",
    "SearchResult",
    "Trait",
]
