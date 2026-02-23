"""Tests for Pydantic models."""

from datetime import datetime

import pytest

from kanka.models.base import Entity, KankaModel, Post
from kanka.models.common import (
    EntityAsset,
    EntityImageData,
    EntityImageInfo,
    GalleryImage,
    Profile,
    SearchResult,
)
from kanka.models.entities import Calendar, Character, Location


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
        )

        assert post.name == "Character Background"
        assert post.entry == "<p>Long ago...</p>"
        assert post.visibility_id is None


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


class TestGalleryImage:
    """Test GalleryImage model."""

    def test_gallery_image_creation(self):
        """Test creating a gallery image."""
        image = GalleryImage(
            id="abc-123",
            name="portrait.png",
            is_folder=False,
            path="https://example.com/image.png",
            ext="png",
            size=12345,
            created_at="2024-01-01T00:00:00.000000Z",
            created_by=1,
        )

        assert image.id == "abc-123"
        assert image.name == "portrait.png"
        assert image.is_folder is False
        assert image.ext == "png"
        assert image.size == 12345

    def test_gallery_image_defaults(self):
        """Test gallery image default values."""
        image = GalleryImage(id="abc-123")

        assert image.name is None
        assert image.is_folder is False
        assert image.folder_id is None
        assert image.path is None
        assert image.focus_x is None
        assert image.focus_y is None


class TestEntityAsset:
    """Test EntityAsset model."""

    def test_entity_asset_creation(self):
        """Test creating an entity asset."""
        asset = EntityAsset(
            id=1,
            entity_id=100,
            name="map.png",
            type_id=1,
            is_pinned=True,
            _url="https://example.com/asset.png",
        )

        assert asset.id == 1
        assert asset.entity_id == 100
        assert asset.name == "map.png"
        assert asset.type_id == 1
        assert asset.is_pinned is True
        assert asset.url == "https://example.com/asset.png"

    def test_entity_asset_link_type(self):
        """Test entity asset with link type."""
        asset = EntityAsset(
            id=2,
            entity_id=100,
            name="Reference",
            type_id=2,
            metadata={"url": "https://example.com", "icon": "fa-link"},
        )

        assert asset.type_id == 2
        assert asset.metadata is not None
        assert asset.metadata["url"] == "https://example.com"

    def test_entity_asset_alias_type(self):
        """Test entity asset with alias type."""
        asset = EntityAsset(
            id=3,
            entity_id=100,
            name="Dragon",
            type_id=3,
        )

        assert asset.type_id == 3
        assert asset.url is None


class TestEntityImageInfo:
    """Test EntityImageInfo model."""

    def test_entity_image_info_creation(self):
        """Test creating entity image info."""
        info = EntityImageInfo(
            image=EntityImageData(
                uuid="img-uuid",
                full="https://example.com/full.png",
                thumbnail="https://example.com/thumb.png",
            ),
            header=EntityImageData(
                uuid="hdr-uuid",
                full="https://example.com/header.png",
            ),
        )

        assert info.image is not None
        assert info.image.uuid == "img-uuid"
        assert info.image.full == "https://example.com/full.png"
        assert info.header is not None
        assert info.header.uuid == "hdr-uuid"

    def test_entity_image_info_defaults(self):
        """Test entity image info defaults."""
        info = EntityImageInfo()
        assert info.image is None
        assert info.header is None
