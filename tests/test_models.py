"""Tests for Pydantic models."""

from datetime import datetime

import pytest

from kanka.models.base import Entity, KankaModel
from kanka.models.common import Post, Profile, SearchResult
from kanka.models.entities import (
    Attribute,
    Calendar,
    Character,
    EntityEvent,
    Location,
    Map,
)


class TestKankaModel:
    """Test base KankaModel."""

    def test_extra_fields_allowed(self):
        """Test that extra fields are stored."""

        class TestModel(KankaModel):
            name: str

        model = TestModel(name="Test", extra_field="value", another=123)
        assert model.name == "Test"
        assert model.extra_field == "value"  # type: ignore
        assert model.another == 123  # type: ignore

    def test_validation_on_assignment(self):
        """Test that validation happens on assignment."""

        class TestModel(KankaModel):
            count: int

        model = TestModel(count=5)
        assert model.count == 5

        # This should convert string to int
        model.count = "10"  # type: ignore
        assert model.count == 10

        # This should raise validation error
        with pytest.raises(ValueError):
            model.count = "not a number"  # type: ignore


class TestEntity:
    """Test base Entity model."""

    def test_entity_creation_minimal(self):
        """Test creating entity with minimal fields."""
        entity = Entity(
            id=1,
            entity_id=100,
            name="Test Entity",
            created_at="2024-01-01T00:00:00.000000Z",
            created_by=1,
            updated_at="2024-01-01T00:00:00.000000Z",
            updated_by=1,
        )

        assert entity.id == 1
        assert entity.entity_id == 100
        assert entity.name == "Test Entity"
        assert entity.is_private is False  # Default
        assert entity.tags == []  # Default empty list
        assert isinstance(entity.created_at, datetime)

    def test_entity_creation_full(self):
        """Test creating entity with all fields."""
        entity = Entity(
            id=1,
            entity_id=100,
            name="Full Entity",
            image="image.jpg",
            image_full="image_full.jpg",
            image_thumb="image_thumb.jpg",
            is_private=True,
            tags=[1, 2, 3],
            created_at="2024-01-01T00:00:00.000000Z",
            created_by=1,
            updated_at="2024-01-02T00:00:00.000000Z",
            updated_by=2,
            entry="<p>Description</p>",
        )

        assert entity.name == "Full Entity"
        assert entity.image == "image.jpg"
        assert entity.is_private is True
        assert entity.tags == [1, 2, 3]
        assert entity.entry == "<p>Description</p>"

    def test_entity_type_property(self):
        """Test entity_type property."""
        entity = Entity(
            id=1,
            entity_id=100,
            name="Test",
            created_at="2024-01-01T00:00:00.000000Z",
            created_by=1,
            updated_at="2024-01-01T00:00:00.000000Z",
            updated_by=1,
        )
        assert entity.entity_type == "entity"

    def test_datetime_parsing(self):
        """Test datetime field parsing."""
        # Test ISO format with Z
        entity = Entity(
            id=1,
            entity_id=100,
            name="Test",
            created_at="2024-01-01T12:30:45.000000Z",
            created_by=1,
            updated_at="2024-01-02T15:45:30.000000Z",
            updated_by=1,
        )

        assert isinstance(entity.created_at, datetime)
        assert entity.created_at.year == 2024
        assert entity.created_at.month == 1
        assert entity.created_at.day == 1
        assert entity.created_at.hour == 12
        assert entity.created_at.minute == 30


class TestCharacter:
    """Test Character model."""

    def test_character_creation(self):
        """Test creating a character."""
        character = Character(
            id=1,
            entity_id=100,
            name="John Doe",
            created_at="2024-01-01T00:00:00.000000Z",
            created_by=1,
            updated_at="2024-01-01T00:00:00.000000Z",
            updated_by=1,
            location_id=5,
            title="Knight",
            age="25",
            sex="Male",
            race_id=3,
            type="NPC",
            family_id=2,
            is_dead=False,
            traits="Brave, Loyal",
        )

        assert character.name == "John Doe"
        assert character.location_id == 5
        assert character.title == "Knight"
        assert character.age == "25"
        assert character.is_dead is False
        assert character.entity_type == "character"

    def test_character_with_relations(self):
        """Test character with related data."""
        character = Character(
            id=1,
            entity_id=100,
            name="Jane Doe",
            created_at="2024-01-01T00:00:00.000000Z",
            created_by=1,
            updated_at="2024-01-01T00:00:00.000000Z",
            updated_by=1,
            posts=[
                {
                    "id": 1,
                    "entity_id": 100,
                    "name": "Background",
                    "entry": "Character background...",
                    "created_at": "2024-01-01T00:00:00.000000Z",
                    "created_by": 1,
                    "updated_at": "2024-01-01T00:00:00.000000Z",
                    "updated_by": 1,
                }
            ],
            attributes=[
                {"name": "Strength", "value": "18"},
                {"name": "Dexterity", "value": "14"},
            ],
        )

        assert character.posts is not None
        assert len(character.posts) == 1
        assert isinstance(character.posts[0], Post)
        assert character.posts[0].name == "Background"
        assert character.attributes is not None
        assert len(character.attributes) == 2
        assert character.attributes[0]["name"] == "Strength"


class TestLocation:
    """Test Location model."""

    def test_location_creation(self):
        """Test creating a location."""
        location = Location(
            id=1,
            entity_id=100,
            name="Castle Black",
            created_at="2024-01-01T00:00:00.000000Z",
            created_by=1,
            updated_at="2024-01-01T00:00:00.000000Z",
            updated_by=1,
            type="Castle",
            parent_location_id=5,
            map="map.jpg",
            map_url="https://example.com/map.jpg",
            is_map_private=1,
        )

        assert location.name == "Castle Black"
        assert location.type == "Castle"
        assert location.parent_location_id == 5
        assert location.map == "map.jpg"
        assert location.is_map_private == 1


