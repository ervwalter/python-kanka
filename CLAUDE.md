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

# Build the package
python -m build

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

3. **Entity Types**:
   - **Implemented in SDK (12 types)**: Calendar, Character, Creature, Event, Family, Journal, Location, Note, Organisation, Quest, Race, Tag
   - **Available in Kanka API but not yet implemented**: Timeline, Item, Relation, DiceRoll, Conversation, AttributeTemplate, Bookmark, Ability, Map, Inventory
   - **Never existed/removed**: EntityNote, EntityEvent, Attribute, Species

## Development Preferences

- When executing test scripts with long output, redirect to file for parsing
- Don't push to origin during long tasks - let user do it manually
- Test frequently during complex refactoring
- Clean up temporary test files after use
- Don't leave comments explaining removed/moved code
- Use python-dotenv for environment variables: `load_dotenv()`

## Code Quality Workflow

**IMPORTANT**: After making any significant code changes, always run:

1. **Format first**: `make format` - Runs black, isort, and ruff --fix to format code
2. **Verify quality**: `make check` - Runs full linting, type checking, and all tests

This ensures:
- Code is properly formatted (black/isort)
- No linting violations (ruff)
- Type checking passes (mypy)
- All unit tests pass (pytest)

**Never commit without running `make check` successfully**. The test `test_request_error_handling` was previously hanging due to rate limiting retry in tests - this has been fixed by disabling rate limiting retry in that specific test.

## Testing Without Breaking Production

When testing against the real API:
1. Always use "Integration Test - DELETE ME" in entity names
2. Clean up created entities in teardown methods
3. Use wait_for_api() between operations to avoid rate limits
4. Integration tests track created IDs for cleanup

## Documentation Maintenance

**CRITICAL**: When making ANY changes to the API, models, exceptions, or client behavior:

1. **Always update API_REFERENCE.md** to reflect:
   - New/changed model fields and their types
   - New/changed method signatures
   - New/changed exception types
   - New/changed client constructor parameters
   - Any breaking changes or deprecations

2. **Always update README.md** when changes affect:
   - Installation instructions
   - Basic usage examples
   - Key features or capabilities
   - Version compatibility

3. **Documentation must be 100% accurate** - inconsistencies between docs and implementation cause significant user confusion

4. **Remove deprecated features** - don't just mark as deprecated, actively remove outdated documentation when legacy code is removed

**Example workflow:**
- Add new model field → Update API_REFERENCE.md model documentation
- Change method signature → Update API_REFERENCE.md method documentation
- Remove deprecated exception → Remove from API_REFERENCE.md exceptions section
- Add new client feature → Update both README.md and API_REFERENCE.md
