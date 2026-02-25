# Search and Filtering

The SDK provides three ways to find entities: global search, the generic entities endpoint, and filtered lists on entity managers.

## Global Search

Search across all entity types in the campaign:

```python
results = client.search("dragon")

for result in results:
    print(f"{result.name} ({result.type})")
    print(f"  Entity ID: {result.entity_id}")
    print(f"  URL: {result.url}")
```

### Search Pagination

The search endpoint supports page-based pagination but **does not respect the `limit` parameter** — the API returns a fixed number of results per page regardless of any limit specified.

```python
# Get page 2 of results
results = client.search("dragon", page=2)

# Check pagination metadata
meta = client.last_search_meta
print(f"Page {meta['current_page']} of {meta['last_page']}")
print(f"Total results: {meta['total']}")

links = client.last_search_links
if links.get("next"):
    print("More results available")
```

### SearchResult Model Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | `int` | Type-specific entity ID |
| `entity_id` | `int` | Universal entity ID |
| `name` | `str` | Entity name |
| `type` | `str \| None` | Entity type (e.g., "character", "location") |
| `url` | `str` | API URL for this entity |
| `image` | `str \| None` | Entity image URL |
| `is_private` | `bool` | Whether entity is private |
| `tooltip` | `str \| None` | Preview tooltip text |
| `tags` | `list[int]` | Tag IDs |
| `created_at` | `datetime \| None` | Creation timestamp |
| `updated_at` | `datetime \| None` | Last update timestamp |

## Generic Entities Endpoint

Query entities across multiple types using the generic endpoint. Returns raw dictionaries (not typed model objects):

```python
# Get all characters and locations
entities = client.entities(types=["character", "location"])

for entity in entities:
    print(f"{entity['name']} ({entity['type']})")
```

### Get a Single Entity by Entity ID

```python
entity = client.entity(456)  # Pass the entity_id (universal ID)
print(entity["name"])
```

### Available Filters

| Filter | Type | Description |
|--------|------|-------------|
| `types` | `list[str]` | Filter by entity types |
| `name` | `str` | Filter by name |
| `tags` | `list[int]` | Filter by tag IDs |
| `is_private` | `bool` | Filter by privacy |
| `created_by` | `int` | Filter by creator user ID |
| `updated_by` | `int` | Filter by last updater user ID |

```python
# Multiple types with name filter
entities = client.entities(
    types=["character", "location"],
    name="Dragon",
    is_private=False,
)

# Filter by tags
entities = client.entities(tags=[1, 2, 3])
```

## Filtered Entity Lists

Entity managers provide typed filtering through the `list()` method. This returns properly typed model objects:

```python
# Filter by type
wizards = client.characters.list(type="Wizard")

# Filter by name (partial match)
matches = client.characters.list(name="Gandalf")

# Filter by privacy
public = client.characters.list(is_private=False)

# Filter by tags
tagged = client.characters.list(tags=[1, 2, 3])

# Filter by dates
recent = client.characters.list(updated_at=">=2024-01-01")

# Filter by creator
mine = client.characters.list(created_by=42)

# Combine multiple filters
results = client.characters.list(
    type="NPC",
    is_private=False,
    tags=[15],
    name="the",
    limit=50,
)
```

### All Supported List Filters

| Filter | Type | Description |
|--------|------|-------------|
| `name` | `str` | Filter by name (partial match) |
| `type` | `str` | Filter by entity type |
| `types` | `list[str]` | Filter by multiple types |
| `tags` | `list[int]` | Filter by tag IDs |
| `is_private` | `bool` | Filter by privacy status |
| `created_at` | `str` | Filter by creation date (ISO format, supports `>=` prefix) |
| `updated_at` | `str` | Filter by update date (ISO format, supports `>=` prefix) |
| `created_by` | `int` | Filter by creator user ID |
| `updated_by` | `int` | Filter by last updater user ID |
| `last_sync` | `str` | Only return entities modified after this ISO 8601 timestamp |

### Filter Value Handling

- **Booleans** are converted to `0`/`1` for the API
- **Lists** are joined with commas (e.g., `tags=[1,2,3]` becomes `"1,2,3"`)
- **Strings** are passed as-is

### Sync Filter

The `last_sync` parameter returns only entities modified since a given timestamp. Each API response includes a sync timestamp (available via the `last_sync` property) that you should capture and reuse. See [Last Sync](last-sync.md) for a complete guide including the full sync workflow, pagination, persistence, and important caveats.

## Choosing the Right Approach

| Need | Use |
|------|-----|
| Search by keyword across all types | `client.search(term)` |
| Query multiple entity types at once | `client.entities(types=[...])` |
| Get a single entity by universal ID | `client.entity(entity_id)` |
| Filter a specific entity type with typed results | `client.characters.list(**filters)` |
