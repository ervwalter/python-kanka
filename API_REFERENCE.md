# Python-Kanka API Reference

> **Note**: This reference is current as of v2.3.0 and reflects the implemented entity types.
> Some entity types available in the Kanka API (Timeline, Item, Relation, DiceRoll, Conversation, AttributeTemplate, Bookmark)
> are not yet implemented in this SDK.

## Table of Contents
- [KankaClient](#kankaclient)
- [Campaign Gallery](#campaign-gallery)
- [Entity Managers](#entity-managers)
- [Entity Assets](#entity-assets)
- [Entity Image](#entity-image)
- [Convenience Images Parameter](#convenience-images-parameter)
- [Models](#models)
- [Exceptions](#exceptions)

## KankaClient

The main client for interacting with the Kanka API.

### Constructor

```python
KankaClient(
    token: str,
    campaign_id: int,
    *,
    enable_rate_limit_retry: bool = True,
    max_retries: int = 8,
    retry_delay: float = 1.0,
    max_retry_delay: float = 15.0
)
```

**Parameters:**
- `token` (str): Your Kanka API personal access token
- `campaign_id` (int): The ID of the campaign to access
- `enable_rate_limit_retry` (bool, optional): Whether to automatically retry on rate limits (default: True)
- `max_retries` (int, optional): Maximum number of retries for rate limited requests (default: 8)
- `retry_delay` (float, optional): Initial delay between retries in seconds (default: 1.0)
- `max_retry_delay` (float, optional): Maximum delay between retries in seconds (default: 15.0)

**Example:**
```python
from kanka import KankaClient

client = KankaClient(token="your-token", campaign_id=12345)
```

### Methods

#### search(term, page=1)
Search across all entities in the campaign.

**Note:** The Kanka API search endpoint does not respect limit parameters, so pagination control is limited to page selection only.

**Parameters:**
- `term` (str): The search term
- `page` (int, optional): Page number for pagination (default: 1)

**Returns:** List[SearchResult]

**Example:**
```python
results = client.search("dragon")
for result in results:
    print(f"{result.name} ({result.type})")
```

#### entities(**filters)
Get entities from the generic /entities endpoint with optional filtering.

**Parameters:**
- `**filters`: Filter parameters including:
  - `types` (List[str]): Filter by entity types
  - `name` (str): Filter by name
  - `tags` (List[int]): Filter by tag IDs
  - `page` (int): Page number (default: 1)
  - `limit` (int): Results per page (default: 30)
  - Additional entity-specific filters

**Returns:** List[Dict[str, Any]]

### Properties

#### Search and Pagination Metadata
- `last_search_meta` - Metadata from the last search() call
- `last_search_links` - Pagination links from the last search() call

#### Client Attributes
- `token` (str) - API authentication token
- `campaign_id` (int) - Campaign ID being accessed
- `session` (requests.Session) - HTTP session for API requests
- `enable_rate_limit_retry` (bool) - Whether automatic retry is enabled
- `max_retries` (int) - Maximum retry attempts for rate limits
- `retry_delay` (float) - Initial retry delay in seconds
- `max_retry_delay` (float) - Maximum retry delay in seconds

## Campaign Gallery

The client provides methods for managing campaign-level gallery images.

#### gallery(page=1, limit=30)
List images in the campaign gallery.

**Parameters:**
- `page` (int, optional): Page number (default: 1)
- `limit` (int, optional): Results per page (default: 30)

**Returns:** List[GalleryImage]

#### gallery_get(image_id)
Get a specific gallery image by UUID.

**Parameters:**
- `image_id` (str): Gallery image UUID

**Returns:** GalleryImage

#### gallery_upload(file_path, folder_id=None, visibility_id=None)
Upload an image to the campaign gallery.

**Parameters:**
- `file_path` (str | Path): Path to the image file
- `folder_id` (str, optional): Folder UUID to upload into
- `visibility_id` (int, optional): Visibility setting

**Returns:** GalleryImage

**Example:**
```python
image = client.gallery_upload("/path/to/image.png")
print(image.id)   # UUID
print(image.path)  # Thumbnail URL
```

#### gallery_delete(image_id)
Delete a gallery image.

**Parameters:**
- `image_id` (str): Gallery image UUID

**Returns:** True if successful

#### Gallery Properties
- `last_gallery_meta` - Metadata from the last gallery() call
- `last_gallery_links` - Pagination links from the last gallery() call

---

#### Entity Managers

Each implemented entity type has its own manager. The SDK currently supports the following entity types:

#### Implemented Entity Types
- `client.calendars` - Calendar entities (for managing timelines and dates)
- `client.characters` - Character entities (NPCs, PCs, and other personas)
- `client.creatures` - Creature entities (monsters, animals, etc.)
- `client.events` - Event entities (historical or campaign events)
- `client.families` - Family entities (dynasties, houses, clans)
- `client.journals` - Journal entities (session notes, logs)
- `client.locations` - Location entities (places, regions, buildings)
- `client.notes` - Note entities (general notes and documentation)
- `client.organisations` - Organisation entities (groups, guilds, companies)
- `client.quests` - Quest entities (missions, objectives)
- `client.races` - Race entities (species, ethnicities)
- `client.tags` - Tag entities (labels for organizing content)

## Entity Managers

All entity managers share the same interface through the `EntityManager` class.

### Methods

#### get(id: int, related: bool = False)
Retrieve a single entity by ID.

**Parameters:**
- `id` (int): The entity ID
- `related` (bool, optional): Include related data (posts, attributes) (default: False)

**Returns:** The entity object

**Raises:** NotFoundError if entity doesn't exist

**Example:**
```python
character = client.characters.get(123)
print(character.name)
```

#### list(page=1, limit=30, related=False, **filters)
List entities with optional filtering.

**Parameters:**
- `page` (int, optional): Page number (default: 1)
- `limit` (int, optional): Results per page (default: 30)
- `related` (bool, optional): Include related data (posts, attributes, etc.) (default: False)
- `**filters`: Filter parameters
  - `name` (str): Filter by name (partial match)
  - `tags` (List[int]): Filter by tag IDs
  - `type` (str): Filter by single entity type
  - `types` (List[str]): Filter by multiple entity types
  - `is_private` (bool): Filter by privacy
  - `created_at` (str): Filter by creation date
  - `updated_at` (str): Filter by update date
  - `created_by` (int): Filter by creator ID
  - `updated_by` (int): Filter by updater ID
  - `lastSync` (str): Get only entities modified after this ISO 8601 timestamp (Kanka's native sync feature)

**Returns:** List of entities

**Example:**
```python
# Get all public NPCs
npcs = client.characters.list(type="NPC", is_private=False)

# Get entities with specific tags
tagged = client.locations.list(tags=[1, 2, 3])

# Get entities with posts included
characters_with_posts = client.characters.list(related=True)

# Get entities modified since last sync (using Kanka's native sync feature)
from datetime import datetime, timedelta, timezone
last_sync = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
updated_chars = client.characters.list(lastSync=last_sync, related=True)
```

#### create(*, images=None, **kwargs)
Create a new entity.

**Parameters:**
- `images` (dict[str, str | Path], optional): Map of placeholder src values in entry HTML to local file paths. Files are uploaded as entity assets and `<img src>` tags are rewritten to CDN URLs.
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

# With automatic image management
character = client.characters.create(
    name="Hero",
    entry='<p><img src="portrait.png" /> The brave hero.</p>',
    images={"portrait.png": "/path/to/portrait.png"},
)
```

#### update(entity_or_id, *, images=None, **kwargs)
Update an entity with partial data.

**Parameters:**
- `entity_or_id`: The entity object or its ID
- `images` (dict[str, str | Path], optional): Map of placeholder src values to local file paths. Changed images are re-uploaded, unchanged ones are reused, and orphaned managed assets are cleaned up.
- `**kwargs`: Fields to update

**Returns:** The updated entity

**Example:**
```python
# Update by entity object
character = client.characters.get(123)
updated = client.characters.update(character, title="The White")

# Update by ID directly
updated = client.characters.update(123, title="The White")

# Update with images
updated = client.characters.update(
    character,
    entry='<p><img src="new_portrait.png" /></p>',
    images={"new_portrait.png": "/path/to/new_portrait.png"},
)
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

Entity managers provide methods for managing posts, which are comments or notes that can be attached to any entity.
Posts are separate from the "Note" entity type - they are a feature available on all entity types.

#### list_posts(entity_or_id, page=1, limit=30)
List posts for an entity.

**Parameters:**
- `entity_or_id`: The entity object or its entity_id (NOT the type-specific ID)
- `page` (int, optional): Page number
- `limit` (int, optional): Results per page

**Returns:** List[Post]

**Example:**
```python
# Preferred: Pass the entity object
character = client.characters.get(123)
posts = client.characters.list_posts(character)

# Alternative: Pass the entity_id directly
posts = client.characters.list_posts(character.entity_id)
```

#### create_post(entity_or_id, name, entry, *, images=None, visibility_id=None, **kwargs)
Create a post for an entity.

**IMPORTANT:** Posts use the entity_id, not the type-specific ID!

**Parameters:**
- `entity_or_id`: The entity object (preferred) or its entity_id (NOT the type-specific ID)
- `name` (str): Post name
- `entry` (str): Post content (supports HTML)
- `images` (dict[str, str | Path], optional): Map of placeholder src values to local file paths. Files are uploaded as entity assets and img src tags are rewritten to CDN URLs.
- `visibility_id` (int, optional): Control who can see the post (1=all, 2=admin, 3=admin-self, 4=self, 5=members). None defaults to campaign's default post visibility
- `**kwargs`: Additional fields

**Returns:** Post

**Example:**
```python
# Preferred: Pass the entity object
character = client.characters.get(123)
post = client.characters.create_post(
    character,  # Pass the full object
    name="Session Notes",
    entry="<p>The character discovered...</p>",
    visibility_id=2  # Admin-only visibility
)
```

#### get_post(entity_or_id, post_id)
Get a specific post.

**Parameters:**
- `entity_or_id`: The entity object or its ID
- `post_id` (int): The post ID

**Returns:** Post

#### update_post(entity_or_id, post_id, *, images=None, visibility_id=None, **kwargs)
Update a post.

**NOTE:** The Kanka API requires the 'name' field even when not changing it.

**Parameters:**
- `entity_or_id`: The entity object or its entity_id (NOT the type-specific ID)
- `post_id` (int): The post ID
- `images` (dict[str, str | Path], optional): Map of placeholder src values to local file paths. Changed images are re-uploaded, unchanged ones reused, orphans cleaned up.
- `visibility_id` (int, optional): Update post visibility (1=all, 2=admin, 3=admin-self, 4=self, 5=members). None keeps existing visibility
- `**kwargs`: Fields to update (must include 'name' even if unchanged)

**Returns:** Post

**Example:**
```python
# Update post to admin-only visibility
post = client.characters.update_post(
    character,
    post_id,
    name=post.name,  # Required even if not changing!
    entry="Updated content...",
    visibility_id=2  # Admin-only
)
```

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
- `last_assets_meta` - Metadata from the last list_assets() call
- `last_assets_links` - Pagination links from the last list_assets() call

## Entity Assets

Entity assets allow you to attach files, links, or aliases to entities.

#### list_assets(entity_or_id, page=1, limit=30)
List assets for an entity.

**Parameters:**
- `entity_or_id`: The entity object or its entity_id
- `page` (int, optional): Page number (default: 1)
- `limit` (int, optional): Results per page (default: 30)

**Returns:** List[EntityAsset]

#### get_asset(entity_or_id, asset_id)
Get a specific asset.

**Parameters:**
- `entity_or_id`: The entity object or its entity_id
- `asset_id` (int): The asset ID

**Returns:** EntityAsset

#### create_file_asset(entity_or_id, file_path, name=None, visibility_id=None, is_pinned=False)
Upload a file asset to an entity.

**Parameters:**
- `entity_or_id`: The entity object or its entity_id
- `file_path` (str | Path): Path to the file
- `name` (str, optional): Asset name (defaults to filename stem)
- `visibility_id` (int, optional): Visibility setting
- `is_pinned` (bool, optional): Whether to pin the asset (default: False)

**Returns:** EntityAsset

**Example:**
```python
character = client.characters.get(123)
asset = client.characters.create_file_asset(
    character, "/path/to/map.png", name="Character Map"
)
print(asset.url)  # CDN URL for the uploaded file
```

#### create_link_asset(entity_or_id, name, url, icon=None, visibility_id=None)
Create a link asset on an entity.

**Parameters:**
- `entity_or_id`: The entity object or its entity_id
- `name` (str): Asset name
- `url` (str): The URL to link to
- `icon` (str, optional): Icon class (e.g., 'fa-link')
- `visibility_id` (int, optional): Visibility setting

**Returns:** EntityAsset

#### create_alias_asset(entity_or_id, name, visibility_id=None)
Create an alias asset on an entity.

**Parameters:**
- `entity_or_id`: The entity object or its entity_id
- `name` (str): The alias name
- `visibility_id` (int, optional): Visibility setting

**Returns:** EntityAsset

#### delete_asset(entity_or_id, asset_id)
Delete an asset from an entity.

**Parameters:**
- `entity_or_id`: The entity object or its entity_id
- `asset_id` (int): The asset ID

**Returns:** True if successful

## Entity Image

Entity managers provide methods for managing entity images (main image and header).

#### get_image(entity_or_id)
Get image information for an entity.

**Parameters:**
- `entity_or_id`: The entity object or its entity_id

**Returns:** EntityImageInfo

**Example:**
```python
character = client.characters.get(123)
info = client.characters.get_image(character)
if info.image:
    print(f"Image: {info.image.full}")
if info.header:
    print(f"Header: {info.header.full}")
```

#### set_image(entity_or_id, file_path, is_header=False)
Set the main image or header image for an entity.

**Parameters:**
- `entity_or_id`: The entity object or its entity_id
- `file_path` (str | Path): Path to the image file
- `is_header` (bool, optional): If True, set as header image (default: False)

**Returns:** EntityImageInfo

#### delete_image(entity_or_id, is_header=False)
Delete the main image or header image for an entity.

**Parameters:**
- `entity_or_id`: The entity object or its entity_id
- `is_header` (bool, optional): If True, delete header image (default: False)

**Returns:** True if successful

## Convenience Images Parameter

The `images` parameter on `create()`, `update()`, `create_post()`, and `update_post()` provides automatic image management. It uploads local files as entity assets and rewrites `<img src>` tags in the HTML entry to use CDN URLs.

### How It Works

The `images` dict maps placeholder src values (as they appear in your HTML) to local file paths:

```python
character = client.characters.create(
    name="Hero",
    entry='<p><img src="portrait.png" /> The brave hero.</p>',
    images={"portrait.png": "/path/to/portrait.png"},
)
# Result: entry HTML has src rewritten to CDN URL
```

### Change Detection

SDK-managed assets use a naming convention: `{name}:{sha256_first12}`. On update:
- **Unchanged files** (same SHA-256 hash) are reused without re-uploading
- **Changed files** are re-uploaded and old assets are deleted
- **Orphaned assets** (managed assets no longer referenced) are cleaned up
- **Non-managed assets** (user-created assets without the hash suffix) are never touched

### Example: Full Lifecycle

```python
# Create with images
character = client.characters.create(
    name="Hero",
    entry='<p><img src="portrait.png" /></p>',
    images={"portrait.png": "/path/to/portrait.png"},
)

# Update with changed image
character = client.characters.update(
    character,
    entry='<p><img src="portrait.png" /></p>',
    images={"portrait.png": "/path/to/new_portrait.png"},  # Different file
)

# Works with posts too
post = client.characters.create_post(
    character,
    "Session Notes",
    '<p><img src="map.png" /> We explored the dungeon.</p>',
    images={"map.png": "/path/to/dungeon_map.png"},
)
```

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
- No fields defined (base class only for configuration)

#### Entity
Base class for all entity types.

**Fields:**
- `id` (int, optional): The entity ID
- `entity_id` (int): The parent entity ID
- `name` (str): Entity name
- `entry` (str, optional): Entity description/content (HTML)
- `image` (str, optional): Image URL
- `image_full` (str, optional): Full image URL
- `image_thumb` (str, optional): Thumbnail URL
- `is_private` (bool): Privacy setting (default: False)
- `tags` (List[int]): Tag IDs (default: [])
- `created_at` (datetime, optional): Creation timestamp
- `created_by` (int, optional): Creator user ID
- `updated_at` (datetime, optional): Last update timestamp
- `updated_by` (int, optional): Last updater user ID
- `posts` (List[Post], optional): Related posts (when related=True)
- `attributes` (List[Dict], optional): Custom attributes (when related=True)

### Entity Types

All entity types inherit from Entity and add type-specific fields:

#### Calendar
- `type` (str, optional): Calendar type
- `date` (str, optional): Current date
- `parameters` (str, optional): Calendar parameters
- `months` (List[Dict], optional): Month definitions
- `weekdays` (List[str], optional): Weekday names
- `years` (Union[Dict, List], optional): Year configuration
- `seasons` (List[Dict], optional): Season definitions
- `moons` (List[Dict], optional): Moon definitions
- `suffix` (str, optional): Date suffix
- `has_leap_year` (bool, optional): Whether calendar has leap years
- `leap_year_amount` (int, optional): Leap year frequency
- `leap_year_month` (int, optional): Month that gets leap day
- `leap_year_offset` (int, optional): Leap year offset
- `leap_year_start` (int, optional): Leap year start

#### Character
- `type` (str, optional): Character type/class
- `title` (str, optional): Character's title or role
- `age` (str, optional): Character's age
- `sex` (str, optional): Character's sex/gender
- `pronouns` (str, optional): Character's pronouns
- `race_id` (int, optional): Link to Race entity
- `family_id` (int, optional): Link to Family entity
- `location_id` (int, optional): Link to Location entity
- `is_dead` (bool, optional): Whether character is dead

#### Creature
- `type` (str, optional): Creature type
- `location_id` (int, optional): Link to Location entity

#### Event
- `type` (str, optional): Event type
- `date` (str, optional): Event date
- `location_id` (int, optional): Link to Location entity

#### Family
- `type` (str, optional): Family type
- `family_id` (int, optional): Parent family ID
- `location_id` (int, optional): Link to Location entity

#### Journal
- `type` (str, optional): Journal type
- `date` (str, optional): Journal date
- `character_id` (int, optional): Link to Character entity

#### Location
- `type` (str, optional): Location type
- `parent_location_id` (int, optional): Parent location ID
- `map` (str, optional): Map data
- `map_url` (str, optional): Map URL
- `is_map_private` (bool, optional): Map privacy setting

#### Note
- `type` (str, optional): Note type
- `location_id` (int, optional): Link to Location entity

#### Organisation
- `type` (str, optional): Organisation type
- `organisation_id` (int, optional): Parent organisation ID
- `location_id` (int, optional): Link to Location entity

#### Quest
- `type` (str, optional): Quest type
- `quest_id` (int, optional): Parent quest ID
- `character_id` (int, optional): Link to Character entity
- `is_completed` (bool, optional): Whether quest is completed

#### Race
- `type` (str, optional): Race type
- `race_id` (int, optional): Parent race ID

#### Tag
- `type` (str, optional): Tag type
- `tag_id` (int, optional): Parent tag ID
- `colour` (str, optional): Tag color (see valid colors in documentation)

### Other Models

#### Post
Represents an entity post/note.

**Fields:**
- `id` (int): Post ID
- `entity_id` (int): Parent entity ID
- `name` (str): Post title
- `entry` (str): Post content (HTML)
- `visibility_id` (int, optional): Control who can see the post (1=all, 2=admin, 3=admin-self, 4=self, 5=members)
- `is_pinned` (bool, optional): Whether post is pinned
- `position` (int, optional): Post position/order
- `created_at` (datetime): Creation timestamp
- `created_by` (int): Creator user ID
- `updated_at` (datetime): Update timestamp
- `updated_by` (int, optional): Updater user ID

#### GalleryImage
Represents a campaign gallery image.

**Fields:**
- `id` (str): UUID identifier
- `name` (str, optional): Image name
- `is_folder` (bool): Whether this is a folder (default: False)
- `folder_id` (str, optional): Parent folder UUID
- `path` (str, optional): Thumbnail URL
- `ext` (str, optional): File extension
- `size` (int, optional): File size in bytes
- `created_at` (datetime, optional): Creation timestamp
- `created_by` (int, optional): Creator user ID
- `updated_at` (datetime, optional): Last update timestamp
- `visibility_id` (int, optional): Visibility setting
- `focus_x` (int, optional): Image focus X coordinate
- `focus_y` (int, optional): Image focus Y coordinate

#### EntityAsset
Represents an entity file, link, or alias asset.

**Fields:**
- `id` (int): Asset ID
- `entity_id` (int): Parent entity ID
- `name` (str): Asset name
- `type_id` (int): Asset type (1=file, 2=link, 3=alias)
- `visibility_id` (int, optional): Visibility setting
- `is_pinned` (bool): Whether pinned (default: False)
- `is_private` (bool): Whether private (default: False)
- `metadata` (dict, optional): Additional metadata
- `created_at` (datetime, optional): Creation timestamp
- `created_by` (int, optional): Creator user ID
- `updated_at` (datetime, optional): Last update timestamp
- `updated_by` (int, optional): Last updater user ID
- `url` (str, optional): CDN URL for file assets (populated from API's `_url` field)

#### EntityImageData
Image URL data for an entity.

**Fields:**
- `uuid` (str, optional): Image UUID in gallery
- `full` (str, optional): Full-size image URL
- `thumbnail` (str, optional): Thumbnail image URL

#### EntityImageInfo
Entity image and header information.

**Fields:**
- `image` (EntityImageData, optional): Main entity image data
- `header` (EntityImageData, optional): Entity header image data

#### SearchResult
Represents a search result.

**Fields:**
- `id` (int): Entity ID
- `entity_id` (int): Parent entity ID
- `name` (str): Entity name
- `type` (str): Entity type
- `url` (str, optional): Entity URL
- `tooltip` (str, optional): Tooltip text
- `tags` (List[int]): Tag IDs (default: [])
- `is_private` (bool): Privacy setting (default: False)
- `created_at` (datetime, optional): Creation timestamp
- `updated_at` (datetime, optional): Update timestamp

#### Trait
Represents a character trait.

**Fields:**
- `id` (int, optional): Trait ID
- `name` (str): Trait name
- `entry` (str, optional): Trait description
- `section` (str, optional): Trait section/category

#### Profile
Represents a user profile.

**Fields:**
- `id` (int, optional): Profile ID
- `avatar` (str, optional): Avatar URL
- `avatar_thumb` (str, optional): Avatar thumbnail URL
- `name` (str): Display name
- `date_format` (str, optional): Preferred date format
- `default_pagination` (int, optional): Default pagination size
- `timezone` (str, optional): User timezone

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

**Note:** The client automatically retries rate-limited requests by default.


### Comprehensive Error Handling

```python
from kanka.exceptions import (
    KankaException, NotFoundError, ValidationError,
    RateLimitError, AuthenticationError, ForbiddenError
)

try:
    character = client.characters.get(123)
except NotFoundError:
    print("Character not found")
except ValidationError as e:
    print(f"Invalid data: {e}")
except RateLimitError:
    # Client automatically retries rate limits by default
    print("Rate limit exceeded after retries")
except AuthenticationError:
    print("Check your API token")
except ForbiddenError:
    print("Access denied - check permissions")
except KankaException as e:
    print(f"Other API error: {e}")
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

### Rate Limiting

The client automatically handles API rate limits with configurable retry behavior:

```python
# Default behavior - automatic retry enabled
client = KankaClient(token="your-token", campaign_id=12345)

# Disable automatic retry
client = KankaClient(
    token="your-token",
    campaign_id=12345,
    enable_rate_limit_retry=False
)

# Customize retry behavior
client = KankaClient(
    token="your-token",
    campaign_id=12345,
    max_retries=5,              # Try up to 5 times (default: 8)
    retry_delay=2.0,            # Initial delay in seconds (default: 1.0)
    max_retry_delay=120.0       # Maximum delay between retries (default: 15.0)
)
```

The client parses rate limit headers from the API to determine optimal retry delays and uses exponential backoff for repeated retries.

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

**Note on Additional Fields:**

The Kanka API accepts entity-specific fields that may not be documented in the SDK models. For example, the Character entity accepts a `sex` field even though it's not in the model definition. However, completely custom fields (not recognized by Kanka) are silently ignored by the API.

```python
# Entity-specific fields are accepted
character = client.characters.create(
    name="Test Character",
    sex="Female",  # Accepted by API even if not in our model
    custom_field="value"  # Silently ignored by API
)

# The 'sex' field will be saved, but 'custom_field' will not
```

## Known API Limitations

The following are known limitations of the Kanka API (not the SDK):

### Search Endpoint
- The `limit` parameter is not respected - the API returns a fixed number of results regardless of the limit specified
- Pagination is available but only through the `page` parameter

### Custom Fields
- The API silently ignores unknown fields when creating or updating entities
- Each entity type has specific additional fields that may be accepted but are not documented
- True custom fields are handled through the Kanka "attributes" system, not as direct fields

### Rate Limiting
- The API has rate limits that vary based on your subscription level
- The SDK automatically handles rate limit retries by default
