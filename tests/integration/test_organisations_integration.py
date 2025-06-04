"""
Integration tests for Organisation entity operations.
"""

from datetime import datetime

# Handle both direct execution and import scenarios
if __name__ == "__main__":
    import setup_test_env

    setup_test_env.setup_environment()

from base import IntegrationTestBase

# Organisation type is imported implicitly through the client


class TestOrganisationIntegration(IntegrationTestBase):
    """Integration tests for Organisation CRUD operations."""

    def __init__(self):
        super().__init__()

    def _register_organisation_cleanup(self, organisation_id: int, name: str):
        """Register a organisation for cleanup."""

        def cleanup():
            if self.client:
                self.client.organisations.delete(organisation_id)

        self.register_cleanup(
            f"Delete organisation '{name}' (ID: {organisation_id})", cleanup
        )

    def test_create_organisation(self):
        """Test creating an organisation."""
        # Create organisation data
        organisation_data = {
            "name": f"Integration Test Organisation - DELETE ME - {datetime.now().isoformat()}",
            "type": "Guild",
            "entry": "<h2>Adventurer's Guild</h2><p>A prestigious <strong>guild</strong> offering:</p><ul><li>Quest Board</li><li>Training Facilities</li><li>Member Benefits</li></ul><p><em>Established in the year 1023</em></p>",
            "is_private": False,
        }

        # Create the organisation
        organisation = self.client.organisations.create(**organisation_data)
        self._register_organisation_cleanup(organisation.id, organisation.name)

        # Verify the organisation was created
        self.assert_not_none(organisation.id, "Organisation ID should not be None")
        self.assert_equal(
            organisation.name, organisation_data["name"], "Organisation name mismatch"
        )
        self.assert_equal(
            organisation.type, organisation_data["type"], "Organisation type mismatch"
        )
        self.assert_equal(
            organisation.entry,
            organisation_data["entry"],
            "Organisation entry mismatch",
        )
        self.assert_equal(
            organisation.is_private, False, "Organisation should not be private"
        )

        print(f"  Created organisation: {organisation.name} (ID: {organisation.id})")

    def test_list_organisations_with_filter(self):
        """Test listing organisations with filters."""
        # First create an organisation to ensure we have something to find
        test_name = (
            f"Integration Test Organisation - DELETE ME - {datetime.now().isoformat()}"
        )
        organisation = self.client.organisations.create(
            name=test_name,
            type="Company",
            entry="<p>A <strong>trading company</strong> with <em>international reach</em>.</p>",
        )
        self._register_organisation_cleanup(organisation.id, organisation.name)

        self.wait_for_api()  # Give API time to index

        # List all organisations with our test prefix
        organisations = list(
            self.client.organisations.list(name="Integration Test Organisation")
        )

        # Verify our organisation appears in the list
        found = False
        for org in organisations:
            if org.id == organisation.id:
                found = True
                break

        self.assert_true(
            found, f"Created organisation {organisation.id} not found in filtered list"
        )
        print(f"  Found {len(organisations)} test organisation(s) in filtered list")

    def test_update_organisation(self):
        """Test updating an organisation."""
        # Create an organisation
        original_name = (
            f"Integration Test Organisation - DELETE ME - {datetime.now().isoformat()}"
        )
        organisation = self.client.organisations.create(
            name=original_name,
            type="Cult",
            entry="<p>A mysterious <strong>cult</strong> worshipping ancient powers.</p>",
        )
        self._register_organisation_cleanup(organisation.id, organisation.name)

        self.wait_for_api()

        # Update the organisation
        updated_data = {
            "type": "Secret Society",
            "entry": "<h2>The Order of Shadows</h2><p>This <em>secret society</em> has evolved with:</p><ol><li>Hidden Chapters</li><li>Coded Messages</li><li>Shadow Network</li></ol><blockquote>Knowledge is power, secrecy is survival</blockquote>",
        }
        updated_organisation = self.client.organisations.update(
            organisation.id, **updated_data
        )

        # Verify updates
        self.assert_equal(
            updated_organisation.name, original_name, "Name should not change"
        )
        self.assert_equal(
            updated_organisation.type, "Secret Society", "Type not updated"
        )
        self.assert_equal(
            updated_organisation.entry, updated_data["entry"], "Entry not updated"
        )

        print(f"  Updated organisation {organisation.id} successfully")

    def test_get_organisation(self):
        """Test getting a specific organisation."""
        # Create an organisation
        organisation_name = (
            f"Integration Test Organisation - DELETE ME - {datetime.now().isoformat()}"
        )
        created = self.client.organisations.create(
            name=organisation_name,
            type="Government",
            entry="<p>The <strong>regional government</strong> maintaining <em>law and order</em>.</p>",
        )
        self._register_organisation_cleanup(created.id, created.name)

        self.wait_for_api()

        # Get the organisation by ID
        organisation = self.client.organisations.get(created.id)

        # Verify we got the right organisation
        self.assert_equal(organisation.id, created.id, "Organisation ID mismatch")
        self.assert_equal(
            organisation.name, organisation_name, "Organisation name mismatch"
        )
        self.assert_equal(organisation.type, "Government", "Organisation type mismatch")
        self.assert_equal(
            organisation.entry,
            "<p>The <strong>regional government</strong> maintaining <em>law and order</em>.</p>",
            "Organisation entry mismatch",
        )

        print(f"  Retrieved organisation {organisation.id} successfully")

    def test_delete_organisation(self):
        """Test deleting an organisation."""
        # Create an organisation
        organisation = self.client.organisations.create(
            name=f"Integration Test Organisation TO DELETE - {datetime.now().isoformat()}",
            entry="<p>This organisation will be <del>disbanded</del> immediately.</p>",
        )
        organisation_id = organisation.id

        self.wait_for_api()

        # Delete the organisation
        self.client.organisations.delete(organisation_id)
        # No need to register cleanup since we\'re testing deletion

        self.wait_for_api()

        # Verify it's deleted by trying to get it
        try:
            self.client.organisations.get(organisation_id)
            self.assert_true(
                False, f"Organisation {organisation_id} should have been deleted"
            )
        except Exception:
            # Expected - organisation should not be found
            pass

        print(f"  Deleted organisation {organisation_id} successfully")

    def run_all_tests(self):
        """Run all organisation integration tests."""
        tests = [
            ("Organisation Creation", self.test_create_organisation),
            (
                "Organisation Listing with Filter",
                self.test_list_organisations_with_filter,
            ),
            ("Organisation Update", self.test_update_organisation),
            ("Organisation Retrieval", self.test_get_organisation),
            ("Organisation Deletion", self.test_delete_organisation),
        ]

        results = []
        for test_name, test_func in tests:
            result = self.run_test(test_name, test_func)
            results.append((test_name, result))

        return results


if __name__ == "__main__":
    tester = TestOrganisationIntegration()
    results = tester.run_all_tests()

    print("\n" + "=" * 50)
    print("ORGANISATION INTEGRATION TEST RESULTS")
    print("=" * 50)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        print(f"{test_name}: {status}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed < total:
        exit(1)
