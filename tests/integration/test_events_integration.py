"""
Integration tests for Event entity operations.
"""

from datetime import datetime

# Handle both direct execution and import scenarios
if __name__ == "__main__":
    import setup_test_env

    setup_test_env.setup_environment()

from base import IntegrationTestBase


class TestEventIntegration(IntegrationTestBase):
    """Integration tests for Event CRUD operations."""

    def __init__(self):
        super().__init__()
        self._created_locations = []

    def _register_event_cleanup(self, event_id: int, name: str):
        """Register an event for cleanup."""

        def cleanup():
            if self.client:
                self.client.events.delete(event_id)

        self.register_cleanup(f"Delete event '{name}' (ID: {event_id})", cleanup)

    def _register_location_cleanup(self, location_id: int, name: str):
        """Register a location for cleanup."""
        self._created_locations.append(location_id)

        def cleanup():
            if self.client:
                self.client.locations.delete(location_id)

        self.register_cleanup(f"Delete location '{name}' (ID: {location_id})", cleanup)

    def test_create_event(self):
        """Test creating an event."""
        # Create event data
        event_data = {
            "name": f"Integration Test Event - DELETE ME - {datetime.now().isoformat()}",
            "type": "Historical",
            "date": "Year 1547, Month of Dragons",
            "entry": "<h2>The Great War</h2><p>A <strong>pivotal event</strong> that shaped the realm:</p><ul><li>Lasted 5 years</li><li>Changed the political landscape</li></ul>",
            "is_private": False,
        }

        # Create the event
        event = self.client.events.create(**event_data)
        self._register_event_cleanup(event.id, event.name)

        # Verify the event was created
        self.assert_not_none(event.id, "Event ID should not be None")
        self.assert_equal(event.name, event_data["name"], "Event name mismatch")
        self.assert_equal(event.type, event_data["type"], "Event type mismatch")
        self.assert_equal(event.date, event_data["date"], "Event date mismatch")
        self.assert_equal(event.entry, event_data["entry"], "Event entry mismatch")
        self.assert_equal(event.is_private, False, "Event should not be private")

        print(f"  Created event: {event.name} (ID: {event.id})")

    def test_create_event_with_location(self):
        """Test creating an event with a location."""
        # First create a location
        location_name = f"Battle Site - DELETE ME - {datetime.now().isoformat()}"
        location = self.client.locations.create(
            name=location_name,
            type="Battlefield",
            entry="<p>The site of a historic battle.</p>",
        )
        self._register_location_cleanup(location.id, location.name)

        self.wait_for_api()

        # Create event with location reference
        event_name = f"Battle Event - DELETE ME - {datetime.now().isoformat()}"
        event = self.client.events.create(
            name=event_name,
            type="Battle",
            date="Year 1548",
            location_id=location.id,
            entry=f"<h3>The Battle</h3><p>This battle took place at <em>{location_name}</em> and decided the fate of the kingdom.</p>",
        )
        self._register_event_cleanup(event.id, event.name)

        # Verify the event was created with location
        self.assert_equal(
            event.location_id, location.id, "Event should reference the location"
        )

        print(
            f"  Created event '{event.name}' (ID: {event.id}) at location '{location_name}'"
        )

    def test_list_events_with_filter(self):
        """Test listing events with filters."""
        # Create an event to ensure we have something to find
        test_name = f"Integration Test Event - DELETE ME - {datetime.now().isoformat()}"
        event = self.client.events.create(
            name=test_name,
            type="Test Type",
            date="Year 1549",
            entry="<h3>Test Event</h3><p>Created for <a href='#'>filter testing</a>.</p>",
        )
        self._register_event_cleanup(event.id, event.name)

        self.wait_for_api()

        # List events with name filter
        events = list(self.client.events.list(name="Integration Test Event"))

        # Verify our event appears in the list
        found = False
        for e in events:
            if e.id == event.id:
                found = True
                break

        self.assert_true(found, f"Created event {event.id} not found in filtered list")
        print(f"  Found {len(events)} test event(s) in filtered list")

    def test_update_event(self):
        """Test updating an event."""
        # Create an event
        original_name = (
            f"Integration Test Event - DELETE ME - {datetime.now().isoformat()}"
        )
        event = self.client.events.create(
            name=original_name,
            type="Original Type",
            date="Year 1550",
            entry="<p>Original event description.</p>",
        )
        self._register_event_cleanup(event.id, event.name)

        self.wait_for_api()

        # Update the event
        updated_data = {
            "type": "Updated Type",
            "date": "Year 1551, Spring",
            "entry": "<h2>Updated Event</h2><p>This event has been <strong>reinterpreted</strong> with new information:</p><ol><li>New evidence discovered</li><li>Different perspective</li></ol>",
        }
        updated_event = self.client.events.update(event.id, **updated_data)

        # Verify updates
        self.assert_equal(updated_event.name, original_name, "Name should not change")
        self.assert_equal(updated_event.type, "Updated Type", "Type not updated")
        self.assert_equal(updated_event.date, "Year 1551, Spring", "Date not updated")
        self.assert_equal(
            updated_event.entry, updated_data["entry"], "Entry not updated"
        )

        print(f"  Updated event {event.id} successfully")

    def test_get_event(self):
        """Test getting a specific event."""
        # Create an event
        event_name = (
            f"Integration Test Event - DELETE ME - {datetime.now().isoformat()}"
        )
        created = self.client.events.create(
            name=event_name,
            type="Ceremony",
            date="Year 1552",
            entry="<p>An event for testing <strong>retrieval</strong>.</p>",
        )
        self._register_event_cleanup(created.id, created.name)

        self.wait_for_api()

        # Get the event by ID
        event = self.client.events.get(created.id)

        # Verify we got the right event
        self.assert_equal(event.id, created.id, "Event ID mismatch")
        self.assert_equal(event.name, event_name, "Event name mismatch")
        self.assert_equal(event.type, "Ceremony", "Event type mismatch")
        self.assert_equal(event.date, "Year 1552", "Event date mismatch")

        print(f"  Retrieved event {event.id} successfully")

    def test_delete_event(self):
        """Test deleting an event."""
        # Create an event
        event = self.client.events.create(
            name=f"Integration Test Event TO DELETE - {datetime.now().isoformat()}",
            entry="<p>This event will be <del>forgotten</del>.</p>",
        )
        event_id = event.id

        self.wait_for_api()

        # Delete the event
        self.client.events.delete(event_id)

        self.wait_for_api()

        # Verify it's deleted by trying to get it
        try:
            self.client.events.get(event_id)
            self.assert_true(False, f"Event {event_id} should have been deleted")
        except Exception:
            # Expected - event should not be found
            pass

        print(f"  Deleted event {event_id} successfully")

    def run_all_tests(self):
        """Run all event integration tests."""
        tests = [
            ("Event Creation", self.test_create_event),
            ("Event with Location", self.test_create_event_with_location),
            ("Event Listing with Filter", self.test_list_events_with_filter),
            ("Event Update", self.test_update_event),
            ("Event Retrieval", self.test_get_event),
            ("Event Deletion", self.test_delete_event),
        ]

        results = []
        for test_name, test_func in tests:
            result = self.run_test(test_name, test_func)
            results.append((test_name, result))

        return results


if __name__ == "__main__":
    # When run directly, execute all tests
    tester = TestEventIntegration()
    results = tester.run_all_tests()

    print("\n" + "=" * 50)
    print("EVENT INTEGRATION TEST RESULTS")
    print("=" * 50)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        print(f"{test_name}: {status}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed < total:
        exit(1)
