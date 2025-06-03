#!/usr/bin/env python3
"""
Runner script for Kanka SDK integration tests.

This script checks for required environment variables and runs all integration tests.
"""
import os
import sys
import time
from typing import List, Tuple

# Add the tests/integration directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import all test modules
from test_characters_integration import TestCharacterIntegration
from test_locations_integration import TestLocationIntegration
from test_organisations_integration import TestOrganisationIntegration
from test_notes_integration import TestNoteIntegration
from test_posts_integration import TestPostIntegration


def check_environment():
    """Check that required environment variables are set."""
    token = os.environ.get('KANKA_TOKEN')
    campaign_id = os.environ.get('KANKA_CAMPAIGN_ID')
    
    if not token:
        print("ERROR: KANKA_TOKEN environment variable is not set!")
        print("Please set it to your Kanka API token:")
        print("  export KANKA_TOKEN='your-api-token-here'")
        return False
        
    if not campaign_id:
        print("ERROR: KANKA_CAMPAIGN_ID environment variable is not set!")
        print("Please set it to your campaign ID:")
        print("  export KANKA_CAMPAIGN_ID='your-campaign-id'")
        return False
        
    try:
        int(campaign_id)
    except ValueError:
        print(f"ERROR: KANKA_CAMPAIGN_ID must be a valid integer, got: {campaign_id}")
        return False
        
    return True


def run_all_integration_tests():
    """Run all integration test suites."""
    print("="*60)
    print("KANKA SDK INTEGRATION TESTS")
    print("="*60)
    print("\nThese tests will create and delete real data in your Kanka campaign.")
    print("All test entities will have 'Integration Test' and 'DELETE ME' in their names.")
    print("\nStarting tests in 3 seconds...\n")
    time.sleep(3)
    
    # Test suites to run
    test_suites = [
        ("Characters", TestCharacterIntegration),
        ("Locations", TestLocationIntegration),
        ("Organisations", TestOrganisationIntegration),
        ("Notes", TestNoteIntegration),
        ("Posts", TestPostIntegration),
    ]
    
    all_results: List[Tuple[str, List[Tuple[str, bool]]]] = []
    suite_results: List[Tuple[str, bool]] = []
    
    for suite_name, test_class in test_suites:
        print(f"\n{'='*60}")
        print(f"Running {suite_name} Integration Tests")
        print(f"{'='*60}")
        
        try:
            tester = test_class()
            results = tester.run_all_tests()
            all_results.append((suite_name, results))
            
            # Check if all tests in this suite passed
            suite_passed = all(result for _, result in results)
            suite_results.append((suite_name, suite_passed))
            
        except Exception as e:
            print(f"\nERROR running {suite_name} tests: {str(e)}")
            import traceback
            traceback.print_exc()
            all_results.append((suite_name, [("Suite Error", False)]))
            suite_results.append((suite_name, False))
            
        # Small delay between test suites to avoid rate limiting
        time.sleep(1)
    
    # Print summary
    print("\n" + "="*60)
    print("INTEGRATION TEST SUMMARY")
    print("="*60)
    
    total_tests = 0
    passed_tests = 0
    
    for suite_name, results in all_results:
        suite_total = len(results)
        suite_passed = sum(1 for _, result in results if result)
        total_tests += suite_total
        passed_tests += suite_passed
        
        print(f"\n{suite_name}: {suite_passed}/{suite_total} tests passed")
        for test_name, result in results:
            status = "✓" if result else "✗"
            print(f"  {status} {test_name}")
    
    print(f"\n{'='*60}")
    print(f"OVERALL: {passed_tests}/{total_tests} tests passed")
    
    # Return exit code based on results
    return 0 if passed_tests == total_tests else 1


def main():
    """Main entry point."""
    # Check environment variables
    if not check_environment():
        return 1
        
    # Run all tests
    return run_all_integration_tests()


if __name__ == "__main__":
    sys.exit(main())