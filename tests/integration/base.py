"""
Base class for integration tests.
"""

import os
import sys
import time
from typing import Any, Callable, Optional

# We need to add the project src to Python path before importing kanka
# This is required because this module is imported by test files
_current_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.abspath(os.path.join(_current_dir, "../.."))
_src_dir = os.path.join(_project_root, "src")
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)

from kanka import KankaClient  # noqa: E402 - Must be after path setup


class IntegrationTestBase:
    """Base class for integration tests with credential checking."""

    def __init__(self):
        self.client: Optional[KankaClient] = None
        self.campaign_id: Optional[int] = None
        self.token: Optional[str] = None
        self._cleanup_tasks: list[tuple[str, Callable]] = []
        self._defer_cleanup = False
        self._pause_before_cleanup = False

    def setup(self):
        """Set up the test client with credentials from environment."""
        self.token = os.environ.get("KANKA_TOKEN")
        campaign_id_str = os.environ.get("KANKA_CAMPAIGN_ID")

        if not self.token:
            raise ValueError(
                "KANKA_TOKEN environment variable is required. "
                "Please set it to your Kanka API token."
            )

        if not campaign_id_str:
            raise ValueError(
                "KANKA_CAMPAIGN_ID environment variable is required. "
                "Please set it to your campaign ID."
            )

        try:
            self.campaign_id = int(campaign_id_str)
        except ValueError as e:
            raise ValueError(
                f"KANKA_CAMPAIGN_ID must be a valid integer, got: {campaign_id_str}"
            ) from e

        self.client = KankaClient(self.token, self.campaign_id)

        # Check environment variables for cleanup behavior
        self._defer_cleanup = (
            os.environ.get("KANKA_TEST_DEFER_CLEANUP", "").lower() == "true"
        )
        self._pause_before_cleanup = (
            os.environ.get("KANKA_TEST_PAUSE_CLEANUP", "").lower() == "true"
        )

    def register_cleanup(self, description: str, cleanup_func: Callable):
        """Register a cleanup task to be executed later."""
        self._cleanup_tasks.append((description, cleanup_func))

    def teardown(self):
        """Clean up resources."""
        if not self._defer_cleanup:
            self._execute_cleanup_tasks()

    def _execute_cleanup_tasks(self):
        """Execute all registered cleanup tasks."""
        if not self._cleanup_tasks:
            return

        print("\nExecuting cleanup tasks...")
        for description, cleanup_func in self._cleanup_tasks:
            try:
                cleanup_func()
                print(f"  ✓ {description}")
            except Exception as e:
                print(f"  ✗ {description} failed: {str(e)}")
        self._cleanup_tasks.clear()

    def run_test(self, test_name: str, test_func):
        """Run a single test with proper setup and teardown."""
        print(f"\nRunning {test_name}...")
        try:
            self.setup()
            test_func()
            print(f"✓ {test_name} passed")
            return True
        except Exception as e:
            print(f"✗ {test_name} failed: {str(e)}")
            import traceback

            traceback.print_exc()
            return False
        finally:
            self.teardown()

    def assert_equal(self, actual: Any, expected: Any, message: str = ""):
        """Assert that two values are equal."""
        if actual != expected:
            raise AssertionError(f"{message}\nExpected: {expected}\nActual: {actual}")

    def assert_true(self, condition: bool, message: str = ""):
        """Assert that a condition is true."""
        if not condition:
            raise AssertionError(f"Assertion failed: {message}")

    def assert_in(self, item: Any, container: Any, message: str = ""):
        """Assert that an item is in a container."""
        if item not in container:
            raise AssertionError(f"{message}\n{item} not found in {container}")

    def assert_not_none(self, value: Any, message: str = ""):
        """Assert that a value is not None."""
        if value is None:
            raise AssertionError(f"Value is None: {message}")

    def wait_for_api(self, seconds: float = 0.5):
        """Wait a bit to avoid rate limiting."""
        time.sleep(seconds)
