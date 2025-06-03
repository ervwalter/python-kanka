"""
Integration tests for Note entity operations.
"""
from datetime import datetime
from typing import Optional

from base import IntegrationTestBase
from kanka.objects import Note


class TestNoteIntegration(IntegrationTestBase):
    """Integration tests for Note CRUD operations."""
    
    def __init__(self):
        super().__init__()
        self.created_note_id: Optional[int] = None
        
    def teardown(self):
        """Clean up any created notes."""
        if self.created_note_id and self.client:
            try:
                self.client.notes.delete(self.created_note_id)
                print(f"  Cleaned up note {self.created_note_id}")
            except Exception:
                pass  # Already deleted or doesn't exist
        super().teardown()
        
    def test_create_note(self):
        """Test creating a note."""
        # Create note data
        note_data = {
            "name": f"Integration Test Note - DELETE ME - {datetime.now().isoformat()}",
            "type": "Lore",
            "entry": "This is a test note created for integration testing purposes.",
            "is_private": False,
            "is_pinned": False
        }
        
        # Create the note
        note = self.client.notes.create(**note_data)
        self.created_note_id = note.id
        
        # Verify the note was created
        self.assert_not_none(note.id, "Note ID should not be None")
        self.assert_equal(note.name, note_data["name"], "Note name mismatch")
        self.assert_equal(note.type, note_data["type"], "Note type mismatch")
        self.assert_equal(note.entry, note_data["entry"], "Note entry mismatch")
        self.assert_equal(note.is_private, False, "Note should not be private")
        self.assert_equal(note.is_pinned, False, "Note should not be pinned")
        
        print(f"  Created note: {note.name} (ID: {note.id})")
        
    def test_list_notes_with_filter(self):
        """Test listing notes with filters."""
        # First create a note to ensure we have something to find
        test_name = f"Integration Test Note - DELETE ME - {datetime.now().isoformat()}"
        note = self.client.notes.create(name=test_name, type="Secret")
        self.created_note_id = note.id
        
        self.wait_for_api()  # Give API time to index
        
        # List all notes with our test prefix
        notes = list(self.client.notes.all(name="Integration Test Note"))
        
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
        original_name = f"Integration Test Note - DELETE ME - {datetime.now().isoformat()}"
        note = self.client.notes.create(
            name=original_name,
            type="History",
            entry="Original note content",
            is_pinned=False
        )
        self.created_note_id = note.id
        
        self.wait_for_api()
        
        # Update the note
        updated_data = {
            "type": "Important History",
            "entry": "Updated note content with additional historical details",
            "is_pinned": True
        }
        updated_note = self.client.notes.update(note.id, **updated_data)
        
        # Verify updates
        self.assert_equal(updated_note.name, original_name, "Name should not change")
        self.assert_equal(updated_note.type, "Important History", "Type not updated")
        self.assert_equal(updated_note.entry, "Updated note content with additional historical details", "Entry not updated")
        self.assert_equal(updated_note.is_pinned, True, "is_pinned not updated")
        
        print(f"  Updated note {note.id} successfully")
        
    def test_get_note(self):
        """Test getting a specific note."""
        # Create a note
        note_name = f"Integration Test Note - DELETE ME - {datetime.now().isoformat()}"
        created = self.client.notes.create(name=note_name, type="Plot")
        self.created_note_id = created.id
        
        self.wait_for_api()
        
        # Get the note by ID
        note = self.client.notes.get(created.id)
        
        # Verify we got the right note
        self.assert_equal(note.id, created.id, "Note ID mismatch")
        self.assert_equal(note.name, note_name, "Note name mismatch")
        self.assert_equal(note.type, "Plot", "Note type mismatch")
        
        print(f"  Retrieved note {note.id} successfully")
        
    def test_delete_note(self):
        """Test deleting a note."""
        # Create a note
        note = self.client.notes.create(
            name=f"Integration Test Note TO DELETE - {datetime.now().isoformat()}"
        )
        note_id = note.id
        
        self.wait_for_api()
        
        # Delete the note
        self.client.notes.delete(note_id)
        self.created_note_id = None  # Already deleted
        
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
    
    print("\n" + "="*50)
    print("NOTE INTEGRATION TEST RESULTS")
    print("="*50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        print(f"{test_name}: {status}")
        
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed < total:
        exit(1)