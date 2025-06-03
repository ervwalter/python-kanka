"""
Backward compatibility module.
All objects are now in kanka.models
"""

from .base import KankaObject, Entity, Trait
from .core import (
    Core,
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

__all__ = [
    'KankaObject',
    'Entity',
    'Trait',
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