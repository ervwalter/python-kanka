# python-kanka Documentation

A modern Python client for the [Kanka API](https://app.kanka.io/api-docs/1.0), the collaborative worldbuilding and campaign management platform.

## Guides

| Page | Description |
|------|-------------|
| [Getting Started](getting-started.md) | Installation, setup, and your first API call |
| [Core Concepts](core-concepts.md) | Client-Manager-Model pattern, entity IDs, immutable models |
| [Entity CRUD Operations](entities.md) | Create, read, update, and delete entities |
| [Entity Types Reference](entity-types-reference.md) | All 12 entity types with their specific fields |
| [Posts](posts.md) | Attach notes and comments to any entity |
| [Search and Filtering](search-and-filtering.md) | Global search, entities endpoint, list filters |
| [Last Sync](last-sync.md) | Incremental sync using the lastSync/sync mechanism |
| [Pagination](pagination.md) | Navigate large result sets |
| [Assets and Images](assets-and-images.md) | File/link/alias assets, entity images, automatic image management |
| [Campaign Gallery](gallery.md) | Campaign-level image storage |
| [Error Handling](error-handling.md) | Exception types and recommended patterns |
| [Rate Limiting](rate-limiting.md) | Automatic retry behavior and configuration |
| [Debug Mode](debug-mode.md) | Request/response logging for troubleshooting |
| [Known Limitations](known-limitations.md) | API quirks and gotchas |

## Reference

| Page | Description |
|------|-------------|
| [API Reference](api-reference.md) | Complete reference for all classes, methods, and models |

## Quick Example

```python
from kanka import KankaClient

client = KankaClient(token="your-token", campaign_id=12345)

# Create a character
character = client.characters.create(
    name="Gandalf",
    type="Wizard",
    title="The Grey",
)

# Search across all entities
results = client.search("dragon")

# List with filters
npcs = client.characters.list(type="NPC", is_private=False)
```

## Links

- [Kanka.io](https://kanka.io) — The Kanka platform
- [Kanka API Docs](https://app.kanka.io/api-docs/1.0) — Official API documentation
- [GitHub Repository](https://github.com/ervwalter/python-kanka) — Source code
- [PyPI](https://pypi.org/project/python-kanka/) — Package page
