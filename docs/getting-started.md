# Getting Started

## Prerequisites

- **Python 3.12+**
- A [Kanka](https://kanka.io) account
- A Kanka API personal access token
- A campaign ID

### Getting Your API Token

1. Log in to [Kanka](https://app.kanka.io)
2. Go to **Settings > API** ([direct link](https://app.kanka.io/settings/api))
3. Create a new personal access token
4. Copy and store the token securely

### Finding Your Campaign ID

Your campaign ID is the number in the URL when viewing your campaign:
```
https://app.kanka.io/w/12345/...
                         ^^^^^
                         This is your campaign ID
```

## Installation

### From PyPI

```bash
pip install python-kanka
```

### From Source

```bash
git clone https://github.com/ervwalter/python-kanka.git
cd python-kanka
uv sync --all-groups
uv pip install -e .
```

## Quick Start

```python
from kanka import KankaClient

# Initialize the client
client = KankaClient(
    token="your-api-token",
    campaign_id=12345
)

# List characters
characters = client.characters.list()
for char in characters:
    print(f"{char.name} (ID: {char.id})")

# Create a character
gandalf = client.characters.create(
    name="Gandalf",
    title="The Grey",
    type="Wizard",
    age="2000+",
)

# Update the character
gandalf = client.characters.update(gandalf, title="The White")

# Search across all entity types
results = client.search("dragon")
for result in results:
    print(f"{result.name} ({result.type})")

# Delete when done
client.characters.delete(gandalf)
```

## Managing Credentials

Store your API token and campaign ID in environment variables or a `.env` file rather than hardcoding them:

```python
import os
from dotenv import load_dotenv
from kanka import KankaClient

load_dotenv()

client = KankaClient(
    token=os.environ["KANKA_TOKEN"],
    campaign_id=int(os.environ["KANKA_CAMPAIGN_ID"]),
)
```

`.env` file:
```
KANKA_TOKEN=your-api-token-here
KANKA_CAMPAIGN_ID=12345
```

## Next Steps

- [Core Concepts](core-concepts.md) — understand the SDK architecture
- [Entity CRUD Operations](entities.md) — create, read, update, and delete entities
- [Entity Types Reference](entity-types-reference.md) — see all available entity types and their fields
