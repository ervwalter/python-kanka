"""
Integration tests for Journal entity operations.
"""

from datetime import datetime

# Handle both direct execution and import scenarios
if __name__ == "__main__":
    import setup_test_env

    setup_test_env.setup_environment()

from base import IntegrationTestBase


class TestJournalIntegration(IntegrationTestBase):
    """Integration tests for Journal CRUD operations."""

    def __init__(self):
        super().__init__()
        self._created_characters = []

    def _register_journal_cleanup(self, journal_id: int, name: str):
        """Register a journal for cleanup."""

        def cleanup():
            if self.client:
                self.client.journals.delete(journal_id)

        self.register_cleanup(f"Delete journal '{name}' (ID: {journal_id})", cleanup)

    def _register_character_cleanup(self, character_id: int, name: str):
        """Register a character for cleanup."""
        self._created_characters.append(character_id)

        def cleanup():
            if self.client:
                self.client.characters.delete(character_id)

        self.register_cleanup(
            f"Delete character '{name}' (ID: {character_id})", cleanup
        )

    def test_create_journal(self):
        """Test creating a journal."""
        # Create journal data
        journal_data = {
            "name": f"Integration Test Journal - DELETE ME - {datetime.now().isoformat()}",
            "type": "Session Log",
            "date": "2024-03-15",
            "entry": "<h2>Session 1</h2><p>The party encountered a <strong>mysterious stranger</strong> in the tavern.</p><ul><li>Received quest</li><li>Gathered supplies</li></ul>",
            "is_private": False,
        }

        # Create the journal
        journal = self.client.journals.create(**journal_data)
        self._register_journal_cleanup(journal.id, journal.name)

        # Verify the journal was created
        self.assert_not_none(journal.id, "Journal ID should not be None")
        self.assert_equal(journal.name, journal_data["name"], "Journal name mismatch")
        self.assert_equal(journal.type, journal_data["type"], "Journal type mismatch")
        self.assert_equal(journal.date, journal_data["date"], "Journal date mismatch")
        self.assert_equal(
            journal.entry, journal_data["entry"], "Journal entry mismatch"
        )
        self.assert_equal(journal.is_private, False, "Journal should not be private")

        print(f"  Created journal: {journal.name} (ID: {journal.id})")

    def test_create_journal_with_character(self):
        """Test creating a journal with an associated character."""
        # First create a character
        character_name = f"Test Author - DELETE ME - {datetime.now().isoformat()}"
        character = self.client.characters.create(
            name=character_name,
            type="PC",
            entry="<p>Character who writes journals.</p>",
        )
        self._register_character_cleanup(character.id, character.name)

        self.wait_for_api()

        # Create journal with character reference
        journal_name = f"Character Journal - DELETE ME - {datetime.now().isoformat()}"
        journal = self.client.journals.create(
            name=journal_name,
            type="Personal Diary",
            date="2024-03-16",
            character_id=character.id,
            entry=f"<h3>{character_name}'s Diary</h3><p>Today I discovered something <em>incredible</em>...</p>",
        )
        self._register_journal_cleanup(journal.id, journal.name)

        # Verify the journal was created with character
        self.assert_equal(
            journal.character_id,
            character.id,
            "Journal should reference the character",
        )

        print(
            f"  Created journal '{journal.name}' (ID: {journal.id}) for character '{character_name}'"
        )

    def test_list_journals_with_filter(self):
        """Test listing journals with filters."""
        # Create a journal to ensure we have something to find
        test_name = (
            f"Integration Test Journal - DELETE ME - {datetime.now().isoformat()}"
        )
        journal = self.client.journals.create(
            name=test_name,
            type="Adventure Log",
            date="2024-03-17",
            entry="<h2>Adventure Log</h2><p>Recording our <a href='#'>adventures</a>.</p>",
        )
        self._register_journal_cleanup(journal.id, journal.name)

        self.wait_for_api()

        # List journals with name filter
        journals = list(self.client.journals.list(name="Integration Test Journal"))

        # Verify our journal appears in the list
        found = False
        for j in journals:
            if j.id == journal.id:
                found = True
                break

        self.assert_true(
            found, f"Created journal {journal.id} not found in filtered list"
        )
        print(f"  Found {len(journals)} test journal(s) in filtered list")

    def test_update_journal(self):
        """Test updating a journal."""
        # Create a journal
        original_name = (
            f"Integration Test Journal - DELETE ME - {datetime.now().isoformat()}"
        )
        journal = self.client.journals.create(
            name=original_name,
            type="Campaign Notes",
            date="2024-03-18",
            entry="<p>Initial journal entry.</p>",
        )
        self._register_journal_cleanup(journal.id, journal.name)

        self.wait_for_api()

        # Update the journal
        updated_data = {
            "type": "Session Summary",
            "date": "2024-03-19",
            "entry": "<h2>Updated Session</h2><p>The session has been <strong>updated</strong> with new information:</p><ol><li>New encounters</li><li>Plot developments</li></ol>",
        }
        updated_journal = self.client.journals.update(journal.id, **updated_data)

        # Verify updates
        self.assert_equal(updated_journal.name, original_name, "Name should not change")
        self.assert_equal(updated_journal.type, "Session Summary", "Type not updated")
        self.assert_equal(updated_journal.date, "2024-03-19", "Date not updated")
        self.assert_equal(
            updated_journal.entry, updated_data["entry"], "Entry not updated"
        )

        print(f"  Updated journal {journal.id} successfully")

    def test_get_journal(self):
        """Test getting a specific journal."""
        # Create a journal
        journal_name = (
            f"Integration Test Journal - DELETE ME - {datetime.now().isoformat()}"
        )
        created = self.client.journals.create(
            name=journal_name,
            type="Quest Log",
            date="2024-03-20",
            entry="<p>A journal for testing <strong>retrieval</strong>.</p>",
        )
        self._register_journal_cleanup(created.id, created.name)

        self.wait_for_api()

        # Get the journal by ID
        journal = self.client.journals.get(created.id)

        # Verify we got the right journal
        self.assert_equal(journal.id, created.id, "Journal ID mismatch")
        self.assert_equal(journal.name, journal_name, "Journal name mismatch")
        self.assert_equal(journal.type, "Quest Log", "Journal type mismatch")
        self.assert_equal(journal.date, "2024-03-20", "Journal date mismatch")

        print(f"  Retrieved journal {journal.id} successfully")

    def test_delete_journal(self):
        """Test deleting a journal."""
        # Create a journal
        journal = self.client.journals.create(
            name=f"Integration Test Journal TO DELETE - {datetime.now().isoformat()}",
            entry="<p>This journal will be <del>deleted</del>.</p>",
        )
        journal_id = journal.id

        self.wait_for_api()

        # Delete the journal
        self.client.journals.delete(journal_id)

        self.wait_for_api()

        # Verify it's deleted by trying to get it
        try:
            self.client.journals.get(journal_id)
            self.assert_true(False, f"Journal {journal_id} should have been deleted")
        except Exception:
            # Expected - journal should not be found
            pass

        print(f"  Deleted journal {journal_id} successfully")

    def run_all_tests(self):
        """Run all journal integration tests."""
        tests = [
            ("Journal Creation", self.test_create_journal),
            ("Journal with Character", self.test_create_journal_with_character),
            ("Journal Listing with Filter", self.test_list_journals_with_filter),
            ("Journal Update", self.test_update_journal),
            ("Journal Retrieval", self.test_get_journal),
            ("Journal Deletion", self.test_delete_journal),
        ]

        results = []
        for test_name, test_func in tests:
            result = self.run_test(test_name, test_func)
            results.append((test_name, result))

        return results


if __name__ == "__main__":
    # When run directly, execute all tests
    tester = TestJournalIntegration()
    results = tester.run_all_tests()

    print("\n" + "=" * 50)
    print("JOURNAL INTEGRATION TEST RESULTS")
    print("=" * 50)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        print(f"{test_name}: {status}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed < total:
        exit(1)
