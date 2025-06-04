"""
Integration tests for Family entity operations.
"""

from datetime import datetime

# Handle both direct execution and import scenarios
if __name__ == "__main__":
    import setup_test_env

    setup_test_env.setup_environment()

from base import IntegrationTestBase


class TestFamilyIntegration(IntegrationTestBase):
    """Integration tests for Family CRUD operations."""

    def __init__(self):
        super().__init__()
        self._created_locations = []

    def _register_family_cleanup(self, family_id: int, name: str):
        """Register a family for cleanup."""

        def cleanup():
            if self.client:
                self.client.families.delete(family_id)

        self.register_cleanup(f"Delete family '{name}' (ID: {family_id})", cleanup)

    def _register_location_cleanup(self, location_id: int, name: str):
        """Register a location for cleanup."""
        self._created_locations.append(location_id)

        def cleanup():
            if self.client:
                self.client.locations.delete(location_id)

        self.register_cleanup(f"Delete location '{name}' (ID: {location_id})", cleanup)

    def test_create_family(self):
        """Test creating a family."""
        # Create family data
        family_data = {
            "name": f"Integration Test Family - DELETE ME - {datetime.now().isoformat()}",
            "entry": "<h2>Noble House</h2><p>An ancient <strong>noble family</strong> with a long history:</p><ul><li>Founded in the First Age</li><li>Known for their honor</li></ul>",
            "is_private": False,
        }

        # Create the family
        family = self.client.families.create(**family_data)
        self._register_family_cleanup(family.id, family.name)

        # Verify the family was created
        self.assert_not_none(family.id, "Family ID should not be None")
        self.assert_equal(family.name, family_data["name"], "Family name mismatch")
        self.assert_equal(family.entry, family_data["entry"], "Family entry mismatch")
        self.assert_equal(family.is_private, False, "Family should not be private")

        print(f"  Created family: {family.name} (ID: {family.id})")

    def test_create_family_with_location(self):
        """Test creating a family with a location (family seat)."""
        # First create a location
        location_name = f"Family Castle - DELETE ME - {datetime.now().isoformat()}"
        location = self.client.locations.create(
            name=location_name,
            type="Castle",
            entry="<p>The ancestral seat of the family.</p>",
        )
        self._register_location_cleanup(location.id, location.name)

        self.wait_for_api()

        # Create family with location reference
        family_name = f"Noble House - DELETE ME - {datetime.now().isoformat()}"
        family = self.client.families.create(
            name=family_name,
            location_id=location.id,
            entry=f"<h3>House Overview</h3><p>This noble house resides in <em>{location_name}</em>.</p>",
        )
        self._register_family_cleanup(family.id, family.name)

        # Verify the family was created with location
        self.assert_equal(
            family.location_id,
            location.id,
            "Family should reference the location",
        )

        print(
            f"  Created family '{family.name}' (ID: {family.id}) at location '{location_name}'"
        )

    def test_create_family_tree(self):
        """Test creating a family tree (parent-child relationship)."""
        # Create parent family
        parent_name = f"Parent Family - DELETE ME - {datetime.now().isoformat()}"
        parent_family = self.client.families.create(
            name=parent_name,
            entry="<p>The main family branch.</p>",
        )
        self._register_family_cleanup(parent_family.id, parent_family.name)

        self.wait_for_api()

        # Create child family (cadet branch)
        child_name = f"Cadet Branch - DELETE ME - {datetime.now().isoformat()}"
        child_family = self.client.families.create(
            name=child_name,
            family_id=parent_family.id,  # Set parent
            entry="<p>A cadet branch of the main family.</p>",
        )
        self._register_family_cleanup(child_family.id, child_family.name)

        # Verify relationships
        self.assert_equal(
            child_family.family_id,
            parent_family.id,
            "Child family should reference parent",
        )

        print(
            f"  Created family tree: {parent_family.name} (ID: {parent_family.id}) -> {child_family.name} (ID: {child_family.id})"
        )

    def test_list_families_with_filter(self):
        """Test listing families with filters."""
        # Create a family to ensure we have something to find
        test_name = (
            f"Integration Test Family - DELETE ME - {datetime.now().isoformat()}"
        )
        family = self.client.families.create(
            name=test_name,
            entry="<h3>Test Family</h3><p>Created for <a href='#'>filter testing</a>.</p>",
        )
        self._register_family_cleanup(family.id, family.name)

        self.wait_for_api()

        # List families with name filter
        families = list(self.client.families.list(name="Integration Test Family"))

        # Verify our family appears in the list
        found = False
        for f in families:
            if f.id == family.id:
                found = True
                break

        self.assert_true(
            found, f"Created family {family.id} not found in filtered list"
        )
        print(f"  Found {len(families)} test family(ies) in filtered list")

    def test_update_family(self):
        """Test updating a family."""
        # Create a family
        original_name = (
            f"Integration Test Family - DELETE ME - {datetime.now().isoformat()}"
        )
        family = self.client.families.create(
            name=original_name,
            entry="<p>Original family description.</p>",
        )
        self._register_family_cleanup(family.id, family.name)

        self.wait_for_api()

        # Update the family
        updated_data = {
            "entry": "<h2>Updated Family</h2><p>This family has <strong>grown</strong> in power:</p><ol><li>New alliances</li><li>Expanded territories</li></ol>",
        }
        updated_family = self.client.families.update(family.id, **updated_data)

        # Verify updates
        self.assert_equal(updated_family.name, original_name, "Name should not change")
        self.assert_equal(
            updated_family.entry, updated_data["entry"], "Entry not updated"
        )

        print(f"  Updated family {family.id} successfully")

    def test_get_family(self):
        """Test getting a specific family."""
        # Create a family
        family_name = (
            f"Integration Test Family - DELETE ME - {datetime.now().isoformat()}"
        )
        created = self.client.families.create(
            name=family_name,
            entry="<p>A family for testing <strong>retrieval</strong>.</p>",
        )
        self._register_family_cleanup(created.id, created.name)

        self.wait_for_api()

        # Get the family by ID
        family = self.client.families.get(created.id)

        # Verify we got the right family
        self.assert_equal(family.id, created.id, "Family ID mismatch")
        self.assert_equal(family.name, family_name, "Family name mismatch")

        print(f"  Retrieved family {family.id} successfully")

    def test_delete_family(self):
        """Test deleting a family."""
        # Create a family
        family = self.client.families.create(
            name=f"Integration Test Family TO DELETE - {datetime.now().isoformat()}",
            entry="<p>This family line will <del>end</del>.</p>",
        )
        family_id = family.id

        self.wait_for_api()

        # Delete the family
        self.client.families.delete(family_id)

        self.wait_for_api()

        # Verify it's deleted by trying to get it
        try:
            self.client.families.get(family_id)
            self.assert_true(False, f"Family {family_id} should have been deleted")
        except Exception:
            # Expected - family should not be found
            pass

        print(f"  Deleted family {family_id} successfully")

    def run_all_tests(self):
        """Run all family integration tests."""
        tests = [
            ("Family Creation", self.test_create_family),
            ("Family with Location", self.test_create_family_with_location),
            ("Family Tree", self.test_create_family_tree),
            ("Family Listing with Filter", self.test_list_families_with_filter),
            ("Family Update", self.test_update_family),
            ("Family Retrieval", self.test_get_family),
            ("Family Deletion", self.test_delete_family),
        ]

        results = []
        for test_name, test_func in tests:
            result = self.run_test(test_name, test_func)
            results.append((test_name, result))

        return results


if __name__ == "__main__":
    # When run directly, execute all tests
    tester = TestFamilyIntegration()
    results = tester.run_all_tests()

    print("\n" + "=" * 50)
    print("FAMILY INTEGRATION TEST RESULTS")
    print("=" * 50)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        print(f"{test_name}: {status}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed < total:
        exit(1)
