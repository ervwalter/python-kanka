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