#!/usr/bin/env python3
"""Test script for Phase 3 functionality."""

import os
from datetime import datetime
from kanka import KankaClient

# Get credentials from environment or use test values
TOKEN = os.environ.get('KANKA_TOKEN', 'test_token')
CAMPAIGN_ID = int(os.environ.get('KANKA_CAMPAIGN_ID', '1'))

def test_search():
    """Test search functionality."""
    print("\n=== Testing Search ===")
    
    # Create client
    client = KankaClient(TOKEN, CAMPAIGN_ID)
    
    try:
        # Test basic search
        results = client.search("test")
        print(f"Found {len(results)} results for 'test'")
        
        # Test search with pagination
        results = client.search("test", page=1, limit=10)
        print(f"Page 1 with limit 10: {len(results)} results")
        
        # Check metadata
        meta = client.last_search_meta
        links = client.last_search_links
        print(f"Search metadata: {meta}")
        print(f"Search links: {links}")
        
        # Display first result if any
        if results:
            result = results[0]
            print(f"\nFirst result:")
            print(f"  - Name: {result.name}")
            print(f"  - Type: {result.type}")
            print(f"  - ID: {result.id}")
            print(f"  - Entity ID: {result.entity_id}")
            print(f"  - Private: {result.is_private}")
            
    except Exception as e:
        print(f"Search test failed: {e}")

def test_filtering():
    """Test filtering functionality."""
    print("\n=== Testing Filtering ===")
    
    client = KankaClient(TOKEN, CAMPAIGN_ID)
    
    try:
        # Test various filters
        print("\n1. Testing name filter:")
        results = client.characters.list(name="test")
        print(f"   Characters with 'test' in name: {len(results)}")
        
        print("\n2. Testing privacy filter:")
        results = client.locations.list(is_private=False)
        print(f"   Public locations: {len(results)}")
        
        print("\n3. Testing tag filter:")
        # Assuming tags with IDs 1, 2 exist
        results = client.characters.list(tags=[1, 2])
        print(f"   Characters with tags [1, 2]: {len(results)}")
        
        print("\n4. Testing combined filters:")
        results = client.characters.list(
            name="test",
            is_private=False,
            page=1,
            limit=5
        )
        print(f"   Public characters with 'test': {len(results)}")
        
        # Check pagination metadata
        meta = client.characters.last_page_meta
        if meta:
            print(f"\n   Pagination info:")
            print(f"   - Current page: {meta.get('current_page', 'N/A')}")
            print(f"   - Total results: {meta.get('total', 'N/A')}")
            print(f"   - Per page: {meta.get('per_page', 'N/A')}")
            
    except Exception as e:
        print(f"Filtering test failed: {e}")

def test_posts():
    """Test posts functionality."""
    print("\n=== Testing Posts ===")
    
    client = KankaClient(TOKEN, CAMPAIGN_ID)
    
    try:
        # First, get a character to work with
        characters = client.characters.list(limit=1)
        if not characters:
            print("No characters found to test posts with")
            return
            
        character = characters[0]
        print(f"\nUsing character: {character.name} (ID: {character.id})")
        
        # 1. List posts
        print("\n1. Listing posts:")
        posts = client.characters.list_posts(character)
        print(f"   Found {len(posts)} posts")
        
        # 2. Create a post
        print("\n2. Creating a post:")
        try:
            new_post = client.characters.create_post(
                character,
                name=f"Test Post {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                entry="This is a test post created by the SDK test script.",
                is_private=True
            )
            print(f"   Created post: {new_post.name} (ID: {new_post.id})")
            
            # 3. Get specific post
            print("\n3. Getting specific post:")
            fetched_post = client.characters.get_post(character, new_post.id)
            print(f"   Fetched post: {fetched_post.name}")
            print(f"   Content: {fetched_post.entry[:50]}...")
            
            # 4. Update post
            print("\n4. Updating post:")
            updated_post = client.characters.update_post(
                character,
                new_post.id,
                name="Updated Test Post",
                entry="This post has been updated."
            )
            print(f"   Updated post name: {updated_post.name}")
            
            # 5. Delete post
            print("\n5. Deleting post:")
            success = client.characters.delete_post(character, new_post.id)
            print(f"   Post deleted: {success}")
            
        except Exception as e:
            print(f"   Post operations failed: {e}")
            
        # Check pagination metadata for posts
        meta = client.characters.last_posts_meta
        if meta:
            print(f"\n   Posts pagination info:")
            print(f"   - Total posts: {meta.get('total', 'N/A')}")
            
    except Exception as e:
        print(f"Posts test failed: {e}")

def test_entities_endpoint():
    """Test the /entities endpoint with filters."""
    print("\n=== Testing /entities Endpoint ===")
    
    client = KankaClient(TOKEN, CAMPAIGN_ID)
    
    try:
        # Test with type filter
        print("\n1. Filter by types:")
        results = client.entities(types=['character', 'location'])
        print(f"   Found {len(results)} characters and locations")
        
        # Test with tags
        print("\n2. Filter by tags:")
        results = client.entities(tags=[1])
        print(f"   Found {len(results)} entities with tag ID 1")
        
        # Test combined filters
        print("\n3. Combined filters:")
        results = client.entities(
            name="test",
            is_private=False,
            types=['character']
        )
        print(f"   Found {len(results)} public characters with 'test' in name")
        
        # Display first result if any
        if results:
            entity = results[0]
            print(f"\n   First entity:")
            print(f"   - Name: {entity.get('name', 'N/A')}")
            print(f"   - Type: {entity.get('type', 'N/A')}")
            print(f"   - ID: {entity.get('id', 'N/A')}")
            
    except Exception as e:
        print(f"Entities endpoint test failed: {e}")

def main():
    """Run all tests."""
    print("Phase 3 SDK Functionality Tests")
    print("=" * 50)
    
    # Check if we have valid credentials
    if TOKEN == 'test_token':
        print("\nWARNING: Using test token. Set KANKA_TOKEN environment variable for real tests.")
        print("Example: export KANKA_TOKEN='your_token_here'")
        print("         export KANKA_CAMPAIGN_ID='your_campaign_id'")
    
    # Run tests
    test_search()
    test_filtering() 
    test_posts()
    test_entities_endpoint()
    
    print("\n" + "=" * 50)
    print("Tests completed!")

if __name__ == "__main__":
    main()