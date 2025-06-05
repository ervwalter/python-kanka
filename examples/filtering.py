#!/usr/bin/env python3
"""
Advanced Filtering and Search Example

This example demonstrates the various filtering and search capabilities
of the python-kanka library.
"""

import os

from kanka import KankaClient

TOKEN = os.environ.get("KANKA_TOKEN")
CAMPAIGN_ID_STR = os.environ.get("KANKA_CAMPAIGN_ID")

if not TOKEN or not CAMPAIGN_ID_STR:
    print("Please set KANKA_TOKEN and KANKA_CAMPAIGN_ID environment variables")
    exit(1)

CAMPAIGN_ID = int(CAMPAIGN_ID_STR)


def main():
    """Demonstrate filtering and search capabilities."""

    assert TOKEN is not None  # We already checked this above
    client = KankaClient(token=TOKEN, campaign_id=CAMPAIGN_ID)
    print("Python-Kanka Filtering & Search Demo")
    print("=" * 50)

    # First, let's create some test data
    print("\nSetting up test data...")

    # Create tags for filtering
    important_tag = client.tags.create(name="Important", colour="#FF0000")
    npc_tag = client.tags.create(name="NPC", colour="#00FF00")
    location_tag = client.tags.create(name="Major Location", colour="#0000FF")

    # Create some characters with different attributes
    gandalf = client.characters.create(
        name="Gandalf the Grey",
        type="Wizard",
        title="Istari",
        is_private=False,
        tags=[important_tag.id, npc_tag.id],
    )

    saruman = client.characters.create(
        name="Saruman the White",
        type="Wizard",
        title="Head of the Istari",
        is_private=False,
        tags=[npc_tag.id],
    )

    frodo = client.characters.create(
        name="Frodo Baggins",
        type="Hobbit",
        title="Ring-bearer",
        is_private=False,
        tags=[important_tag.id],
    )

    secret_char = client.characters.create(
        name="Secret Agent", type="Spy", is_private=True
    )

    # Create some locations
    rivendell = client.locations.create(
        name="Rivendell",
        type="City",
        is_private=False,
        tags=[important_tag.id, location_tag.id],
    )

    mordor = client.locations.create(
        name="Mordor", type="Dark Land", is_private=False, tags=[location_tag.id]
    )

    print("Test data created successfully!")

    # 1. Basic filtering by type
    print("\n1. Filter characters by type:")
    wizards = client.characters.list(type="Wizard")
    print(f"   Found {len(wizards)} wizards:")
    for wizard in wizards:
        print(f"   - {wizard.name} ({wizard.title})")

    # 2. Filter by privacy setting
    print("\n2. Filter by privacy:")
    public_chars = client.characters.list(is_private=False)
    print(f"   Found {len(public_chars)} public characters")
    private_chars = client.characters.list(is_private=True)
    print(f"   Found {len(private_chars)} private characters")

    # 3. Filter by tags
    print("\n3. Filter by tags:")
    important_chars = client.characters.list(tags=[important_tag.id])
    print(f"   Characters with 'Important' tag: {len(important_chars)}")
    for char in important_chars:
        print(f"   - {char.name}")

    # 4. Filter by multiple tags
    print("\n4. Filter by multiple tags:")
    npc_important = client.characters.list(tags=[important_tag.id, npc_tag.id])
    print(f"   Characters with both 'Important' and 'NPC' tags: {len(npc_important)}")
    for char in npc_important:
        print(f"   - {char.name}")

    # 5. Name filtering (partial match)
    print("\n5. Filter by name (partial match):")
    name_filter = client.characters.list(name="the")
    print(f"   Characters with 'the' in name: {len(name_filter)}")
    for char in name_filter:
        print(f"   - {char.name}")

    # 6. Sorting
    print("\n6. Sorting results:")
    sorted_asc = client.characters.list(order_by="name", desc=False)
    print("   Characters sorted by name (ascending):")
    for char in sorted_asc[:3]:
        print(f"   - {char.name}")

    sorted_desc = client.characters.list(order_by="created_at", desc=True)
    print("\n   Characters sorted by creation date (newest first):")
    for char in sorted_desc[:3]:
        print(f"   - {char.name} (created: {char.created_at})")

    # 7. Pagination
    print("\n7. Pagination:")
    page1 = client.characters.list(page=1, limit=2)
    print(f"   Page 1 (limit 2): {[c.name for c in page1]}")

    if len(client.characters.list()) > 2:
        page2 = client.characters.list(page=2, limit=2)
        print(f"   Page 2 (limit 2): {[c.name for c in page2]}")

    # 8. Search across all entity types
    print("\n8. Global search:")
    search_results = client.search("the")
    print(f"   Found {len(search_results)} results for 'the':")
    for result in search_results[:5]:
        print(f"   - {result.name} ({result.type})")

    # 9. Search with pagination
    print("\n9. Search with pagination:")
    page1_search = client.search("the", page=1)
    print(f"   Search page 1: {len(page1_search)} results")

    # 10. Entity endpoint with type filtering
    print("\n10. Generic entities endpoint:")
    all_entities = client.entities(types=["character", "location"])
    print(f"   Found {len(all_entities)} characters and locations")

    # 11. Complex filtering combinations
    print("\n11. Complex filtering:")
    complex_filter = client.characters.list(
        type="Wizard", is_private=False, tags=[npc_tag.id], order_by="name"
    )
    print(f"   Public wizard NPCs: {len(complex_filter)}")
    for char in complex_filter:
        print(f"   - {char.name}")

    # 12. Filter different entity types
    print("\n12. Filtering other entity types:")

    # Locations by tag
    major_locations = client.locations.list(tags=[location_tag.id])
    print(f"   Major locations: {len(major_locations)}")
    for loc in major_locations:
        print(f"   - {loc.name} ({loc.type})")

    # Cleanup
    print("\n\nCleaning up test data...")
    for char in [gandalf, saruman, frodo, secret_char]:
        client.characters.delete(char)
    for loc in [rivendell, mordor]:
        client.locations.delete(loc)
    for tag in [important_tag, npc_tag, location_tag]:
        client.tags.delete(tag)

    print("Demo complete!")


if __name__ == "__main__":
    main()
