"""
Integration tests for Race entity operations.
"""

from datetime import datetime

# Handle both direct execution and import scenarios
if __name__ == "__main__":
    import setup_test_env

    setup_test_env.setup_environment()

from base import IntegrationTestBase


class TestRaceIntegration(IntegrationTestBase):
    """Integration tests for Race CRUD operations."""

    def __init__(self):
        super().__init__()

    def _register_race_cleanup(self, race_id: int, name: str):
        """Register a race for cleanup."""

        def cleanup():
            if self.client:
                self.client.races.delete(race_id)

        self.register_cleanup(f"Delete race '{name}' (ID: {race_id})", cleanup)

    def test_create_race(self):
        """Test creating a race."""
        # Create race data
        race_data = {
            "name": f"Integration Test Race - DELETE ME - {datetime.now().isoformat()}",
            "type": "Humanoid",
            "entry": "<h2>Test Race</h2><p>A <strong>mystical race</strong> with unique abilities:</p><ul><li>Enhanced vision</li><li>Natural magic affinity</li></ul>",
            "is_private": False,
        }

        # Create the race
        race = self.client.races.create(**race_data)
        self._register_race_cleanup(race.id, race.name)

        # Verify the race was created
        self.assert_not_none(race.id, "Race ID should not be None")
        self.assert_equal(race.name, race_data["name"], "Race name mismatch")
        self.assert_equal(race.type, race_data["type"], "Race type mismatch")
        self.assert_equal(race.entry, race_data["entry"], "Race entry mismatch")
        self.assert_equal(race.is_private, False, "Race should not be private")

        print(f"  Created race: {race.name} (ID: {race.id})")

    def test_create_subrace(self):
        """Test creating a subrace (race with parent)."""
        # Create parent race
        parent_name = f"Parent Race - DELETE ME - {datetime.now().isoformat()}"
        parent_race = self.client.races.create(
            name=parent_name,
            type="Major Race",
            entry="<p>The main race category.</p>",
        )
        self._register_race_cleanup(parent_race.id, parent_race.name)

        self.wait_for_api()

        # Create subrace
        subrace_name = f"Subrace - DELETE ME - {datetime.now().isoformat()}"
        subrace = self.client.races.create(
            name=subrace_name,
            type="Subrace",
            race_id=parent_race.id,  # Set parent
            entry="<p>A variant of the main race with <em>distinct features</em>.</p>",
        )
        self._register_race_cleanup(subrace.id, subrace.name)

        # Verify relationships
        self.assert_equal(
            subrace.race_id, parent_race.id, "Subrace should reference parent race"
        )

        print(
            f"  Created race hierarchy: {parent_race.name} (ID: {parent_race.id}) -> {subrace.name} (ID: {subrace.id})"
        )

    def test_list_races_with_filter(self):
        """Test listing races with filters."""
        # Create a race to ensure we have something to find
        test_name = f"Integration Test Race - DELETE ME - {datetime.now().isoformat()}"
        race = self.client.races.create(
            name=test_name,
            type="Test Species",
            entry="<h3>Test Species</h3><p>Created for <a href='#'>filter testing</a>.</p>",
        )
        self._register_race_cleanup(race.id, race.name)

        self.wait_for_api()

        # List races with name filter
        races = list(self.client.races.list(name="Integration Test Race"))

        # Verify our race appears in the list
        found = False
        for r in races:
            if r.id == race.id:
                found = True
                break

        self.assert_true(found, f"Created race {race.id} not found in filtered list")
        print(f"  Found {len(races)} test race(s) in filtered list")

    def test_update_race(self):
        """Test updating a race."""
        # Create a race
        original_name = (
            f"Integration Test Race - DELETE ME - {datetime.now().isoformat()}"
        )
        race = self.client.races.create(
            name=original_name,
            type="Original Type",
            entry="<p>Original race description.</p>",
        )
        self._register_race_cleanup(race.id, race.name)

        self.wait_for_api()

        # Update the race
        updated_data = {
            "type": "Updated Species",
            "entry": "<h2>Updated Race</h2><p>This race has been <strong>evolved</strong> with new traits:</p><ol><li>Enhanced abilities</li><li>New weaknesses</li></ol>",
        }
        updated_race = self.client.races.update(race.id, **updated_data)

        # Verify updates
        self.assert_equal(updated_race.name, original_name, "Name should not change")
        self.assert_equal(updated_race.type, "Updated Species", "Type not updated")
        self.assert_equal(
            updated_race.entry, updated_data["entry"], "Entry not updated"
        )

        print(f"  Updated race {race.id} successfully")

    def test_get_race(self):
        """Test getting a specific race."""
        # Create a race
        race_name = f"Integration Test Race - DELETE ME - {datetime.now().isoformat()}"
        created = self.client.races.create(
            name=race_name,
            type="Unique Species",
            entry="<p>A race for testing <strong>retrieval</strong>.</p>",
        )
        self._register_race_cleanup(created.id, created.name)

        self.wait_for_api()

        # Get the race by ID
        race = self.client.races.get(created.id)

        # Verify we got the right race
        self.assert_equal(race.id, created.id, "Race ID mismatch")
        self.assert_equal(race.name, race_name, "Race name mismatch")
        self.assert_equal(race.type, "Unique Species", "Race type mismatch")

        print(f"  Retrieved race {race.id} successfully")

    def test_delete_race(self):
        """Test deleting a race."""
        # Create a race
        race = self.client.races.create(
            name=f"Integration Test Race TO DELETE - {datetime.now().isoformat()}",
            entry="<p>This race will be <del>extinct</del>.</p>",
        )
        race_id = race.id

        self.wait_for_api()

        # Delete the race
        self.client.races.delete(race_id)

        self.wait_for_api()

        # Verify it's deleted by trying to get it
        try:
            self.client.races.get(race_id)
            self.assert_true(False, f"Race {race_id} should have been deleted")
        except Exception:
            # Expected - race should not be found
            pass

        print(f"  Deleted race {race_id} successfully")

    def run_all_tests(self):
        """Run all race integration tests."""
        tests = [
            ("Race Creation", self.test_create_race),
            ("Subrace Creation", self.test_create_subrace),
            ("Race Listing with Filter", self.test_list_races_with_filter),
            ("Race Update", self.test_update_race),
            ("Race Retrieval", self.test_get_race),
            ("Race Deletion", self.test_delete_race),
        ]

        results = []
        for test_name, test_func in tests:
            result = self.run_test(test_name, test_func)
            results.append((test_name, result))

        return results


if __name__ == "__main__":
    # When run directly, execute all tests
    tester = TestRaceIntegration()
    results = tester.run_all_tests()

    print("\n" + "=" * 50)
    print("RACE INTEGRATION TEST RESULTS")
    print("=" * 50)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        print(f"{test_name}: {status}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed < total:
        exit(1)
