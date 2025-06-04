#!/usr/bin/env python3
"""
CRUD Operations Example

This example demonstrates Create, Read, Update, and Delete operations
for all supported entity types in the python-kanka library.
"""

import os

from kanka import KankaClient

# Get credentials
TOKEN = os.environ.get("KANKA_TOKEN")
CAMPAIGN_ID_STR = os.environ.get("KANKA_CAMPAIGN_ID")

if not TOKEN or not CAMPAIGN_ID_STR:
    print("Please set KANKA_TOKEN and KANKA_CAMPAIGN_ID environment variables")
    exit(1)

CAMPAIGN_ID = int(CAMPAIGN_ID_STR)


def demonstrate_entity_crud(client, entity_type, manager, create_data, update_data):
    """Demonstrate CRUD operations for an entity type."""
    print(f"\n{'='*50}")
    print(f"{entity_type.upper()} CRUD Operations")
    print("=" * 50)
    print(f"   Campaign ID: {client.campaign_id}")

    # CREATE
    print(f"\n1. Creating {entity_type}...")
    entity = manager.create(**create_data)
    print(f"   Created: {entity.name} (ID: {entity.id})")

    # READ
    print(f"\n2. Reading {entity_type}...")
    retrieved = manager.get(entity.id)
    print(f"   Retrieved: {retrieved.name}")
    print(f"   Created at: {retrieved.created_at}")

    # UPDATE
    print(f"\n3. Updating {entity_type}...")
    updated = manager.update(entity, **update_data)
    print(f"   Updated: {updated.name}")
    for key in update_data:
        if hasattr(updated, key):
            print(f"   {key}: {getattr(updated, key)}")

    # LIST
    print(f"\n4. Listing {entity_type}s...")
    items = manager.list(limit=5)
    print(f"   Found {len(items)} {entity_type}s")

    # DELETE
    print(f"\n5. Deleting {entity_type}...")
    manager.delete(updated)
    print("   Deleted successfully")

    return updated


def main():
    """Demonstrate CRUD for all entity types."""

    assert TOKEN is not None  # We already checked this above
    client = KankaClient(token=TOKEN, campaign_id=CAMPAIGN_ID)
    print("Python-Kanka CRUD Operations Demo")
    print("=================================")

    # Characters
    demonstrate_entity_crud(
        client,
        "character",
        client.characters,
        create_data={
            "name": "Frodo Baggins",
            "title": "Ring-bearer",
            "type": "Hobbit",
            "age": "50",
            "sex": "Male",
            "pronouns": "he/him",
        },
        update_data={"title": "Hero of Middle-earth", "is_dead": False},
    )

    # Locations
    demonstrate_entity_crud(
        client,
        "location",
        client.locations,
        create_data={
            "name": "The Shire",
            "type": "Region",
            "entry": "A peaceful land inhabited by hobbits",
        },
        update_data={"type": "Homeland", "is_private": False},
    )

    # Organizations
    demonstrate_entity_crud(
        client,
        "organisation",
        client.organisations,
        create_data={
            "name": "The Fellowship",
            "type": "Adventuring Party",
            "entry": "Nine companions united against Sauron",
        },
        update_data={"type": "Legendary Group"},
    )

    # Families
    demonstrate_entity_crud(
        client,
        "family",
        client.families,
        create_data={
            "name": "House Baggins",
            "type": "Hobbit Family",
            "entry": "A respectable hobbit family",
        },
        update_data={"type": "Noble House"},
    )

    # Journals
    demonstrate_entity_crud(
        client,
        "journal",
        client.journals,
        create_data={
            "name": "The Red Book",
            "type": "Chronicle",
            "date": "3019-03-25",
            "entry": "There and Back Again",
        },
        update_data={"type": "Historical Record"},
    )

    # Notes
    demonstrate_entity_crud(
        client,
        "note",
        client.notes,
        create_data={
            "name": "DM Secret",
            "type": "Plot Point",
            "entry": "The eagles are coming!",
            "is_private": True,
        },
        update_data={"is_pinned": True},
    )

    # Quests
    demonstrate_entity_crud(
        client,
        "quest",
        client.quests,
        create_data={
            "name": "Destroy the Ring",
            "type": "Main Quest",
            "entry": "Take the ring to Mount Doom",
            "is_completed": False,
        },
        update_data={"is_completed": True},
    )

    # Tags
    demonstrate_entity_crud(
        client,
        "tag",
        client.tags,
        create_data={"name": "Epic", "type": "Category", "colour": "#FFD700"},
        update_data={"colour": "#FF0000"},
    )

    # Events
    demonstrate_entity_crud(
        client,
        "event",
        client.events,
        create_data={
            "name": "Battle of Pelennor Fields",
            "type": "Battle",
            "date": "March 15, 3019",
            "entry": "The greatest battle of the war",
        },
        update_data={"type": "Historic Battle"},
    )

    # Races
    demonstrate_entity_crud(
        client,
        "race",
        client.races,
        create_data={
            "name": "Elves",
            "type": "Immortal Race",
            "entry": "The Firstborn of Ilúvatar",
        },
        update_data={"type": "Elder Race"},
    )

    # Creatures
    demonstrate_entity_crud(
        client,
        "creature",
        client.creatures,
        create_data={
            "name": "Balrog",
            "type": "Demon",
            "entry": "Ancient evil of Morgoth",
        },
        update_data={"is_extinct": False},
    )

    # Calendars
    demonstrate_entity_crud(
        client,
        "calendar",
        client.calendars,
        create_data={
            "name": "Shire Reckoning",
            "type": "Hobbit Calendar",
            "entry": "The calendar of the Shire",
        },
        update_data={"type": "Regional Calendar"},
    )

    print("\n" + "=" * 50)
    print("CRUD Operations Demo Complete!")
    print("=" * 50)


if __name__ == "__main__":
    main()
