"""
Entity models for Kanka API.
"""

from typing import Optional, List, Dict
from .base import Entity


class Character(Entity):
    """Character entity with all fields."""
    location_id: Optional[int] = None
    title: Optional[str] = None
    age: Optional[str] = None
    sex: Optional[str] = None
    race_id: Optional[int] = None
    type: Optional[str] = None
    family_id: Optional[int] = None
    is_dead: bool = False
    traits: Optional[str] = None
    
    # Related data (populated when ?related=1)
    posts: Optional[List['Post']] = None
    attributes: Optional[List[Dict]] = None


class Location(Entity):
    """Location entity."""
    type: Optional[str] = None
    map: Optional[str] = None
    map_url: Optional[str] = None
    is_map_private: Optional[int] = None
    parent_location_id: Optional[int] = None
    
    # Related data
    posts: Optional[List['Post']] = None
    attributes: Optional[List[Dict]] = None


class Organisation(Entity):
    """Organisation entity."""
    location_id: Optional[int] = None
    type: Optional[str] = None
    organisation_id: Optional[int] = None
    
    # Related data
    posts: Optional[List['Post']] = None
    attributes: Optional[List[Dict]] = None


class Note(Entity):
    """Note entity."""
    type: Optional[str] = None
    
    # Related data
    posts: Optional[List['Post']] = None
    attributes: Optional[List[Dict]] = None


class Race(Entity):
    """Race entity."""
    type: Optional[str] = None
    race_id: Optional[int] = None
    
    # Related data
    posts: Optional[List['Post']] = None
    attributes: Optional[List[Dict]] = None


class Quest(Entity):
    """Quest entity."""
    type: Optional[str] = None
    quest_id: Optional[int] = None
    character_id: Optional[int] = None
    
    # Related data
    posts: Optional[List['Post']] = None
    attributes: Optional[List[Dict]] = None


class Journal(Entity):
    """Journal entity."""
    type: Optional[str] = None
    date: Optional[str] = None
    character_id: Optional[int] = None
    
    # Related data
    posts: Optional[List['Post']] = None
    attributes: Optional[List[Dict]] = None


class Family(Entity):
    """Family entity."""
    location_id: Optional[int] = None
    family_id: Optional[int] = None
    
    # Related data
    posts: Optional[List['Post']] = None
    attributes: Optional[List[Dict]] = None


class Item(Entity):
    """Item entity."""
    type: Optional[str] = None
    location_id: Optional[int] = None
    character_id: Optional[int] = None
    
    # Related data
    posts: Optional[List['Post']] = None
    attributes: Optional[List[Dict]] = None


class Event(Entity):
    """Event entity."""
    type: Optional[str] = None
    date: Optional[str] = None
    location_id: Optional[int] = None
    
    # Related data
    posts: Optional[List['Post']] = None
    attributes: Optional[List[Dict]] = None


class Ability(Entity):
    """Ability entity."""
    type: Optional[str] = None
    ability_id: Optional[int] = None
    charges: Optional[int] = None
    
    # Related data
    posts: Optional[List['Post']] = None
    attributes: Optional[List[Dict]] = None


class Conversation(Entity):
    """Conversation entity."""
    type: Optional[str] = None
    target: Optional[str] = None
    
    # Related data
    posts: Optional[List['Post']] = None
    attributes: Optional[List[Dict]] = None


class Creature(Entity):
    """Creature entity (missing from original but in plan)."""
    type: Optional[str] = None
    location_id: Optional[int] = None
    
    # Related data
    posts: Optional[List['Post']] = None
    attributes: Optional[List[Dict]] = None


class Tag(Entity):
    """Tag entity."""
    type: Optional[str] = None
    colour: Optional[str] = None
    tag_id: Optional[int] = None  # Parent tag
    
    # Related data
    posts: Optional[List['Post']] = None
    attributes: Optional[List[Dict]] = None


class Species(Entity):
    """Species entity."""
    type: Optional[str] = None
    species_id: Optional[int] = None
    
    # Related data
    posts: Optional[List['Post']] = None
    attributes: Optional[List[Dict]] = None


class Calendar(Entity):
    """Calendar entity."""
    type: Optional[str] = None
    date: Optional[str] = None
    parameters: Optional[str] = None
    months: Optional[List[Dict]] = None
    weekdays: Optional[List[str]] = None
    years: Optional[Dict] = None
    seasons: Optional[List[Dict]] = None
    moons: Optional[List[Dict]] = None
    suffix: Optional[str] = None
    has_leap_year: Optional[bool] = None
    leap_year_amount: Optional[int] = None
    leap_year_month: Optional[int] = None
    leap_year_offset: Optional[int] = None
    leap_year_start: Optional[int] = None
    
    # Related data
    posts: Optional[List['Post']] = None
    attributes: Optional[List[Dict]] = None


class Timeline(Entity):
    """Timeline entity."""
    type: Optional[str] = None
    calendar_id: Optional[int] = None
    
    # Related data
    posts: Optional[List['Post']] = None
    attributes: Optional[List[Dict]] = None


class Map(Entity):
    """Map entity."""
    type: Optional[str] = None
    map: Optional[str] = None
    map_url: Optional[str] = None
    grid: Optional[int] = None
    is_real: Optional[bool] = None
    width: Optional[int] = None
    height: Optional[int] = None
    distance_name: Optional[str] = None
    distance_measure: Optional[float] = None
    
    # Related data
    posts: Optional[List['Post']] = None
    attributes: Optional[List[Dict]] = None


class Attribute(Entity):
    """Attribute entity."""
    entity_id: int
    type: Optional[str] = None
    api_key: Optional[str] = None
    
    # Related data
    posts: Optional[List['Post']] = None


class EntityNote(Entity):
    """Entity note."""
    entity_id: int
    visibility: Optional[str] = None
    
    # Related data
    posts: Optional[List['Post']] = None
    attributes: Optional[List[Dict]] = None


class EntityEvent(Entity):
    """Entity event."""
    entity_id: int
    calendar_id: Optional[int] = None
    date: Optional[str] = None
    length: Optional[int] = None
    comment: Optional[str] = None
    is_recurring: Optional[bool] = None
    recurring_until: Optional[str] = None
    recurring_periodicity: Optional[str] = None
    colour: Optional[str] = None
    
    # Related data
    posts: Optional[List['Post']] = None
    attributes: Optional[List[Dict]] = None


# Forward reference updates
from .common import Post
Character.model_rebuild()
Location.model_rebuild()
Organisation.model_rebuild()
Note.model_rebuild()
Race.model_rebuild()
Quest.model_rebuild()
Journal.model_rebuild()
Family.model_rebuild()
Item.model_rebuild()
Event.model_rebuild()
Ability.model_rebuild()
Conversation.model_rebuild()
Creature.model_rebuild()
Tag.model_rebuild()
Species.model_rebuild()
Calendar.model_rebuild()
Timeline.model_rebuild()
Map.model_rebuild()
Attribute.model_rebuild()
EntityNote.model_rebuild()
EntityEvent.model_rebuild()