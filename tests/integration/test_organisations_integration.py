"""
Integration tests for Organisation entity operations.
"""
from datetime import datetime
from typing import Optional

from base import IntegrationTestBase
from kanka.objects import Organisation


class TestOrganisationIntegration(IntegrationTestBase):
    """Integration tests for Organisation CRUD operations."""
    
    def __init__(self):
        super().__init__()
        self.created_organisation_id: Optional[int] = None
        
    def teardown(self):
        """Clean up any created organisations."""
        if self.created_organisation_id and self.client:
            try:
                self.client.organisations.delete(self.created_organisation_id)
                print(f"  Cleaned up organisation {self.created_organisation_id}")
            except Exception:
                pass  # Already deleted or doesn't exist
        super().teardown()
        
    def test_create_organisation(self):
        """Test creating an organisation."""
        # Create organisation data
        organisation_data = {
            "name": f"Integration Test Organisation - DELETE ME - {datetime.now().isoformat()}",
            "type": "Guild",
            "entry": "A test organisation created for integration testing.",
            "is_private": False
        }
        
        # Create the organisation
        organisation = self.client.organisations.create(**organisation_data)
        self.created_organisation_id = organisation.id
        
        # Verify the organisation was created
        self.assert_not_none(organisation.id, "Organisation ID should not be None")
        self.assert_equal(organisation.name, organisation_data["name"], "Organisation name mismatch")
        self.assert_equal(organisation.type, organisation_data["type"], "Organisation type mismatch")
        self.assert_equal(organisation.entry, organisation_data["entry"], "Organisation entry mismatch")
        self.assert_equal(organisation.is_private, False, "Organisation should not be private")
        
        print(f"  Created organisation: {organisation.name} (ID: {organisation.id})")
        
    def test_list_organisations_with_filter(self):
        """Test listing organisations with filters."""
        # First create an organisation to ensure we have something to find
        test_name = f"Integration Test Organisation - DELETE ME - {datetime.now().isoformat()}"
        organisation = self.client.organisations.create(name=test_name, type="Company")
        self.created_organisation_id = organisation.id
        
        self.wait_for_api()  # Give API time to index
        
        # List all organisations with our test prefix
        organisations = list(self.client.organisations.all(name="Integration Test Organisation"))
        
        # Verify our organisation appears in the list
        found = False
        for org in organisations:
            if org.id == organisation.id:
                found = True
                break
                
        self.assert_true(found, f"Created organisation {organisation.id} not found in filtered list")
        print(f"  Found {len(organisations)} test organisation(s) in filtered list")
        
    def test_update_organisation(self):
        """Test updating an organisation."""
        # Create an organisation
        original_name = f"Integration Test Organisation - DELETE ME - {datetime.now().isoformat()}"
        organisation = self.client.organisations.create(
            name=original_name,
            type="Cult",
            entry="Original description"
        )
        self.created_organisation_id = organisation.id
        
        self.wait_for_api()
        
        # Update the organisation
        updated_data = {
            "type": "Secret Society",
            "entry": "Updated description with more mysterious details"
        }
        updated_organisation = self.client.organisations.update(organisation.id, **updated_data)
        
        # Verify updates
        self.assert_equal(updated_organisation.name, original_name, "Name should not change")
        self.assert_equal(updated_organisation.type, "Secret Society", "Type not updated")
        self.assert_equal(updated_organisation.entry, "Updated description with more mysterious details", "Entry not updated")
        
        print(f"  Updated organisation {organisation.id} successfully")
        
    def test_get_organisation(self):
        """Test getting a specific organisation."""
        # Create an organisation
        organisation_name = f"Integration Test Organisation - DELETE ME - {datetime.now().isoformat()}"
        created = self.client.organisations.create(name=organisation_name, type="Government")
        self.created_organisation_id = created.id
        
        self.wait_for_api()
        
        # Get the organisation by ID
        organisation = self.client.organisations.get(created.id)
        
        # Verify we got the right organisation
        self.assert_equal(organisation.id, created.id, "Organisation ID mismatch")
        self.assert_equal(organisation.name, organisation_name, "Organisation name mismatch")
        self.assert_equal(organisation.type, "Government", "Organisation type mismatch")
        
        print(f"  Retrieved organisation {organisation.id} successfully")
        
    def test_delete_organisation(self):
        """Test deleting an organisation."""
        # Create an organisation
        organisation = self.client.organisations.create(
            name=f"Integration Test Organisation TO DELETE - {datetime.now().isoformat()}"
        )
        organisation_id = organisation.id
        
        self.wait_for_api()
        
        # Delete the organisation
        self.client.organisations.delete(organisation_id)
        self.created_organisation_id = None  # Already deleted
        
        self.wait_for_api()
        
        # Verify it's deleted by trying to get it
        try:
            self.client.organisations.get(organisation_id)
            self.assert_true(False, f"Organisation {organisation_id} should have been deleted")
        except Exception:
            # Expected - organisation should not be found
            pass
            
        print(f"  Deleted organisation {organisation_id} successfully")
        
    def run_all_tests(self):
        """Run all organisation integration tests."""
        tests = [
            ("Organisation Creation", self.test_create_organisation),
            ("Organisation Listing with Filter", self.test_list_organisations_with_filter),
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
    
    print("\n" + "="*50)
    print("ORGANISATION INTEGRATION TEST RESULTS")
    print("="*50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        print(f"{test_name}: {status}")
        
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed < total:
        exit(1)