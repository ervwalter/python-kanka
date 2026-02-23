# Assets and Images

The SDK provides three related features for managing files and images on entities:

1. **Entity Assets** — Attach files, links, or aliases to entities
2. **Entity Images** — Set the main image and header image for entities
3. **Automatic Image Management** — Upload local images referenced in HTML content

All three use the `entity_id` (universal ID), not the type-specific `id`. When you pass an entity object, the SDK handles this automatically.

---

## Entity Assets

Assets are files, links, or aliases attached to an entity. Each asset has a `type_id`:

| `type_id` | Type | Description |
|-----------|------|-------------|
| `1` | File | An uploaded file (images, documents, etc.) |
| `2` | Link | A URL reference |
| `3` | Alias | An alternative name for the entity |

### Listing Assets

```python
character = client.characters.get(123)
assets = client.characters.list_assets(character)

for asset in assets:
    print(f"{asset.name} (type: {asset.type_id})")
    if asset.url:
        print(f"  URL: {asset.url}")
```

Supports pagination:

```python
assets = client.characters.list_assets(character, page=1, limit=10)
meta = client.characters.last_assets_meta
```

### Getting a Specific Asset

```python
asset = client.characters.get_asset(character, asset_id=42)
```

### Uploading File Assets

```python
asset = client.characters.create_file_asset(
    character,
    "/path/to/map.png",
    name="Character Map",         # Defaults to filename stem
    visibility_id=1,              # Optional: visibility setting
    is_pinned=True,               # Optional: pin the asset
)
print(asset.url)  # CDN URL for the uploaded file
```

### Creating Link Assets

```python
asset = client.characters.create_link_asset(
    character,
    name="Character Sheet",
    url="https://dndbeyond.com/characters/12345",
    icon="fa-link",               # Optional: FontAwesome icon class
    visibility_id=1,
)
```

### Creating Alias Assets

Aliases provide alternative names for an entity, useful for search:

```python
asset = client.characters.create_alias_asset(
    character,
    name="Strider",               # Alternative name
    visibility_id=1,
)
```

### Deleting Assets

```python
client.characters.delete_asset(character, asset.id)

# Also delete the underlying gallery image to prevent orphans:
client.characters.delete_asset(character, asset.id, delete_gallery_image=True)
```

### EntityAsset Model Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | `int` | Asset ID |
| `entity_id` | `int` | Parent entity ID |
| `name` | `str` | Asset name |
| `type_id` | `int` | Asset type (1=file, 2=link, 3=alias) |
| `visibility_id` | `int \| None` | Visibility setting |
| `is_pinned` | `bool` | Whether pinned (default: `False`) |
| `is_private` | `bool` | Whether private (default: `False`) |
| `metadata` | `dict \| None` | Additional metadata (e.g., URL for links) |
| `url` | `str \| None` | CDN URL for file assets (aliased from API's `_url` field) |
| `created_at` | `datetime \| None` | Creation timestamp |
| `created_by` | `int \| None` | Creator user ID |
| `updated_at` | `datetime \| None` | Last update timestamp |
| `updated_by` | `int \| None` | Last updater user ID |

---

## Entity Images

Every entity can have a **main image** and a **header image**. These are separate from file assets.

### Getting Image Information

```python
character = client.characters.get(123)
info = client.characters.get_image(character)

if info.image:
    print(f"Image UUID: {info.image.uuid}")
    print(f"Full URL: {info.image.full}")
    print(f"Thumbnail: {info.image.thumbnail}")

if info.header:
    print(f"Header URL: {info.header.full}")
```

### Setting the Main Image

```python
info = client.characters.set_image(character, "/path/to/portrait.png")
print(info.image.full)  # CDN URL
```

### Setting the Header Image

```python
info = client.characters.set_image(
    character,
    "/path/to/banner.png",
    is_header=True,
)
print(info.header.full)
```

### Deleting Images

```python
# Delete main image
client.characters.delete_image(character)

# Delete header image
client.characters.delete_image(character, is_header=True)
```

### Image Model Fields

**EntityImageInfo:**

| Field | Type | Description |
|-------|------|-------------|
| `image` | `EntityImageData \| None` | Main entity image |
| `header` | `EntityImageData \| None` | Entity header image |

**EntityImageData:**

| Field | Type | Description |
|-------|------|-------------|
| `uuid` | `str \| None` | Image UUID in gallery |
| `full` | `str \| None` | Full-size image URL |
| `thumbnail` | `str \| None` | Thumbnail image URL |

---

## Automatic Image Management

The `images` parameter on `create()`, `update()`, `create_post()`, and `update_post()` provides a convenient way to embed local images in HTML content. The SDK uploads files as entity assets and rewrites `<img src>` tags to use CDN URLs.

### How It Works

The `images` dict maps placeholder `src` values in your HTML to local file paths:

```python
character = client.characters.create(
    name="Hero",
    entry='<p><img src="portrait.png" /> The brave hero.</p>',
    images={"portrait.png": "/path/to/portrait.png"},
)
# Result: entry HTML has src="portrait.png" rewritten to a CDN URL
```

### Managed Asset Naming

The SDK uses a naming convention for assets it manages: `{name}:{sha256_first12}`. For example, `portrait:a1b2c3d4e5f6`. This naming convention:

- Tracks which assets are SDK-managed vs user-created
- Enables change detection by comparing file hashes
- Non-managed assets (those you create manually) are never modified

### Change Detection on Update

When you call `update()` or `update_post()` with `images`, the SDK compares file hashes:

- **Unchanged files** (same SHA-256 hash) — reused without re-uploading
- **Changed files** (different hash) — old asset deleted (along with its gallery image), new one uploaded
- **Orphaned managed assets** (no longer referenced in `images` dict) — automatically cleaned up (both entity asset and gallery image)
- **Non-managed assets** (user-created assets without the hash suffix) — never touched

### Full Lifecycle Example

```python
# Create with images
character = client.characters.create(
    name="Hero",
    entry='<p><img src="portrait.png" /> The brave hero.</p>',
    images={"portrait.png": "/path/to/portrait.png"},
)

# Update with a different image file
character = client.characters.update(
    character,
    entry='<p><img src="portrait.png" /> The brave hero returns.</p>',
    images={"portrait.png": "/path/to/new_portrait.png"},  # Different file
)
# Old asset is deleted, new one uploaded

# Add more images
character = client.characters.update(
    character,
    entry='<p><img src="portrait.png" /><img src="map.png" /></p>',
    images={
        "portrait.png": "/path/to/new_portrait.png",  # Reused (same hash)
        "map.png": "/path/to/dungeon_map.png",         # New upload
    },
)

# Remove an image by omitting it from the dict
character = client.characters.update(
    character,
    entry='<p><img src="portrait.png" /></p>',
    images={"portrait.png": "/path/to/new_portrait.png"},
    # map.png is no longer in images dict — its managed asset is deleted
)
```

### Works with Posts Too

```python
post = client.characters.create_post(
    character,
    "Session Notes",
    '<p><img src="map.png" /> We explored the dungeon.</p>',
    images={"map.png": "/path/to/dungeon_map.png"},
)

# Update post with changed image
client.characters.update_post(
    character,
    post.id,
    name="Session Notes",
    entry='<p><img src="map.png" /> Updated notes.</p>',
    images={"map.png": "/path/to/updated_map.png"},
)
```
