"""Entity managers for Kanka API."""

from typing import TYPE_CHECKING, Any, Dict, Generic, List, Type, TypeVar, Union

from .models.base import Entity
from .models.common import Post

if TYPE_CHECKING:
    from .client import KankaClient


T = TypeVar("T", bound=Entity)


class EntityManager(Generic[T]):
    """Manages CRUD operations for a specific entity type."""

    def __init__(self, client: "KankaClient", endpoint: str, model: Type[T]):
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
        params = {"related": 1} if related else {}
        url = f"{self.endpoint}/{id}"

        response = self.client._request("GET", url, params=params)
        return self.model(**response["data"])

    def list(self, page: int = 1, limit: int = 30, **filters) -> List[T]:
        """List entities with optional filters.

        Args:
            page: Page number (default: 1)
            limit: Number of results per page (default: 30)
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

        Examples:
            # Get all public characters
            characters = client.characters.list(is_private=False)

            # Get entities with specific tags
            tagged = client.locations.list(tags=[1, 5, 10])

            # Filter by name
            dragons = client.creatures.list(name="dragon")

            # Combine filters
            results = client.characters.list(
                name="John",
                tags=[1, 2],
                is_private=False,
                page=2
            )
        """
        # Build parameters
        params = {"page": page, "limit": limit}

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
                elif isinstance(value, (list, tuple)):
                    # For any other list parameters, join with comma
                    params[key] = ",".join(map(str, value))
                else:
                    params[key] = value

        response = self.client._request("GET", self.endpoint, params=params)

        # Store pagination metadata on the manager for access if needed
        self._last_meta = response.get("meta", {})
        self._last_links = response.get("links", {})

        return [self.model(**item) for item in response["data"]]

    def create(self, **kwargs) -> T:
        """Create a new entity.

        Args:
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
        return self.model(**response["data"])

    def update(self, entity_or_id: Union[T, int], **kwargs) -> T:
        """Update an entity with partial data.

        Args:
            entity_or_id: The entity to update or its ID
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

    def delete(self, entity_or_id: Union[T, int]) -> bool:
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
    def last_page_meta(self) -> Dict[str, Any]:
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
    def last_page_links(self) -> Dict[str, Any]:
        """Get pagination links from the last list() call.
        
        Returns:
            Dict[str, Any]: Pagination links including:
                - first: URL to first page
                - last: URL to last page  
                - prev: URL to previous page (if applicable)
                - next: URL to next page (if applicable)
        """
        return getattr(self, "_last_links", {})

    # Posts functionality
    def list_posts(
        self, entity_or_id: Union[T, int], page: int = 1, limit: int = 30
    ) -> List[Post]:
        """List posts for an entity.

        Args:
            entity_or_id: The entity or its ID
            page: Page number (default: 1)
            limit: Number of results per page (default: 30)

        Returns:
            List of Post instances

        Example:
            posts = client.characters.list_posts(character_id)
            posts = client.locations.list_posts(location_entity)
        """
        entity_id = entity_or_id.id if hasattr(entity_or_id, "id") else entity_or_id

        params = {"page": page, "limit": limit}

        url = f"{self.endpoint}/{entity_id}/posts"
        response = self.client._request("GET", url, params=params)

        # Store pagination metadata
        self._last_posts_meta = response.get("meta", {})
        self._last_posts_links = response.get("links", {})

        return [Post(**item) for item in response["data"]]

    def create_post(
        self,
        entity_or_id: Union[T, int],
        name: str,
        entry: str,
        is_private: bool = False,
        **kwargs,
    ) -> Post:
        """Create a post for an entity.

        Args:
            entity_or_id: The entity or its ID
            name: Post name/title
            entry: Post content (supports HTML)
            is_private: Whether the post is private (default: False)
            **kwargs: Additional post fields

        Returns:
            The created Post instance

        Example:
            post = client.characters.create_post(
                character_id,
                name="Session Notes",
                entry="The character discovered a hidden treasure...",
                is_private=True
            )
        """
        entity_id = entity_or_id.id if hasattr(entity_or_id, "id") else entity_or_id

        data = {"name": name, "entry": entry, "is_private": int(is_private), **kwargs}

        url = f"{self.endpoint}/{entity_id}/posts"
        response = self.client._request("POST", url, json=data)
        return Post(**response["data"])

    def get_post(self, entity_or_id: Union[T, int], post_id: int) -> Post:
        """Get a specific post for an entity.

        Args:
            entity_or_id: The entity or its ID
            post_id: The post ID

        Returns:
            The Post instance
        """
        entity_id = entity_or_id.id if hasattr(entity_or_id, "id") else entity_or_id

        url = f"{self.endpoint}/{entity_id}/posts/{post_id}"
        response = self.client._request("GET", url)
        return Post(**response["data"])

    def update_post(self, entity_or_id: Union[T, int], post_id: int, **kwargs) -> Post:
        """Update a post for an entity.

        Args:
            entity_or_id: The entity or its ID
            post_id: The post ID
            **kwargs: Fields to update (name, entry, is_private, etc.)

        Returns:
            The updated Post instance

        Example:
            updated = client.characters.update_post(
                character_id,
                post_id,
                name="Updated Title",
                entry="New content..."
            )
        """
        entity_id = entity_or_id.id if hasattr(entity_or_id, "id") else entity_or_id

        # Convert boolean is_private to int if present
        if "is_private" in kwargs and isinstance(kwargs["is_private"], bool):
            kwargs["is_private"] = int(kwargs["is_private"])

        url = f"{self.endpoint}/{entity_id}/posts/{post_id}"
        response = self.client._request("PATCH", url, json=kwargs)
        return Post(**response["data"])

    def delete_post(self, entity_or_id: Union[T, int], post_id: int) -> bool:
        """Delete a post for an entity.

        Args:
            entity_or_id: The entity or its ID
            post_id: The post ID

        Returns:
            True if successful
        """
        entity_id = entity_or_id.id if hasattr(entity_or_id, "id") else entity_or_id

        url = f"{self.endpoint}/{entity_id}/posts/{post_id}"
        self.client._request("DELETE", url)
        return True

    @property
    def last_posts_meta(self) -> Dict[str, Any]:
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
    def last_posts_links(self) -> Dict[str, Any]:
        """Get pagination links from the last list_posts() call.
        
        Returns:
            Dict[str, Any]: Pagination links for posts including:
                - first: URL to first page
                - last: URL to last page
                - prev: URL to previous page (if applicable)
                - next: URL to next page (if applicable)
        """
        return getattr(self, "_last_posts_links", {})
