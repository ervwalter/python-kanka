# Last Sync

The Kanka API provides a synchronization mechanism that lets you efficiently fetch only entities that have changed since your last request. This avoids repeatedly downloading your entire campaign and is essential for applications that need to keep a local cache or database in sync with Kanka.

## How It Works

Every list response from the Kanka API includes a top-level `sync` timestamp. This timestamp represents the exact moment the server processed your request. To get only entities that changed since then, pass that timestamp back as the `last_sync` parameter on your next request. The API returns only entities created or modified after that timestamp.

The workflow is:

1. **Initial fetch** — Call the API without `last_sync`. Capture the sync timestamp from the response.
2. **Subsequent fetches** — Call the API with `last_sync` set to the previously captured value. Only modified entities are returned. Capture the new sync timestamp for next time.
3. **Repeat** — Each call gives you a new sync timestamp to use on the next call.

## Using last_sync with Entity Managers

The `last_sync` parameter is a named parameter on all entity manager `list()` calls. After each call, the sync timestamp is available via the `last_sync` property.

```python
from kanka import KankaClient

client = KankaClient(token="your-token", campaign_id=12345)

# Initial fetch — get all characters
characters = client.characters.list(page=1, limit=100)
sync_timestamp = client.characters.last_sync
print(f"Fetched {len(characters)} characters")
print(f"Sync timestamp: {sync_timestamp}")

# ... later, fetch only characters that changed ...
updated = client.characters.list(last_sync=sync_timestamp)
new_sync = client.characters.last_sync
print(f"{len(updated)} characters changed since last sync")
```

## Using last_sync with the Generic Entities Endpoint

The generic `client.entities()` endpoint also supports `last_sync` as a named parameter. This is useful when you want to sync all entity types at once rather than syncing each type separately. The sync timestamp is available via the `last_entities_sync` property.

```python
# Initial fetch — get all entities
entities = client.entities(page=1, limit=100)
sync_timestamp = client.last_entities_sync

# ... later, fetch only entities that changed ...
updated = client.entities(last_sync=sync_timestamp)
new_sync = client.last_entities_sync
print(f"{len(updated)} entities changed since last sync")
```

## Paginating with last_sync

When your campaign has more entities than fit in a single page, you need to paginate through all pages on both the initial fetch and on subsequent syncs. Use the same `last_sync` value across all pages of a single sync operation, and capture the sync timestamp from the **first** page to use for the next sync.

```python
def sync_all_characters(client, last_sync=None):
    """Fetch all characters, optionally only those changed since last_sync."""
    all_characters = []
    page = 1
    next_sync = None

    while True:
        batch = client.characters.list(
            page=page, limit=100, last_sync=last_sync
        )
        all_characters.extend(batch)

        # Capture sync timestamp from the first page
        if page == 1:
            next_sync = client.characters.last_sync

        if not client.characters.has_next_page:
            break
        page += 1

    return all_characters, next_sync


# Initial full sync
characters, sync_timestamp = sync_all_characters(client)
print(f"Full sync: {len(characters)} characters")

# ... time passes, entities are modified in Kanka ...

# Incremental sync — only fetches what changed
changed, sync_timestamp = sync_all_characters(client, last_sync=sync_timestamp)
print(f"Incremental sync: {len(changed)} characters changed")
```

## Persisting the Sync Timestamp

For the sync pattern to work across application restarts, you need to persist the sync timestamp. How you store it depends on your application — a file, database, or configuration store all work:

```python
import json
from pathlib import Path

SYNC_FILE = Path("kanka_sync_state.json")


def load_sync_state():
    """Load the last sync timestamp from disk."""
    if SYNC_FILE.exists():
        return json.loads(SYNC_FILE.read_text())
    return {}


def save_sync_state(state):
    """Save the sync timestamp to disk."""
    SYNC_FILE.write_text(json.dumps(state, indent=2))


# Load previous state
state = load_sync_state()

# Sync characters
characters, new_sync = sync_all_characters(
    client, last_sync=state.get("characters_sync")
)
state["characters_sync"] = new_sync

# Save state for next run
save_sync_state(state)
```

## Important Notes

- **The sync timestamp is server-generated.** Always use the value from the API response rather than generating your own timestamp. This avoids clock skew issues between your machine and the Kanka server.
- **`last_sync` filters by modification time.** It returns entities that were created or updated after the given timestamp. It does **not** tell you about deleted entities.
- **Deleted entities are not included.** The `last_sync` response only contains entities that still exist. If you maintain a local cache, you may need a separate mechanism to detect deletions (e.g., periodically doing a full sync and comparing IDs).
- **Use ISO 8601 format.** The sync value from the API is already in the correct format. If you construct a timestamp manually, use full ISO 8601 with timezone (e.g., `2026-02-25T01:35:39.768695Z`).
- **Works with all filters.** You can combine `last_sync` with other filters like `type`, `name`, or `tags`. The API returns entities matching all filters that were also modified after the `last_sync` timestamp.
