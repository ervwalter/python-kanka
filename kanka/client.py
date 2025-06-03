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

from typing import Any, Dict, List

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
    Ability,
    AttributeTemplate,
    Bookmark,
    Calendar,
    Character,
    Conversation,
    Creature,
    DiceRoll,
    Event,
    Family,
    Item,
    Journal,
    Location,
    Map,
    Note,
    Organisation,
    Quest,
    Race,
    Tag,
    Timeline,
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
        abilities: Access to Ability entities
        attribute_templates: Access to AttributeTemplate entities
        bookmarks: Access to Bookmark entities
        calendars: Access to Calendar entities
        characters: Access to Character entities
        conversations: Access to Conversation entities
        creatures: Access to Creature entities
        dice_rolls: Access to DiceRoll entities
        events: Access to Event entities
        families: Access to Family entities
        items: Access to Item entities
        journals: Access to Journal entities
        locations: Access to Location entities
        maps: Access to Map entities
        notes: Access to Note entities
        organisations: Access to Organisation entities
        quests: Access to Quest entities
        races: Access to Race entities
        tags: Access to Tag entities
        timelines: Access to Timeline entities
    
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
        self._abilities = EntityManager(self, "abilities", Ability)
        self._attribute_templates = EntityManager(self, "attribute_templates", AttributeTemplate)
        self._bookmarks = EntityManager(self, "bookmarks", Bookmark)
        self._calendars = EntityManager(self, "calendars", Calendar)
        self._characters = EntityManager(self, "characters", Character)
        self._conversations = EntityManager(self, "conversations", Conversation)
        self._creatures = EntityManager(self, "creatures", Creature)
        self._dice_rolls = EntityManager(self, "dice_rolls", DiceRoll)
        self._events = EntityManager(self, "events", Event)
        self._families = EntityManager(self, "families", Family)
        self._items = EntityManager(self, "items", Item)
        self._journals = EntityManager(self, "journals", Journal)
        self._locations = EntityManager(self, "locations", Location)
        self._maps = EntityManager(self, "maps", Map)
        self._notes = EntityManager(self, "notes", Note)
        self._organisations = EntityManager(self, "organisations", Organisation)
        self._quests = EntityManager(self, "quests", Quest)
        self._races = EntityManager(self, "races", Race)
        self._tags = EntityManager(self, "tags", Tag)
        self._timelines = EntityManager(self, "timelines", Timeline)

    @property
    def abilities(self) -> EntityManager[Ability]:
        """Access ability entities.
        
        Returns:
            EntityManager[Ability]: Manager for Ability entity operations
        """
        return self._abilities

    @property
    def attribute_templates(self) -> EntityManager[AttributeTemplate]:
        """Access attribute template entities.
        
        Returns:
            EntityManager[AttributeTemplate]: Manager for AttributeTemplate entity operations
        """
        return self._attribute_templates

    @property
    def bookmarks(self) -> EntityManager[Bookmark]:
        """Access bookmark entities.
        
        Returns:
            EntityManager[Bookmark]: Manager for Bookmark entity operations
        """
        return self._bookmarks

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
    def conversations(self) -> EntityManager[Conversation]:
        """Access conversation entities.
        
        Returns:
            EntityManager[Conversation]: Manager for Conversation entity operations
        """
        return self._conversations

    @property
    def creatures(self) -> EntityManager[Creature]:
        """Access creature entities.
        
        Returns:
            EntityManager[Creature]: Manager for Creature entity operations
        """
        return self._creatures

    @property
    def dice_rolls(self) -> EntityManager[DiceRoll]:
        """Access dice roll entities.
        
        Returns:
            EntityManager[DiceRoll]: Manager for DiceRoll entity operations
        """
        return self._dice_rolls

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
    def items(self) -> EntityManager[Item]:
        """Access item entities.
        
        Returns:
            EntityManager[Item]: Manager for Item entity operations
        """
        return self._items

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
    def maps(self) -> EntityManager[Map]:
        """Access map entities.
        
        Returns:
            EntityManager[Map]: Manager for Map entity operations
        """
        return self._maps

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

    @property
    def timelines(self) -> EntityManager[Timeline]:
        """Access timeline entities.
        
        Returns:
            EntityManager[Timeline]: Manager for Timeline entity operations
        """
        return self._timelines

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
        params = {"page": page, "limit": limit}
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
        params = {}

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
        return response["data"]

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

        return response.json()

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
