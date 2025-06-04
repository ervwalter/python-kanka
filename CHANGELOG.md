# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-01-06

### Added

- Complete rewrite with Pydantic v2 models for robust data validation
- Type-safe entity managers for all Kanka entity types
- Full CRUD support for all implemented entities
- Entity posts/notes management through dedicated methods
- Advanced filtering with type-safe parameters
- Comprehensive error handling with specific exception types
- Full type hints and IDE autocomplete support
- Search functionality across all entity types
- Pagination support with metadata access
- Related data loading (posts, attributes) with `related=True`
- Direct access to generic `/entities` endpoint
- Support for all major entity types:
  - Characters, Locations, Organisations, Families
  - Calendars, Timelines, Races, Creatures
  - Events, Journals, Tags, Notes, Quests, Items
  - Maps, Abilities, Conversations, Relations
  - DiceRolls, AttributeTemplates, Bookmarks
- Development tools: black, isort, ruff, pytest
- Comprehensive test suite with pytest
- Pre-commit hooks for code quality

### Changed

- **BREAKING**: Complete API redesign - not compatible with v0.x
- **BREAKING**: Moved from procedural to object-oriented API
- **BREAKING**: Campaign is now part of client initialization
- **BREAKING**: Entity updates now return new objects (immutable)
- **BREAKING**: Renamed some methods for consistency
- Minimum Python version is now 3.8
- All models are now Pydantic BaseModel subclasses
- Consistent naming and structure across all entities
- Better separation of concerns with dedicated managers

### Removed

- **BREAKING**: Removed old Campaign class
- **BREAKING**: Removed direct entity mutation
- **BREAKING**: Removed upload() method - use create/update instead
- Legacy procedural API completely removed

### Migration Notes

The v2.0 release is a complete rewrite and is not backwards compatible with v0.x. Key changes:

1. **Initialize client differently**:
   ```python
   # Old
   client = kanka.KankaClient(token)
   campaign = client.campaign(campaign_id)
   
   # New
   client = KankaClient(token, campaign_id)
   ```

2. **Access entities through managers**:
   ```python
   # Old
   char = campaign.character(char_id)
   
   # New
   char = client.characters.get(char_id)
   ```

3. **Updates return new objects**:
   ```python
   # Old
   char.name = "New Name"
   char.update()
   
   # New
   char = client.characters.update(char, name="New Name")
   ```

4. **Create entities with manager**:
   ```python
   # Old
   char = campaign.new_entity("character")
   char.name = "Gandalf"
   char.upload()
   
   # New
   char = client.characters.create(name="Gandalf")
   ```

5. **Search uses client method**:
   ```python
   # Old
   results = campaign.search("term")
   
   # New
   results = client.search("term")
   ```

See the README.md migration guide for more details.

## [0.0.1] - Previous version

Initial release with basic Kanka API support.