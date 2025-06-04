#!/usr/bin/env python3
"""
Migration Example

This example shows how to migrate from the old python-kanka API (v0.x)
to the new API (v2.0+).
"""

import os

# Get credentials
TOKEN = os.environ.get("KANKA_TOKEN")
CAMPAIGN_ID = int(os.environ.get("KANKA_CAMPAIGN_ID", 0))

if not TOKEN or not CAMPAIGN_ID:
    print("Please set KANKA_TOKEN and KANKA_CAMPAIGN_ID environment variables")
    exit(1)

print("Python-Kanka Migration Guide")
print("=" * 50)
print("\nThis guide shows how to migrate from v0.x to v2.0+\n")

# ============================================================================
# 1. CLIENT INITIALIZATION
# ============================================================================
print("1. CLIENT INITIALIZATION")
print("-" * 30)

print("OLD WAY (v0.x):")
print(
    """
import kanka
client = kanka.KankaClient(token)
campaign = client.campaign(campaign_id)
"""
)

print("\nNEW WAY (v2.0+):")
print(
    """
from kanka import KankaClient
client = KankaClient(token, campaign_id)
"""
)

print("\nKey differences:")
print("- Import from 'kanka' package directly")
print("- Campaign ID is part of client initialization")
print("- No separate campaign object")

# ============================================================================
# 2. GETTING ENTITIES
# ============================================================================
print("\n\n2. GETTING ENTITIES")
print("-" * 30)

print("OLD WAY:")
print(
    """
# Get a character
character = campaign.character(character_id)
location = campaign.location(location_id)
"""
)

print("\nNEW WAY:")
print(
    """
# Get a character
character = client.characters.get(character_id)
location = client.locations.get(location_id)
"""
)

print("\nKey differences:")
print("- Use entity managers (client.characters, client.locations, etc.)")
print("- Consistent naming: plural for managers, get() method")

# ============================================================================
# 3. LISTING ENTITIES
# ============================================================================
print("\n\n3. LISTING ENTITIES")
print("-" * 30)

print("OLD WAY:")
print(
    """
# List characters
characters = campaign.get_list_of("characters")
"""
)

print("\nNEW WAY:")
print(
    """
# List characters
characters = client.characters.list()

# With filters
wizards = client.characters.list(type="Wizard", is_private=False)
"""
)

print("\nKey differences:")
print("- Use manager.list() instead of get_list_of()")
print("- Better filtering support with named parameters")

# ============================================================================
# 4. CREATING ENTITIES
# ============================================================================
print("\n\n4. CREATING ENTITIES")
print("-" * 30)

print("OLD WAY:")
print(
    """
# Create empty entity, set fields, upload
char = campaign.new_entity("character")
char.name = "Gandalf"
char.type = "Wizard"
char.age = "2000+"
result = char.upload()
"""
)

print("\nNEW WAY:")
print(
    """
# Create with all data at once
char = client.characters.create(
    name="Gandalf",
    type="Wizard",
    age="2000+"
)
"""
)

print("\nKey differences:")
print("- Single create() call with all data")
print("- No separate upload step")
print("- Returns the created entity directly")

# ============================================================================
# 5. UPDATING ENTITIES
# ============================================================================
print("\n\n5. UPDATING ENTITIES")
print("-" * 30)

print("OLD WAY:")
print(
    """
# Modify attributes and update
char.name = "Gandalf the White"
char.title = "The White Wizard"
char.update()
"""
)

print("\nNEW WAY:")
print(
    """
# Update returns new object (immutable)
char = client.characters.update(
    char,
    name="Gandalf the White",
    title="The White Wizard"
)
"""
)

print("\nKey differences:")
print("- Entities are immutable - update returns new object")
print("- Pass entity and changes to update()")
print("- Must reassign to get updated version")

# ============================================================================
# 6. DELETING ENTITIES
# ============================================================================
print("\n\n6. DELETING ENTITIES")
print("-" * 30)

print("OLD WAY:")
print(
    """
# Delete by type and ID
campaign.delete("character", character_id)
"""
)

print("\nNEW WAY:")
print(
    """
# Delete through manager
client.characters.delete(character)
# or
client.characters.delete(character_id)
"""
)

print("\nKey differences:")
print("- Use manager.delete()")
print("- Can pass entity object or just ID")

# ============================================================================
# 7. SEARCHING
# ============================================================================
print("\n\n7. SEARCHING")
print("-" * 30)

