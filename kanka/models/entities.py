"""
Entity models for Kanka API.

This module contains all the specific entity type models that represent
the various entities available in Kanka campaigns. Each model inherits
from the base Entity class and adds type-specific fields.

Entity Types:
    - Character: Player characters, NPCs, and other persons
    - Location: Places, regions, buildings, etc.
    - Organisation: Groups, guilds, governments, etc.
    - Family: Family groups and lineages
    - Event: Historical or campaign events
    - Item: Objects, artifacts, equipment
    - Note: Campaign notes and documentation
    - Quest: Quests and objectives
    - Journal: Journal entries and logs
    - Race: Character races/species templates
    - Creature: Creature and monster templates
    - Calendar: Campaign calendars
    - Timeline: Campaign timelines
    - Map: Maps with markers and layers
    - Tag: Organizational tags
    - Ability: Spells, skills, and abilities
    - Conversation: Dialog and conversations
    - Species: Species taxonomy
    - Attribute: Custom attributes
    - EntityNote: Notes attached to entities
    - EntityEvent: Events attached to entities
"""

from typing import Dict, List, Optional

from .base import Entity
from .common import Post  # Import at top for forward reference


class Character(Entity):
    """Character entity representing people in the campaign.
    
    Characters can be player characters, NPCs, historical figures,
    or any other person in your campaign world.
    
    Attributes:
        location_id: Current location of the character
        title: Character's title or role
        age: Character's age
        sex: Character's sex/gender
        race_id: Link to Race entity
        type: Character type/class
        family_id: Link to Family entity
        is_dead: Whether character is deceased
        traits: Character traits (deprecated, use attributes)
        posts: Related posts (when ?related=1)
        attributes: Custom attributes (when ?related=1)
    """

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
    posts: Optional[List["Post"]] = None
    attributes: Optional[List[Dict]] = None


class Location(Entity):
    """Location entity representing places in the campaign.
    
    Locations can be countries, cities, buildings, rooms, or any
    other place in your campaign world.
    
    Attributes:
        type: Location type (e.g., 'City', 'Country', 'Building')
        map: Map image filename
        map_url: Full URL to map image
        is_map_private: Privacy setting for map
        parent_location_id: Parent location for hierarchy
        posts: Related posts (when ?related=1)
        attributes: Custom attributes (when ?related=1)
    """

    type: Optional[str] = None
    map: Optional[str] = None
    map_url: Optional[str] = None
    is_map_private: Optional[int] = None
    parent_location_id: Optional[int] = None

    # Related data
    posts: Optional[List["Post"]] = None
    attributes: Optional[List[Dict]] = None


class Organisation(Entity):
    """Organisation entity representing groups in the campaign.
    
    Organisations can be guilds, governments, cults, companies,
    or any other group in your campaign.
    
    Attributes:
        location_id: Organisation's headquarters/location
        type: Organisation type
        organisation_id: Parent organisation for hierarchy
        posts: Related posts (when ?related=1)
        attributes: Custom attributes (when ?related=1)
    """

    location_id: Optional[int] = None
    type: Optional[str] = None
    organisation_id: Optional[int] = None

    # Related data
    posts: Optional[List["Post"]] = None
    attributes: Optional[List[Dict]] = None


class Note(Entity):
    """Note entity for campaign documentation.
    
    Notes are used for campaign lore, DM notes, world-building
    documentation, or any other textual information.
    
    Attributes:
        type: Note type/category
        posts: Related posts (when ?related=1)
        attributes: Custom attributes (when ?related=1)
    """

    type: Optional[str] = None

    # Related data
    posts: Optional[List["Post"]] = None
    attributes: Optional[List[Dict]] = None


class Race(Entity):
    """Race entity representing character races/species.
    
    Races define the various species or races that characters
    can belong to in your campaign.
    
    Attributes:
        type: Race type/category
        race_id: Parent race for sub-races
        posts: Related posts (when ?related=1)
        attributes: Custom attributes (when ?related=1)
    """

    type: Optional[str] = None
    race_id: Optional[int] = None

    # Related data
    posts: Optional[List["Post"]] = None
    attributes: Optional[List[Dict]] = None


class Quest(Entity):
    """Quest entity representing objectives and missions.
    
    Quests track objectives, missions, and goals for characters
    or the party in your campaign.
    
    Attributes:
        type: Quest type (e.g., 'Main', 'Side', 'Personal')
        quest_id: Parent quest for sub-quests
        character_id: Quest giver or related character
        posts: Related posts (when ?related=1)
        attributes: Custom attributes (when ?related=1)
    """

    type: Optional[str] = None
    quest_id: Optional[int] = None
    character_id: Optional[int] = None

    # Related data
    posts: Optional[List["Post"]] = None
    attributes: Optional[List[Dict]] = None


