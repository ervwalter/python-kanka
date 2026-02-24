# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Key Development Commands

This project uses [uv](https://docs.astral.sh/uv/) for dependency management. All commands are wrapped in the Makefile for convenience:

```bash
# Install development environment (uses uv sync)
make install

# Sync dependencies without updating lock file
make sync

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
make build

# Generate coverage report
make coverage
```

### Direct uv commands

```bash
# Install dependencies
uv sync --all-groups

# Run a command in the environment
uv run pytest

# Add a new dependency
uv add package-name

# Add a dev dependency
uv add --group dev package-name

# Update dependencies
uv lock --upgrade

# Build the package
uv build
```

## Git Commit Message Format

This project uses conventional commits format:
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only changes
- `style`: Code style changes (formatting, missing semicolons, etc)
- `refactor`: Code change that neither fixes a bug nor adds a feature
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to build process, dependencies, or auxiliary tools

**Examples:**
- `feat: add pagination properties to EntityManager`
- `fix: replace is_private with visibility_id parameter for posts`
- `chore(deps): update dependency ruff to v0.11.13`
- `refactor: reorganize package structure for PyPI publishing`

**Note:** When Claude generates commits, they should include the attribution at the end of the commit body:
```
🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
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

## Version Bumping

This project uses `bump2version` for version management. The version is tracked in three files:
- `pyproject.toml` — package version
- `src/kanka/_version.py` — runtime version
- `.bumpversion.cfg` — bump2version's own tracking (must stay in sync)

**To bump the version:**

```bash
# Patch (bug fixes): 2.4.1 → 2.4.2
uv run bump2version patch

# Minor (new features): 2.4.1 → 2.5.0
uv run bump2version minor

# Major (breaking changes): 2.4.1 → 3.0.0
uv run bump2version major
```

This automatically:
1. Updates the version in `pyproject.toml`, `src/kanka/_version.py`, and `.bumpversion.cfg`
2. Creates a commit with message `Bump version: X.Y.Z → A.B.C`
3. Creates a git tag `vA.B.C`

**After bumping, always run `uv sync`** to update `uv.lock`, then amend the lock file into the bump commit and retag:

```bash
uv sync
git add uv.lock
git commit --amend --no-edit
git tag -d vA.B.C
git tag vA.B.C
```

**Important notes:**
- The working tree must be clean before running bump2version (use `--allow-dirty` only if `.bumpversion.cfg` is the dirty file due to a sync fix)
- If `.bumpversion.cfg`'s `current_version` is out of sync with the actual version in `pyproject.toml`, fix it manually before bumping
- Use `feat` commits → minor bump, `fix` commits → patch bump

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

1. **Always update the relevant files in `docs/`** to reflect:
   - New/changed model fields and their types → `docs/entity-types-reference.md` and `docs/api-reference.md`
   - New/changed method signatures → `docs/api-reference.md` and the relevant guide page
   - New/changed exception types → `docs/error-handling.md` and `docs/api-reference.md`
   - New/changed client constructor parameters → `docs/api-reference.md`
   - New features or usage patterns → the relevant guide page in `docs/`

2. **Always update `README.md`** when changes affect:
   - Installation instructions
   - Basic usage examples
   - Key features or capabilities

3. **Documentation must be 100% accurate** - inconsistencies between docs and implementation cause significant user confusion

4. **Remove deprecated features** - don't just mark as deprecated, actively remove outdated documentation when legacy code is removed

**Documentation structure:**
- `docs/README.md` — Index page linking to all docs
- `docs/getting-started.md` — Installation and quick start
- `docs/core-concepts.md` — Architecture and key concepts
- `docs/entities.md` — CRUD operations guide
- `docs/entity-types-reference.md` — All entity type fields
- `docs/posts.md` — Posts management
- `docs/assets-and-images.md` — Assets, images, automatic image management
- `docs/gallery.md` — Campaign gallery
- `docs/search-and-filtering.md` — Search and filtering
- `docs/pagination.md` — Pagination
- `docs/error-handling.md` — Exception types and patterns
- `docs/rate-limiting.md` — Rate limit configuration
- `docs/api-reference.md` — Complete API reference
- `docs/debug-mode.md` — Debug mode
- `docs/known-limitations.md` — API quirks and gotchas
