#!/usr/bin/env python3
"""
Entity Posts Example

This example demonstrates how to work with entity posts (notes attached to entities)
in the python-kanka library.
"""

import os
from kanka import KankaClient

TOKEN = os.environ.get("KANKA_TOKEN")
CAMPAIGN_ID = int(os.environ.get("KANKA_CAMPAIGN_ID", 0))

if not TOKEN or not CAMPAIGN_ID:
    print("Please set KANKA_TOKEN and KANKA_CAMPAIGN_ID environment variables")
    exit(1)

def main():
    """Demonstrate working with entity posts."""
    
    client = KankaClient(token=TOKEN, campaign_id=CAMPAIGN_ID)
    print("Python-Kanka Entity Posts Demo")
    print("=" * 50)
    
    # Create a character to work with
    print("\n1. Creating a character...")
    character = client.characters.create(
        name="Bilbo Baggins",
        title="Burglar",
        type="Hobbit",
        entry="A hobbit of the Shire who found the One Ring"
    )
    print(f"   Created: {character.name} (ID: {character.id})")
    
    # Get character with related data
    print("\n2. Getting character with related data...")
    character_with_posts = client.characters.get(character.id, related=True)
    print(f"   Character has {len(character_with_posts.posts or [])} posts")
    
    # Create posts for the character
    print("\n3. Creating posts for the character...")
    
    # Public post
    post1 = client.characters.create_post(
        character,
        name="Finding the Ring",
        entry="""On his adventure with the dwarves, Bilbo found a mysterious ring 
in a dark cave. Little did he know it was the One Ring of power.""",
        is_private=False
    )
    print(f"   Created post: '{post1.name}' (Public)")
    
    # Private post (DM notes)
    post2 = client.characters.create_post(
        character,
        name="DM Notes",
        entry="Remember: Bilbo is starting to show signs of the ring's corruption",
        is_private=True
    )
    print(f"   Created post: '{post2.name}' (Private)")
    
    # Post with position (for ordering)
    post3 = client.characters.create_post(
        character,
        name="Early Life",
        entry="Born in the Shire to Bungo Baggins and Belladonna Took",
        position=1  # This will appear first
    )
    print(f"   Created post: '{post3.name}' (Position: 1)")
    
    # List all posts for the character
    print("\n4. Listing all posts for the character...")
    posts = client.characters.posts(character)
    print(f"   Found {len(posts)} posts:")
    for post in posts:
        visibility = "Private" if post.is_private else "Public"
        print(f"   - {post.name} ({visibility}, Position: {post.position})")
    
    # Get a specific post
    print("\n5. Getting a specific post...")
    retrieved_post = client.characters.get_post(character, post1.id)
    print(f"   Retrieved: '{retrieved_post.name}'")
    print(f"   Entry preview: {retrieved_post.entry[:50]}...")
    
    # Update a post
    print("\n6. Updating a post...")
    updated_post = client.characters.update_post(
        character,
        post1,
        name="Discovery of the One Ring",
        entry="""While lost in the goblin tunnels, Bilbo stumbled upon Gollum's cave.
There he found a golden ring that would change the fate of Middle-earth."""
    )
    print(f"   Updated post: '{updated_post.name}'")
    
    # Working with posts on different entity types
    print("\n7. Posts on other entity types...")
    
    # Create a location
    location = client.locations.create(
        name="Bag End",
        type="Hobbit Hole",
        entry="The most comfortable hobbit hole in all of Hobbiton"
    )
    print(f"   Created location: {location.name}")
    
    # Add a post to the location
    location_post = client.locations.create_post(
        location,
        name="Architectural Details",
        entry="Round green door, brass knob in the exact middle..."
    )
    print(f"   Added post to location: '{location_post.name}'")
    
    # Create an organization
    org = client.organisations.create(
        name="Thorin's Company",
        type="Adventuring Party"
    )
    print(f"   Created organization: {org.name}")
    
    # Add a post to the organization
    org_post = client.organisations.create_post(
        org,
        name="Member List",
        entry="Thorin, Balin, Dwalin, Fili, Kili, Dori, Nori, Ori, Oin, Gloin, Bifur, Bofur, Bombur, and Bilbo"
    )
    print(f"   Added post to organization: '{org_post.name}'")
    
    # Delete a post
    print("\n8. Deleting a post...")
    client.characters.delete_post(character, post2)
    print(f"   Deleted post: '{post2.name}'")
    
    # Verify deletion
    remaining_posts = client.characters.posts(character)
    print(f"   Remaining posts: {len(remaining_posts)}")
    
    # Get character with posts included
    print("\n9. Getting entity with posts included...")
    full_character = client.characters.get(character.id, related=True)
    if full_character.posts:
        print(f"   Character has {len(full_character.posts)} posts attached")
        for post in full_character.posts:
            print(f"   - {post.name}")
    
    # Cleanup
    print("\n\nCleaning up...")
    client.characters.delete(character)
    print(f"   Deleted character: {character.name}")
    client.locations.delete(location)
    print(f"   Deleted location: {location.name}")
    client.organisations.delete(org)
    print(f"   Deleted organization: {org.name}")
    
    print("\nPosts demo complete!")
    print("\nKey takeaways:")
    print("- Posts can be attached to any entity type")
    print("- Posts can be public or private (DM notes)")
    print("- Posts can be ordered using the position field")
    print("- Use related=True when getting an entity to include posts")

if __name__ == "__main__":
    main()