class TestCalendar:
    """Test Calendar model."""

    def test_calendar_complex_fields(self):
        """Test calendar with complex fields."""
        calendar = Calendar(
            id=1,
            entity_id=100,
            name="Fantasy Calendar",
            created_at="2024-01-01T00:00:00.000000Z",
            created_by=1,
            updated_at="2024-01-01T00:00:00.000000Z",
            updated_by=1,
            type="Solar",
            date="1st of Spring, Year 1000",
            months=[{"name": "Spring", "length": 30}, {"name": "Summer", "length": 31}],
            weekdays=["Monday", "Tuesday", "Wednesday"],
            years={"current": 1000, "start": 1},
            seasons=[{"name": "Spring", "month": 1}, {"name": "Summer", "month": 4}],
            has_leap_year=True,
            leap_year_amount=1,
            leap_year_month=2,
        )

        assert calendar.name == "Fantasy Calendar"
        assert calendar.months is not None
        assert len(calendar.months) == 2
        assert calendar.months[0]["name"] == "Spring"
        assert calendar.weekdays is not None
        assert len(calendar.weekdays) == 3
        assert calendar.has_leap_year is True


class TestMap:
    """Test Map model."""

    def test_map_with_measurements(self):
        """Test map with distance measurements."""
        map_entity = Map(
            id=1,
            entity_id=100,
            name="World Map",
            created_at="2024-01-01T00:00:00.000000Z",
            created_by=1,
            updated_at="2024-01-01T00:00:00.000000Z",
            updated_by=1,
            type="World",
            map="worldmap.jpg",
            map_url="https://example.com/worldmap.jpg",
            grid=1,
            is_real=True,
            width=1920,
            height=1080,
            distance_name="miles",
            distance_measure=10.5,
        )

        assert map_entity.name == "World Map"
        assert map_entity.width == 1920
        assert map_entity.height == 1080
        assert map_entity.distance_name == "miles"
        assert map_entity.distance_measure == 10.5


class TestAttribute:
    """Test Attribute model."""

    def test_attribute_required_entity_id(self):
        """Test that entity_id is required for attributes."""
        attribute = Attribute(
            id=1,
            entity_id=100,  # Required field
            name="Strength",
            created_at="2024-01-01T00:00:00.000000Z",
            created_by=1,
            updated_at="2024-01-01T00:00:00.000000Z",
            updated_by=1,
            type="number",
            api_key="str",
        )

        assert attribute.entity_id == 100
        assert attribute.type == "number"
        assert attribute.api_key == "str"

    def test_attribute_missing_entity_id(self):
        """Test that missing entity_id raises error."""
        with pytest.raises(ValueError):
            Attribute(
                id=1,
                # entity_id missing - should raise error
                name="Strength",
                created_at="2024-01-01T00:00:00.000000Z",
                created_by=1,
                updated_at="2024-01-01T00:00:00.000000Z",
                updated_by=1,
            )


class TestEntityEvent:
    """Test EntityEvent model."""

    def test_entity_event_creation(self):
        """Test creating an entity event."""
        event = EntityEvent(
            id=1,
            entity_id=100,  # Required
            name="Battle of Five Armies",
            created_at="2024-01-01T00:00:00.000000Z",
            created_by=1,
            updated_at="2024-01-01T00:00:00.000000Z",
            updated_by=1,
            calendar_id=5,
            date="15th of Summer",
            length=3,
            comment="A great battle",
            is_recurring=False,
            colour="#FF0000",
        )

        assert event.entity_id == 100
        assert event.calendar_id == 5
        assert event.date == "15th of Summer"
        assert event.length == 3
        assert event.colour == "#FF0000"


class TestPost:
    """Test Post model."""

    def test_post_creation(self):
        """Test creating a post."""
        post = Post(
            id=1,
            entity_id=100,
            name="Character Background",
            entry="<p>Long ago...</p>",
            created_at="2024-01-01T00:00:00.000000Z",
            created_by=1,
            updated_at="2024-01-01T00:00:00.000000Z",
            updated_by=1,
            is_private=False,
            is_pinned=True,
            visibility="all",
            position=1,
        )

        assert post.name == "Character Background"
        assert post.entry == "<p>Long ago...</p>"
        assert post.is_pinned is True
        assert post.visibility == "all"


class TestSearchResult:
    """Test SearchResult model."""

    def test_search_result_creation(self):
        """Test creating a search result."""
        result = SearchResult(
            id=1,
            entity_id=100,
            name="Dragon",
            type="creature",
            url="https://app.kanka.io/w/1/entities/100",
            is_private=False,
            tags=[1, 2],
            created_at="2024-01-01T00:00:00.000000Z",
            updated_at="2024-01-01T00:00:00.000000Z",
        )

        assert result.name == "Dragon"
        assert result.type == "creature"
        assert result.tags == [1, 2]


class TestProfile:
    """Test Profile model."""

    def test_profile_creation(self):
        """Test creating a profile."""
        profile = Profile(
            id=1,
            name="John Doe",
            avatar="avatar.jpg",
            avatar_thumb="avatar_thumb.jpg",
            locale="en",
            timezone="UTC",
            date_format="Y-m-d",
            default_pagination=30,
            theme="dark",
            is_patreon=True,
            last_campaign_id=5,
        )

        assert profile.name == "John Doe"
        assert profile.locale == "en"
        assert profile.theme == "dark"
        assert profile.is_patreon is True