print("OLD WAY:")
print(
    """
# Search returns mixed entity types
results = campaign.search("Gandalf")
for entity in results:
    print(entity.name)
"""
)

print("\nNEW WAY:")
print(
    """
# Search returns SearchResult objects
results = client.search("Gandalf")
for result in results:
    print(f"{result.name} ({result.type})")
"""
)

print("\nKey differences:")
print("- Search is on client, not campaign")
print("- Returns SearchResult objects with type info")

# ============================================================================
# 8. ERROR HANDLING
# ============================================================================
print("\n\n8. ERROR HANDLING")
print("-" * 30)

print("OLD WAY:")
print(
    """
# Limited error handling
try:
    char = campaign.character(999)
except Exception as e:
    print(f"Error: {e}")
"""
)

print("\nNEW WAY:")
print(
    """
from kanka.exceptions import NotFoundError, ValidationError

try:
    char = client.characters.get(999)
except NotFoundError:
    print("Character not found")
except ValidationError as e:
    print(f"Invalid data: {e.errors}")
"""
)

print("\nKey differences:")
print("- Specific exception types")
print("- Better error messages")
print("- Can handle different errors appropriately")

# ============================================================================
# 9. WORKING WITH POSTS
# ============================================================================
print("\n\n9. WORKING WITH POSTS")
print("-" * 30)

print("OLD WAY:")
print(
    """
# Posts were not well supported in v0.x
# Had to use raw API calls
"""
)

print("\nNEW WAY:")
print(
    """
# Full post support
post = client.characters.create_post(
    character,
    name="Background",
    entry="Character backstory..."
)

# List posts
posts = client.characters.posts(character)

# Update post
post = client.characters.update_post(character, post, entry="Updated...")

# Delete post
client.characters.delete_post(character, post)
"""
)

# ============================================================================
# 10. COMPLETE EXAMPLE
# ============================================================================
print("\n\n10. COMPLETE MIGRATION EXAMPLE")
print("-" * 30)

print("\nOLD CODE:")
print(
    """
import kanka

# Initialize
client = kanka.KankaClient(token)
campaign = client.campaign(campaign_id)

# Create character
char = campaign.new_entity("character")
char.name = "Frodo"
char.type = "Hobbit"
char.upload()

# Update
char.title = "Ring-bearer"
char.update()

# Search
results = campaign.search("Frodo")

# Delete
campaign.delete("character", char.id)
"""
)

print("\nNEW CODE:")
print(
    """
from kanka import KankaClient

# Initialize
client = KankaClient(token, campaign_id)

# Create character
char = client.characters.create(
    name="Frodo",
    type="Hobbit"
)

# Update
char = client.characters.update(
    char,
    title="Ring-bearer"
)

# Search
results = client.search("Frodo")

# Delete
client.characters.delete(char)
"""
)

# ============================================================================
# SUMMARY
# ============================================================================
print("\n\nMIGRATION SUMMARY")
print("=" * 50)
print(
    """
1. Single client object (no separate campaign)
2. Entity managers for each type (client.characters, etc.)
3. Consistent CRUD methods: create(), get(), update(), delete(), list()
4. Immutable entities (update returns new object)
5. Better error handling with specific exceptions
6. Full support for posts and related data
7. Type safety with Pydantic models
8. Better filtering and search capabilities

The new API is more consistent, type-safe, and easier to use!
"""
)

# ============================================================================
# WORKING EXAMPLE
# ============================================================================
print("\n\nWORKING EXAMPLE WITH NEW API")
print("=" * 50)

# Only run if we have valid credentials
if TOKEN and CAMPAIGN_ID:
    from kanka import KankaClient

    # Initialize new client
    client = KankaClient(TOKEN, CAMPAIGN_ID)

    print("\nCreating a test character...")
    character = client.characters.create(
        name="Migration Test Character", type="Test Type", title="Created with v2.0 API"
    )
    print(f"✓ Created: {character.name} (ID: {character.id})")

    print("\nUpdating the character...")
    character = client.characters.update(character, title="Updated with v2.0 API")
    print(f"✓ Updated title: {character.title}")

    print("\nSearching for the character...")
    results = client.search("Migration Test")
    print(f"✓ Found {len(results)} results")

    print("\nDeleting the character...")
    client.characters.delete(character)
    print("✓ Deleted successfully")

    print("\nMigration example complete!")
else:
    print("\n(Skipping working example - no credentials provided)")
