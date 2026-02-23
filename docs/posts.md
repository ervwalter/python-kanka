# Posts

Posts are text entries that can be attached to any entity type. They function as notes, comments, or additional narrative content on an entity. Posts are distinct from the `Note` entity type — posts are a sub-resource available on all entity types.

## Important: entity_id vs id

Posts use the **`entity_id`** (universal ID), not the type-specific `id`. The SDK handles this automatically when you pass an entity object:

```python
character = client.characters.get(123)
print(character.id)         # 123 — type-specific ID
print(character.entity_id)  # 456 — universal entity ID

# Pass the entity object — the SDK extracts entity_id for you
posts = client.characters.list_posts(character)  # Uses entity_id internally
```

If you pass an integer instead of an entity object, it must be the `entity_id`:

```python
# Correct: pass entity_id
posts = client.characters.list_posts(character.entity_id)

# WRONG: passing the type-specific id will look up the wrong entity
# posts = client.characters.list_posts(character.id)  # Don't do this!
```

## Listing Posts

```python
character = client.characters.get(123)
posts = client.characters.list_posts(character)

for post in posts:
    print(f"{post.name} (visibility: {post.visibility_id})")
    print(f"  {post.entry[:100]}...")
```

Supports pagination:

```python
posts = client.characters.list_posts(character, page=1, limit=10)
meta = client.characters.last_posts_meta
print(f"Total posts: {meta['total']}")
```

## Creating Posts

```python
character = client.characters.get(123)

post = client.characters.create_post(
    character,
    name="Background",
    entry="<p>Born in the ancient times...</p>",
)
```

### Visibility

Control who can see a post with the `visibility_id` parameter:

| Value | Meaning |
|-------|---------|
| `1` | All (visible to everyone) |
| `2` | Admin only |
| `3` | Admin and self |
| `4` | Self only |
| `5` | Members only |
| `None` | Uses campaign's default post visibility |

```python
# Admin-only post
post = client.characters.create_post(
    character,
    name="DM Notes",
    entry="<p>Secret plot information...</p>",
    visibility_id=2,
)

# Public post
post = client.characters.create_post(
    character,
    name="Public Knowledge",
    entry="<p>Everyone knows this...</p>",
    visibility_id=1,
)
```

### With Images

Posts support automatic image management, just like entity creation:

```python
post = client.characters.create_post(
    character,
    name="Battle Map",
    entry='<p><img src="map.png" /> The battle took place here.</p>',
    images={"map.png": "/path/to/battle_map.png"},
)
```

See [Assets and Images](assets-and-images.md) for details.

## Getting a Specific Post

```python
post = client.characters.get_post(character, post_id=42)
print(post.name)
print(post.entry)
```

## Updating Posts

The Kanka API **requires the `name` field** even when you're not changing it:

```python
post = client.characters.get_post(character, 42)

updated = client.characters.update_post(
    character,
    post.id,
    name=post.name,           # Required even if not changing!
    entry="<p>Updated content</p>",
)
```

Update visibility:

```python
updated = client.characters.update_post(
    character,
    post.id,
    name=post.name,
    visibility_id=2,  # Change to admin-only
)
```

## Deleting Posts

```python
client.characters.delete_post(character, post.id)
```

## Post Model Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | `int` | Post ID |
| `name` | `str` | Post title |
| `entry` | `str` | Post content (HTML) |
| `entity_id` | `int` | Parent entity's universal ID |
| `visibility_id` | `int \| None` | Visibility setting (1-5) |
| `created_by` | `int` | Creator user ID |
| `updated_by` | `int \| None` | Last updater user ID |
| `created_at` | `datetime` | Creation timestamp |
| `updated_at` | `datetime` | Last update timestamp |

## Posts Work on All Entity Types

The same interface works on every entity manager:

```python
# Posts on locations
client.locations.create_post(location, name="History", entry="...")

# Posts on organisations
client.organisations.create_post(org, name="Member List", entry="...")

# Posts on quests
client.quests.create_post(quest, name="Objectives", entry="...")
```

## Complete Example

```python
# Create a character
character = client.characters.create(
    name="Bilbo Baggins",
    type="Hobbit",
)

# Add posts
backstory = client.characters.create_post(
    character,
    name="Early Life",
    entry="<p>Born in the Shire to Bungo Baggins and Belladonna Took.</p>",
    visibility_id=1,  # Public
)

dm_notes = client.characters.create_post(
    character,
    name="DM Notes",
    entry="<p>Bilbo is starting to show signs of the ring's corruption.</p>",
    visibility_id=2,  # Admin only
)

# List all posts
posts = client.characters.list_posts(character)
print(f"Character has {len(posts)} posts")

# Update a post
client.characters.update_post(
    character,
    backstory.id,
    name="Early Life",  # Required!
    entry="<p>Born in the Shire. Later adventured with dwarves.</p>",
)

# Delete the DM notes
client.characters.delete_post(character, dm_notes.id)
```
