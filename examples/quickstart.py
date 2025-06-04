#!/usr/bin/env python3
"""
Python-Kanka Quick Start Tutorial

This example demonstrates the basic usage of the python-kanka library.
You'll learn how to:
- Initialize the client
- Create entities
- Retrieve and update entities
- Search for entities
- Delete entities
"""

import os

from kanka import KankaClient
from kanka.exceptions import NotFoundError, ValidationError

# Get credentials from environment variables
# Set these in your environment:
# export KANKA_TOKEN="your-api-token"
# export KANKA_CAMPAIGN_ID="your-campaign-id"
TOKEN = os.environ.get("KANKA_TOKEN")
CAMPAIGN_ID_STR = os.environ.get("KANKA_CAMPAIGN_ID")

if not TOKEN or not CAMPAIGN_ID_STR:
    print("Please set KANKA_TOKEN and KANKA_CAMPAIGN_ID environment variables")
    exit(1)

CAMPAIGN_ID = int(CAMPAIGN_ID_STR)


def main():
    """Run the quickstart tutorial."""

    # 1. Initialize the client
    print("1. Initializing Kanka client...")
    assert TOKEN is not None  # We already checked this above
    client = KankaClient(token=TOKEN, campaign_id=CAMPAIGN_ID)
    print("   Client initialized successfully!")

    # 2. Create a character
    print("\n2. Creating a character...")
    character = client.characters.create(
        name="Aragorn",
        title="Ranger of the North",
        type="Human",
        age="87",
        is_private=False,
    )
    print(f"   Created character: {character.name} (ID: {character.id})")

    # 3. Retrieve the character
    print("\n3. Retrieving the character...")
    retrieved = client.characters.get(character.id)
    print(f"   Retrieved: {retrieved.name} - {retrieved.title}")

    # 4. Update the character
    print("\n4. Updating the character...")
    updated = client.characters.update(
        character, title="King of Gondor", name="Aragorn II Elessar"
    )
    print(f"   Updated: {updated.name} - {updated.title}")

    # 5. Create a location
    print("\n5. Creating a location...")
    location = client.locations.create(
        name="Minas Tirith", type="City", entry="The capital city of Gondor"
    )
    print(f"   Created location: {location.name} (ID: {location.id})")

    # 6. Link character to location
    print("\n6. Linking character to location...")
    updated = client.characters.update(updated, location_id=location.id)
    print(f"   Linked {updated.name} to {location.name}")

    # 7. Search for entities
    print("\n7. Searching for entities...")
    results = client.search("Aragorn")
    print(f"   Found {len(results)} results:")
    for result in results:
        print(f"   - {result.name} ({result.type})")

    # 8. List all characters
    print("\n8. Listing characters...")
    characters = client.characters.list(limit=5)
    print(f"   Found {len(characters)} characters:")
    for char in characters[:3]:  # Show first 3
        print(f"   - {char.name}")

    # 9. Create a tag
    print("\n9. Creating and applying tags...")
    tag = client.tags.create(name="Main Characters", colour="#ff0000")
    print(f"   Created tag: {tag.name}")

    # Apply tag to character
    updated = client.characters.update(updated, tags=[tag.id])
    print(f"   Applied tag to {updated.name}")

    # 10. Error handling example
    print("\n10. Demonstrating error handling...")
    try:
        # Try to get a non-existent character
        client.characters.get(999999)
    except NotFoundError:
        print("   Caught NotFoundError as expected")

    try:
        # Try to create invalid entity
        client.characters.create(name="")  # Empty name
    except ValidationError as e:
        print(f"   Caught ValidationError: {e}")

    # 11. Cleanup
    print("\n11. Cleaning up...")
    if input("   Delete created entities? (y/n): ").lower() == "y":
        client.characters.delete(updated)
        print(f"   Deleted character: {updated.name}")

        client.locations.delete(location)
        print(f"   Deleted location: {location.name}")

        client.tags.delete(tag)
        print(f"   Deleted tag: {tag.name}")

        print("\nQuickstart completed! All test entities cleaned up.")
    else:
        print("\nQuickstart completed! Test entities retained.")
        print(f"Character ID: {updated.id}")
        print(f"Location ID: {location.id}")
        print(f"Tag ID: {tag.id}")


if __name__ == "__main__":
    main()
