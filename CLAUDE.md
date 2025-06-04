# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Key Development Commands

```bash
# Install development environment
make install

# Run unit tests only (no integration tests)
make test

# Run integration tests (requires KANKA_TOKEN and KANKA_CAMPAIGN_ID)
cd tests/integration
python run_integration_tests.py

# Run a single integration test file (loads .env automatically)
python tests/integration/test_characters_integration.py

# Format code
make format

# Run all linting checks
make lint

# Run type checking
make typecheck

# Run everything (lint + typecheck + tests)
make check

# Generate coverage report
make coverage
```

## Architecture Overview

The SDK follows a **Client → Manager → Model** pattern that requires understanding across multiple files:

1. **KankaClient** (`client.py`): Entry point that instantiates entity managers
   - Each entity type gets a property that returns an `EntityManager[T]` instance
   - Handles authentication and base request logic

2. **EntityManager[T]** (`managers.py`): Generic manager for CRUD operations
   - Type-safe operations via TypeVar bound to Entity
   - Handles both entity operations and sub-resource posts
   - Critical: Posts use `entity_id`, not the type-specific ID

3. **Model Hierarchy** (`models/`):
   - `base.py`: KankaModel → Entity base classes
   - `entities.py`: All entity types inherit from Entity
   - `common.py`: Shared models like Post, SearchResult

## Integration Testing Notes

Integration tests are NOT pytest tests - they have custom runners:
- Use `python test_*.py` to run individual test files
- Tests create real data with "Integration Test - DELETE ME" markers
- Environment setup required:
  ```bash
  export KANKA_TOKEN='your-token'
  export KANKA_CAMPAIGN_ID='your-campaign-id'
  # Or create tests/integration/.env file
  ```

## Critical Implementation Details

1. **Posts API Structure**: Posts are accessed via `/entities/{entity_id}/posts`, not `/{entity_type}/{id}/posts`. The `entity_id` field from any entity must be used, not the type-specific `id`.

2. **Field Handling**:
   - `updated_by` can be null from the API
   - `traits` field returns empty list `[]`, not string
   - Post updates require `name` field even if unchanged
   - HTML content is normalized by API (quotes converted)

3. **Entity Types**: Current valid types are:
   - Core: Character, Location, Organisation, Family, Calendar, Timeline, Race
   - Items: Item, Note, Event, Quest, Journal, Tag, Relation
   - Extra: DiceRoll, Conversation, AttributeTemplate, Bookmark
   - Removed: EntityNote, EntityEvent, Attribute, Species (don't exist in API)

## Development Preferences

- When executing test scripts with long output, redirect to file for parsing
- Don't push to origin during long tasks - let user do it manually
- Test frequently during complex refactoring
- Clean up temporary test files after use
- Don't leave comments explaining removed/moved code
- Use python-dotenv for environment variables: `load_dotenv()`

## Testing Without Breaking Production

When testing against the real API:
1. Always use "Integration Test - DELETE ME" in entity names
2. Clean up created entities in teardown methods
3. Use wait_for_api() between operations to avoid rate limits
4. Integration tests track created IDs for cleanup