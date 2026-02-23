# Core Concepts

## Client → Manager → Model

The SDK follows a three-layer pattern:

```
KankaClient
  └── EntityManager[Character]    ← client.characters
        └── Character              ← Pydantic model
  └── EntityManager[Location]     ← client.locations
        └── Location               ← Pydantic model
  └── ... (12 entity types total)
```

1. **KankaClient** — The entry point. Handles authentication, HTTP requests, rate limiting, and provides access to entity managers and campaign-level features (search, gallery).

2. **EntityManager[T]** — A generic manager for CRUD operations on a specific entity type. Each entity type has its own manager (e.g., `client.characters`, `client.locations`). All managers share the same interface.

3. **Models** — Pydantic models representing API data. Entity models like `Character` and `Location` inherit from the `Entity` base class and add type-specific fields.

```python
from kanka import KankaClient

client = KankaClient(token="...", campaign_id=12345)

# client.characters is an EntityManager[Character]
character = client.characters.get(123)    # Returns a Character model
characters = client.characters.list()     # Returns list[Character]
```

## Entity IDs: `id` vs `entity_id`

Every entity has **two IDs**. Understanding the difference is critical:

| Field | Description | Used For |
|-------|-------------|----------|
| `id` | Type-specific ID | CRUD operations (`get`, `update`, `delete`) |
| `entity_id` | Universal entity ID | Posts, assets, images, cross-type references |

The **type-specific `id`** is unique within its entity type. For example, character ID 5 and location ID 5 are different entities.

The **universal `entity_id`** is unique across all entity types. It's used by the Kanka API for sub-resources like posts, assets, and images, which are accessed via `/entities/{entity_id}/posts`.

```python
character = client.characters.get(123)
print(character.id)         # 123 — used for client.characters.get/update/delete
print(character.entity_id)  # 456 — used for posts, assets, images
```

When using post and asset methods, you can pass the entity object directly and the SDK handles the ID extraction automatically:

```python
# Preferred: pass the entity object
posts = client.characters.list_posts(character)

# Also works: pass the entity_id (NOT the type-specific id)
posts = client.characters.list_posts(character.entity_id)
```

## Immutable Models

Entity models are Pydantic objects. You don't mutate them directly — instead, pass updated fields to the manager's `update()` method, which returns a new object:

```python
character = client.characters.get(123)

# Don't do this — it won't save to the API:
# character.name = "New Name"

# Do this instead:
character = client.characters.update(character, name="New Name")
```

## Extra Fields

All models use Pydantic's `extra="allow"` configuration. This means any fields returned by the API that aren't explicitly defined in the model are preserved on the object, not discarded. This ensures forward compatibility when the Kanka API adds new fields.

## Supported Entity Types

The SDK currently supports 12 entity types:

| Manager | Model | Description |
|---------|-------|-------------|
| `client.calendars` | `Calendar` | Custom calendar systems |
| `client.characters` | `Character` | NPCs, PCs, and other persons |
| `client.creatures` | `Creature` | Monsters, animals, beasts |
| `client.events` | `Event` | Historical or campaign events |
| `client.families` | `Family` | Dynasties, houses, clans |
| `client.journals` | `Journal` | Session notes, chronicles |
| `client.locations` | `Location` | Places, regions, buildings |
| `client.notes` | `Note` | General notes and documentation |
| `client.organisations` | `Organisation` | Guilds, governments, companies |
| `client.quests` | `Quest` | Missions and objectives |
| `client.races` | `Race` | Species, ethnicities |
| `client.tags` | `Tag` | Labels for organizing content |

The Kanka API also supports entity types not yet implemented in this SDK, including: Timeline, Item, Relation, DiceRoll, Conversation, AttributeTemplate, Bookmark, Ability, Map, and Inventory.
