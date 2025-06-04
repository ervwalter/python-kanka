#!/usr/bin/env python3
"""
Runner script for Kanka SDK integration tests.

This script checks for required environment variables and runs all integration tests.
"""
import importlib
import os
import sys
import time
from typing import List, Tuple

# Add the project root to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
tests_dir = os.path.dirname(current_dir)
project_dir = os.path.dirname(tests_dir)
sys.path.insert(0, project_dir)
sys.path.insert(0, current_dir)


def check_environment():
    """Check that required environment variables are set."""
    # Try to load from .env file first
    try:
        from dotenv import load_dotenv

        env_file = os.path.join(current_dir, ".env")
        if os.path.exists(env_file):
            load_dotenv(env_file)
            print(f"Loaded environment from {env_file}")
    except ImportError:
        pass

    # Check for required variables
    missing = []
    if not os.environ.get("KANKA_TOKEN"):
        missing.append("KANKA_TOKEN")
    if not os.environ.get("KANKA_CAMPAIGN_ID"):
        missing.append("KANKA_CAMPAIGN_ID")

    if missing:
        print("ERROR: Missing required environment variables:")
        for var in missing:
            print(f"  - {var}")
        print("\nPlease set these variables or create a .env file")
        return False

    return True


def load_test_classes():
    """Dynamically load test classes to avoid import order issues."""
    test_modules = [
        ("test_characters_integration", "TestCharacterIntegration"),
        ("test_locations_integration", "TestLocationIntegration"),
        ("test_notes_integration", "TestNoteIntegration"),
        ("test_organisations_integration", "TestOrganisationIntegration"),
        ("test_posts_integration", "TestPostIntegration"),
    ]

    test_classes = []
    for module_name, class_name in test_modules:
        try:
            module = importlib.import_module(module_name)
            test_class = getattr(module, class_name)
            test_classes.append((class_name, test_class))
        except (ImportError, AttributeError) as e:
            print(f"Warning: Could not load {module_name}.{class_name}: {e}")

    return test_classes


def run_all_tests():
    """Run all integration tests and report results."""
    print("=" * 60)
    print("KANKA SDK INTEGRATION TESTS")
    print("=" * 60)
    print(f"Start time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Check environment first
    if not check_environment():
        return False

    # Load test classes dynamically
    test_classes = load_test_classes()
    if not test_classes:
        print("ERROR: No test classes could be loaded")
        return False

    # Run all test suites
    all_results: List[Tuple[str, bool]] = []

    for class_name, test_class in test_classes:
        print(f"\n{'='*50}")
        print(
            f"Running {class_name.replace('Test', '').replace('Integration', '')} Tests"
        )
        print("=" * 50)

        try:
            tester = test_class()
            results = tester.run_all_tests()
            all_results.extend(results)
        except Exception as e:
            print(f"ERROR running {class_name}: {e}")
            import traceback

            traceback.print_exc()

    # Print summary
    print("\n" + "=" * 60)
    print("INTEGRATION TEST SUMMARY")
    print("=" * 60)

    total_tests = len(all_results)
    passed_tests = sum(1 for _, passed in all_results if passed)
    failed_tests = total_tests - passed_tests

    # Group results by test suite
    current_suite = ""
    for test_name, passed in all_results:
        suite = test_name.split()[0]
        if suite != current_suite:
            current_suite = suite
            print(f"\n{suite} Tests:")

        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"  {test_name}: {status}")

    print(f"\nTotal Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success Rate: {passed_tests/total_tests*100:.1f}%")

    print(f"\nEnd time: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    return failed_tests == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
