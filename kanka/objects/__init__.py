"""
Backward compatibility module.
All objects are now in kanka.models
"""

from ..models.common import Post
from .base import Entity, KankaObject, Trait
from .core import (
    Character,
    Core,
    Event,
    Family,
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
    "Event",
]
