"""
Common models used across the Kanka API.

This module contains models that are used across multiple entity types
or represent common data structures in the Kanka API.

Classes:
    SearchResult: Represents search result items from global search
    Profile: User profile information
    Trait: Entity traits/attributes
    GalleryImage: Campaign gallery image
    EntityAsset: Entity file/link/alias asset
    EntityImageData: Image URL data (uuid, full, thumbnail)
    EntityImageInfo: Entity image and header info
    EntityResponse: Single entity API response wrapper
    ListResponse: List API response wrapper with pagination
"""

from datetime import datetime
from typing import Any, TypeVar

from pydantic import Field

from .base import KankaModel  # Import Post from base module


class SearchResult(KankaModel):
    """Search result item from global search.

    Represents a single result from the global search endpoint,
    providing basic information about matching entities.

    Attributes:
        id: Entity-specific ID
        entity_id: Universal entity ID
        name: Entity name
        type: Entity type (e.g., 'character', 'location')
        url: API URL for this entity
        image: Entity image URL (if available)
        is_private: Whether entity is private
        tooltip: Preview tooltip text
        tags: List of tag IDs
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    id: int
    entity_id: int
    name: str
    type: str | None = None
    url: str
    image: str | None = None
    is_private: bool = False
    tooltip: str | None = None
    tags: list[int] = []
    created_at: datetime | None = None
    updated_at: datetime | None = None


class Profile(KankaModel):
    """User profile information.

    Contains information about a Kanka user account.

    Attributes:
        id: User ID
        name: Username
        avatar: Avatar image URL
        avatar_thumb: Thumbnail avatar URL
        locale: User's locale setting
        timezone: User's timezone
        date_format: Preferred date format
        default_pagination: Default items per page
        theme: UI theme preference
        is_patreon: Whether user is a Patreon supporter
        last_campaign_id: ID of last accessed campaign
    """

    id: int
    name: str
    avatar: str | None = None
    avatar_thumb: str | None = None
    locale: str | None = None
    timezone: str | None = None
    date_format: str | None = None
    default_pagination: int | None = None
    theme: str | None = None
    is_patreon: bool | None = None
    last_campaign_id: int | None = None


class Trait(KankaModel):
    """Trait/attribute for entities.

    Traits are custom fields that can be added to entities to store
    additional structured information.

    Attributes:
        id: Trait ID (optional for creation)
        name: Trait name/label
        entry: Trait value/content
        section: Section grouping for organization
        is_private: Whether trait is private
        default_order: Display order (0-based)
    """

    id: int | None = None
    name: str
    entry: str
    section: str
    is_private: bool = False
    default_order: int = 0


class GalleryImage(KankaModel):
    """Campaign gallery image.

    Attributes:
        id: UUID identifier
        name: Image name
        is_folder: Whether this is a folder
        folder_id: Parent folder UUID
        path: Thumbnail URL
        ext: File extension
        size: File size in bytes
        created_at: Creation timestamp
        created_by: User ID who uploaded
        updated_at: Last update timestamp
        visibility_id: Visibility setting
        focus_x: Image focus X coordinate
        focus_y: Image focus Y coordinate
    """

    id: str
    name: str | None = None
    is_folder: bool = False
    folder_id: str | None = None
    path: str | None = None
    ext: str | None = None
    size: int | None = None
    created_at: datetime | None = None
    created_by: int | None = None
    updated_at: datetime | None = None
    visibility_id: int | None = None
    focus_x: int | None = None
    focus_y: int | None = None


class EntityAsset(KankaModel):
    """Entity file, link, or alias asset.

    Attributes:
        id: Asset ID
        entity_id: Parent entity ID
        name: Asset name
        type_id: Asset type (1=file, 2=link, 3=alias)
        visibility_id: Visibility setting
        is_pinned: Whether asset is pinned
        is_private: Whether asset is private
        metadata: Additional metadata
        created_at: Creation timestamp
        created_by: User ID who created
        updated_at: Last update timestamp
        updated_by: User ID who last updated
        url: CDN URL for file assets (aliased from _url)
    """

    id: int
    entity_id: int
    name: str
    type_id: int
    visibility_id: int | None = None
    is_pinned: bool = False
    is_private: bool = False
    metadata: dict[str, Any] | None = None
    created_at: datetime | None = None
    created_by: int | None = None
    updated_at: datetime | None = None
    updated_by: int | None = None
    url: str | None = Field(default=None, alias="_url")


class EntityImageData(KankaModel):
    """Image URL data for an entity.

    Attributes:
        uuid: Image UUID in gallery
        full: Full-size image URL
        thumbnail: Thumbnail image URL
    """

    uuid: str | None = None
    full: str | None = None
    thumbnail: str | None = None


class EntityImageInfo(KankaModel):
    """Entity image and header information.

    Attributes:
        image: Main entity image data
        header: Entity header image data
    """

    image: EntityImageData | None = None
    header: EntityImageData | None = None


# Type variable for generic responses
T = TypeVar("T", bound=KankaModel)


class EntityResponse[T: KankaModel](KankaModel):
    """Single entity API response wrapper.

    Generic wrapper for API responses containing a single entity.

    Type Parameters:
        T: The entity type contained in the response

    Attributes:
        data: The entity instance
    """

    data: T


class ListResponse[T: KankaModel](KankaModel):
    """List API response wrapper with pagination.

    Generic wrapper for API responses containing multiple entities
    with pagination metadata.

    Type Parameters:
        T: The entity type contained in the response

    Attributes:
        data: List of entity instances
        links: Pagination links (first, last, prev, next)
        meta: Pagination metadata (current_page, total, etc.)
    """

    data: list[T]
    links: dict[str, Any]
    meta: dict[str, Any]