class Journal(Entity):
    """Journal entity for session logs and chronicles.
    
    Journals are used to record session notes, character journals,
    or chronicle campaign events.
    
    Attributes:
        type: Journal type
        date: In-game date of journal entry
        character_id: Character who wrote the journal
        posts: Related posts (when ?related=1)
        attributes: Custom attributes (when ?related=1)
    """

    type: Optional[str] = None
    date: Optional[str] = None
    character_id: Optional[int] = None

    # Related data
    posts: Optional[List["Post"]] = None
    attributes: Optional[List[Dict]] = None


class Family(Entity):
    """Family entity representing family groups and lineages.
    
    Families track bloodlines, clans, houses, or other family
    structures in your campaign.
    
    Attributes:
        location_id: Family seat/home location
        family_id: Parent family for family trees
        posts: Related posts (when ?related=1)
        attributes: Custom attributes (when ?related=1)
    """

    location_id: Optional[int] = None
    family_id: Optional[int] = None

    # Related data
    posts: Optional[List["Post"]] = None
    attributes: Optional[List[Dict]] = None


class Item(Entity):
    """Item entity representing objects and equipment.
    
    Items can be weapons, armor, artifacts, mundane objects,
    or any other physical item in your campaign.
    
    Attributes:
        type: Item type/category
        location_id: Current location of item
        character_id: Character who owns/carries item
        posts: Related posts (when ?related=1)
        attributes: Custom attributes (when ?related=1)
    """

    type: Optional[str] = None
    location_id: Optional[int] = None
    character_id: Optional[int] = None

    # Related data
    posts: Optional[List["Post"]] = None
    attributes: Optional[List[Dict]] = None


class Event(Entity):
    """Event entity representing historical or campaign events.
    
    Events track important occurrences in your campaign's
    history or timeline.
    
    Attributes:
        type: Event type/category
        date: When the event occurred
        location_id: Where the event took place
        posts: Related posts (when ?related=1)
        attributes: Custom attributes (when ?related=1)
    """

    type: Optional[str] = None
    date: Optional[str] = None
    location_id: Optional[int] = None

    # Related data
    posts: Optional[List["Post"]] = None
    attributes: Optional[List[Dict]] = None


class Ability(Entity):
    """Ability entity representing spells, skills, and powers.
    
    Abilities define spells, skills, feats, or other special
    powers that characters can possess.
    
    Attributes:
        type: Ability type (e.g., 'Spell', 'Skill', 'Feat')
        ability_id: Parent ability for hierarchies
        charges: Number of uses/charges
        posts: Related posts (when ?related=1)
        attributes: Custom attributes (when ?related=1)
    """

    type: Optional[str] = None
    ability_id: Optional[int] = None
    charges: Optional[int] = None

    # Related data
    posts: Optional[List["Post"]] = None
    attributes: Optional[List[Dict]] = None


class Conversation(Entity):
    """Conversation entity for dialog and discussions.
    
    Conversations store important dialogs, negotiations,
    or other verbal exchanges in your campaign.
    
    Attributes:
        type: Conversation type
        target: Conversation participants or subject
        posts: Related posts (when ?related=1)
        attributes: Custom attributes (when ?related=1)
    """

    type: Optional[str] = None
    target: Optional[str] = None

    # Related data
    posts: Optional[List["Post"]] = None
    attributes: Optional[List[Dict]] = None


class Creature(Entity):
    """Creature entity representing monsters and beasts.
    
    Creatures define the various monsters, animals, and
    non-character beings in your campaign.
    
    Attributes:
        type: Creature type/category
        location_id: Creature's habitat/location
        posts: Related posts (when ?related=1)
        attributes: Custom attributes (when ?related=1)
    """

    type: Optional[str] = None
    location_id: Optional[int] = None

    # Related data
    posts: Optional[List["Post"]] = None
    attributes: Optional[List[Dict]] = None


class Tag(Entity):
    """Tag entity for organizing and categorizing content.
    
    Tags provide a flexible way to categorize and link
    entities across your campaign.
    
    Attributes:
        type: Tag type/category
        colour: Tag color for visual organization
        tag_id: Parent tag for tag hierarchies
        posts: Related posts (when ?related=1)
        attributes: Custom attributes (when ?related=1)
    """

    type: Optional[str] = None
    colour: Optional[str] = None
    tag_id: Optional[int] = None  # Parent tag

    # Related data
    posts: Optional[List["Post"]] = None
    attributes: Optional[List[Dict]] = None


