# python-kanka

A modern Python client for the [Kanka API](https://app.kanka.io/api-docs/1.0), the collaborative worldbuilding and campaign management platform.

*Originally inspired by/forked from [Kathrin Weihe's python-kanka](https://github.com/rbtnx/python-kanka). Thank you to Kathrin for the foundation and inspiration.*

## Features

- **Entity Support**: Support for 12 core Kanka entity types:
  - Characters, Locations, Organisations, Families
  - Calendars, Events, Quests, Journals
  - Notes, Tags, Races, Creatures
- **Type Safety**: Built with Pydantic v2 for data validation and type hints
- **Python 3.9+**: Full typing support for modern Python versions
- **Pythonic API**: Consistent interface patterns across all entity types
- **Error Handling**: Specific exception types for different API errors
- **Rate Limit Handling**: Automatic retry with exponential backoff
- **Entity Posts**: Support for entity posts/comments management
- **Filtering and Search**: Filter entities by various criteria and search across types
- **Pagination**: Built-in pagination support for large result sets

## Installation

Install from PyPI:
```bash
pip install python-kanka
```

Or install from source:
```bash
git clone https://github.com/ervwalter/python-kanka.git
cd python-kanka
pip install -e .
```

## Quick Start

```python
from kanka import KankaClient

# Initialize the client
client = KankaClient(
    token="your-api-token",      # Get from https://app.kanka.io/settings/api
    campaign_id=12345            # Your campaign ID
)

# Create a character
gandalf = client.characters.create(
    name="Gandalf the Grey",
    title="Wizard",
    type="Istari",
    age="2000+ years",
    is_private=False
)

# Update the character
gandalf = client.characters.update(
    gandalf,
    name="Gandalf the White"
)

# Search across all entities
results = client.search("Dragon")
for result in results:
    print(f"{result.name} ({result.type})")

# List characters with filters
wizards = client.characters.list(
    type="Wizard",
    is_private=False
)

# Delete when done
client.characters.delete(gandalf)
```

## Common Use Cases

### Working with Entity Posts

```python
# Get a character
character = client.characters.get(character_id)

# Create a new post/note (pass the entity object, not just ID)
post = client.characters.create_post(
    character,  # Pass the full entity object
    name="Background",
    entry="*Born in the ancient times...*",
    is_private=False
)

# List all posts for an entity
posts = client.characters.list_posts(character)
for post in posts:
    print(f"{post.name}: {post.entry[:50]}...")

# Update a post (name field is required even if not changing)
update = client.characters.update_post(
    character,
    post.id,
    name=post.name,  # Required by API
    entry="Updated content..."
)
```

### Advanced Filtering

```python
# Filter by multiple criteria
results = client.characters.list(
    name="Gandalf",          # Partial name match
    type="Wizard",           # Exact type match
    is_private=False,        # Only public entities
    tags=[15, 23],          # Has specific tags
    page=1,                 # Pagination
    limit=30                # Results per page
)

# Access the generic entities endpoint
entities = client.entities(
    types=["character", "location"],  # Multiple entity types
    name="Dragon",                    # Name filter
    tags=[15, 23],                   # Tag filter
    is_private=False
)
```

### Working with Multiple Entity Types

All entity types follow the same pattern:

```python
# Locations
rivendell = client.locations.create(
    name="Rivendell",
    type="City",
    parent_location_id=middle_earth.id
)

# Organizations
council = client.organisations.create(
    name="The White Council",
    type="Council"
)

# Journals
journal = client.journals.create(
    name="Campaign Log",
    date="3019-03-25"
)

# Notes (for DM/private notes)
note = client.notes.create(
    name="DM Notes",
    entry="Remember: Gandalf knows about the ring",
    is_private=True
)

# Tags
tag = client.tags.create(
    name="Important NPC",
    colour="#ff0000"
)
```

### Error Handling

```python
from kanka.exceptions import (
    NotFoundError,
    ValidationError,
    RateLimitError,
    AuthenticationError
)

try:
    character = client.characters.get(99999)
except NotFoundError:
    print("Character not found")
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds")
except ValidationError as e:
    print(f"Invalid data: {e.errors}")
except AuthenticationError:
    print("Invalid API token")
```

## Rate Limiting

The client automatically handles API rate limits by retrying requests with exponential backoff:

```python
# Default behavior - automatic retry on rate limits
client = KankaClient(token, campaign_id)

# Disable automatic retry
client = KankaClient(
    token,
    campaign_id,
    enable_rate_limit_retry=False
)

# Customize retry behavior
client = KankaClient(
    token,
    campaign_id,
    max_retries=5,              # Try up to 5 times (default: 3)
    retry_delay=2.0,            # Initial delay in seconds (default: 1.0)
    max_retry_delay=120.0       # Maximum delay between retries (default: 60.0)
)
```

The client parses rate limit headers from the API to determine retry delays and respects the API's rate limits.

## Migration Guide

### Upgrading from v0.x to v2.0

The v2.0 release introduces a new API design with Pydantic models and type safety. Here's how to migrate:

#### Old API (v0.x)
```python
# Old way - procedural API
import kanka
client = kanka.KankaClient(token)
campaign = client.campaign(campaign_id)
char = campaign.character(char_id)
char.name = "New Name"
char.update()
```

#### New API (v2.0+)
```python
# New way - object-oriented with managers
from kanka import KankaClient
client = KankaClient(token, campaign_id)
char = client.characters.get(char_id)
char = client.characters.update(char, name="New Name")
```

### Key Differences

1. **Single Client**: No more separate campaign object - everything through `KankaClient`
2. **Entity Managers**: Each entity type has a dedicated manager (`client.characters`, `client.locations`, etc.)
3. **Immutable Models**: Models are Pydantic objects - use manager methods to update
4. **Better Types**: Full typing support with IDE autocomplete
5. **Consistent API**: All entities follow the same CRUD pattern

## Development Setup

For development, install additional dependencies:

```bash
# Clone the repository
git clone https://github.com/ervwalter/python-kanka.git
cd python-kanka

# Install dev dependencies
pip install -r dev-requirements.txt
pip install -e .  # Install in editable mode
```

### Development Tools

This project uses several tools to maintain code quality:

- **black** - Code formatter
- **isort** - Import sorter
- **ruff** - Fast Python linter
- **pytest** - Testing framework
- **mypy** - Static type checker

Use the Makefile for common development tasks:

```bash
make install   # Install all dependencies
make format    # Format code with black and isort
make lint      # Run linting checks
make test      # Run all tests
make coverage  # Run tests with coverage report
make check     # Run all checks (lint + test)
make clean     # Clean up temporary files
```

### Pre-commit Hooks (Optional)

To automatically run formatting and linting before each commit:

```bash
pre-commit install
```

## API Documentation

See the [API Reference](API_REFERENCE.md) for detailed documentation of all classes and methods.

## Examples

Check out the [examples/](examples/) directory for more detailed examples:

- `quickstart.py` - Basic usage tutorial
- `crud_operations.py` - Full CRUD examples for all entity types
- `filtering.py` - Advanced filtering and search
- `posts.py` - Working with entity posts
- `error_handling.py` - Proper error handling patterns
- `migration.py` - Migrating from the old API

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Links

- [Kanka.io](https://kanka.io) - The Kanka platform
- [Kanka API Documentation](https://app.kanka.io/api-docs/1.0) - Official API docs
- [GitHub Repository](https://github.com/ervwalter/python-kanka) - Source code
- [Issue Tracker](https://github.com/ervwalter/python-kanka/issues) - Report bugs or request features
