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
    - Note: Campaign notes and documentation
    - Quest: Quests and objectives
    - Journal: Journal entries and logs
    - Race: Character races/species templates
    - Creature: Creature and monster templates
    - Calendar: Campaign calendars
    - Tag: Organizational tags
"""

from typing import Optional, Union

from .base import Entity


class Character(Entity):
    """Character entity representing people in the campaign.

    Characters can be player characters, NPCs, historical figures,
    or any other person in your campaign world.

    Attributes:
        location_id: Current location of the character
        title: Character's title or role
        age: Character's age
        sex: Character's sex/gender
        pronouns: Character's pronouns
        race_id: Link to Race entity
        type: Character type/class
        family_id: Link to Family entity
        is_dead: Whether character is deceased
    """

    location_id: Optional[int] = None
    title: Optional[str] = None
    age: Optional[str] = None
    sex: Optional[str] = None
    pronouns: Optional[str] = None
    race_id: Optional[int] = None
    type: Optional[str] = None
    family_id: Optional[int] = None
    is_dead: bool = False


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
    location_id: Optional[int] = None


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


class Tag(Entity):
    """Tag entity for organizing and categorizing content.

    Tags provide a flexible way to categorize and link
    entities across your campaign.

    Attributes:
        type: Tag type/category
        colour: Tag color for visual organization. Valid values are:
                'aqua', 'black', 'brown', 'grey', 'green', 'light-blue',
                'maroon', 'navy', 'orange', 'pink', 'purple', 'red',
                'teal', 'yellow', or None/empty string for no color
        tag_id: Parent tag for tag hierarchies
        posts: Related posts (when ?related=1)
        attributes: Custom attributes (when ?related=1)
    """

    type: Optional[str] = None
    colour: Optional[str] = None
    tag_id: Optional[int] = None  # Parent tag


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
    months: Optional[list[dict]] = None
    weekdays: Optional[list[str]] = None
    years: Optional[Union[dict, list]] = None
    seasons: Optional[list[dict]] = None
    moons: Optional[list[dict]] = None
    suffix: Optional[str] = None
    has_leap_year: Optional[bool] = None
    leap_year_amount: Optional[int] = None
    leap_year_month: Optional[int] = None
    leap_year_offset: Optional[int] = None
    leap_year_start: Optional[int] = None


# Forward reference updates
Character.model_rebuild()
Location.model_rebuild()
Organisation.model_rebuild()
Note.model_rebuild()
Race.model_rebuild()
Quest.model_rebuild()
Journal.model_rebuild()
Family.model_rebuild()
Event.model_rebuild()
Creature.model_rebuild()
Tag.model_rebuild()
Calendar.model_rebuild()
