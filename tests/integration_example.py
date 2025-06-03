"""
Integration test examples for python-kanka SDK.

WARNING: These tests require real API credentials and will make actual API calls.
Do not run without proper credentials and a test campaign.

To run these tests:
1. Set environment variables:
   export KANKA_TOKEN='your_api_token'
   export KANKA_CAMPAIGN_ID='your_test_campaign_id'
   
2. Run with pytest:
   pytest tests/integration_example.py -v

Note: These tests may create, modify, and delete data in your campaign.
Only run against a test campaign!
"""

import os
import pytest
from datetime import datetime
from kanka import KankaClient
from kanka.exceptions import NotFoundError, ValidationError


# Skip all tests if credentials not provided
pytestmark = pytest.mark.skipif(
    not os.environ.get('KANKA_TOKEN') or not os.environ.get('KANKA_CAMPAIGN_ID'),
    reason="KANKA_TOKEN and KANKA_CAMPAIGN_ID environment variables required"
)


class TestIntegration:
    """Integration tests with real API."""
    
    @pytest.fixture
    def client(self):
        """Create a client with real credentials."""
        token = os.environ.get('KANKA_TOKEN', '')
        campaign_id = int(os.environ.get('KANKA_CAMPAIGN_ID', '0'))
        return KankaClient(token=token, campaign_id=campaign_id)
    
    @pytest.fixture
    def test_character_name(self):
        """Generate unique test character name."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"Test Character {timestamp}"
    
    def test_character_crud_operations(self, client, test_character_name):
        """Test full CRUD cycle for a character."""
        # CREATE
        print(f"\nCreating character: {test_character_name}")
        character = client.characters.create(
            name=test_character_name,
            title="Test Knight",
            age="25",
            sex="Male",
            type="NPC",
            entry="<p>This is a test character created by integration tests.</p>",
            is_private=True
        )
        
        assert character.name == test_character_name
        assert character.title == "Test Knight"
        assert character.is_private is True
        character_id = character.id
        
        try:
            # READ
            print(f"Reading character {character_id}")
            fetched = client.characters.get(character_id)
            assert fetched.id == character_id
            assert fetched.name == test_character_name
            
            # UPDATE
            print(f"Updating character {character_id}")
            updated = client.characters.update(
                character_id,
                title="Test Paladin",
                age="26",
                traits="Brave and loyal"
            )
            assert updated.title == "Test Paladin"
            assert updated.age == "26"
            assert updated.traits == "Brave and loyal"
            
            # LIST with filters
            print("Listing characters with filters")
            characters = client.characters.list(name=test_character_name)
            assert len(characters) >= 1
            assert any(c.id == character_id for c in characters)
            
        finally:
            # DELETE (cleanup)
            print(f"Deleting character {character_id}")
            deleted = client.characters.delete(character_id)
            assert deleted is True
            
            # Verify deletion
            with pytest.raises(NotFoundError):
                client.characters.get(character_id)
    
    def test_location_with_posts(self, client):
        """Test location with posts functionality."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        location_name = f"Test Location {timestamp}"
        
        # Create location
        print(f"\nCreating location: {location_name}")
        location = client.locations.create(
            name=location_name,
            type="Castle",
            entry="<p>A test castle for integration testing.</p>",
            is_private=True
        )
        
        location_id = location.id
        
        try:
            # Create a post
            print(f"Creating post for location {location_id}")
            post = client.locations.create_post(
                location_id,
                name="History",
                entry="<p>This castle was built long ago...</p>",
                is_private=True
            )
            assert post.name == "History"
            post_id = post.id
            
            # List posts
            print(f"Listing posts for location {location_id}")
            posts = client.locations.list_posts(location_id)
            assert len(posts) >= 1
            assert any(p.id == post_id for p in posts)
            
            # Update post
            print(f"Updating post {post_id}")
            updated_post = client.locations.update_post(
                location_id,
                post_id,
                name="Updated History",
                entry="<p>This castle has a rich history...</p>"
            )
            assert updated_post.name == "Updated History"
            
            # Delete post
            print(f"Deleting post {post_id}")
            deleted = client.locations.delete_post(location_id, post_id)
            assert deleted is True
            
        finally:
            # Cleanup location
            print(f"Deleting location {location_id}")
            client.locations.delete(location_id)
    
    def test_search_functionality(self, client):
        """Test search across entities."""
        # Note: This test assumes there's at least some data in the campaign
        print("\nTesting search functionality")
        
        # Search for a common term
        results = client.search("the", limit=5)
        print(f"Found {len(results)} results for 'the'")
        
        # Check result structure
        if results:
            result = results[0]
            assert hasattr(result, 'id')
            assert hasattr(result, 'entity_id')
            assert hasattr(result, 'name')
            assert hasattr(result, 'type')
            print(f"First result: {result.name} (type: {result.type})")
    
    def test_entities_endpoint(self, client):
        """Test the entities endpoint with filters."""
        print("\nTesting entities endpoint")
        
        # Get all entities (limited)
        entities = client.entities()
        print(f"Total entities (first page): {len(entities)}")
        
        if entities:
            # Test type filtering
            first_type = entities[0].get('type')
            if first_type:
                filtered = client.entities(types=[first_type])
                print(f"Entities of type '{first_type}': {len(filtered)}")
                assert all(e.get('type') == first_type for e in filtered)
    
    def test_validation_errors(self, client):
        """Test that validation errors are properly raised."""
        print("\nTesting validation error handling")
        
        # Try to create character without required name
        with pytest.raises(ValidationError):
            client.characters.create(
                # name is missing - should raise ValidationError
                title="No Name Knight"
            )
    
    def test_pagination(self, client):
        """Test pagination functionality."""
        print("\nTesting pagination")
        
        # Get first page
        page1 = client.characters.list(page=1, limit=5)
        print(f"Page 1: {len(page1)} characters")
        
        # Get second page
        page2 = client.characters.list(page=2, limit=5)
        print(f"Page 2: {len(page2)} characters")
        
        # Check metadata
        meta = client.characters.last_page_meta
        if meta:
            print(f"Total characters: {meta.get('total', 'N/A')}")
            print(f"Current page: {meta.get('current_page', 'N/A')}")
            print(f"Per page: {meta.get('per_page', 'N/A')}")


def main():
    """Run integration tests manually."""
    print("Python-Kanka SDK Integration Tests")
    print("==================================")
    
    # Check credentials
    if not os.environ.get('KANKA_TOKEN'):
        print("\nERROR: KANKA_TOKEN environment variable not set!")
        print("Set it with: export KANKA_TOKEN='your_token_here'")
        return
    
    if not os.environ.get('KANKA_CAMPAIGN_ID'):
        print("\nERROR: KANKA_CAMPAIGN_ID environment variable not set!")
        print("Set it with: export KANKA_CAMPAIGN_ID='your_campaign_id'")
        return
    
    print("\nCredentials found. Run with pytest to execute tests:")
    print("pytest tests/integration_example.py -v")


if __name__ == "__main__":
    main()