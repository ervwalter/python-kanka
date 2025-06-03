"""
:mod: kanka.core
"""

# Re-export from new models location for backward compatibility
from ..models.entities import (
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
    Conversation
)

# For backward compatibility - Core was base class for entities
from ..models.base import Entity as Core

__all__ = [
    'Core',
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
    'Conversation'
]