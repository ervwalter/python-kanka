"""Entity managers for Kanka API."""

import hashlib
import re
from pathlib import Path
from typing import TYPE_CHECKING, Any, List, TypeVar  # noqa: UP035

from .models.base import Entity, Post
from .models.common import EntityAsset, EntityImageInfo

if TYPE_CHECKING:
    from .client import KankaClient


T = TypeVar("T", bound=Entity)

# Pattern to identify SDK-managed asset names: name:12hexchars
_MANAGED_ASSET_RE = re.compile(r"^(.+):([0-9a-f]{12})$")


class EntityManager[T: Entity]:
    """Manages CRUD operations for a specific entity type."""

    def __init__(self, client: "KankaClient", endpoint: str, model: type[T]):
        """Initialize the entity manager.

        Args:
            client: The KankaClient instance
            endpoint: The API endpoint for this entity type (e.g., 'characters')
            model: The Pydantic model class for this entity type
        """
        self.client = client
        self.endpoint = endpoint
        self.model = model

    def get(self, id: int, related: bool = False) -> T:
        """Get a single entity by ID.

        Args:
            id: The entity ID
            related: Include related data (posts, attributes, etc.)

        Returns:
            The entity instance

        Raises:
            NotFoundError: If entity doesn't exist
            AuthenticationError: If authentication fails
            ForbiddenError: If access is forbidden
        """
        params: dict[str, int | str] = {"related": 1} if related else {}
        url = f"{self.endpoint}/{id}"

        response = self.client._request("GET", url, params=params)
        return self.model(**response["data"])

    @property
    def pagination_meta(self) -> dict[str, Any]:
        """Get pagination metadata from the last list() call.

        Returns:
            Dictionary containing pagination info like total, per_page, current_page, etc.
        """
        return getattr(self, "_last_meta", {})

    @property
    def pagination_links(self) -> dict[str, str | None]:
        """Get pagination links from the last list() call.

        Returns:
            Dictionary containing pagination URLs: first, last, prev, next
        """
        return getattr(self, "_last_links", {})

    @property
    def has_next_page(self) -> bool:
        """Check if there's a next page available."""
        return bool(self.pagination_links.get("next"))

    def list(
        self, page: int = 1, limit: int = 30, related: bool = False, **filters
    ) -> list[T]:
        """List entities with optional filters.

        Args:
            page: Page number (default: 1)
            limit: Number of results per page (default: 30)
            related: Include related data (posts, attributes, etc.)
            **filters: Additional filters supported by the API

        Supported filters:
            name (str): Filter by name (partial match)
            tags (list[int]): Filter by tag IDs, e.g., tags=[1, 2, 3]
            type (str): Filter by entity type
            is_private (bool): Filter by privacy status
            created_at (str): Filter by creation date (ISO format)
            updated_at (str): Filter by update date (ISO format)
            created_by (int): Filter by creator user ID
            updated_by (int): Filter by last updater user ID

        Returns:
            List of entity instances

        Note:
            Pagination information is available after calling list():
            - manager.pagination_meta: Contains total count, current page, etc.
            - manager.pagination_links: Contains URLs for first, last, prev, next
            - manager.has_next_page: True if more pages are available

        Examples:
            # Get all public characters
            characters = client.characters.list(is_private=False)

            # Get entities with specific tags
            tagged = client.locations.list(tags=[1, 5, 10])

            # Filter by name
            dragons = client.creatures.list(name="dragon")

            # Get characters with posts included
            chars_with_posts = client.characters.list(related=True)

            # Handle pagination manually
            page = 1
            all_characters = []
            while True:
                chars = client.characters.list(page=page)
                all_characters.extend(chars)
                if not client.characters.has_next_page:
                    break
                page += 1

            # Check pagination info
            chars = client.characters.list(page=1)
            print(f"Total characters: {client.characters.pagination_meta['total']}")
            print(f"Current page: {client.characters.pagination_meta['current_page']}")
            print(f"Last page: {client.characters.pagination_meta['last_page']}")

            # Combine filters
            results = client.characters.list(
                name="John",
                tags=[1, 2],
                is_private=False,
                related=True,
                page=2
            )
        """
        # Build parameters
        params: dict[str, int | str] = {"page": page, "limit": limit}

        # Add related parameter if requested
        if related:
            params["related"] = 1

        # Add filters
        for key, value in filters.items():
            if value is not None:
                # Handle special cases
                if key == "tags" and isinstance(value, list):
                    # Tags should be comma-separated IDs
                    params["tags"] = ",".join(map(str, value))
                elif key == "types" and isinstance(value, list):
                    # Entity types should be comma-separated
                    params["types"] = ",".join(value)
                elif isinstance(value, bool):
                    # Convert booleans to 0/1
                    params[key] = int(value)
                elif isinstance(value, list | tuple):
                    # For any other list parameters, join with comma
                    params[key] = ",".join(map(str, value))
                else:
                    params[key] = value

        response = self.client._request("GET", self.endpoint, params=params)

        # Store pagination metadata on the manager for access if needed
        self._last_meta = response.get("meta", {})
        self._last_links = response.get("links", {})

        return [self.model(**item) for item in response["data"]]

    def create(
        self,
        *,
        images: dict[str, str | Path] | None = None,
        **kwargs,
    ) -> T:
        """Create a new entity.

        Args:
            images: Optional dict mapping placeholder src values in entry HTML
                to local file paths. The files will be uploaded as entity assets
                and the img src tags rewritten to CDN URLs.
            **kwargs: Entity fields

        Returns:
            The created entity

        Raises:
            ValidationError: If the data is invalid
        """
        # Don't validate with full model since we don't have ID fields yet
        # Just prepare the data for the API
        data = kwargs.copy()

        # Remove any fields that shouldn't be sent in creation
        for field in [
            "id",
            "entity_id",
            "created_at",
            "created_by",
            "updated_at",
            "updated_by",
        ]:
            data.pop(field, None)

        response = self.client._request("POST", self.endpoint, json=data)
        entity = self.model(**response["data"])

        if images:
            updated_entry = self._process_images_for_create(
                entity.entity_id, entity.entry, images
            )
            if updated_entry and updated_entry != entity.entry:
                url = f"{self.endpoint}/{entity.id}"
                response = self.client._request(
                    "PATCH", url, json={"entry": updated_entry}
                )
                entity = self.model(**response["data"])

        return entity

    def update(
        self,
        entity_or_id: T | int,
        *,
        images: dict[str, str | Path] | None = None,
        **kwargs,
    ) -> T:
        """Update an entity with partial data.

        Args:
            entity_or_id: The entity to update or its ID
            images: Optional dict mapping placeholder src values in entry HTML
                to local file paths. Changed images are re-uploaded, unchanged
                ones are reused, and orphaned managed assets are cleaned up.
            **kwargs: Fields to update

        Returns:
            The updated entity

        Raises:
            NotFoundError: If entity doesn't exist
            ValidationError: If the data is invalid
        """
        # Determine if we got an entity or just an ID
        if isinstance(entity_or_id, int):
            # Direct update by ID
            entity_id = entity_or_id
            # Just use the kwargs directly - don't try to validate with full model
            data = kwargs
        else:
            # Entity object provided
            entity = entity_or_id
            entity_id = entity.id

            # Create a copy with updates
            updates = entity.model_copy(update=kwargs)

            # Get only the changed fields
            data = updates.model_dump(
                exclude_unset=True,
                exclude={
                    "id",
                    "entity_id",
                    "created_at",
                    "created_by",
                    "updated_at",
                    "updated_by",
                },
            )

            # Only include fields that actually changed
            original_data = entity.model_dump(
                exclude={
                    "id",
                    "entity_id",
                    "created_at",
                    "created_by",
                    "updated_at",
                    "updated_by",
                }
            )
            data = {
                k: v
                for k, v in data.items()
                if k not in original_data or original_data[k] != v
            }

        # Handle images param
        if images:
            # Get entity_id for assets API
            if isinstance(entity_or_id, int):
                eid = self._extract_entity_id(self.get(entity_or_id))
            else:
                eid = entity_or_id.entity_id

            # Get entry from kwargs, entity object, or fetch
            entry = data.get("entry")
            if entry is None and not isinstance(entity_or_id, int):
                entry = entity_or_id.entry
            if entry is None:
                fetched = self.get(entity_id)
                entry = fetched.entry

            updated_entry = self._process_images_for_update(eid, entry, images)
            if updated_entry is not None:
                data["entry"] = updated_entry

        if not data:
            # No changes
            if isinstance(entity_or_id, int):
                # If we only had an ID, fetch and return the entity
                return self.get(entity_id)
            else:
                # Return original entity
                return entity_or_id

        url = f"{self.endpoint}/{entity_id}"
        response = self.client._request("PATCH", url, json=data)
        return self.model(**response["data"])

    def delete(self, entity_or_id: T | int) -> bool:
        """Delete an entity.

        Args:
            entity_or_id: The entity to delete or its ID

        Returns:
            True if successful

        Raises:
            NotFoundError: If entity doesn't exist
        """
        # Determine if we got an entity or just an ID
        entity_id = entity_or_id if isinstance(entity_or_id, int) else entity_or_id.id

        url = f"{self.endpoint}/{entity_id}"
        self.client._request("DELETE", url)
        return True

    @property
    def last_page_meta(self) -> dict[str, Any]:
        """Get metadata from the last list() call.

        Returns:
            Dict[str, Any]: Pagination metadata including:
                - current_page: Current page number
                - from: Starting record number
                - to: Ending record number
                - last_page: Total number of pages
                - per_page: Records per page
                - total: Total number of records
        """
        return getattr(self, "_last_meta", {})

    @property
    def last_page_links(self) -> dict[str, Any]:
        """Get pagination links from the last list() call.

        Returns:
            Dict[str, Any]: Pagination links including:
                - first: URL to first page
                - last: URL to last page
                - prev: URL to previous page (if applicable)
                - next: URL to next page (if applicable)
        """
        return getattr(self, "_last_links", {})

    def _extract_entity_id(self, entity_or_id: T | int) -> int:
        """Extract entity_id from an entity object or integer.

        Args:
            entity_or_id: An entity object (uses entity_id) or an integer entity_id

        Returns:
            The entity_id as an integer
        """
        if isinstance(entity_or_id, int):
            return entity_or_id
        return entity_or_id.entity_id

    @staticmethod
    def _compute_file_hash(file_path: str | Path) -> str:
        """Compute SHA-256 hash of a file, returning first 12 hex chars."""
        h = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()[:12]

    @staticmethod
    def _format_managed_asset_name(name: str, hash_prefix: str) -> str:
        """Build a managed asset name: truncated_name:hash12.

        Total max length is 45 chars (45 - 1 colon - 12 hash = 32 for name).
        """
        max_name_len = 32
        truncated = name[:max_name_len]
        return f"{truncated}:{hash_prefix}"

    @staticmethod
    def _parse_managed_asset_name(asset_name: str) -> tuple[str, str] | None:
        """Parse a managed asset name back to (name, hash).

        Returns None if the name doesn't match the managed pattern.
        """
        m = _MANAGED_ASSET_RE.match(asset_name)
        if m:
            return m.group(1), m.group(2)
        return None

    @staticmethod
    def _rewrite_image_srcs(html: str, url_map: dict[str, str]) -> str:
        """Rewrite <img src="key"> tags, replacing keys with CDN URLs."""
        for placeholder, cdn_url in url_map.items():
            escaped = re.escape(placeholder)
            html = re.sub(
                rf'src=(["\']){escaped}\1',
                f"src=\\1{cdn_url}\\1",
                html,
            )
        return html

    def _process_images_for_create(
        self,
        entity_id: int,
        entry: str | None,
        images: dict[str, str | Path],
    ) -> str | None:
        """Upload images as assets and rewrite entry HTML. Returns updated entry."""
        if not images or not entry:
            return entry

        url_map: dict[str, str] = {}
        for placeholder, file_path in images.items():
            file_path = Path(file_path)
            file_hash = self._compute_file_hash(file_path)
            managed_name = self._format_managed_asset_name(placeholder, file_hash)
            asset = self.create_file_asset(entity_id, file_path, name=managed_name)
            if asset.url:
                url_map[placeholder] = asset.url

        if url_map:
            return self._rewrite_image_srcs(entry, url_map)
        return entry

    def _process_images_for_update(
        self,
        entity_id: int,
        entry: str | None,
        images: dict[str, str | Path],
    ) -> str | None:
        """Handle image assets for update: reuse unchanged, replace changed, cleanup orphans."""
        if not images or not entry:
            return entry

        # Get existing managed assets
        existing_assets = self.list_assets(entity_id)
        managed: dict[str, tuple[str, EntityAsset]] = {}
        for asset in existing_assets:
            parsed = self._parse_managed_asset_name(asset.name)
            if parsed:
                name_part, hash_part = parsed
                managed[name_part] = (hash_part, asset)

        url_map: dict[str, str] = {}
        used_names: set[str] = set()

        for placeholder, file_path in images.items():
            file_path = Path(file_path)
            file_hash = self._compute_file_hash(file_path)
            used_names.add(placeholder)

            if placeholder in managed:
                old_hash, old_asset = managed[placeholder]
                if old_hash == file_hash:
                    # Same file, reuse URL
                    if old_asset.url:
                        url_map[placeholder] = old_asset.url
                    continue
                else:
                    # Changed file, delete old and upload new
                    self.delete_asset(entity_id, old_asset.id)

            managed_name = self._format_managed_asset_name(placeholder, file_hash)
            asset = self.create_file_asset(entity_id, file_path, name=managed_name)
            if asset.url:
                url_map[placeholder] = asset.url

        # Orphan cleanup: delete managed assets not in current images dict
        for name_part, (_, old_asset) in managed.items():
            if name_part not in used_names:
                self.delete_asset(entity_id, old_asset.id)

        if url_map:
            return self._rewrite_image_srcs(entry, url_map)
        return entry

    # Posts functionality
    def list_posts(
        self, entity_or_id: T | int, page: int = 1, limit: int = 30
    ) -> List[Post]:  # noqa: UP006
        """List posts for an entity.

        Args:
            entity_or_id: The entity or its entity_id
            page: Page number (default: 1)
            limit: Number of results per page (default: 30)

        Returns:
            List of Post instances

        Example:
            posts = client.characters.list_posts(character_entity)
            posts = client.locations.list_posts(location_entity_id)
        """
        entity_id = self._extract_entity_id(entity_or_id)

        params: dict[str, int | str] = {"page": page, "limit": limit}

        url = f"entities/{entity_id}/posts"
        response = self.client._request("GET", url, params=params)

        # Store pagination metadata
        self._last_posts_meta = response.get("meta", {})
        self._last_posts_links = response.get("links", {})

        return [Post(**item) for item in response["data"]]

    def create_post(
        self,
        entity_or_id: T | int,
        name: str,
        entry: str,
        *,
        images: dict[str, str | Path] | None = None,
        visibility_id: int | None = None,
        **kwargs,
    ) -> Post:
        """Create a post for an entity.

        IMPORTANT: Posts use the entity_id, not the type-specific ID!
        - If passing an entity object: Uses entity.entity_id automatically
        - If passing an integer: Must be the entity_id, NOT the character/location/etc ID

        Args:
            entity_or_id: The entity object OR its entity_id (NOT the type-specific ID!)
            name: Post name/title
            entry: Post content (supports HTML)
            images: Optional dict mapping placeholder src values in entry HTML
                to local file paths. Files are uploaded as entity assets and
                img src tags are rewritten to CDN URLs.
            visibility_id: Control who can see the post (1=all, 2=admin, 3=admin-self, 4=self, 5=members)
                          None defaults to campaign's default post visibility
            **kwargs: Additional post fields

        Returns:
            The created Post instance

        Example:
            # Preferred: Pass the full entity object
            character = client.characters.get(123)
            post = client.characters.create_post(
                character,  # Pass the full object
                name="Session Notes",
                entry="The character discovered a hidden treasure...",
                visibility_id=2  # Admin-only visibility
            )

            # Public post (visible to all)
            post = client.characters.create_post(
                character,
                name="Public Notice",
                entry="This information is public knowledge.",
                visibility_id=1
            )
        """
        entity_id = self._extract_entity_id(entity_or_id)

        if images:
            updated_entry = self._process_images_for_create(entity_id, entry, images)
            if updated_entry is not None:
                entry = updated_entry

        data: dict[str, Any] = {"name": name, "entry": entry, **kwargs}
        if visibility_id is not None:
            data["visibility_id"] = visibility_id

        url = f"entities/{entity_id}/posts"
        response = self.client._request("POST", url, json=data)
        return Post(**response["data"])

    def get_post(self, entity_or_id: T | int, post_id: int) -> Post:
        """Get a specific post for an entity.

        Args:
            entity_or_id: The entity or its entity_id
            post_id: The post ID

        Returns:
            The Post instance
        """
        entity_id = self._extract_entity_id(entity_or_id)

        url = f"entities/{entity_id}/posts/{post_id}"
        response = self.client._request("GET", url)
        return Post(**response["data"])

    def update_post(
        self,
        entity_or_id: T | int,
        post_id: int,
        *,
        images: dict[str, str | Path] | None = None,
        visibility_id: int | None = None,
        **kwargs,
    ) -> Post:
        """Update a post for an entity.

        IMPORTANT: Posts use the entity_id, not the type-specific ID!
        NOTE: The Kanka API requires the 'name' field even when not changing it.

        Args:
            entity_or_id: The entity object OR its entity_id (NOT the type-specific ID!)
            post_id: The post ID
            images: Optional dict mapping placeholder src values in entry HTML
                to local file paths. Changed images are re-uploaded, unchanged
                ones are reused, and orphaned managed assets are cleaned up.
            visibility_id: Update post visibility (1=all, 2=admin, 3=admin-self, 4=self, 5=members)
                          None keeps existing visibility
            **kwargs: Fields to update (must include 'name' even if unchanged)

        Returns:
            The updated Post instance

        Example:
            # Update post to admin-only visibility
            updated = client.characters.update_post(
                character,  # or character.entity_id
                post_id,
                name="Post Title",  # Required even if not changing!
                visibility_id=2  # Admin-only
                entry="New content..."
            )
        """
        entity_id = self._extract_entity_id(entity_or_id)

        if images:
            entry = kwargs.get("entry")
            if entry is None:
                post = self.get_post(entity_or_id, post_id)
                entry = post.entry
            updated_entry = self._process_images_for_update(entity_id, entry, images)
            if updated_entry is not None:
                kwargs["entry"] = updated_entry

        # Add visibility_id to kwargs if provided
        if visibility_id is not None:
            kwargs["visibility_id"] = visibility_id

        url = f"entities/{entity_id}/posts/{post_id}"
        response = self.client._request("PATCH", url, json=kwargs)
        return Post(**response["data"])

    def delete_post(self, entity_or_id: T | int, post_id: int) -> bool:
        """Delete a post for an entity.

        Args:
            entity_or_id: The entity or its entity_id
            post_id: The post ID

        Returns:
            True if successful
        """
        entity_id = self._extract_entity_id(entity_or_id)

        url = f"entities/{entity_id}/posts/{post_id}"
        self.client._request("DELETE", url)
        return True

    @property
    def last_posts_meta(self) -> dict[str, Any]:
        """Get metadata from the last list_posts() call.

        Returns:
            Dict[str, Any]: Pagination metadata for posts including:
                - current_page: Current page number
                - from: Starting record number
                - to: Ending record number
                - last_page: Total number of pages
                - per_page: Records per page
                - total: Total number of posts
        """
        return getattr(self, "_last_posts_meta", {})

    @property
    def last_posts_links(self) -> dict[str, Any]:
        """Get pagination links from the last list_posts() call.

        Returns:
            Dict[str, Any]: Pagination links for posts including:
                - first: URL to first page
                - last: URL to last page
                - prev: URL to previous page (if applicable)
                - next: URL to next page (if applicable)
        """
        return getattr(self, "_last_posts_links", {})

    # Entity Assets functionality

    def list_assets(
        self, entity_or_id: T | int, page: int = 1, limit: int = 30
    ) -> List[EntityAsset]:  # noqa: UP006
        """List assets for an entity.

        Args:
            entity_or_id: The entity or its entity_id
            page: Page number (default: 1)
            limit: Number of results per page (default: 30)

        Returns:
            List of EntityAsset instances
        """
        entity_id = self._extract_entity_id(entity_or_id)
        params: dict[str, int | str] = {"page": page, "limit": limit}
        url = f"entities/{entity_id}/entity_assets"
        response = self.client._request("GET", url, params=params)
        self._last_assets_meta = response.get("meta", {})
        self._last_assets_links = response.get("links", {})
        return [EntityAsset(**item) for item in response["data"]]

    def get_asset(self, entity_or_id: T | int, asset_id: int) -> EntityAsset:
        """Get a specific asset for an entity.

        Args:
            entity_or_id: The entity or its entity_id
            asset_id: The asset ID

        Returns:
            EntityAsset instance
        """
        entity_id = self._extract_entity_id(entity_or_id)
        url = f"entities/{entity_id}/entity_assets/{asset_id}"
        response = self.client._request("GET", url)
        return EntityAsset(**response["data"])

    def create_file_asset(
        self,
        entity_or_id: T | int,
        file_path: str | Path,
        name: str | None = None,
        visibility_id: int | None = None,
        is_pinned: bool = False,
    ) -> EntityAsset:
        """Upload a file asset to an entity.

        Args:
            entity_or_id: The entity or its entity_id
            file_path: Path to the file to upload
            name: Asset name (defaults to filename)
            visibility_id: Visibility setting
            is_pinned: Whether to pin the asset

        Returns:
            The created EntityAsset instance
        """
        entity_id = self._extract_entity_id(entity_or_id)
        file_path = Path(file_path)

        data: dict[str, Any] = {
            "type_id": 1,
            "name": name or file_path.stem,
        }
        if visibility_id is not None:
            data["visibility_id"] = visibility_id
        data["is_pinned"] = 1 if is_pinned else 0

        url = f"entities/{entity_id}/entity_assets"
        with open(file_path, "rb") as f:
            files = {"file": (file_path.name, f)}
            response = self.client._upload_request("POST", url, files=files, data=data)

        return EntityAsset(**response["data"])

    def create_link_asset(
        self,
        entity_or_id: T | int,
        name: str,
        url: str,
        icon: str | None = None,
        visibility_id: int | None = None,
    ) -> EntityAsset:
        """Create a link asset on an entity.

        Args:
            entity_or_id: The entity or its entity_id
            name: Asset name
            url: The URL to link to
            icon: Optional icon class (e.g., 'fa-link')
            visibility_id: Visibility setting

        Returns:
            The created EntityAsset instance
        """
        entity_id = self._extract_entity_id(entity_or_id)

        metadata: dict[str, str] = {"url": url}
        if icon is not None:
            metadata["icon"] = icon

        data: dict[str, Any] = {
            "type_id": 2,
            "name": name,
            "metadata": metadata,
        }
        if visibility_id is not None:
            data["visibility_id"] = visibility_id

        endpoint = f"entities/{entity_id}/entity_assets"
        response = self.client._request("POST", endpoint, json=data)
        return EntityAsset(**response["data"])

    def create_alias_asset(
        self,
        entity_or_id: T | int,
        name: str,
        visibility_id: int | None = None,
    ) -> EntityAsset:
        """Create an alias asset on an entity.

        Args:
            entity_or_id: The entity or its entity_id
            name: The alias name
            visibility_id: Visibility setting

        Returns:
            The created EntityAsset instance
        """
        entity_id = self._extract_entity_id(entity_or_id)

        data: dict[str, Any] = {
            "type_id": 3,
            "name": name,
        }
        if visibility_id is not None:
            data["visibility_id"] = visibility_id

        endpoint = f"entities/{entity_id}/entity_assets"
        response = self.client._request("POST", endpoint, json=data)
        return EntityAsset(**response["data"])

    def delete_asset(self, entity_or_id: T | int, asset_id: int) -> bool:
        """Delete an asset from an entity.

        Args:
            entity_or_id: The entity or its entity_id
            asset_id: The asset ID

        Returns:
            True if successful
        """
        entity_id = self._extract_entity_id(entity_or_id)
        url = f"entities/{entity_id}/entity_assets/{asset_id}"
        self.client._request("DELETE", url)
        return True

    @property
    def last_assets_meta(self) -> dict[str, Any]:
        """Get metadata from the last list_assets() call."""
        return getattr(self, "_last_assets_meta", {})

    @property
    def last_assets_links(self) -> dict[str, Any]:
        """Get pagination links from the last list_assets() call."""
        return getattr(self, "_last_assets_links", {})

    # Entity Image functionality

    def get_image(self, entity_or_id: T | int) -> EntityImageInfo:
        """Get image information for an entity.

        Args:
            entity_or_id: The entity or its entity_id

        Returns:
            EntityImageInfo with image and header data
        """
        entity_id = self._extract_entity_id(entity_or_id)
        url = f"entities/{entity_id}/image"
        response = self.client._request("GET", url)
        return EntityImageInfo(**response["data"])

    def set_image(
        self,
        entity_or_id: T | int,
        file_path: str | Path,
        is_header: bool = False,
    ) -> EntityImageInfo:
        """Set the main image or header image for an entity.

        Args:
            entity_or_id: The entity or its entity_id
            file_path: Path to the image file
            is_header: If True, set as header image instead of main image

        Returns:
            Updated EntityImageInfo
        """
        entity_id = self._extract_entity_id(entity_or_id)
        file_path = Path(file_path)

        data: dict[str, Any] = {}
        if is_header:
            data["is_header"] = 1

        url = f"entities/{entity_id}/image"
        with open(file_path, "rb") as f:
            files = {"file": (file_path.name, f)}
            response = self.client._upload_request("POST", url, files=files, data=data)

        return EntityImageInfo(**response["data"])

    def delete_image(self, entity_or_id: T | int, is_header: bool = False) -> bool:
        """Delete the main image or header image for an entity.

        Args:
            entity_or_id: The entity or its entity_id
            is_header: If True, delete header image instead of main image

        Returns:
            True if successful
        """
        entity_id = self._extract_entity_id(entity_or_id)
        url = f"entities/{entity_id}/image"
        params: dict[str, int | str] = {}
        if is_header:
            params["is_header"] = 1
        self.client._request("DELETE", url, params=params)
        return True
