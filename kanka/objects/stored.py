""" Objects to store downloaded information about entities."""

from typing import List, Optional
from ..models.entities import (
    Character, Location, Organisation, Note, Race, Quest, Journal, Family
)
from ..models.base import KankaModel

# For backward compatibility - the stored versions are now just aliases
StoredCharacter = Character
StoredLocation = Location
StoredOrganisation = Organisation
StoredNote = Note
StoredRace = Race
StoredQuest = Quest
StoredJournal = Journal
StoredFamily = Family


class StoredCampaign(KankaModel):
    """Campaign with all related entities."""
    name: str
    id: int
    entry: Optional[str] = None
    characters: Optional[List[Character]] = None
    locations: Optional[List[Location]] = None
    organisations: Optional[List[Organisation]] = None
    notes: Optional[List[Note]] = None
    races: Optional[List[Race]] = None
    quests: Optional[List[Quest]] = None
    journals: Optional[List[Journal]] = None
    families: Optional[List[Family]] = None