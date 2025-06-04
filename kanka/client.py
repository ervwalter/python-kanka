"""Main Kanka API client for interacting with the Kanka API.

This module provides the primary interface for working with Kanka's RESTful API.
It handles authentication, request management, and provides convenient access to
all entity types through manager objects.

Example:
    Basic usage of the KankaClient:

    >>> from kanka import KankaClient
    >>> client = KankaClient(token="your-api-token", campaign_id=12345)
    >>> characters = client.characters.list()
    >>> dragon = client.search("dragon")
"""

from typing import Any, Dict, List, Union

from .exceptions import (
    AuthenticationError,
    ForbiddenError,
    KankaException,
    NotFoundError,
    RateLimitError,
    ValidationError,
)
from .managers import EntityManager
from .models.common import SearchResult
from .models.entities import (
    Calendar,
    Character,
    Creature,
    Event,
    Family,
    Journal,
    Location,
    Note,
    Organisation,
    Quest,
    Race,
    Tag,
)


class KankaClient:
    """Main client for Kanka API interaction.

    This client provides a unified interface to access all Kanka entities
    within a specific campaign. It handles authentication, request management,
    and provides entity-specific managers for CRUD operations.

    Attributes:
        BASE_URL (str): The base URL for the Kanka API
        token (str): Authentication token for API access
        campaign_id (int): ID of the campaign to work with
        session: Configured requests.Session instance

    Entity Managers:
        calendars: Access to Calendar entities
        characters: Access to Character entities
        creatures: Access to Creature entities
        events: Access to Event entities
        families: Access to Family entities
        journals: Access to Journal entities
        locations: Access to Location entities
        notes: Access to Note entities
        organisations: Access to Organisation entities
        quests: Access to Quest entities
        races: Access to Race entities
        tags: Access to Tag entities

    Example:
        >>> client = KankaClient("your-token", 12345)
        >>> # List all characters
        >>> chars = client.characters.list()
        >>> # Get a specific location
        >>> loc = client.locations.get(123)
        >>> # Search across all entities
        >>> results = client.search("dragon")
    """

    BASE_URL = "https://api.kanka.io/1.0"

    def __init__(self, token: str, campaign_id: int):
        """Initialize the Kanka client.

        Args:
            token: API authentication token
            campaign_id: Campaign ID to work with
        """
        self.token = token
        self.campaign_id = campaign_id

        # Set up session with default headers
        # Import requests here to avoid import issues
        import requests

        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )

        # Initialize entity managers
        self._init_managers()

    def _init_managers(self):
        """Initialize entity managers for each entity type."""
        # Core entities
        self._calendars = EntityManager(self, "calendars", Calendar)
        self._characters = EntityManager(self, "characters", Character)
        self._creatures = EntityManager(self, "creatures", Creature)
        self._events = EntityManager(self, "events", Event)
        self._families = EntityManager(self, "families", Family)
        self._journals = EntityManager(self, "journals", Journal)
        self._locations = EntityManager(self, "locations", Location)
        self._notes = EntityManager(self, "notes", Note)
        self._organisations = EntityManager(self, "organisations", Organisation)
        self._quests = EntityManager(self, "quests", Quest)
        self._races = EntityManager(self, "races", Race)
        self._tags = EntityManager(self, "tags", Tag)

    @property
    def calendars(self) -> EntityManager[Calendar]:
        """Access calendar entities.

        Returns:
            EntityManager[Calendar]: Manager for Calendar entity operations
        """
        return self._calendars

    @property
    def characters(self) -> EntityManager[Character]:
        """Access character entities.

        Returns:
            EntityManager[Character]: Manager for Character entity operations
        """
        return self._characters

    @property
    def creatures(self) -> EntityManager[Creature]:
        """Access creature entities.

        Returns:
            EntityManager[Creature]: Manager for Creature entity operations
        """
        return self._creatures

    @property
    def events(self) -> EntityManager[Event]:
        """Access event entities.

        Returns:
            EntityManager[Event]: Manager for Event entity operations
        """
        return self._events

    @property
    def families(self) -> EntityManager[Family]:
        """Access family entities.

        Returns:
            EntityManager[Family]: Manager for Family entity operations
        """
        return self._families

    @property
    def journals(self) -> EntityManager[Journal]:
        """Access journal entities.

        Returns:
            EntityManager[Journal]: Manager for Journal entity operations
        """
        return self._journals

    @property
    def locations(self) -> EntityManager[Location]:
        """Access location entities.

        Returns:
            EntityManager[Location]: Manager for Location entity operations
        """
        return self._locations

    @property
    def notes(self) -> EntityManager[Note]:
        """Access note entities.

        Returns:
            EntityManager[Note]: Manager for Note entity operations
        """
        return self._notes

    @property
    def organisations(self) -> EntityManager[Organisation]:
        """Access organisation entities.

        Returns:
            EntityManager[Organisation]: Manager for Organisation entity operations
        """
        return self._organisations

    @property
    def quests(self) -> EntityManager[Quest]:
        """Access quest entities.

        Returns:
            EntityManager[Quest]: Manager for Quest entity operations
        """
        return self._quests

    @property
    def races(self) -> EntityManager[Race]:
        """Access race entities.

        Returns:
            EntityManager[Race]: Manager for Race entity operations
        """
        return self._races

    @property
    def tags(self) -> EntityManager[Tag]:
        """Access tag entities.

        Returns:
            EntityManager[Tag]: Manager for Tag entity operations
        """
        return self._tags

    def search(self, term: str, page: int = 1, limit: int = 30) -> List[SearchResult]:
        """Search across all entity types.

        Args:
            term: Search term
            page: Page number (default: 1)
            limit: Number of results per page (default: 30)

        Returns:
            List of search results

        Example:
            results = client.search("dragon")
            results = client.search("dragon", page=2, limit=50)
        """
        params: Dict[str, Union[int, str]] = {"page": page, "limit": limit}
        response = self._request("GET", f"search/{term}", params=params)

        # Store pagination metadata for access if needed
        self._last_search_meta = response.get("meta", {})
        self._last_search_links = response.get("links", {})

        return [SearchResult(**item) for item in response["data"]]

    def entities(self, **filters) -> List[Dict[str, Any]]:
        """Access the /entities endpoint with filters.

        This endpoint provides a unified way to query entities across all types
        with various filtering options.

        Args:
            **filters: Filter parameters like types, name, is_private, tags

        Returns:
            List of entity data
        """
        params: Dict[str, Union[int, str]] = {}

        # Handle special filters
        if "types" in filters and isinstance(filters["types"], list):
            params["types"] = ",".join(filters["types"])
        elif "types" in filters:
            params["types"] = filters["types"]

        if "tags" in filters and isinstance(filters["tags"], list):
            params["tags"] = ",".join(map(str, filters["tags"]))
        elif "tags" in filters:
            params["tags"] = filters["tags"]

        # Add other filters
        for key in ["name", "is_private", "created_by", "updated_by"]:
            if key in filters and filters[key] is not None:
                if isinstance(filters[key], bool):
                    params[key] = int(filters[key])
                else:
                    params[key] = filters[key]

        response = self._request("GET", "entities", params=params)
        return response["data"]  # type: ignore[no-any-return]

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to Kanka API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (relative to campaign)
            **kwargs: Additional request parameters

        Returns:
            Response data

        Raises:
            Various exceptions based on status code
        """
        # Build full URL
        url = f"{self.BASE_URL}/campaigns/{self.campaign_id}/{endpoint}"

        # Make request
        response = self.session.request(method, url, **kwargs)

        # Handle errors
        if response.status_code == 401:
            raise AuthenticationError("Invalid authentication token")
        elif response.status_code == 403:
            raise ForbiddenError("Access forbidden")
        elif response.status_code == 404:
            raise NotFoundError(f"Resource not found: {endpoint}")
        elif response.status_code == 422:
            error_data = response.json() if response.text else {}
            raise ValidationError(f"Validation error: {error_data}")
        elif response.status_code == 429:
            raise RateLimitError("Rate limit exceeded")
        elif response.status_code >= 400:
            raise KankaException(f"API error {response.status_code}: {response.text}")

        # Return empty dict for DELETE requests
        if method == "DELETE":
            return {}

        return response.json()  # type: ignore[no-any-return]

    @property
    def last_search_meta(self) -> Dict[str, Any]:
        """Get metadata from the last search() call.

        Returns:
            Dict[str, Any]: Pagination metadata including current_page, from, to,
                           last_page, per_page, total
        """
        return getattr(self, "_last_search_meta", {})

    @property
    def last_search_links(self) -> Dict[str, Any]:
        """Get pagination links from the last search() call.

        Returns:
            Dict[str, Any]: Links for pagination including first, last, prev, next URLs
        """
        return getattr(self, "_last_search_links", {})
