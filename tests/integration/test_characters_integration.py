"""
Integration tests for Character entity operations.
"""

from datetime import datetime

# Handle both direct execution and import scenarios
if __name__ == "__main__":
    import setup_test_env

    setup_test_env.setup_environment()

from base import IntegrationTestBase

# Character type is imported implicitly through the client


class TestCharacterIntegration(IntegrationTestBase):
    """Integration tests for Character CRUD operations."""

    def __init__(self):
        super().__init__()

    def _register_character_cleanup(self, character_id: int, name: str):
        """Register a character for cleanup."""

        def cleanup():
            if self.client:
                self.client.characters.delete(character_id)

        self.register_cleanup(
            f"Delete character '{name}' (ID: {character_id})", cleanup
        )

    def test_create_character(self):
        """Test creating a character."""
        # Create character data
        character_data = {
            "name": f"Integration Test Character - DELETE ME - {datetime.now().isoformat()}",
            "title": "Test Title",
            "age": "25",
            "pronouns": "they/them",
            "type": "NPC",
            "entry": "<p>This is a <strong>test character</strong> with <em>HTML content</em>.</p><ul><li>First ability</li><li>Second skill</li></ul>",
            "is_dead": False,
            "is_private": False,
        }

        # Create the character
        character = self.client.characters.create(**character_data)
        self._register_character_cleanup(character.id, character.name)

        # Verify the character was created
        self.assert_not_none(character.id, "Character ID should not be None")
        self.assert_equal(
            character.name, character_data["name"], "Character name mismatch"
        )
        self.assert_equal(
            character.title, character_data["title"], "Character title mismatch"
        )
        self.assert_equal(
            character.age, character_data["age"], "Character age mismatch"
        )
        self.assert_equal(
            character.pronouns,
            character_data["pronouns"],
            "Character pronouns mismatch",
        )
        self.assert_equal(
            character.type, character_data["type"], "Character type mismatch"
        )
        self.assert_equal(character.is_dead, False, "Character should not be dead")
        self.assert_equal(
            character.is_private, False, "Character should not be private"
        )
        self.assert_equal(
            character.entry, character_data["entry"], "Character entry mismatch"
        )

        print(f"  Created character: {character.name} (ID: {character.id})")

    def test_list_characters_with_filter(self):
        """Test listing characters with filters."""
        # First create a character to ensure we have something to find
        test_name = (
            f"Integration Test Character - DELETE ME - {datetime.now().isoformat()}"
        )
        character = self.client.characters.create(
            name=test_name,
            type="NPC",
            entry="<h2>Test NPC</h2><p>A character created for <a href='#'>testing</a>.</p>",
        )
        self._register_character_cleanup(character.id, character.name)

        self.wait_for_api()  # Give API time to index

        # List all characters with our test prefix
        characters = list(
            self.client.characters.list(name="Integration Test Character")
        )

        # Verify our character appears in the list
        found = False
        for c in characters:
            if c.id == character.id:
                found = True
                break

        self.assert_true(
            found, f"Created character {character.id} not found in filtered list"
        )
        print(f"  Found {len(characters)} test character(s) in filtered list")

    def test_update_character(self):
        """Test updating a character."""
        # Create a character
        original_name = (
            f"Integration Test Character - DELETE ME - {datetime.now().isoformat()}"
        )
        character = self.client.characters.create(
            name=original_name,
            title="Original Title",
            age="20",
            entry="<p>Original character description with <strong>basic HTML</strong>.</p>",
        )
        self._register_character_cleanup(character.id, character.name)

        self.wait_for_api()

        # Update the character
        updated_data = {
            "title": "Updated Title",
            "age": "30",
            "pronouns": "she/her",
            "entry": "<h2>Updated Character</h2><p>This character has been <em>updated</em> with new information:</p><ol><li>New title</li><li>New age</li><li>New pronouns</li></ol>",
            "is_dead": True,
        }
        updated_character = self.client.characters.update(character.id, **updated_data)

        # Verify updates
        self.assert_equal(
            updated_character.name, original_name, "Name should not change"
        )
        self.assert_equal(updated_character.title, "Updated Title", "Title not updated")
        self.assert_equal(updated_character.age, "30", "Age not updated")
        self.assert_equal(updated_character.pronouns, "she/her", "Pronouns not updated")
        self.assert_equal(updated_character.is_dead, True, "is_dead not updated")
        self.assert_equal(
            updated_character.entry, updated_data["entry"], "Entry not updated"
        )

        print(f"  Updated character {character.id} successfully")

    def test_get_character(self):
        """Test getting a specific character."""
        # Create a character
        character_name = (
            f"Integration Test Character - DELETE ME - {datetime.now().isoformat()}"
        )
        created = self.client.characters.create(
            name=character_name,
            type="PC",
            entry="<p>A <strong>player character</strong> for testing retrieval.</p>",
        )
        self._register_character_cleanup(created.id, created.name)

        self.wait_for_api()

        # Get the character by ID
        character = self.client.characters.get(created.id)

        # Verify we got the right character
        self.assert_equal(character.id, created.id, "Character ID mismatch")
        self.assert_equal(character.name, character_name, "Character name mismatch")
        self.assert_equal(character.type, "PC", "Character type mismatch")
        self.assert_equal(
            character.entry,
            "<p>A <strong>player character</strong> for testing retrieval.</p>",
            "Character entry mismatch",
        )

        print(f"  Retrieved character {character.id} successfully")

    def test_delete_character(self):
        """Test deleting a character."""
        # Create a character
        character = self.client.characters.create(
            name=f"Integration Test Character TO DELETE - {datetime.now().isoformat()}",
            entry="<p>This character will be <del>deleted</del> soon.</p>",
        )
        character_id = character.id

        self.wait_for_api()

        # Delete the character
        self.client.characters.delete(character_id)
        # No need to register cleanup since we're testing deletion

        self.wait_for_api()

        # Verify it's deleted by trying to get it
        try:
            self.client.characters.get(character_id)
            self.assert_true(
                False, f"Character {character_id} should have been deleted"
            )
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
    # When run directly, execute all tests
    tester = TestCharacterIntegration()
    results = tester.run_all_tests()

    print("\n" + "=" * 50)
    print("CHARACTER INTEGRATION TEST RESULTS")
    print("=" * 50)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        print(f"{test_name}: {status}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed < total:
        exit(1)
