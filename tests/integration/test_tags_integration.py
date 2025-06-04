"""
Integration tests for Tag entity operations.
"""

from datetime import datetime

# Handle both direct execution and import scenarios
if __name__ == "__main__":
    import setup_test_env

    setup_test_env.setup_environment()

from base import IntegrationTestBase


class TestTagIntegration(IntegrationTestBase):
    """Integration tests for Tag CRUD operations."""

    def __init__(self):
        super().__init__()

    def _register_tag_cleanup(self, tag_id: int, name: str):
        """Register a tag for cleanup."""

        def cleanup():
            if self.client:
                self.client.tags.delete(tag_id)

        self.register_cleanup(f"Delete tag '{name}' (ID: {tag_id})", cleanup)

    def test_create_tag(self):
        """Test creating a tag."""
        # Create tag data
        tag_data = {
            "name": f"Integration Test Tag - DELETE ME - {datetime.now().isoformat()}",
            "type": "Category",
            "colour": "red",
            "entry": "<p>This is a <strong>test tag</strong> for categorizing entities.</p>",
            "is_private": False,
        }

        # Create the tag
        tag = self.client.tags.create(**tag_data)
        self._register_tag_cleanup(tag.id, tag.name)

        # Verify the tag was created
        self.assert_not_none(tag.id, "Tag ID should not be None")
        self.assert_equal(tag.name, tag_data["name"], "Tag name mismatch")
        self.assert_equal(tag.type, tag_data["type"], "Tag type mismatch")
        self.assert_equal(tag.colour, tag_data["colour"], "Tag colour mismatch")
        self.assert_equal(tag.entry, tag_data["entry"], "Tag entry mismatch")
        self.assert_equal(tag.is_private, False, "Tag should not be private")

        print(f"  Created tag: {tag.name} (ID: {tag.id})")

    def test_create_nested_tags(self):
        """Test creating nested tags (parent-child relationship)."""
        # Create parent tag
        parent_name = f"Parent Tag - DELETE ME - {datetime.now().isoformat()}"
        parent_tag = self.client.tags.create(
            name=parent_name,
            type="Parent Category",
            colour="light-blue",
            entry="<p>Parent tag for testing hierarchies.</p>",
        )
        self._register_tag_cleanup(parent_tag.id, parent_tag.name)

        self.wait_for_api()

        # Create child tag
        child_name = f"Child Tag - DELETE ME - {datetime.now().isoformat()}"
        child_tag = self.client.tags.create(
            name=child_name,
            type="Sub Category",
            colour="green",
            tag_id=parent_tag.id,  # Set parent
            entry="<p>Child tag under parent.</p>",
        )
        self._register_tag_cleanup(child_tag.id, child_tag.name)

        # Verify relationships
        self.assert_equal(
            child_tag.tag_id, parent_tag.id, "Child tag should reference parent"
        )

        print(
            f"  Created tag hierarchy: {parent_tag.name} (ID: {parent_tag.id}) -> {child_tag.name} (ID: {child_tag.id})"
        )

    def test_list_tags_with_filter(self):
        """Test listing tags with filters."""
        # Create a tag to ensure we have something to find
        test_name = f"Integration Test Tag - DELETE ME - {datetime.now().isoformat()}"
        tag = self.client.tags.create(
            name=test_name,
            type="Test Type",
            colour="purple",
            entry="<p>Tag for <em>filter testing</em>.</p>",
        )
        self._register_tag_cleanup(tag.id, tag.name)

        self.wait_for_api()

        # List tags with name filter
        tags = list(self.client.tags.list(name="Integration Test Tag"))

        # Verify our tag appears in the list
        found = False
        for t in tags:
            if t.id == tag.id:
                found = True
                break

        self.assert_true(found, f"Created tag {tag.id} not found in filtered list")
        print(f"  Found {len(tags)} test tag(s) in filtered list")

    def test_update_tag(self):
        """Test updating a tag."""
        # Create a tag
        original_name = (
            f"Integration Test Tag - DELETE ME - {datetime.now().isoformat()}"
        )
        tag = self.client.tags.create(
            name=original_name,
            type="Original Type",
            colour="black",
            entry="<p>Original tag description.</p>",
        )
        self._register_tag_cleanup(tag.id, tag.name)

        self.wait_for_api()

        # Update the tag
        updated_data = {
            "type": "Updated Type",
            "colour": "yellow",
            "entry": "<h2>Updated Tag</h2><p>This tag has been <strong>updated</strong>.</p>",
        }
        updated_tag = self.client.tags.update(tag.id, **updated_data)

        # Verify updates
        self.assert_equal(updated_tag.name, original_name, "Name should not change")
        self.assert_equal(updated_tag.type, "Updated Type", "Type not updated")
        self.assert_equal(updated_tag.colour, "yellow", "Colour not updated")
        self.assert_equal(updated_tag.entry, updated_data["entry"], "Entry not updated")

        print(f"  Updated tag {tag.id} successfully")

    def test_get_tag(self):
        """Test getting a specific tag."""
        # Create a tag
        tag_name = f"Integration Test Tag - DELETE ME - {datetime.now().isoformat()}"
        created = self.client.tags.create(
            name=tag_name,
            type="Retrieval Test",
            colour="orange",
            entry="<p>A tag for testing retrieval.</p>",
        )
        self._register_tag_cleanup(created.id, created.name)

        self.wait_for_api()

        # Get the tag by ID
        tag = self.client.tags.get(created.id)

        # Verify we got the right tag
        self.assert_equal(tag.id, created.id, "Tag ID mismatch")
        self.assert_equal(tag.name, tag_name, "Tag name mismatch")
        self.assert_equal(tag.type, "Retrieval Test", "Tag type mismatch")
        self.assert_equal(tag.colour, "orange", "Tag colour mismatch")

        print(f"  Retrieved tag {tag.id} successfully")

    def test_delete_tag(self):
        """Test deleting a tag."""
        # Create a tag
        tag = self.client.tags.create(
            name=f"Integration Test Tag TO DELETE - {datetime.now().isoformat()}",
            entry="<p>This tag will be deleted.</p>",
        )
        tag_id = tag.id

        self.wait_for_api()

        # Delete the tag
        self.client.tags.delete(tag_id)

        self.wait_for_api()

        # Verify it's deleted by trying to get it
        try:
            self.client.tags.get(tag_id)
            self.assert_true(False, f"Tag {tag_id} should have been deleted")
        except Exception:
            # Expected - tag should not be found
            pass

        print(f"  Deleted tag {tag_id} successfully")

    def run_all_tests(self):
        """Run all tag integration tests."""
        tests = [
            ("Tag Creation", self.test_create_tag),
            ("Nested Tags", self.test_create_nested_tags),
            ("Tag Listing with Filter", self.test_list_tags_with_filter),
            ("Tag Update", self.test_update_tag),
            ("Tag Retrieval", self.test_get_tag),
            ("Tag Deletion", self.test_delete_tag),
        ]

        results = []
        for test_name, test_func in tests:
            result = self.run_test(test_name, test_func)
            results.append((test_name, result))

        return results


if __name__ == "__main__":
    # When run directly, execute all tests
    tester = TestTagIntegration()
    results = tester.run_all_tests()

    print("\n" + "=" * 50)
    print("TAG INTEGRATION TEST RESULTS")
    print("=" * 50)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        print(f"{test_name}: {status}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed < total:
        exit(1)
