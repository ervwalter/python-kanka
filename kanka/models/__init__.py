"""
Pydantic models for Kanka API entities.

This package contains all the data models used by the Kanka API client.
The models are built using Pydantic v2 for automatic validation and
serialization.

Model Categories:
    - Base models: KankaModel, Entity
    - Entity models: All specific entity types (Character, Location, etc.)
    - Common models: Post, SearchResult, Trait

All models provide:
    - Automatic validation of API responses
    - Type hints for better IDE support
    - Serialization to/from JSON
    - Extra field handling for API flexibility
"""

from .base import Entity, KankaModel
from .common import Post, SearchResult, Trait
from .entities import (
    Ability,
    Attribute,
    Calendar,
    Character,
    Conversation,
    Creature,
    EntityEvent,
    EntityNote,
    Event,
    Family,
    Item,
    Journal,
    Location,
    Map,
    Note,
    Organisation,
    Quest,
    Race,
    Species,
    Tag,
    Timeline,
)

__all__ = [
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
    "Species",
    "Calendar",
    "Timeline",
    "Map",
    "Attribute",
    "EntityNote",
    "EntityEvent",
    # Common models
    "Post",
    "SearchResult",
    "Trait",
]
