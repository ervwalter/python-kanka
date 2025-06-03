"""
Common models used across the Kanka API.
"""

from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, TypeVar

from .base import KankaModel


class Post(KankaModel):
    """Post/comment on entities."""

    id: int
    name: str
    entry: str
    entity_id: int
    created_by: int
    updated_by: int
    created_at: datetime
    updated_at: datetime
    is_private: bool = False


class SearchResult(KankaModel):
    """Search result item."""

    id: int
    entity_id: int
    name: str
    type: str
    url: str
    image: Optional[str] = None
    is_private: bool = False
    tooltip: Optional[str] = None
    tags: List[int] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class Profile(KankaModel):
    """User profile."""

    id: int
    name: str
    avatar: Optional[str] = None
    avatar_thumb: Optional[str] = None
    locale: Optional[str] = None
    timezone: Optional[str] = None
    date_format: Optional[str] = None
    default_pagination: Optional[int] = None
    theme: Optional[str] = None
    is_patreon: Optional[bool] = None
    last_campaign_id: Optional[int] = None


class Trait(KankaModel):
    """Trait for entities."""

    id: Optional[int] = None
    name: str
    entry: str
    section: str
    is_private: bool = False
    default_order: int = 0


# Type variable for generic responses
T = TypeVar("T", bound=KankaModel)


class EntityResponse(KankaModel, Generic[T]):
    """Single entity API response wrapper."""

    data: T


class ListResponse(KankaModel, Generic[T]):
    """List API response wrapper with pagination."""

    data: List[T]
    links: Dict[str, Any]
    meta: Dict[str, Any]
