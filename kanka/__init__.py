# Import the new client
from .client import KankaClient

# Keep backward compatibility imports
from .api import KankaClient as LegacyKankaClient
from .exceptions import KankaError, KankaException, NotFoundError, ValidationError, AuthenticationError, ForbiddenError, RateLimitError

# Import models for easier access
from .models import (
    # Base models
    KankaModel,
    Entity,
    # Entity models
    Character,
    Location,
    Organisation,
    Note,
    Race,
    Quest,
    Journal,
    Family,
    Item,
    Event,
    Ability,
    Conversation,
    Creature,
    Tag,
    # Common models
    Post,
    SearchResult,
    Trait
)

__all__ = [
    'KankaClient',
    'LegacyKankaClient',
    'KankaError',
    'KankaException',
    'NotFoundError',
    'ValidationError', 
    'AuthenticationError',
    'ForbiddenError',
    'RateLimitError',
    # Base models
    'KankaModel',
    'Entity',
    # Entity models
    'Character',
    'Location',
    'Organisation',
    'Note',
    'Race',
    'Quest',
    'Journal',
    'Family',
    'Item',
    'Event',
    'Ability',
    'Conversation',
    'Creature',
    'Tag',
    # Common models
    'Post',
    'SearchResult',
    'Trait'
]