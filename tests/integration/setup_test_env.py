"""
Helper module to set up test environment for individual test files.
"""

import os
import sys


def setup_environment():
    """Set up the test environment for running individual integration tests."""
    # Add the project root to the Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    tests_dir = os.path.dirname(current_dir)
    project_dir = os.path.dirname(tests_dir)

    if project_dir not in sys.path:
        sys.path.insert(0, project_dir)

    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)

    # Try to load environment variables from .env file
    try:
        from dotenv import load_dotenv

        env_file = os.path.join(current_dir, ".env")
        if os.path.exists(env_file):
            load_dotenv(env_file)
            print(f"Loaded environment from {env_file}")
    except ImportError:
        # dotenv not available, continue without it
        pass

    # Check for required environment variables
    if not os.environ.get("KANKA_TOKEN"):
        print("ERROR: KANKA_TOKEN environment variable is required")
        print("Please set it to your Kanka API token")
        sys.exit(1)

    if not os.environ.get("KANKA_CAMPAIGN_ID"):
        print("ERROR: KANKA_CAMPAIGN_ID environment variable is required")
        print("Please set it to your campaign ID")
        sys.exit(1)
