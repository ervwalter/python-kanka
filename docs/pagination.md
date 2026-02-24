# Pagination

All list endpoints in the SDK support pagination. By default, results are returned 30 per page.

## Basic Usage

```python
# First page, 30 results (defaults)
characters = client.characters.list()

# Specific page and limit
characters = client.characters.list(page=2, limit=50)
```

## Pagination Metadata

After any list call, pagination metadata is available on the manager:

```python
characters = client.characters.list(page=1)

meta = client.characters.pagination_meta
print(f"Current page: {meta['current_page']}")
print(f"Last page: {meta['last_page']}")
print(f"Per page: {meta['per_page']}")
print(f"Total: {meta['total']}")
print(f"From: {meta['from']}")
print(f"To: {meta['to']}")

links = client.characters.pagination_links
print(f"First: {links['first']}")
print(f"Last: {links['last']}")
print(f"Prev: {links.get('prev')}")   # None on first page
print(f"Next: {links.get('next')}")   # None on last page
```

### Quick Next-Page Check

```python
if client.characters.has_next_page:
    print("More pages available")
```

## Iterating All Pages

```python
all_characters = []
page = 1

while True:
    batch = client.characters.list(page=page)
    all_characters.extend(batch)
    if not client.characters.has_next_page:
        break
    page += 1

print(f"Total characters: {len(all_characters)}")
```

## Pagination Properties by Endpoint

Each list endpoint stores its own pagination state:

### Entity Lists

| Property | Aliases | Description |
|----------|---------|-------------|
| `manager.pagination_meta` | `manager.last_page_meta` | Metadata from last `list()` |
| `manager.pagination_links` | `manager.last_page_links` | Links from last `list()` |
| `manager.has_next_page` | — | `True` if next page exists |

### Posts

| Property | Description |
|----------|-------------|
| `manager.last_posts_meta` | Metadata from last `list_posts()` |
| `manager.last_posts_links` | Links from last `list_posts()` |

### Assets

| Property | Description |
|----------|-------------|
| `manager.last_assets_meta` | Metadata from last `list_assets()` |
| `manager.last_assets_links` | Links from last `list_assets()` |

### Entities

| Property | Description |
|----------|-------------|
| `client.last_entities_meta` | Metadata from last `entities()` |
| `client.last_entities_links` | Links from last `entities()` |
| `client.entities_has_next_page` | `True` if next page exists |

### Gallery

| Property | Description |
|----------|-------------|
| `client.last_gallery_meta` | Metadata from last `gallery()` |
| `client.last_gallery_links` | Links from last `gallery()` |

### Search

| Property | Description |
|----------|-------------|
| `client.last_search_meta` | Metadata from last `search()` |
| `client.last_search_links` | Links from last `search()` |

## Metadata Fields

All pagination metadata dictionaries contain:

| Field | Type | Description |
|-------|------|-------------|
| `current_page` | `int` | Current page number |
| `from` | `int` | Starting record number on this page |
| `to` | `int` | Ending record number on this page |
| `last_page` | `int` | Total number of pages |
| `per_page` | `int` | Records per page |
| `total` | `int` | Total number of records |

All pagination links dictionaries contain:

| Field | Type | Description |
|-------|------|-------------|
| `first` | `str` | URL to first page |
| `last` | `str` | URL to last page |
| `prev` | `str \| None` | URL to previous page (null on first page) |
| `next` | `str \| None` | URL to next page (null on last page) |

## Known Limitation

The search endpoint (`client.search()`) does not respect the `limit` parameter. The API returns a fixed number of results per page regardless of any limit specified. Pagination is available only through the `page` parameter.
