"""
Integration tests for Location entity operations.
"""

from datetime import datetime

# Handle both direct execution and import scenarios
if __name__ == "__main__":
    import setup_test_env

    setup_test_env.setup_environment()

from base import IntegrationTestBase

# Location type is imported implicitly through the client


class TestLocationIntegration(IntegrationTestBase):
    """Integration tests for Location CRUD operations."""

    def __init__(self):
        super().__init__()

    def _register_location_cleanup(self, location_id: int, name: str):
        """Register a location for cleanup."""

        def cleanup():
            if self.client:
                self.client.locations.delete(location_id)

        self.register_cleanup(f"Delete location '{name}' (ID: {location_id})", cleanup)

    def test_create_location(self):
        """Test creating a location."""
        # Create location data
        location_data = {
            "name": f"Integration Test Location - DELETE ME - {datetime.now().isoformat()}",
            "type": "City",
            "entry": '<h2>Test City</h2><p>This location has <a href="#">links</a> and lists:</p><ul><li>Market Square</li><li>Temple District</li><li>Royal Palace</li></ul>',
            "is_private": False,
        }

        # Create the location
        location = self.client.locations.create(**location_data)
        self._register_location_cleanup(location.id, location.name)

        # Verify the location was created
        self.assert_not_none(location.id, "Location ID should not be None")
        self.assert_equal(
            location.name, location_data["name"], "Location name mismatch"
        )
        self.assert_equal(
            location.type, location_data["type"], "Location type mismatch"
        )
        self.assert_equal(
            location.entry, location_data["entry"], "Location entry mismatch"
        )
        self.assert_equal(location.is_private, False, "Location should not be private")

        print(f"  Created location: {location.name} (ID: {location.id})")

    def test_list_locations_with_filter(self):
        """Test listing locations with filters."""
        # First create a location to ensure we have something to find
        test_name = (
            f"Integration Test Location - DELETE ME - {datetime.now().isoformat()}"
        )
        location = self.client.locations.create(
            name=test_name,
            type="Village",
            entry="<p>A small <em>village</em> with <strong>peaceful</strong> residents.</p>",
        )
        self._register_location_cleanup(location.id, location.name)

        self.wait_for_api()  # Give API time to index

        # List all locations with our test prefix
        locations = list(self.client.locations.list(name="Integration Test Location"))

        # Verify our location appears in the list
        found = False
        for loc in locations:
            if loc.id == location.id:
                found = True
                break

        self.assert_true(
            found, f"Created location {location.id} not found in filtered list"
        )
        print(f"  Found {len(locations)} test location(s) in filtered list")

    def test_update_location(self):
        """Test updating a location."""
        # Create a location
        original_name = (
            f"Integration Test Location - DELETE ME - {datetime.now().isoformat()}"
        )
        location = self.client.locations.create(
            name=original_name,
            type="Town",
            entry="<p>A <strong>bustling town</strong> with various districts.</p>",
        )
        self._register_location_cleanup(location.id, location.name)

        self.wait_for_api()

        # Update the location
        updated_data = {
            "type": "Metropolis",
            "entry": "<h2>Grand Metropolis</h2><p>This location has grown into a <em>massive city</em> with:</p><ol><li>Commercial Hub</li><li>Industrial Zone</li><li>Entertainment District</li></ol><p>Population: <strong>1 million+</strong></p>",
        }
        updated_location = self.client.locations.update(location.id, **updated_data)

        # Verify updates
        self.assert_equal(
            updated_location.name, original_name, "Name should not change"
        )
        self.assert_equal(updated_location.type, "Metropolis", "Type not updated")
        self.assert_equal(
            updated_location.entry, updated_data["entry"], "Entry not updated"
        )

        print(f"  Updated location {location.id} successfully")

    def test_get_location(self):
        """Test getting a specific location."""
        # Create a location
        location_name = (
            f"Integration Test Location - DELETE ME - {datetime.now().isoformat()}"
        )
        created = self.client.locations.create(
            name=location_name,
            type="Castle",
            entry="<p>An ancient <strong>castle</strong> perched on a <em>rocky cliff</em>.</p>",
        )
        self._register_location_cleanup(created.id, created.name)

        self.wait_for_api()

        # Get the location by ID
        location = self.client.locations.get(created.id)

        # Verify we got the right location
        self.assert_equal(location.id, created.id, "Location ID mismatch")
        self.assert_equal(location.name, location_name, "Location name mismatch")
        self.assert_equal(location.type, "Castle", "Location type mismatch")
        self.assert_equal(
            location.entry,
            "<p>An ancient <strong>castle</strong> perched on a <em>rocky cliff</em>.</p>",
            "Location entry mismatch",
        )

        print(f"  Retrieved location {location.id} successfully")

    def test_delete_location(self):
        """Test deleting a location."""
        # Create a location
        location = self.client.locations.create(
            name=f"Integration Test Location TO DELETE - {datetime.now().isoformat()}",
            entry="<p>This location will be <del>removed</del> from the map.</p>",
        )
        location_id = location.id

        self.wait_for_api()

        # Delete the location
        self.client.locations.delete(location_id)
        # No need to register cleanup since we\'re testing deletion

        self.wait_for_api()

        # Verify it's deleted by trying to get it
        try:
            self.client.locations.get(location_id)
            self.assert_true(False, f"Location {location_id} should have been deleted")
        except Exception:
            # Expected - location should not be found
            pass

        print(f"  Deleted location {location_id} successfully")

    def run_all_tests(self):
        """Run all location integration tests."""
        tests = [
            ("Location Creation", self.test_create_location),
            ("Location Listing with Filter", self.test_list_locations_with_filter),
            ("Location Update", self.test_update_location),
            ("Location Retrieval", self.test_get_location),
            ("Location Deletion", self.test_delete_location),
        ]

        results = []
        for test_name, test_func in tests:
            result = self.run_test(test_name, test_func)
            results.append((test_name, result))

        return results


if __name__ == "__main__":
    tester = TestLocationIntegration()
    results = tester.run_all_tests()

    print("\n" + "=" * 50)
    print("LOCATION INTEGRATION TEST RESULTS")
    print("=" * 50)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        print(f"{test_name}: {status}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed < total:
        exit(1)
