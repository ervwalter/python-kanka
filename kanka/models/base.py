"""
Base Pydantic models for Kanka API.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime


class KankaModel(BaseModel):
    """Base for all Kanka models with common config."""
    model_config = ConfigDict(
        extra='allow',  # Store unknown fields
        validate_assignment=True,
        use_enum_values=True,
        populate_by_name=True  # Allow both field names and aliases
    )


class Entity(KankaModel):
    """Base for all entities from API."""
    id: int
    entity_id: int
    name: str
    image: Optional[str] = None
    image_full: Optional[str] = None
    image_thumb: Optional[str] = None
    is_private: bool = False
    tags: List[int] = Field(default_factory=list)
    created_at: datetime
    created_by: int
    updated_at: datetime
    updated_by: int
    entry: Optional[str] = None
    
    # For MCP: easy access to entity type
    @property
    def entity_type(self) -> str:
        """Return the entity type name."""
        return self.__class__.__name__.lower()