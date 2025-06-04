"""
Integration tests for Note entity operations.
"""

from datetime import datetime

# Handle both direct execution and import scenarios
if __name__ == "__main__":
    import setup_test_env

    setup_test_env.setup_environment()

from base import IntegrationTestBase

# Note type is imported implicitly through the client


class TestNoteIntegration(IntegrationTestBase):
    """Integration tests for Note CRUD operations."""

    def __init__(self):
        super().__init__()

    def _register_note_cleanup(self, note_id: int, name: str):
        """Register a note for cleanup."""

        def cleanup():
            if self.client:
                self.client.notes.delete(note_id)

        self.register_cleanup(f"Delete note '{name}' (ID: {note_id})", cleanup)

    def test_create_note(self):
        """Test creating a note."""
        # Create note data
        note_data = {
            "name": f"Integration Test Note - DELETE ME - {datetime.now().isoformat()}",
            "type": "Lore",
            "entry": "<h2>Ancient Lore</h2><p>This <strong>mystical knowledge</strong> contains:</p><ul><li>Forgotten spells</li><li>Lost artifacts</li><li>Secret rituals</li></ul><p><em>Handle with care - powerful magic within</em></p>",
            "is_private": False,
        }

        # Create the note
        note = self.client.notes.create(**note_data)
        self._register_note_cleanup(note.id, note.name)

        # Verify the note was created
        self.assert_not_none(note.id, "Note ID should not be None")
        self.assert_equal(note.name, note_data["name"], "Note name mismatch")
        self.assert_equal(note.type, note_data["type"], "Note type mismatch")
        self.assert_equal(note.entry, note_data["entry"], "Note entry mismatch")
        self.assert_equal(note.is_private, False, "Note should not be private")

        print(f"  Created note: {note.name} (ID: {note.id})")

    def test_list_notes_with_filter(self):
        """Test listing notes with filters."""
        # First create a note to ensure we have something to find
        test_name = f"Integration Test Note - DELETE ME - {datetime.now().isoformat()}"
        note = self.client.notes.create(
            name=test_name,
            type="Secret",
            entry="<p>A <strong>secret note</strong> containing <em>classified information</em>.</p>",
        )
        self._register_note_cleanup(note.id, note.name)

        self.wait_for_api()  # Give API time to index

        # List all notes with our test prefix
        notes = list(self.client.notes.list(name="Integration Test Note"))

        # Verify our note appears in the list
        found = False
        for n in notes:
            if n.id == note.id:
                found = True
                break

        self.assert_true(found, f"Created note {note.id} not found in filtered list")
        print(f"  Found {len(notes)} test note(s) in filtered list")

    def test_update_note(self):
        """Test updating a note."""
        # Create a note
        original_name = (
            f"Integration Test Note - DELETE ME - {datetime.now().isoformat()}"
        )
        note = self.client.notes.create(
            name=original_name,
            type="History",
            entry="<p>Original <strong>historical record</strong> from the archives.</p>",
        )
        self._register_note_cleanup(note.id, note.name)

        self.wait_for_api()

        # Update the note
        updated_data = {
            "type": "Important History",
            "entry": "<h2>Updated Historical Records</h2><p>These <em>crucial documents</em> reveal:</p><ol><li>Timeline of Events</li><li>Key Figures</li><li>Historical Impact</li></ol><blockquote>Those who forget history are doomed to repeat it</blockquote>",
        }
        updated_note = self.client.notes.update(note.id, **updated_data)

        # Verify updates
        self.assert_equal(updated_note.name, original_name, "Name should not change")
        self.assert_equal(updated_note.type, "Important History", "Type not updated")
        self.assert_equal(
            updated_note.entry, updated_data["entry"], "Entry not updated"
        )

        print(f"  Updated note {note.id} successfully")

    def test_get_note(self):
        """Test getting a specific note."""
        # Create a note
        note_name = f"Integration Test Note - DELETE ME - {datetime.now().isoformat()}"
        created = self.client.notes.create(
            name=note_name,
            type="Plot",
            entry="<p>Key <strong>plot points</strong> for the <em>upcoming campaign</em>.</p>",
        )
        self._register_note_cleanup(created.id, created.name)

        self.wait_for_api()

        # Get the note by ID
        note = self.client.notes.get(created.id)

        # Verify we got the right note
        self.assert_equal(note.id, created.id, "Note ID mismatch")
        self.assert_equal(note.name, note_name, "Note name mismatch")
        self.assert_equal(note.type, "Plot", "Note type mismatch")
        self.assert_equal(
            note.entry,
            "<p>Key <strong>plot points</strong> for the <em>upcoming campaign</em>.</p>",
            "Note entry mismatch",
        )

        print(f"  Retrieved note {note.id} successfully")

    def test_delete_note(self):
        """Test deleting a note."""
        # Create a note
        note = self.client.notes.create(
            name=f"Integration Test Note TO DELETE - {datetime.now().isoformat()}",
            entry="<p>This note will be <del>erased</del> from the records.</p>",
        )
        note_id = note.id

        self.wait_for_api()

        # Delete the note
        self.client.notes.delete(note_id)
        # No need to register cleanup since we\'re testing deletion

        self.wait_for_api()

        # Verify it's deleted by trying to get it
        try:
            self.client.notes.get(note_id)
            self.assert_true(False, f"Note {note_id} should have been deleted")
        except Exception:
            # Expected - note should not be found
            pass

        print(f"  Deleted note {note_id} successfully")

    def run_all_tests(self):
        """Run all note integration tests."""
        tests = [
            ("Note Creation", self.test_create_note),
            ("Note Listing with Filter", self.test_list_notes_with_filter),
            ("Note Update", self.test_update_note),
            ("Note Retrieval", self.test_get_note),
            ("Note Deletion", self.test_delete_note),
        ]

        results = []
        for test_name, test_func in tests:
            result = self.run_test(test_name, test_func)
            results.append((test_name, result))

        return results


if __name__ == "__main__":
    tester = TestNoteIntegration()
    results = tester.run_all_tests()

    print("\n" + "=" * 50)
    print("NOTE INTEGRATION TEST RESULTS")
    print("=" * 50)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        print(f"{test_name}: {status}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed < total:
        exit(1)
