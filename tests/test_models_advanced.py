"""Advanced tests for model features and edge cases."""

from datetime import datetime

import pytest

from kanka.models.base import Entity, Post
from kanka.models.common import Trait
from kanka.models.entities import Character, Location, Tag


class TestExtraFieldHandling:
    """Test handling of extra fields in models."""

    def test_entity_with_undocumented_fields(self):
        """Test that entities can accept undocumented but valid API fields."""
        # Character with 'sex' field (accepted by API but not in our model)
        character = Character(
            id=1,
            entity_id=100,
            name="Test Character",
            created_at="2024-01-01T00:00:00.000000Z",
            created_by=1,
            updated_at="2024-01-01T00:00:00.000000Z",
            updated_by=1,
            sex="Female",  # Extra field accepted by API
            custom_field="Custom Value",  # Completely custom field
        )

        assert character.name == "Test Character"
        assert hasattr(character, "sex")
        assert character.sex == "Female"  # type: ignore[attr-defined]
        assert character.custom_field == "Custom Value"  # type: ignore[attr-defined]

    def test_location_with_extra_fields(self):
        """Test location with extra fields."""
        location = Location(
            id=1,
            entity_id=100,
            name="Test Location",
            created_at="2024-01-01T00:00:00.000000Z",
            created_by=1,
            updated_at="2024-01-01T00:00:00.000000Z",
            updated_by=1,
            # Extra fields
            population=50000,
            climate="Temperate",
            custom_data={"key": "value"},
        )

        assert location.population == 50000  # type: ignore
        assert location.climate == "Temperate"  # type: ignore
        assert location.custom_data == {"key": "value"}  # type: ignore

    def test_post_with_extra_fields(self):
        """Test post with visibility and position fields."""
        post = Post(
            id=1,
            entity_id=100,
            name="Test Post",
            entry="<p>Content</p>",
            created_at="2024-01-01T00:00:00.000000Z",
            created_by=1,
            updated_at="2024-01-01T00:00:00.000000Z",
            updated_by=1,
            # Extra fields from API
            is_pinned=True,
            position=1,
            visibility="all",
        )

        # Extra fields are stored dynamically
        assert hasattr(post, "is_pinned")
        assert post.is_pinned is True  # type: ignore[attr-defined]
        assert post.position == 1  # type: ignore[attr-defined]
        assert post.visibility == "all"  # type: ignore[attr-defined]

    def test_tag_with_nested_data(self):
        """Test tag with nested/complex data structures."""
        tag = Tag(
            id=1,
            entity_id=100,
            name="Complex Tag",
            created_at="2024-01-01T00:00:00.000000Z",
            created_by=1,
            updated_at="2024-01-01T00:00:00.000000Z",
            updated_by=1,
            # Extra nested data
            metadata={
                "usage_count": 15,
                "categories": ["npc", "important"],
                "custom_fields": {"priority": "high", "group": "main_campaign"},
            },
        )

        assert tag.metadata["usage_count"] == 15  # type: ignore
        assert "npc" in tag.metadata["categories"]  # type: ignore


