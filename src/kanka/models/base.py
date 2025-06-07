"""
Base Pydantic models for Kanka API.

This module provides the foundational model classes that all Kanka entities
inherit from. It establishes common configuration and shared fields across
all entity types.

Classes:
    KankaModel: Base model with common Pydantic configuration
    Entity: Base entity model with standard fields all entities share
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class KankaModel(BaseModel):
    """Base for all Kanka models with common configuration.

    This base model provides consistent configuration for all Kanka API models,
    ensuring proper handling of unknown fields, validation, and field naming.

    Configuration:
        extra="allow": Store unknown fields from API responses
        validate_assignment=True: Validate field values on assignment
        use_enum_values=True: Use actual enum values instead of enum instances
        populate_by_name=True: Allow both field names and aliases
    """

    model_config = ConfigDict(
        extra="allow",  # Store unknown fields
        validate_assignment=True,
        use_enum_values=True,
        populate_by_name=True,  # Allow both field names and aliases
    )


class Entity(KankaModel):
    """Base model for all Kanka entities.

    This class defines the common fields shared by all entity types in Kanka.
    All specific entity types (Character, Location, etc.) inherit from this base.

    Attributes:
        id: Unique identifier for this specific entity type
        entity_id: Universal entity ID across all types
        name: Entity name
        image: URL to entity image
        image_full: URL to full-size entity image
        image_thumb: URL to thumbnail entity image
        is_private: Whether entity is private
        tags: List of tag IDs associated with entity
        created_at: Creation timestamp
        created_by: User ID who created entity
        updated_at: Last update timestamp
        updated_by: User ID who last updated entity
        entry: Main text/description content

    Properties:
        entity_type: Returns the lowercase entity type name
    """

    id: int
    entity_id: int
    name: str
    image: Optional[str] = None
    image_full: Optional[str] = None
    image_thumb: Optional[str] = None
    is_private: bool = False
    tags: list[int] = Field(default_factory=list)
    created_at: datetime
    created_by: int
    updated_at: datetime
    updated_by: Optional[int] = None
    entry: Optional[str] = None

    @property
    def entity_type(self) -> str:
        """Return the entity type name.

        Returns:
            str: Lowercase name of the entity class (e.g., 'character', 'location')

        Example:
            >>> char = Character(id=1, entity_id=100, name="Hero")
            >>> char.entity_type
            'character'
        """
        return self.__class__.__name__.lower()
