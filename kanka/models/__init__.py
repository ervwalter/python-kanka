"""
Pydantic models for Kanka API entities.
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
