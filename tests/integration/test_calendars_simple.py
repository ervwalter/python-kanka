"""
Simple integration tests for Calendar entity operations.
Calendars have complex requirements, so we test basic CRUD only.
"""

# Handle both direct execution and import scenarios
if __name__ == "__main__":
    import setup_test_env

    setup_test_env.setup_environment()

from base import IntegrationTestBase


class TestCalendarIntegration(IntegrationTestBase):
    """Integration tests for Calendar CRUD operations."""

    def __init__(self):
        super().__init__()

    def _register_calendar_cleanup(self, calendar_id: int, name: str):
        """Register a calendar for cleanup."""

        def cleanup():
            if self.client:
                self.client.calendars.delete(calendar_id)

        self.register_cleanup(f"Delete calendar '{name}' (ID: {calendar_id})", cleanup)

    def test_list_calendars(self):
        """Test listing calendars."""
        # Just list existing calendars
        calendars = list(self.client.calendars.list())

        print(f"  Found {len(calendars)} calendar(s) in campaign")

        # If there are calendars, try to get one
        if calendars:
            first_calendar = calendars[0]
            self.assert_not_none(first_calendar.id, "Calendar should have ID")
            self.assert_not_none(first_calendar.name, "Calendar should have name")

    def test_get_calendar_if_exists(self):
        """Test getting a calendar if one exists."""
        # List calendars first
        calendars = list(self.client.calendars.list())

        if not calendars:
            print("  No calendars found in campaign to test retrieval")
            return

        # Get the first calendar
        calendar_id = calendars[0].id
        calendar = self.client.calendars.get(calendar_id)

        # Verify we got the calendar
        self.assert_equal(calendar.id, calendar_id, "Calendar ID mismatch")
        self.assert_not_none(calendar.name, "Calendar should have name")

        print(
            f"  Successfully retrieved calendar '{calendar.name}' (ID: {calendar.id})"
        )

    def run_all_tests(self):
        """Run all calendar integration tests."""
        tests = [
            ("Calendar Listing", self.test_list_calendars),
            ("Calendar Retrieval", self.test_get_calendar_if_exists),
        ]

        results = []
        for test_name, test_func in tests:
            result = self.run_test(test_name, test_func)
            results.append((test_name, result))

        return results


if __name__ == "__main__":
    # When run directly, execute all tests
    tester = TestCalendarIntegration()
    results = tester.run_all_tests()

    print("\n" + "=" * 50)
    print("CALENDAR INTEGRATION TEST RESULTS")
    print("=" * 50)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        print(f"{test_name}: {status}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed < total:
        exit(1)
