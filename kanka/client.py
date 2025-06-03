"""Main Kanka API client."""

from typing import Optional, Dict, Any, List
from .managers import EntityManager
from .models.entities import (
    Character, Location, Organisation, Family, 
    Species, Calendar, Timeline, Race, Creature,
    Event, Journal, Tag, Note, Quest, Item,
    Attribute, Map, EntityNote, EntityEvent
)
from .models.common import SearchResult
from .exceptions import (
    NotFoundError, ValidationError, AuthenticationError, 
    ForbiddenError, RateLimitError, KankaException
)


class KankaClient:
    """Main client for Kanka API interaction."""
    
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
        self.session.headers.update({
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        
        # Initialize entity managers
        self._init_managers()
    
    def _init_managers(self):
        """Initialize entity managers for each entity type."""
        # Core entities
        self._characters = EntityManager(self, 'characters', Character)
        self._locations = EntityManager(self, 'locations', Location)
        self._organisations = EntityManager(self, 'organisations', Organisation)
        self._families = EntityManager(self, 'families', Family)
        self._species = EntityManager(self, 'species', Species)
        self._calendars = EntityManager(self, 'calendars', Calendar)
        self._timelines = EntityManager(self, 'timelines', Timeline)
        self._races = EntityManager(self, 'races', Race)
        self._creatures = EntityManager(self, 'creatures', Creature)
        self._events = EntityManager(self, 'events', Event)
        self._journals = EntityManager(self, 'journals', Journal)
        self._tags = EntityManager(self, 'tags', Tag)
        self._notes = EntityManager(self, 'notes', Note)
        self._quests = EntityManager(self, 'quests', Quest)
        self._items = EntityManager(self, 'items', Item)
        self._attributes = EntityManager(self, 'attributes', Attribute)
        self._maps = EntityManager(self, 'maps', Map)
        self._entity_notes = EntityManager(self, 'entity_notes', EntityNote)
        self._entity_events = EntityManager(self, 'entity_events', EntityEvent)
    
    @property
    def characters(self) -> EntityManager[Character]:
        """Access character entities."""
        return self._characters
    
    @property
    def locations(self) -> EntityManager[Location]:
        """Access location entities."""
        return self._locations
    
    @property
    def organisations(self) -> EntityManager[Organisation]:
        """Access organisation entities."""
        return self._organisations
    
    @property
    def families(self) -> EntityManager[Family]:
        """Access family entities."""
        return self._families
    
    @property
    def species(self) -> EntityManager[Species]:
        """Access species entities."""
        return self._species
    
    @property
    def calendars(self) -> EntityManager[Calendar]:
        """Access calendar entities."""
        return self._calendars
    
    @property
    def timelines(self) -> EntityManager[Timeline]:
        """Access timeline entities."""
        return self._timelines
    
    @property
    def races(self) -> EntityManager[Race]:
        """Access race entities."""
        return self._races
    
    @property
    def creatures(self) -> EntityManager[Creature]:
        """Access creature entities."""
        return self._creatures
    
    @property
    def events(self) -> EntityManager[Event]:
        """Access event entities."""
        return self._events
    
    @property
    def journals(self) -> EntityManager[Journal]:
        """Access journal entities."""
        return self._journals
    
    @property
    def tags(self) -> EntityManager[Tag]:
        """Access tag entities."""
        return self._tags
    
    @property
    def notes(self) -> EntityManager[Note]:
        """Access note entities."""
        return self._notes
    
    @property
    def quests(self) -> EntityManager[Quest]:
        """Access quest entities."""
        return self._quests
    
    @property
    def items(self) -> EntityManager[Item]:
        """Access item entities."""
        return self._items
    
    @property
    def attributes(self) -> EntityManager[Attribute]:
        """Access attribute entities."""
        return self._attributes
    
    @property
    def maps(self) -> EntityManager[Map]:
        """Access map entities."""
        return self._maps
    
    @property
    def entity_notes(self) -> EntityManager[EntityNote]:
        """Access entity note entities."""
        return self._entity_notes
    
    @property
    def entity_events(self) -> EntityManager[EntityEvent]:
        """Access entity event entities."""
        return self._entity_events
    
    def search(self, term: str) -> List[SearchResult]:
        """Search across all entity types.
        
        Args:
            term: Search term
            
        Returns:
            List of search results
        """
        response = self._request('GET', f'search/{term}')
        return [SearchResult(**item) for item in response['data']]
    
    def entities(self, **filters) -> List[Dict[str, Any]]:
        """Access the /entities endpoint with filters.
        
        Args:
            **filters: Filter parameters like types, name, is_private, tags
            
        Returns:
            List of entity data
        """
        params = {}
        
        # Handle special filters
        if 'types' in filters and isinstance(filters['types'], list):
            params['types'] = ','.join(filters['types'])
        elif 'types' in filters:
            params['types'] = filters['types']
            
        if 'tags' in filters and isinstance(filters['tags'], list):
            params['tags'] = ','.join(map(str, filters['tags']))
        elif 'tags' in filters:
            params['tags'] = filters['tags']
        
        # Add other filters
        for key in ['name', 'is_private', 'created_by', 'updated_by']:
            if key in filters and filters[key] is not None:
                if isinstance(filters[key], bool):
                    params[key] = int(filters[key])
                else:
                    params[key] = filters[key]
        
        response = self._request('GET', 'entities', params=params)
        return response['data']
    
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
        if method == 'DELETE':
            return {}
        
        return response.json()