class Species(Entity):
    """Species entity for detailed taxonomy.
    
    Species provide more detailed biological/taxonomical
    organization than races.
    
    Attributes:
        type: Species type/category
        species_id: Parent species for subspecies
        posts: Related posts (when ?related=1)
        attributes: Custom attributes (when ?related=1)
    """

    type: Optional[str] = None
    species_id: Optional[int] = None

    # Related data
    posts: Optional[List["Post"]] = None
    attributes: Optional[List[Dict]] = None


class Calendar(Entity):
    """Calendar entity for campaign time tracking.
    
    Calendars define custom calendar systems with months,
    weeks, and special dates for your campaign world.
    
    Attributes:
        type: Calendar type
        date: Current date in the calendar
        parameters: Calendar configuration
        months: List of month definitions
        weekdays: List of weekday names
        years: Year configuration
        seasons: Season definitions
        moons: Moon/celestial body definitions
        suffix: Year suffix format
        has_leap_year: Whether calendar has leap years
        leap_year_amount: Frequency of leap years
        leap_year_month: Which month gets extra day
        leap_year_offset: Leap year calculation offset
        leap_year_start: Starting year for leap calculations
        posts: Related posts (when ?related=1)
        attributes: Custom attributes (when ?related=1)
    """

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
    posts: Optional[List["Post"]] = None
    attributes: Optional[List[Dict]] = None


class Timeline(Entity):
    """Timeline entity for organizing events chronologically.
    
    Timelines provide a visual way to organize and display
    events in chronological order.
    
    Attributes:
        type: Timeline type
        calendar_id: Associated calendar for dates
        posts: Related posts (when ?related=1)
        attributes: Custom attributes (when ?related=1)
    """

    type: Optional[str] = None
    calendar_id: Optional[int] = None

    # Related data
    posts: Optional[List["Post"]] = None
    attributes: Optional[List[Dict]] = None


class Map(Entity):
    """Map entity for visual campaign geography.
    
    Maps store images with markers, allowing visual representation
    of your campaign world's geography.
    
    Attributes:
        type: Map type
        map: Map image filename
        map_url: Full URL to map image
        grid: Grid overlay setting
        is_real: Whether to use real coordinates
        width: Map width in pixels
        height: Map height in pixels
        distance_name: Unit name for distances
        distance_measure: Distance per grid unit
        posts: Related posts (when ?related=1)
        attributes: Custom attributes (when ?related=1)
    """

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
    posts: Optional[List["Post"]] = None
    attributes: Optional[List[Dict]] = None


class Attribute(Entity):
    """Attribute entity for custom entity fields.
    
    Attributes allow adding custom fields to any entity,
    providing flexible data storage.
    
    Attributes:
        entity_id: Parent entity this attribute belongs to
        type: Attribute type
        api_key: API key for programmatic access
        posts: Related posts (when ?related=1)
    """

    entity_id: int
    type: Optional[str] = None
    api_key: Optional[str] = None

    # Related data
    posts: Optional[List["Post"]] = None


class EntityNote(Entity):
    """Entity note for private annotations.
    
    Entity notes are private annotations that can be attached
    to any entity, visible only to authorized users.
    
    Attributes:
        entity_id: Parent entity this note belongs to
        visibility: Visibility level of the note
        posts: Related posts (when ?related=1)
        attributes: Custom attributes (when ?related=1)
    """

    entity_id: int
    visibility: Optional[str] = None

    # Related data
    posts: Optional[List["Post"]] = None
    attributes: Optional[List[Dict]] = None


class EntityEvent(Entity):
    """Entity event for calendar integration.
    
    Entity events link entities to specific dates on calendars,
    allowing timeline and calendar integration.
    
    Attributes:
        entity_id: Parent entity this event belongs to
        calendar_id: Calendar this event appears on
        date: Event date
        length: Event duration in days
        comment: Event description
        is_recurring: Whether event repeats
        recurring_until: End date for recurring events
        recurring_periodicity: How often event recurs
        colour: Event color on calendar
        posts: Related posts (when ?related=1)
        attributes: Custom attributes (when ?related=1)
    """

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
    posts: Optional[List["Post"]] = None
    attributes: Optional[List[Dict]] = None


# Forward reference updates
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
