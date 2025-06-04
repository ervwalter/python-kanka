#!/usr/bin/env python3
"""Run only the posts integration test."""

import os
import sys

# Add the project root to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
tests_dir = os.path.dirname(current_dir)
project_dir = os.path.dirname(tests_dir)
sys.path.insert(0, project_dir)
sys.path.insert(0, current_dir)

from test_posts_integration import TestPostIntegration

# Load env
try:
    from dotenv import load_dotenv
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_file):
        load_dotenv(env_file)
except ImportError:
    pass

# Check environment
if not os.environ.get('KANKA_TOKEN') or not os.environ.get('KANKA_CAMPAIGN_ID'):
    print("ERROR: KANKA_TOKEN and KANKA_CAMPAIGN_ID must be set")
    sys.exit(1)

# Run posts tests
print("Running Posts Integration Tests...")
print("="*60)

tester = TestPostIntegration()
results = tester.run_all_tests()

print("\nResults:")
for test_name, result in results:
    status = "✓" if result else "✗"
    print(f"  {status} {test_name}")

# Return appropriate exit code
passed = sum(1 for _, result in results if result)
total = len(results)
print(f"\nPassed: {passed}/{total}")
sys.exit(0 if passed == total else 1)