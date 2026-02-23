# Campaign Gallery

The campaign gallery is a campaign-level image store, separate from entity-level assets. Gallery images are managed directly through the `KankaClient`, not through entity managers.

## Listing Gallery Images

```python
images = client.gallery()

for image in images:
    if image.is_folder:
        print(f"Folder: {image.name} (ID: {image.id})")
    else:
        print(f"Image: {image.name} ({image.ext}, {image.size} bytes)")
        print(f"  Thumbnail: {image.path}")
```

With pagination:

```python
images = client.gallery(page=1, limit=50)

meta = client.last_gallery_meta
print(f"Total images: {meta['total']}")
print(f"Page {meta['current_page']} of {meta['last_page']}")
```

## Getting a Specific Image

Gallery images use UUID identifiers (strings), not integer IDs:

```python
image = client.gallery_get("550e8400-e29b-41d4-a716-446655440000")
print(image.name)
print(image.path)  # Thumbnail URL
```

## Uploading Images

```python
image = client.gallery_upload("/path/to/image.png")
print(image.id)    # UUID string
print(image.path)  # Thumbnail URL
```

Upload to a specific folder:

```python
image = client.gallery_upload(
    "/path/to/image.png",
    folder_id="folder-uuid-here",
    visibility_id=1,
)
```

## Deleting Images

```python
client.gallery_delete(image.id)  # Pass the UUID string
```

Returns `True` on success.

## GalleryImage Model Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | `str` | UUID identifier |
| `name` | `str \| None` | Image name |
| `is_folder` | `bool` | Whether this is a folder (default: `False`) |
| `folder_id` | `str \| None` | Parent folder UUID |
| `path` | `str \| None` | Thumbnail URL |
| `ext` | `str \| None` | File extension |
| `size` | `int \| None` | File size in bytes |
| `created_at` | `datetime \| None` | Creation timestamp |
| `created_by` | `int \| None` | Creator user ID |
| `updated_at` | `datetime \| None` | Last update timestamp |
| `visibility_id` | `int \| None` | Visibility setting |
| `focus_x` | `int \| None` | Image focus X coordinate |
| `focus_y` | `int \| None` | Image focus Y coordinate |

## Pagination Properties

After calling `client.gallery()`:

- `client.last_gallery_meta` — Pagination metadata (`current_page`, `total`, `last_page`, etc.)
- `client.last_gallery_links` — Pagination URLs (`first`, `last`, `prev`, `next`)
