"""
Backward compatibility module.
All objects are now in kanka.models
"""

from .base import Entity, KankaObject, Trait
from ..models.common import Post
from .core import (
    Ability,
    Character,
    Conversation,
    Core,
    Event,
    Family,
    Item,
    Journal,
    Location,
    Note,
    Organisation,
    Quest,
    Race,
)

__all__ = [
    "KankaObject",
    "Entity",
    "Trait",
    "Post",
    "Core",
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
]
