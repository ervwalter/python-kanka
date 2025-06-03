"""
Integration tests for Character entity operations.
"""
from datetime import datetime
from typing import Optional

from base import IntegrationTestBase
from kanka.objects import Character


class TestCharacterIntegration(IntegrationTestBase):
    """Integration tests for Character CRUD operations."""
    
    def __init__(self):
        super().__init__()
        self.created_character_id: Optional[int] = None
        
    def teardown(self):
        """Clean up any created characters."""
        if self.created_character_id and self.client:
            try:
                self.client.characters.delete(self.created_character_id)
                print(f"  Cleaned up character {self.created_character_id}")
            except Exception:
                pass  # Already deleted or doesn't exist
        super().teardown()
        
    def test_create_character(self):
        """Test creating a character."""
        # Create character data
        character_data = {
            "name": f"Integration Test Character - DELETE ME - {datetime.now().isoformat()}",
            "title": "Test Title",
            "age": "25",
            "pronouns": "they/them",
            "type": "NPC",
            "is_dead": False,
            "is_private": False
        }
        
        # Create the character
        character = self.client.characters.create(**character_data)
        self.created_character_id = character.id
        
        # Verify the character was created
        self.assert_not_none(character.id, "Character ID should not be None")
        self.assert_equal(character.name, character_data["name"], "Character name mismatch")
        self.assert_equal(character.title, character_data["title"], "Character title mismatch")
        self.assert_equal(character.age, character_data["age"], "Character age mismatch")
        self.assert_equal(character.pronouns, character_data["pronouns"], "Character pronouns mismatch")
        self.assert_equal(character.type, character_data["type"], "Character type mismatch")
        self.assert_equal(character.is_dead, False, "Character should not be dead")
        self.assert_equal(character.is_private, False, "Character should not be private")
        
        print(f"  Created character: {character.name} (ID: {character.id})")
        
    def test_list_characters_with_filter(self):
        """Test listing characters with filters."""
        # First create a character to ensure we have something to find
        test_name = f"Integration Test Character - DELETE ME - {datetime.now().isoformat()}"
        character = self.client.characters.create(name=test_name, type="NPC")
        self.created_character_id = character.id
        
        self.wait_for_api()  # Give API time to index
        
        # List all characters with our test prefix
        characters = list(self.client.characters.all(name="Integration Test Character"))
        
        # Verify our character appears in the list
        found = False
        for c in characters:
            if c.id == character.id:
                found = True
                break
                
        self.assert_true(found, f"Created character {character.id} not found in filtered list")
        print(f"  Found {len(characters)} test character(s) in filtered list")
        
    def test_update_character(self):
        """Test updating a character."""
        # Create a character
        original_name = f"Integration Test Character - DELETE ME - {datetime.now().isoformat()}"
        character = self.client.characters.create(
            name=original_name,
            title="Original Title",
            age="20"
        )
        self.created_character_id = character.id
        
        self.wait_for_api()
        
        # Update the character
        updated_data = {
            "title": "Updated Title",
            "age": "30",
            "pronouns": "she/her",
            "is_dead": True
        }
        updated_character = self.client.characters.update(character.id, **updated_data)
        
        # Verify updates
        self.assert_equal(updated_character.name, original_name, "Name should not change")
        self.assert_equal(updated_character.title, "Updated Title", "Title not updated")
        self.assert_equal(updated_character.age, "30", "Age not updated")
        self.assert_equal(updated_character.pronouns, "she/her", "Pronouns not updated")
        self.assert_equal(updated_character.is_dead, True, "is_dead not updated")
        
        print(f"  Updated character {character.id} successfully")
        
    def test_get_character(self):
        """Test getting a specific character."""
        # Create a character
        character_name = f"Integration Test Character - DELETE ME - {datetime.now().isoformat()}"
        created = self.client.characters.create(name=character_name, type="PC")
        self.created_character_id = created.id
        
        self.wait_for_api()
        
        # Get the character by ID
        character = self.client.characters.get(created.id)
        
        # Verify we got the right character
        self.assert_equal(character.id, created.id, "Character ID mismatch")
        self.assert_equal(character.name, character_name, "Character name mismatch")
        self.assert_equal(character.type, "PC", "Character type mismatch")
        
        print(f"  Retrieved character {character.id} successfully")
        
    def test_delete_character(self):
        """Test deleting a character."""
        # Create a character
        character = self.client.characters.create(
            name=f"Integration Test Character TO DELETE - {datetime.now().isoformat()}"
        )
        character_id = character.id
        
        self.wait_for_api()
        
        # Delete the character
        self.client.characters.delete(character_id)
        self.created_character_id = None  # Already deleted
        
        self.wait_for_api()
        
        # Verify it's deleted by trying to get it
        try:
            self.client.characters.get(character_id)
            self.assert_true(False, f"Character {character_id} should have been deleted")
        except Exception:
            # Expected - character should not be found
            pass
            
        print(f"  Deleted character {character_id} successfully")
        
    def run_all_tests(self):
        """Run all character integration tests."""
        tests = [
            ("Character Creation", self.test_create_character),
            ("Character Listing with Filter", self.test_list_characters_with_filter),
            ("Character Update", self.test_update_character),
            ("Character Retrieval", self.test_get_character),
            ("Character Deletion", self.test_delete_character),
        ]
        
        results = []
        for test_name, test_func in tests:
            result = self.run_test(test_name, test_func)
            results.append((test_name, result))
            
        return results


if __name__ == "__main__":
    tester = TestCharacterIntegration()
    results = tester.run_all_tests()
    
    print("\n" + "="*50)
    print("CHARACTER INTEGRATION TEST RESULTS")
    print("="*50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        print(f"{test_name}: {status}")
        
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed < total:
        exit(1)