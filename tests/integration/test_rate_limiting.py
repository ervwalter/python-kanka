"""
Test rate limiting functionality of the SDK.
"""

import time
from datetime import datetime

# Handle both direct execution and import scenarios
if __name__ == "__main__":
    import setup_test_env

    setup_test_env.setup_environment()

from base import IntegrationTestBase

from kanka.exceptions import RateLimitError


class TestRateLimitingIntegration(IntegrationTestBase):
    """Integration tests for rate limiting handling."""

    def __init__(self):
        super().__init__()
        self._created_characters = []

    def _register_character_cleanup(self, character_id: int, name: str):
        """Register a character for cleanup."""
        self._created_characters.append(character_id)

        def cleanup():
            if self.client:
                from contextlib import suppress

                with suppress(Exception):
                    self.client.characters.delete(character_id)

        self.register_cleanup(
            f"Delete character '{name}' (ID: {character_id})", cleanup
        )

    def test_rate_limit_retry_enabled(self):
        """Test that rate limit retry works when enabled (default)."""
        print("  Testing with retry enabled (default behavior)...")

        # Create many requests quickly to trigger rate limit
        created_count = 0
        start_time = time.time()

        try:
            for i in range(50):  # Try to create 50 characters quickly
                character = self.client.characters.create(
                    name=f"Rate Limit Test {i} - DELETE ME - {datetime.now().isoformat()}",
                    entry="Testing rate limits",
                )
                self._register_character_cleanup(character.id, character.name)
                created_count += 1

                # No delay - hammer the API

        except RateLimitError as e:
            # Should not happen with retry enabled
            print(f"  Unexpected RateLimitError after {created_count} creations: {e}")
            self.assert_true(False, "Should not get RateLimitError with retry enabled")

        elapsed = time.time() - start_time
        print(f"  Successfully created {created_count} characters in {elapsed:.1f}s")
        print(f"  Average time per request: {elapsed/created_count:.2f}s")

        # If we created all 50, the retry logic worked
        if created_count == 50:
            print("  ✓ Rate limit retry handled all requests successfully!")

    def test_rate_limit_retry_disabled(self):
        """Test that rate limit raises exception when retry is disabled."""
        print("  Testing with retry disabled...")

        # Create a new client with retry disabled
        import os

        from kanka import KankaClient

        client_no_retry = KankaClient(
            os.environ.get("KANKA_TOKEN"),
            int(os.environ.get("KANKA_CAMPAIGN_ID")),
            enable_rate_limit_retry=False,
        )

        # Create many requests quickly to trigger rate limit
        created_count = 0
        got_rate_limit = False

        try:
            for i in range(50):  # Try to create 50 characters quickly
                character = client_no_retry.characters.create(
                    name=f"No Retry Test {i} - DELETE ME - {datetime.now().isoformat()}",
                    entry="Testing rate limits without retry",
                )
                self._register_character_cleanup(character.id, character.name)
                created_count += 1

        except RateLimitError:
            # This is expected
            got_rate_limit = True
            print(f"  Got expected RateLimitError after {created_count} creations")

        self.assert_true(
            got_rate_limit,
            "Should get RateLimitError when retry is disabled and hitting rate limits",
        )

    def test_rate_limit_with_custom_settings(self):
        """Test rate limiting with custom retry settings."""
        print("  Testing with custom retry settings...")

        # Create a new client with custom settings
        import os

        from kanka import KankaClient

        client_custom = KankaClient(
            os.environ.get("KANKA_TOKEN"),
            int(os.environ.get("KANKA_CAMPAIGN_ID")),
            max_retries=2,  # Only 2 retries
            retry_delay=0.5,  # Start with 0.5s delay
            max_retry_delay=5.0,  # Max 5s delay
        )

        # Track timing
        start_time = time.time()
        created_count = 0

        try:
            for i in range(30):  # Try to create 30 characters
                character = client_custom.characters.create(
                    name=f"Custom Retry Test {i} - DELETE ME - {datetime.now().isoformat()}",
                    entry="Testing custom retry settings",
                )
                self._register_character_cleanup(character.id, character.name)
                created_count += 1

        except RateLimitError:
            # Might happen if we exceed max retries
            print(
                f"  Hit rate limit after {created_count} creations with custom settings"
            )

        elapsed = time.time() - start_time
        print(
            f"  Created {created_count} characters in {elapsed:.1f}s with custom settings"
        )

    def run_all_tests(self):
        """Run all rate limiting tests."""
        tests = [
            ("Rate Limit Retry Enabled", self.test_rate_limit_retry_enabled),
            ("Rate Limit Retry Disabled", self.test_rate_limit_retry_disabled),
            ("Rate Limit Custom Settings", self.test_rate_limit_with_custom_settings),
        ]

        # Note: These tests might take a while due to rate limiting
        print("\nNOTE: Rate limiting tests may take several minutes to complete")
        print("as they intentionally trigger and test rate limit behavior.\n")

        results = []
        for test_name, test_func in tests:
            result = self.run_test(test_name, test_func)
            results.append((test_name, result))

            # Wait between tests to reset rate limits
            if test_name != tests[-1][0]:  # Not the last test
                print("\n  Waiting 30s between tests to reset rate limits...")
                time.sleep(30)

        return results


if __name__ == "__main__":
    # When run directly, execute all tests
    tester = TestRateLimitingIntegration()
    results = tester.run_all_tests()

    print("\n" + "=" * 50)
    print("RATE LIMITING INTEGRATION TEST RESULTS")
    print("=" * 50)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        print(f"{test_name}: {status}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed < total:
        exit(1)
