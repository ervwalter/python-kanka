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

from .base import Entity, KankaModel, Post
from .common import SearchResult, Trait
from .entities import (
    Calendar,
    Character,
    Creature,
    Event,
    Family,
    Journal,
    Location,
    Note,
    Organisation,
    Quest,
    Race,
    Tag,
)

__all__ = [
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
]
