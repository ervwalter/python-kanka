"""Entity managers for Kanka API."""

from typing import Type, TypeVar, Generic, List, Dict, Any, Optional, Union
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
            # Validate the update data by creating a partial model
            # We create a model with just the update fields to validate them
            try:
                self.model(**{**kwargs, 'id': entity_id})  # Validate fields
            except Exception as e:
                raise ValidationError(f"Invalid update data: {str(e)}")
            
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
                exclude={'id', 'entity_id', 'created_at', 'created_by',
                        'updated_at', 'updated_by'}
            )
            
            # Only include fields that actually changed
            original_data = entity.model_dump(exclude={'id', 'entity_id', 'created_at', 
                                                       'created_by', 'updated_at', 'updated_by'})
            data = {k: v for k, v in data.items() if k not in original_data or original_data[k] != v}
        
        if not data:
            # No changes
            if isinstance(entity_or_id, int):
                # If we only had an ID, fetch and return the entity
                return self.get(entity_id)
            else:
                # Return original entity
                return entity_or_id
        
        url = f"{self.endpoint}/{entity_id}"
        response = self.client._request('PATCH', url, json=data)
        return self.model(**response['data'])
    
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
        if isinstance(entity_or_id, int):
            entity_id = entity_or_id
        else:
            entity_id = entity_or_id.id
            
        url = f"{self.endpoint}/{entity_id}"
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