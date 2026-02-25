# API Reference

Complete reference for all public classes, methods, and models in the python-kanka SDK.

## Table of Contents

- [KankaClient](#kankaclient)
- [EntityManager](#entitymanagert)
- [Models](#models)
  - [Entity (base)](#entity)
  - [Entity Types](#entity-types)
  - [Post](#post)
  - [SearchResult](#searchresult)
  - [Trait](#trait)
  - [GalleryImage](#galleryimage)
  - [EntityAsset](#entityasset)
  - [EntityImageData](#entityimagedata)
  - [EntityImageInfo](#entityimageinfo)
  - [Profile](#profile)
- [Exceptions](#exceptions)

---

## KankaClient

```python
from kanka import KankaClient
```

### Constructor

```python
KankaClient(
    token: str,
    campaign_id: int,
    *,
    enable_rate_limit_retry: bool = True,
    max_retries: int = 8,
    retry_delay: float = 1.0,
    max_retry_delay: float = 15.0,
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `token` | `str` | — | API personal access token |
| `campaign_id` | `int` | — | Campaign ID |
| `enable_rate_limit_retry` | `bool` | `True` | Auto-retry on rate limits |
| `max_retries` | `int` | `8` | Max retry attempts |
| `retry_delay` | `float` | `1.0` | Initial retry delay (seconds) |
| `max_retry_delay` | `float` | `15.0` | Max retry delay (seconds) |

### Entity Manager Properties

| Property | Returns |
|----------|---------|
| `calendars` | `EntityManager[Calendar]` |
| `characters` | `EntityManager[Character]` |
| `creatures` | `EntityManager[Creature]` |
| `events` | `EntityManager[Event]` |
| `families` | `EntityManager[Family]` |
| `journals` | `EntityManager[Journal]` |
| `locations` | `EntityManager[Location]` |
| `notes` | `EntityManager[Note]` |
| `organisations` | `EntityManager[Organisation]` |
| `quests` | `EntityManager[Quest]` |
| `races` | `EntityManager[Race]` |
| `tags` | `EntityManager[Tag]` |

### Methods

#### search

```python
search(term: str, page: int = 1) → list[SearchResult]
```

Search across all entity types. The `limit` parameter is not supported by the API.

#### entity

```python
entity(entity_id: int) → dict[str, Any]
```

Get a single entity by its universal `entity_id`. Returns a raw dictionary.

**Raises:** `NotFoundError`

#### entities

```python
entities(
    page: int = 1,
    limit: int = 15,
    last_sync: str | None = None,
    **filters,
) → list[dict[str, Any]]
```

Query the generic `/entities` endpoint. Returns raw dictionaries.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | `int` | `1` | Page number |
| `limit` | `int` | `15` | Results per page |
| `last_sync` | `str \| None` | `None` | Only return entities modified after this ISO 8601 timestamp. See [Last Sync](last-sync.md). |
| `types` | `list[str]` | — | Filter by entity types |
| `name` | `str` | — | Filter by name |
| `tags` | `list[int]` | — | Filter by tag IDs |
| `is_private` | `bool` | — | Filter by privacy |
| `created_by` | `int` | — | Filter by creator ID |
| `updated_by` | `int` | — | Filter by updater ID |

#### gallery

```python
gallery(page: int = 1, limit: int = 30) → list[GalleryImage]
```

List campaign gallery images.

#### gallery_get

```python
gallery_get(image_id: str) → GalleryImage
```

Get a specific gallery image by UUID.

#### gallery_upload

```python
gallery_upload(
    file_path: str | Path,
    folder_id: str | None = None,
    visibility_id: int | None = None,
) → GalleryImage
```

Upload an image to the campaign gallery.

#### gallery_delete

```python
gallery_delete(image_id: str) → bool
```

Delete a gallery image by UUID.

### Pagination Properties

| Property | Type | Description |
|----------|------|-------------|
| `last_entities_meta` | `dict` | Pagination metadata from last `entities()` |
| `last_entities_links` | `dict` | Pagination links from last `entities()` |
| `entities_has_next_page` | `bool` | Whether next page exists for `entities()` |
| `last_entities_sync` | `str \| None` | Sync timestamp from last `entities()` call. See [Last Sync](last-sync.md). |
| `last_search_meta` | `dict` | Pagination metadata from last `search()` |
| `last_search_links` | `dict` | Pagination links from last `search()` |
| `last_search_sync` | `str \| None` | Sync timestamp from last `search()` call |
| `last_gallery_meta` | `dict` | Pagination metadata from last `gallery()` |
| `last_gallery_links` | `dict` | Pagination links from last `gallery()` |

### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `BASE_URL` | `str` | `"https://api.kanka.io/1.0"` |
| `token` | `str` | API auth token |
| `campaign_id` | `int` | Campaign ID |
| `session` | `requests.Session` | HTTP session |
| `enable_rate_limit_retry` | `bool` | Rate limit retry enabled |
| `max_retries` | `int` | Max retry attempts |
| `retry_delay` | `float` | Initial retry delay |
| `max_retry_delay` | `float` | Max retry delay |

---

## EntityManager[T]

```python
from kanka.managers import EntityManager
```

Generic manager for CRUD operations on a specific entity type. `T` is bound to `Entity`.

### CRUD Methods

#### get

```python
get(id: int, related: bool = False) → T
```

Get a single entity by its type-specific ID.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `id` | `int` | — | Type-specific entity ID |
| `related` | `bool` | `False` | Include posts and attributes |

**Returns:** Entity model instance

**Raises:** `NotFoundError`, `AuthenticationError`, `ForbiddenError`

#### list

```python
list(
    page: int = 1,
    limit: int = 30,
    related: bool = False,
    last_sync: str | None = None,
    **filters,
) → list[T]
```

List entities with optional filtering.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | `int` | `1` | Page number |
| `limit` | `int` | `30` | Results per page |
| `related` | `bool` | `False` | Include posts and attributes |
| `last_sync` | `str \| None` | `None` | Only return entities modified after this ISO 8601 timestamp. See [Last Sync](last-sync.md). |
| `name` | `str` | — | Filter by name (partial match) |
| `type` | `str` | — | Filter by entity type |
| `types` | `list[str]` | — | Filter by multiple types |
| `tags` | `list[int]` | — | Filter by tag IDs |
| `is_private` | `bool` | — | Filter by privacy |
| `created_at` | `str` | — | Filter by creation date |
| `updated_at` | `str` | — | Filter by update date |
| `created_by` | `int` | — | Filter by creator ID |
| `updated_by` | `int` | — | Filter by updater ID |

**Returns:** List of entity model instances

#### create

```python
create(*, images: dict[str, str | Path] | None = None, **kwargs) → T
```

Create a new entity. All entity fields are passed as keyword arguments.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `images` | `dict` | `None` | Map of placeholder src values to local file paths |
| `**kwargs` | — | — | Entity fields (e.g., `name`, `type`, `entry`) |

**Returns:** The created entity

**Raises:** `ValidationError`

#### update

```python
update(
    entity_or_id: T | int,
    *,
    images: dict[str, str | Path] | None = None,
    **kwargs,
) → T
```

Update an entity with partial data.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `entity_or_id` | `T \| int` | — | Entity object or type-specific ID |
| `images` | `dict` | `None` | Map of placeholder src values to local file paths |
| `**kwargs` | — | — | Fields to update |

**Returns:** The updated entity

**Raises:** `NotFoundError`, `ValidationError`

#### delete

```python
delete(entity_or_id: T | int) → bool
```

Delete an entity.

**Returns:** `True` on success

**Raises:** `NotFoundError`

### Post Methods

All post methods accept an entity object or an `entity_id` (integer). If passing an integer, it must be the `entity_id`, not the type-specific `id`.

#### list_posts

```python
list_posts(entity_or_id: T | int, page: int = 1, limit: int = 30) → list[Post]
```

#### create_post

```python
create_post(
    entity_or_id: T | int,
    name: str,
    entry: str,
    *,
    images: dict[str, str | Path] | None = None,
    visibility_id: int | None = None,
    **kwargs,
) → Post
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `entity_or_id` | `T \| int` | — | Entity object or entity_id |
| `name` | `str` | — | Post title |
| `entry` | `str` | — | Post content (HTML) |
| `images` | `dict` | `None` | Map of placeholder src values to local file paths |
| `visibility_id` | `int` | `None` | 1=all, 2=admin, 3=admin-self, 4=self, 5=members |
| `**kwargs` | — | — | Additional post fields |

#### get_post

```python
get_post(entity_or_id: T | int, post_id: int) → Post
```

#### update_post

```python
update_post(
    entity_or_id: T | int,
    post_id: int,
    *,
    images: dict[str, str | Path] | None = None,
    visibility_id: int | None = None,
    **kwargs,
) → Post
```

Note: The Kanka API requires the `name` field even when not changing it.

#### delete_post

```python
delete_post(entity_or_id: T | int, post_id: int) → bool
```

### Asset Methods

All asset methods accept an entity object or an `entity_id` (integer).

#### list_assets

```python
list_assets(entity_or_id: T | int, page: int = 1, limit: int = 30) → list[EntityAsset]
```

#### get_asset

```python
get_asset(entity_or_id: T | int, asset_id: int) → EntityAsset
```

#### create_file_asset

```python
create_file_asset(
    entity_or_id: T | int,
    file_path: str | Path,
    name: str | None = None,
    visibility_id: int | None = None,
    is_pinned: bool = False,
) → EntityAsset
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `entity_or_id` | `T \| int` | — | Entity object or entity_id |
| `file_path` | `str \| Path` | — | Path to file |
| `name` | `str` | `None` | Asset name (defaults to filename stem) |
| `visibility_id` | `int` | `None` | Visibility setting |
| `is_pinned` | `bool` | `False` | Pin the asset |

#### create_link_asset

```python
create_link_asset(
    entity_or_id: T | int,
    name: str,
    url: str,
    icon: str | None = None,
    visibility_id: int | None = None,
) → EntityAsset
```

#### create_alias_asset

```python
create_alias_asset(
    entity_or_id: T | int,
    name: str,
    visibility_id: int | None = None,
) → EntityAsset
```

#### delete_asset

```python
delete_asset(entity_or_id: T | int, asset_id: int, *, delete_gallery_image: bool = False) → bool
```

When `delete_gallery_image=True`, also deletes the underlying campaign gallery image to prevent orphaned images from accumulating. The gallery image UUID is extracted from the asset's CDN URL.

### Image Methods

All image methods accept an entity object or an `entity_id` (integer).

#### get_image

```python
get_image(entity_or_id: T | int) → EntityImageInfo
```

#### set_image

```python
set_image(
    entity_or_id: T | int,
    file_path: str | Path,
    is_header: bool = False,
) → EntityImageInfo
```

#### delete_image

```python
delete_image(entity_or_id: T | int, is_header: bool = False) → bool
```

### Pagination Properties

| Property | Type | Description |
|----------|------|-------------|
| `pagination_meta` | `dict` | Metadata from last `list()` |
| `pagination_links` | `dict` | Links from last `list()` |
| `has_next_page` | `bool` | Whether next page exists |
| `last_sync` | `str \| None` | Sync timestamp from last `list()` call. See [Last Sync](last-sync.md). |
| `last_page_meta` | `dict` | Alias for `pagination_meta` |
| `last_page_links` | `dict` | Alias for `pagination_links` |
| `last_posts_meta` | `dict` | Metadata from last `list_posts()` |
| `last_posts_links` | `dict` | Links from last `list_posts()` |
| `last_assets_meta` | `dict` | Metadata from last `list_assets()` |
| `last_assets_links` | `dict` | Links from last `list_assets()` |

---

## Models

All models inherit from `KankaModel` (which inherits from `pydantic.BaseModel`) with this configuration:
- `extra="allow"` — unknown fields are preserved
- `validate_assignment=True` — field values are validated on assignment
- `populate_by_name=True` — both field names and aliases are accepted

### Entity

Base class for all entity types.

| Field | Type | Default |
|-------|------|---------|
| `id` | `int` | — |
| `entity_id` | `int` | — |
| `name` | `str` | — |
| `entry` | `str \| None` | `None` |
| `image` | `str \| None` | `None` |
| `image_full` | `str \| None` | `None` |
| `image_thumb` | `str \| None` | `None` |
| `is_private` | `bool` | `False` |
| `tags` | `list[int]` | `[]` |
| `created_at` | `datetime` | — |
| `created_by` | `int` | — |
| `updated_at` | `datetime` | — |
| `updated_by` | `int \| None` | `None` |
| `posts` | `list[Post] \| None` | `None` |
| `attributes` | `list[dict] \| None` | `None` |

**Property:** `entity_type` → `str` (lowercase class name)

### Entity Types

See [Entity Types Reference](entity-types-reference.md) for complete field tables. Summary of type-specific fields:

| Type | Key Fields |
|------|------------|
| `Calendar` | `type`, `date`, `parameters`, `months`, `weekdays`, `years`, `seasons`, `moons`, `suffix`, `has_leap_year`, `leap_year_amount`, `leap_year_month`, `leap_year_offset`, `leap_year_start` |
| `Character` | `type`, `title`, `age`, `sex`, `pronouns`, `race_id`, `family_id`, `location_id`, `is_dead` |
| `Creature` | `type`, `location_id` |
| `Event` | `type`, `date`, `location_id` |
| `Family` | `location_id`, `family_id` |
| `Journal` | `type`, `date`, `character_id` |
| `Location` | `type`, `parent_location_id`, `map`, `map_url`, `is_map_private` |
| `Note` | `type`, `location_id` |
| `Organisation` | `type`, `location_id`, `organisation_id` |
| `Quest` | `type`, `quest_id`, `character_id` |
| `Race` | `type`, `race_id` |
| `Tag` | `type`, `colour`, `tag_id` |

### Post

| Field | Type | Default |
|-------|------|---------|
| `id` | `int` | — |
| `name` | `str` | — |
| `entry` | `str` | — |
| `entity_id` | `int` | — |
| `visibility_id` | `int \| None` | `None` |
| `created_by` | `int` | — |
| `updated_by` | `int \| None` | `None` |
| `created_at` | `datetime` | — |
| `updated_at` | `datetime` | — |

### SearchResult

| Field | Type | Default |
|-------|------|---------|
| `id` | `int` | — |
| `entity_id` | `int` | — |
| `name` | `str` | — |
| `type` | `str \| None` | `None` |
| `url` | `str` | — |
| `image` | `str \| None` | `None` |
| `is_private` | `bool` | `False` |
| `tooltip` | `str \| None` | `None` |
| `tags` | `list[int]` | `[]` |
| `created_at` | `datetime \| None` | `None` |
| `updated_at` | `datetime \| None` | `None` |

### Trait

| Field | Type | Default |
|-------|------|---------|
| `id` | `int \| None` | `None` |
| `name` | `str` | — |
| `entry` | `str` | — |
| `section` | `str` | — |
| `is_private` | `bool` | `False` |
| `default_order` | `int` | `0` |

### GalleryImage

| Field | Type | Default |
|-------|------|---------|
| `id` | `str` | — |
| `name` | `str \| None` | `None` |
| `is_folder` | `bool` | `False` |
| `folder_id` | `str \| None` | `None` |
| `path` | `str \| None` | `None` |
| `ext` | `str \| None` | `None` |
| `size` | `int \| None` | `None` |
| `created_at` | `datetime \| None` | `None` |
| `created_by` | `int \| None` | `None` |
| `updated_at` | `datetime \| None` | `None` |
| `visibility_id` | `int \| None` | `None` |
| `focus_x` | `int \| None` | `None` |
| `focus_y` | `int \| None` | `None` |

### EntityAsset

| Field | Type | Default |
|-------|------|---------|
| `id` | `int` | — |
| `entity_id` | `int` | — |
| `name` | `str` | — |
| `type_id` | `int` | — |
| `visibility_id` | `int \| None` | `None` |
| `is_pinned` | `bool` | `False` |
| `is_private` | `bool` | `False` |
| `metadata` | `dict \| None` | `None` |
| `url` | `str \| None` | `None` |
| `created_at` | `datetime \| None` | `None` |
| `created_by` | `int \| None` | `None` |
| `updated_at` | `datetime \| None` | `None` |
| `updated_by` | `int \| None` | `None` |

Note: `url` is aliased from the API's `_url` field.

### EntityImageData

| Field | Type | Default |
|-------|------|---------|
| `uuid` | `str \| None` | `None` |
| `full` | `str \| None` | `None` |
| `thumbnail` | `str \| None` | `None` |

### EntityImageInfo

| Field | Type | Default |
|-------|------|---------|
| `image` | `EntityImageData \| None` | `None` |
| `header` | `EntityImageData \| None` | `None` |

### Profile

| Field | Type | Default |
|-------|------|---------|
| `id` | `int` | — |
| `name` | `str` | — |
| `avatar` | `str \| None` | `None` |
| `avatar_thumb` | `str \| None` | `None` |
| `locale` | `str \| None` | `None` |
| `timezone` | `str \| None` | `None` |
| `date_format` | `str \| None` | `None` |
| `default_pagination` | `int \| None` | `None` |
| `theme` | `str \| None` | `None` |
| `is_patreon` | `bool \| None` | `None` |
| `last_campaign_id` | `int \| None` | `None` |

---

## Exceptions

All exceptions inherit from `KankaException`. Import from `kanka` or `kanka.exceptions`.

| Exception | HTTP Status | Description |
|-----------|-------------|-------------|
| `KankaException` | — | Base exception for all SDK errors |
| `AuthenticationError` | 401 | Invalid or expired API token |
| `ForbiddenError` | 403 | Insufficient permissions |
| `NotFoundError` | 404 | Entity not found |
| `ValidationError` | 422 | Invalid request data |
| `RateLimitError` | 429 | Rate limit exceeded (after retries if enabled) |
