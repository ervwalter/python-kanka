#!/usr/bin/env python3
"""
Runner script for Kanka SDK integration tests.

This script checks for required environment variables and runs all integration tests.
"""
import argparse
import importlib
import os
import shutil
import sys
import time

# Add the project root to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
tests_dir = os.path.dirname(current_dir)
project_dir = os.path.dirname(tests_dir)
src_dir = os.path.join(project_dir, "src")
sys.path.insert(0, src_dir)
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
        ("test_calendars_integration", "TestCalendarIntegration"),
        ("test_creatures_integration", "TestCreatureIntegration"),
        ("test_events_integration", "TestEventIntegration"),
        ("test_families_integration", "TestFamilyIntegration"),
        ("test_journals_integration", "TestJournalIntegration"),
        ("test_quests_integration", "TestQuestIntegration"),
        ("test_races_integration", "TestRaceIntegration"),
        ("test_tags_integration", "TestTagIntegration"),
        ("test_entity_tags_integration", "TestEntityTagsIntegration"),
        ("test_mentions_integration", "TestMentionsIntegration"),
        ("test_entities_api_integration", "TestEntitiesApiIntegration"),
        ("test_search_integration", "TestSearchIntegration"),
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


def run_all_tests(pause_before_cleanup=False, debug_mode=False):
    """Run all integration tests and report results."""
    print("=" * 60)
    print("KANKA SDK INTEGRATION TESTS")
    print("=" * 60)
    print(f"Start time: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Set environment variables based on arguments
    if pause_before_cleanup:
        os.environ["KANKA_TEST_DEFER_CLEANUP"] = "true"
        os.environ["KANKA_TEST_PAUSE_CLEANUP"] = "true"
        print("\nCleanup Mode: DEFERRED with PAUSE")

    # Set debug mode if requested
    debug_dir = None
    if debug_mode:
        os.environ["KANKA_DEBUG_MODE"] = "true"
        debug_dir = os.path.join(current_dir, "kanka_debug")
        os.environ["KANKA_DEBUG_DIR"] = debug_dir
        print(f"\nDebug Mode: ENABLED (logs will be saved to {debug_dir})")

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
    all_results: list[tuple[str, bool]] = []
    all_testers = []
    all_cleanup_tasks = []

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
            all_testers.append(tester)

            # Collect cleanup tasks if in pause mode
            if pause_before_cleanup and tester._cleanup_tasks:
                all_cleanup_tasks.extend(tester._cleanup_tasks)
                tester._cleanup_tasks = (
                    []
                )  # Clear so they won't be executed by individual testers
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

    # Execute deferred cleanup if enabled
    if pause_before_cleanup and all_cleanup_tasks:
        print("\n" + "=" * 60)
        print("PAUSED BEFORE CLEANUP")
        print("=" * 60)
        print(f"About to clean up {len(all_cleanup_tasks)} entities:")
        for description, _ in all_cleanup_tasks:
            print(f"  - {description}")
        print("\nYou can now inspect these entities in the Kanka web app.")
        input("Press Enter to continue with cleanup...")

        print("\nExecuting cleanup tasks...")
        for description, cleanup_func in all_cleanup_tasks:
            try:
                cleanup_func()
                print(f"  ✓ {description}")
            except Exception as e:
                print(f"  ✗ {description} failed: {str(e)}")

    print(f"\nEnd time: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Clean up debug files if they were created
    if debug_mode and debug_dir and os.path.exists(debug_dir):
        print(f"\nCleaning up debug directory: {debug_dir}")
        try:
            shutil.rmtree(debug_dir)
            print("  ✓ Debug files cleaned up")
        except Exception as e:
            print(f"  ✗ Failed to clean up debug files: {e}")

    return failed_tests == 0


def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description="Run Kanka SDK integration tests",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run tests normally (cleanup immediately after each test)
  python run_integration_tests.py

  # Run tests with pause before cleanup to inspect entities in Kanka
  python run_integration_tests.py --pause

  # Run tests with debug mode enabled (logs all HTTP requests/responses)
  python run_integration_tests.py --debug

  # Combine options
  python run_integration_tests.py -p -d
""",
    )

    parser.add_argument(
        "-p",
        "--pause",
        action="store_true",
        help="Defer cleanup to end and pause before cleanup to allow manual inspection in Kanka web app",
    )

    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="Enable debug mode to log all HTTP requests and responses to files",
    )

    args = parser.parse_args()

    success = run_all_tests(pause_before_cleanup=args.pause, debug_mode=args.debug)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
