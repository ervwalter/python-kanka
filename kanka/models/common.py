"""
Common models used across the Kanka API.
"""

from typing import Optional, List, TypeVar, Generic, Dict, Any
from datetime import datetime
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
    image: Optional[str] = None
    is_private: bool = False
    tooltip: Optional[str] = None
    url: str


class Trait(KankaModel):
    """Trait for entities."""
    id: Optional[int] = None
    name: str
    entry: str
    section: str
    is_private: bool = False
    default_order: int = 0


# Type variable for generic responses
T = TypeVar('T', bound=KankaModel)


class EntityResponse(KankaModel, Generic[T]):
    """Single entity API response wrapper."""
    data: T


class ListResponse(KankaModel, Generic[T]):
    """List API response wrapper with pagination."""
    data: List[T]
    links: Dict[str, Any]
    meta: Dict[str, Any]