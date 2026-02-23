# Debug Mode

The SDK can log every API request and response to JSON files, useful for debugging API issues or understanding request/response payloads.

## Enabling Debug Mode

Set the `KANKA_DEBUG_MODE` environment variable:

```bash
export KANKA_DEBUG_MODE=true
```

Optionally specify a custom output directory (default: `kanka_debug`):

```bash
export KANKA_DEBUG_DIR=/path/to/debug/output
```

The debug directory is created automatically when the client initializes.

## Output Format

Each request generates a JSON file named:

```
{counter}_{timestamp}_{method}_{endpoint}.json
```

For example: `0001_20240115_143022_GET_characters.json`

### JSON Structure

```json
{
  "timestamp": "2024-01-15T14:30:22.123456",
  "request_number": 1,
  "request": {
    "method": "GET",
    "url": "https://api.kanka.io/1.0/campaigns/12345/characters",
    "headers": { "Authorization": "Bearer ...", "..." : "..." },
    "params": { "page": 1, "limit": 30 },
    "json": {}
  },
  "response": {
    "status_code": 200,
    "headers": { "..." : "..." },
    "time_seconds": 0.45,
    "body": { "data": [ "..." ] }
  }
}
```

## Usage

```python
import os
os.environ["KANKA_DEBUG_MODE"] = "true"
os.environ["KANKA_DEBUG_DIR"] = "my_debug_output"

from kanka import KankaClient

client = KankaClient(token="...", campaign_id=12345)
client.characters.list()
# Check my_debug_output/ for the request/response JSON file
```

Debug mode is only active when `KANKA_DEBUG_MODE` is set to `"true"` (case-insensitive) at the time the `KankaClient` is instantiated.