class TestModelEdgeCases:
    """Test edge cases in model handling."""

    def test_entity_with_null_updated_by(self):
        """Test entity where updated_by can be null."""
        entity = Entity(
            id=1,
            entity_id=100,
            name="Test Entity",
            created_at="2024-01-01T00:00:00.000000Z",
            created_by=1,
            updated_at="2024-01-01T00:00:00.000000Z",
            updated_by=None,  # Can be null from API
        )

        assert entity.updated_by is None

    def test_entity_with_empty_tags(self):
        """Test that empty tags list is handled correctly."""
        entity = Entity(
            id=1,
            entity_id=100,
            name="Test Entity",
            created_at="2024-01-01T00:00:00.000000Z",
            created_by=1,
            updated_at="2024-01-01T00:00:00.000000Z",
            updated_by=1,
            tags=[],  # Explicitly empty
        )

        assert entity.tags == []
        assert isinstance(entity.tags, list)

    def test_character_extra_fields(self):
        """Test character with extra fields from API."""
        # The API can return extra fields that aren't in our model
        character = Character(
            id=1,
            entity_id=100,
            name="Test Character",
            created_at="2024-01-01T00:00:00.000000Z",
            created_by=1,
            updated_at="2024-01-01T00:00:00.000000Z",
            updated_by=1,
            traits=[],  # Extra field from API
        )

        # Extra fields are stored dynamically
        assert hasattr(character, "traits")
        assert character.traits == []  # type: ignore[attr-defined]

    def test_datetime_with_microseconds(self):
        """Test datetime parsing with different microsecond formats."""
        # Test with 6-digit microseconds
        entity1 = Entity(
            id=1,
            entity_id=100,
            name="Test",
            created_at="2024-01-01T12:30:45.123456Z",
            created_by=1,
            updated_at="2024-01-01T12:30:45.000000Z",
            updated_by=1,
        )

        assert entity1.created_at.microsecond == 123456

    def test_model_dict_export(self):
        """Test exporting models to dict."""
        character = Character(
            id=1,
            entity_id=100,
            name="Test Character",
            created_at="2024-01-01T00:00:00.000000Z",
            created_by=1,
            updated_at="2024-01-01T00:00:00.000000Z",
            updated_by=1,
            title="Knight",
            extra_field="extra_value",
        )

        # Convert to dict
        char_dict = character.model_dump()

        assert char_dict["name"] == "Test Character"
        assert char_dict["title"] == "Knight"
        assert char_dict["extra_field"] == "extra_value"
        assert isinstance(char_dict["created_at"], datetime)

    def test_model_json_export(self):
        """Test exporting models to JSON."""
        location = Location(
            id=1,
            entity_id=100,
            name="Test Location",
            created_at="2024-01-01T00:00:00.000000Z",
            created_by=1,
            updated_at="2024-01-01T00:00:00.000000Z",
            updated_by=1,
            type="City",
        )

        # Convert to JSON string
        json_str = location.model_dump_json()

        assert '"name":"Test Location"' in json_str
        assert '"type":"City"' in json_str

    def test_model_field_exclusion(self):
        """Test excluding fields when exporting."""
        character = Character(
            id=1,
            entity_id=100,
            name="Test Character",
            created_at="2024-01-01T00:00:00.000000Z",
            created_by=1,
            updated_at="2024-01-01T00:00:00.000000Z",
            updated_by=1,
            title="Knight",
        )

        # Exclude certain fields
        char_dict = character.model_dump(
            exclude={"created_at", "updated_at", "created_by", "updated_by"}
        )

        assert "created_at" not in char_dict
        assert "updated_at" not in char_dict
        assert "name" in char_dict
        assert "title" in char_dict


class TestTraitModel:
    """Test Trait model features."""

    def test_trait_creation(self):
        """Test creating a trait."""
        trait = Trait(
            id=1,
            name="Strength",
            entry="18",
            section="Attributes",
        )

        assert trait.name == "Strength"
        assert trait.entry == "18"
        assert trait.section == "Attributes"

    def test_trait_with_empty_section(self):
        """Test trait with empty section."""
        trait = Trait(
            id=2,
            name="Brave",
            entry="Always courageous in battle",
            section="",  # Section is required but can be empty
        )

        assert trait.name == "Brave"
        assert trait.section == ""


class TestModelValidation:
    """Test model validation edge cases."""

    def test_entity_name_required(self):
        """Test that entity name is required."""
        with pytest.raises(ValueError) as exc_info:
            Entity(
                id=1,
                entity_id=100,
                # name is missing - this will raise a validation error
                created_at="2024-01-01T00:00:00.000000Z",
                created_by=1,
                updated_at="2024-01-01T00:00:00.000000Z",
                updated_by=1,
            )
        assert "name" in str(exc_info.value)

    def test_post_name_required(self):
        """Test that post name is required."""
        with pytest.raises(ValueError) as exc_info:
            Post(
                id=1,
                entity_id=100,
                # name is missing - this will raise a validation error
                entry="Content",
                created_at="2024-01-01T00:00:00.000000Z",
                created_by=1,
                updated_at="2024-01-01T00:00:00.000000Z",
                updated_by=1,
            )
        assert "name" in str(exc_info.value)

    def test_entity_invalid_tags_type(self):
        """Test that tags field validates type correctly."""
        # Tags must be a list, not a string
        with pytest.raises(ValueError):
            Entity(
                id=1,
                entity_id=100,
                name="Test",
                created_at="2024-01-01T00:00:00.000000Z",
                created_by=1,
                updated_at="2024-01-01T00:00:00.000000Z",
                updated_by=1,
                tags="1,2,3",  # Invalid - must be a list
            )

    def test_boolean_field_conversion(self):
        """Test boolean field conversion."""
        # Test various boolean representations
        char1 = Character(
            id=1,
            entity_id=100,
            name="Test",
            created_at="2024-01-01T00:00:00.000000Z",
            created_by=1,
            updated_at="2024-01-01T00:00:00.000000Z",
            updated_by=1,
            is_dead=1,  # Integer 1 should convert to True
        )
        assert char1.is_dead is True

        char2 = Character(
            id=2,
            entity_id=101,
            name="Test2",
            created_at="2024-01-01T00:00:00.000000Z",
            created_by=1,
            updated_at="2024-01-01T00:00:00.000000Z",
            updated_by=1,
            is_dead=0,  # Integer 0 should convert to False
        )
        assert char2.is_dead is False
