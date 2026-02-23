# Entity CRUD Operations

All 12 entity types share the same interface through the `EntityManager` class. This guide uses characters as the example, but the same methods work for all entity types.

## Getting a Single Entity

```python
character = client.characters.get(123)
print(character.name)
print(character.title)
```

### Including Related Data

Pass `related=True` to include posts and attributes on the returned entity:

```python
character = client.characters.get(123, related=True)

# Posts are populated as a list
if character.posts:
    for post in character.posts:
        print(f"{post.name}: {post.entry[:50]}...")

# Custom attributes
if character.attributes:
    for attr in character.attributes:
        print(attr)
```

## Listing Entities

```python
# Basic list (first page, 30 results)
characters = client.characters.list()

# With pagination
characters = client.characters.list(page=2, limit=50)

# With related data
characters = client.characters.list(related=True)
```

### Filtering

```python
# Filter by name (partial match)
characters = client.characters.list(name="Gandalf")

# Filter by type
wizards = client.characters.list(type="Wizard")

# Filter by privacy
public = client.characters.list(is_private=False)

# Filter by tags
tagged = client.characters.list(tags=[1, 2, 3])

# Filter by creator
mine = client.characters.list(created_by=42)

# Filter by date
recent = client.characters.list(updated_at=">=2024-01-01")

# Combine filters
results = client.characters.list(
    type="NPC",
    is_private=False,
    tags=[15],
    page=1,
    limit=50,
)
```

### The `lastSync` Filter

Use the `lastSync` filter with an ISO 8601 timestamp to retrieve only entities modified after a specific time. This is useful for synchronization workflows:

```python
from datetime import datetime, timedelta, timezone

last_sync = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
updated = client.characters.list(lastSync=last_sync, related=True)
```

### Iterating All Pages

```python
all_characters = []
page = 1

while True:
    batch = client.characters.list(page=page)
    all_characters.extend(batch)
    if not client.characters.has_next_page:
        break
    page += 1

print(f"Total: {len(all_characters)} characters")
```

See [Pagination](pagination.md) for more details.

## Creating Entities

Create entities using keyword arguments. The `name` field is required for all entity types:

```python
character = client.characters.create(
    name="Gandalf the Grey",
    title="Wizard",
    type="Istari",
    age="2000+",
    is_private=False,
)

location = client.locations.create(
    name="Rivendell",
    type="City",
    entry="<p>The Last Homely House East of the Sea</p>",
    parent_location_id=middle_earth.id,
)

tag = client.tags.create(
    name="Important NPC",
    colour="red",
)
```

### Creating with Images

You can embed local images in the `entry` HTML. The SDK uploads them as entity assets and rewrites the `<img src>` tags to CDN URLs:

```python
character = client.characters.create(
    name="Hero",
    entry='<p><img src="portrait.png" /> The brave hero.</p>',
    images={"portrait.png": "/path/to/portrait.png"},
)
```

See [Assets and Images](assets-and-images.md) for details.

## Updating Entities

Pass the entity object (or its ID) and the fields to change:

```python
# Update by entity object (preferred — only changed fields are sent)
character = client.characters.get(123)
updated = client.characters.update(character, title="The White")

# Update by ID (sends all provided fields)
updated = client.characters.update(123, title="The White")
```

When passing an entity object, the SDK computes a diff and only sends fields that actually changed. When passing an integer ID, all provided keyword arguments are sent.

The `update()` method returns a new entity object with the updated data. The original is not modified.

## Deleting Entities

```python
# Delete by entity object
client.characters.delete(character)

# Delete by ID
client.characters.delete(123)
```

Returns `True` on success. Raises `NotFoundError` if the entity doesn't exist.

## Complete Lifecycle Example

```python
from kanka import KankaClient

client = KankaClient(token="...", campaign_id=12345)

# Create
character = client.characters.create(
    name="Frodo Baggins",
    type="Hobbit",
    title="Ring-bearer",
    age="50",
)
print(f"Created: {character.name} (ID: {character.id})")

# Read
retrieved = client.characters.get(character.id)
print(f"Retrieved: {retrieved.name}")

# Update
updated = client.characters.update(character, title="Hero of Middle-earth")
print(f"Updated title: {updated.title}")

# List
hobbits = client.characters.list(type="Hobbit")
print(f"Found {len(hobbits)} hobbits")

# Delete
client.characters.delete(updated)
print("Deleted successfully")
```

## Works the Same for All Entity Types

```python
# Locations
rivendell = client.locations.create(name="Rivendell", type="City")

# Organisations
fellowship = client.organisations.create(name="The Fellowship", type="Party")

# Journals
journal = client.journals.create(name="Session 1", date="3019-03-25")

# Notes
note = client.notes.create(name="DM Notes", is_private=True)

# Tags
tag = client.tags.create(name="Important", colour="red")

# Quests
quest = client.quests.create(name="Destroy the Ring", type="Main Quest")

# Events
battle = client.events.create(name="Battle of Pelennor Fields", date="March 15")

# Families
house = client.families.create(name="House Baggins", type="Hobbit Family")

# Races
elves = client.races.create(name="Elves", type="Immortal Race")

# Creatures
balrog = client.creatures.create(name="Balrog", type="Demon")

# Calendars
calendar = client.calendars.create(name="Shire Reckoning", type="Regional")
```

See [Entity Types Reference](entity-types-reference.md) for the specific fields available on each entity type.
