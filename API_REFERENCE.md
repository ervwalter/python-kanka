# Python-Kanka API Reference

## Table of Contents
- [KankaClient](#kankaclient)
- [Entity Managers](#entity-managers)
- [Models](#models)
- [Exceptions](#exceptions)

## KankaClient

The main client for interacting with the Kanka API.

### Constructor

```python
KankaClient(token: str, campaign_id: int, base_url: str = "https://api.kanka.io/1.0")
```

**Parameters:**
- `token` (str): Your Kanka API personal access token
- `campaign_id` (int): The ID of the campaign to access
- `base_url` (str, optional): The base URL for the API

**Example:**
```python
from kanka import KankaClient

client = KankaClient(token="your-token", campaign_id=12345)
```

### Methods

#### search(query, page=1, limit=5)
Search across all entities in the campaign.

**Parameters:**
- `query` (str): The search term
- `page` (int, optional): Page number for pagination (default: 1)
- `limit` (int, optional): Number of results per page (default: 5)

**Returns:** List[SearchResult]

**Example:**
```python
results = client.search("dragon")
for result in results:
    print(f"{result.name} ({result.type})")
```

#### entities(types=None, name=None, tags=None, page=1, limit=30, **filters)
Get entities from the generic /entities endpoint with optional filtering.

**Parameters:**
- `types` (List[str], optional): Filter by entity types
- `name` (str, optional): Filter by name
- `tags` (List[int], optional): Filter by tag IDs
- `page` (int, optional): Page number (default: 1)
- `limit` (int, optional): Results per page (default: 30)
- `**filters`: Additional filters

**Returns:** List[Entity]

### Properties

Each entity type has its own manager:

- `client.characters` - Character entities
- `client.locations` - Location entities
- `client.organisations` - Organisation entities
- `client.families` - Family entities
- `client.calendars` - Calendar entities
- `client.events` - Event entities
- `client.races` - Race entities
- `client.maps` - Map entities
- `client.notes` - Note entities
- `client.journals` - Journal entities
- `client.tags` - Tag entities
- `client.quests` - Quest entities
- `client.items` - Item entities
- `client.abilities` - Ability entities
- `client.creatures` - Creature entities
- `client.conversations` - Conversation entities
- `client.timelines` - Timeline entities
- `client.species` - Species entities
- `client.attributes` - Attribute entities
- `client.entity_notes` - Entity note entities
- `client.entity_events` - Entity event entities

## Entity Managers

All entity managers share the same interface through the `EntityManager` class.

### Methods

#### get(entity_id: int)
Retrieve a single entity by ID.

**Parameters:**
- `entity_id` (int): The entity ID

**Returns:** The entity object

**Raises:** NotFoundError if entity doesn't exist

**Example:**
```python
character = client.characters.get(123)
print(character.name)
```

#### list(page=1, limit=30, **filters)
List entities with optional filtering.

**Parameters:**
- `page` (int, optional): Page number (default: 1)
- `limit` (int, optional): Results per page (default: 30)
- `**filters`: Filter parameters
  - `name` (str): Filter by name (partial match)
  - `tags` (List[int]): Filter by tag IDs
  - `type` (str): Filter by type
  - `is_private` (bool): Filter by privacy
  - `created_at` (str): Filter by creation date
  - `updated_at` (str): Filter by update date
  - `created_by` (int): Filter by creator ID
  - `updated_by` (int): Filter by updater ID

**Returns:** List of entities

**Example:**
```python
# Get all public NPCs
npcs = client.characters.list(type="NPC", is_private=False)

# Get entities with specific tags
tagged = client.locations.list(tags=[1, 2, 3])
```

#### create(**kwargs)
Create a new entity.

**Parameters:**
- `**kwargs`: Entity fields (varies by type)

**Returns:** The created entity

**Raises:** ValidationError if data is invalid

**Example:**
```python
character = client.characters.create(
    name="Gandalf",
    type="NPC",
    title="The Grey",
    is_private=False
)
```

#### update(entity_or_id: Union[Entity, int], **kwargs)
Update an entity with partial data.

**Parameters:**
- `entity_or_id`: The entity object or its ID
- `**kwargs`: Fields to update

**Returns:** The updated entity

**Example:**
```python
# Update by entity object
character = client.characters.get(123)
updated = client.characters.update(character, title="The White")

# Update by ID directly
updated = client.characters.update(123, title="The White")
```

#### delete(entity_or_id: Union[Entity, int])
Delete an entity.

**Parameters:**
- `entity_or_id`: The entity object or its ID

**Returns:** True if successful

**Example:**
```python
# Delete by entity object
character = client.characters.get(123)
client.characters.delete(character)

# Delete by ID directly
client.characters.delete(123)
```

### Post Management

Entity managers also provide methods for managing posts (entity notes).

#### list_posts(entity_or_id, page=1, limit=30)
List posts for an entity.

**Parameters:**
- `entity_or_id`: The entity object or its ID
- `page` (int, optional): Page number
- `limit` (int, optional): Results per page

**Returns:** List[Post]

#### create_post(entity_or_id, name, entry, is_private=False, **kwargs)
Create a post for an entity.

**Parameters:**
- `entity_or_id`: The entity object or its ID
- `name` (str): Post name
- `entry` (str): Post content (supports HTML)
- `is_private` (bool, optional): Privacy setting
- `**kwargs`: Additional fields

**Returns:** Post

#### get_post(entity_or_id, post_id)
Get a specific post.

**Parameters:**
- `entity_or_id`: The entity object or its ID
- `post_id` (int): The post ID

**Returns:** Post

#### update_post(entity_or_id, post_id, **kwargs)
Update a post.

**Parameters:**
- `entity_or_id`: The entity object or its ID
- `post_id` (int): The post ID
- `**kwargs`: Fields to update

**Returns:** Post

#### delete_post(entity_or_id, post_id)
Delete a post.

**Parameters:**
- `entity_or_id`: The entity object or its ID
- `post_id` (int): The post ID

**Returns:** True if successful

### Properties

- `last_page_meta` - Metadata from the last list() call
- `last_page_links` - Pagination links from the last list() call
- `last_posts_meta` - Metadata from the last list_posts() call
- `last_posts_links` - Pagination links from the last list_posts() call

## Models

All models inherit from Pydantic's BaseModel and support:
- Automatic validation
- JSON serialization/deserialization
- Extra fields preservation
- Type conversion

### Base Models

#### KankaModel
Base class for all Kanka models.

**Fields:**
- `id` (int, optional): The entity ID
- `created_at` (datetime, optional): Creation timestamp
- `created_by` (int, optional): Creator user ID
- `updated_at` (datetime, optional): Last update timestamp
- `updated_by` (int, optional): Last updater user ID

#### Entity
Base class for all entity types.

**Fields:** (inherits from KankaModel)
- `entity_id` (int, optional): The parent entity ID
- `name` (str): Entity name
- `image` (str, optional): Image URL
- `image_full` (str, optional): Full image URL
- `image_thumb` (str, optional): Thumbnail URL
- `is_private` (bool): Privacy setting (default: False)
- `tags` (List[int]): Tag IDs (default: [])
- `type` (str, optional): Entity subtype

### Entity Types

All entity types inherit from Entity and add type-specific fields:

- **Character**: `title`, `age`, `sex`, `location_id`, `race_id`, `family_id`, etc.
- **Location**: `parent_location_id`, `map`, etc.
- **Organisation**: `organisation_id` (parent), `members`, etc.
- **Family**: `family_id` (parent), `members`, etc.
- **Calendar**: `date`, `months`, `weekdays`, `years`, etc.
- **Event**: `date`, `location_id`, etc.
- **Race**: `race_id` (parent), etc.
- **Map**: `map_id` (parent), `width`, `height`, `grid`, `layers`, etc.
- **Note**: (no additional fields)
- **Journal**: `journal_id` (parent), `date`, etc.
- **Tag**: `tag_id` (parent), `colour`, etc.
- **Quest**: `quest_id` (parent), `characters`, `locations`, etc.
- **Item**: `item_id` (parent), `location_id`, `character_id`, `price`, `size`, etc.
- **Ability**: `ability_id` (parent), `charges`, etc.
- **Creature**: `creature_id` (parent), `locations`, etc.
- **Conversation**: `target`, `participants`, etc.
- **Timeline**: `timeline_id` (parent), `eras`, etc.
- **Species**: `species_id` (parent), `locations`, etc.
- **Attribute**: (no additional fields)
- **EntityNote**: (no additional fields)
- **EntityEvent**: `calendar_id`, `date`, etc.

### Other Models

#### Post
Represents an entity post/note.

**Fields:**
- `id` (int, optional): Post ID
- `name` (str): Post title
- `entry` (str, optional): Post content (HTML)
- `is_private` (bool): Privacy setting (default: False)
- `created_at` (datetime, optional): Creation timestamp
- `created_by` (int, optional): Creator user ID
- `updated_at` (datetime, optional): Update timestamp
- `updated_by` (int, optional): Updater user ID

#### SearchResult
Represents a search result.

**Fields:**
- `id` (int): Entity ID
- `entity_id` (int): Parent entity ID
- `name` (str): Entity name
- `type` (str): Entity type
- `tags` (List[int]): Tag IDs (default: [])
- `is_private` (bool): Privacy setting (default: False)
- `image` (str, optional): Image URL
- `image_thumb` (str, optional): Thumbnail URL

## Exceptions

The SDK defines custom exceptions for different error scenarios:

### KankaException
Base exception for all Kanka-related errors.

### NotFoundError
Raised when an entity is not found (404).

```python
try:
    character = client.characters.get(999999)
except NotFoundError:
    print("Character not found")
```

### ValidationError
Raised when request data is invalid (422).

```python
try:
    client.characters.create()  # Missing required 'name'
except ValidationError as e:
    print(f"Validation error: {e}")
```

### AuthenticationError
Raised when authentication fails (401).

```python
try:
    client = KankaClient(token="invalid", campaign_id=123)
    client.characters.list()
except AuthenticationError:
    print("Invalid API token")
```

### ForbiddenError
Raised when access is denied (403).

```python
try:
    client.characters.get(private_char_id)
except ForbiddenError:
    print("Access denied to private character")
```

### RateLimitError
Raised when rate limit is exceeded (429).

```python
try:
    for i in range(1000):
        client.characters.list()
except RateLimitError:
    print("Rate limit exceeded, please wait")
```

## Advanced Usage

### Pagination

Access pagination metadata after list operations:

```python
characters = client.characters.list(page=2)
meta = client.characters.last_page_meta
print(f"Page {meta['current_page']} of {meta['last_page']}")
print(f"Total characters: {meta['total']}")

links = client.characters.last_page_links
if links.get('next'):
    print(f"Next page URL: {links['next']}")
```

### Filtering Examples

```python
# Complex filtering
entities = client.entities(
    types=['character', 'location'],
    name="Dragon",
    tags=[1, 2],
    is_private=False,
    created_at="2024-01-01"
)

# Date filtering
recent = client.notes.list(
    created_at=">=2024-01-01",
    updated_at=">=2024-06-01"
)
```

### Error Handling

```python
from kanka.exceptions import KankaException, NotFoundError, ValidationError

try:
    character = client.characters.get(123)
    updated = client.characters.update(character, name="")
except NotFoundError:
    print("Character not found")
except ValidationError as e:
    print(f"Invalid data: {e}")
except KankaException as e:
    print(f"API error: {e}")
```

### Working with Extra Fields

Pydantic models preserve unknown fields:

```python
# API returns custom fields
character = client.characters.get(123)
print(character.model_extra)  # Access extra fields

# Include extra fields in updates
data = character.model_dump()
data['custom_field'] = 'value'
updated = client.characters.update(character, **data)
```