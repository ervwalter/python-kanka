"""
:mod: kanka.core
"""

# For backward compatibility - Core was base class for entities
from ..models.base import Entity as Core

# Re-export from new models location for backward compatibility
from ..models.entities import (
    Character,
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
