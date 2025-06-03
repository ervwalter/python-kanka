"""Entity managers for Kanka API."""

from typing import Type, TypeVar, Generic, List, Dict, Any, Optional
from .models.base import Entity, KankaModel
from .models.common import EntityResponse, ListResponse
from .exceptions import NotFoundError, ValidationError, AuthenticationError, ForbiddenError, RateLimitError, KankaException


T = TypeVar('T', bound=Entity)


class EntityManager(Generic[T]):
    """Manages CRUD operations for a specific entity type."""
    
    def __init__(self, client: 'KankaClient', endpoint: str, model: Type[T]):
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
        params = {'related': 1} if related else {}
        url = f"{self.endpoint}/{id}"
        
        response = self.client._request('GET', url, params=params)
        return self.model(**response['data'])
    
    def list(self, page: int = 1, limit: int = 30, **filters) -> List[T]:
        """List entities with optional filters.
        
        Args:
            page: Page number (default: 1)
            limit: Number of results per page (default: 30)
            **filters: Additional filters like name, type, is_private, tags
            
        Returns:
            List of entity instances
        """
        # Build parameters
        params = {
            'page': page,
            'limit': limit
        }
        
        # Add filters
        for key, value in filters.items():
            if value is not None:
                # Handle special cases
                if key == 'tags' and isinstance(value, list):
                    params['tags'] = ','.join(map(str, value))
                elif isinstance(value, bool):
                    params[key] = int(value)
                else:
                    params[key] = value
        
        response = self.client._request('GET', self.endpoint, params=params)
        
        # Store pagination metadata on the manager for access if needed
        self._last_meta = response.get('meta', {})
        self._last_links = response.get('links', {})
        
        return [self.model(**item) for item in response['data']]
    
    def create(self, **kwargs) -> T:
        """Create a new entity.
        
        Args:
            **kwargs: Entity fields
            
        Returns:
            The created entity
            
        Raises:
            ValidationError: If the data is invalid
        """
        # Create model instance to validate data
        entity = self.model(**kwargs)
        
        # Convert to dict, excluding unset fields
        data = entity.model_dump(exclude_unset=True, exclude={'id', 'entity_id', 
                                                              'created_at', 'created_by',
                                                              'updated_at', 'updated_by'})
        
        response = self.client._request('POST', self.endpoint, json=data)
        return self.model(**response['data'])
    
    def update(self, entity: T, **kwargs) -> T:
        """Update an entity with partial data.
        
        Args:
            entity: The entity to update
            **kwargs: Fields to update
            
        Returns:
            The updated entity
            
        Raises:
            NotFoundError: If entity doesn't exist
            ValidationError: If the data is invalid
        """
        # Create a copy with updates
        updates = entity.model_copy(update=kwargs)
        
        # Get only the changed fields
        data = updates.model_dump(
            exclude_unset=True,
            exclude={'id', 'entity_id', 'created_at', 'created_by',
                    'updated_at', 'updated_by'}
        )
        
        # Only include fields that actually changed
        original_data = entity.model_dump(exclude={'id', 'entity_id', 'created_at', 
                                                   'created_by', 'updated_at', 'updated_by'})
        data = {k: v for k, v in data.items() if k not in original_data or original_data[k] != v}
        
        if not data:
            # No changes, return original
            return entity
        
        url = f"{self.endpoint}/{entity.id}"
        response = self.client._request('PATCH', url, json=data)
        return self.model(**response['data'])
    
    def delete(self, entity: T) -> bool:
        """Delete an entity.
        
        Args:
            entity: The entity to delete
            
        Returns:
            True if successful
            
        Raises:
            NotFoundError: If entity doesn't exist
        """
        url = f"{self.endpoint}/{entity.id}"
        self.client._request('DELETE', url)
        return True
    
    @property
    def last_page_meta(self) -> Dict[str, Any]:
        """Get metadata from the last list() call."""
        return getattr(self, '_last_meta', {})
    
    @property
    def last_page_links(self) -> Dict[str, Any]:
        """Get pagination links from the last list() call."""
        return getattr(self, '_last_links', {})