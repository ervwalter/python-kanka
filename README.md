# python-kanka

A modern Python client for the [Kanka API](https://app.kanka.io/api-docs/1.0), the collaborative worldbuilding and campaign management platform.

*Originally inspired by/forked from [Kathrin Weihe's python-kanka](https://github.com/rbtnx/python-kanka). Thank you to Kathrin for the foundation and inspiration.*

## Features

- **12 Entity Types**: Characters, Locations, Organisations, Families, Calendars, Events, Quests, Journals, Notes, Tags, Races, Creatures
- **Type Safety**: Built with Pydantic v2 for data validation and type hints
- **Consistent API**: Same CRUD interface across all entity types
- **Posts, Assets & Images**: Full support for entity sub-resources and automatic image management
- **Search & Filtering**: Search across types, filter by name/tags/privacy/dates
- **Rate Limit Handling**: Automatic retry with exponential backoff
- **Pagination**: Built-in pagination support with metadata

## Installation

```bash
pip install python-kanka
```

## Quick Start

```python
from kanka import KankaClient

client = KankaClient(token="your-api-token", campaign_id=12345)

# Create a character
gandalf = client.characters.create(
    name="Gandalf the Grey",
    type="Wizard",
    title="Istari",
)

# List with filters
wizards = client.characters.list(type="Wizard", is_private=False)

# Search across all entity types
results = client.search("dragon")

# Update and delete
gandalf = client.characters.update(gandalf, title="The White")
client.characters.delete(gandalf)
```

## Documentation

See the **[full documentation](https://python-kanka.ewal.dev/)** for guides, examples, and complete API reference.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Links

- [Kanka.io](https://kanka.io) - The Kanka platform
- [Kanka API Documentation](https://app.kanka.io/api-docs/1.0) - Official API docs
- [GitHub Repository](https://github.com/ervwalter/python-kanka) - Source code
- [Issue Tracker](https://github.com/ervwalter/python-kanka/issues) - Report bugs or request features
