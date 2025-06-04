#!/usr/bin/env python3
"""
Error Handling Example

This example demonstrates proper error handling patterns when using
the python-kanka library.
"""

import os
import time

from kanka import KankaClient
from kanka.exceptions import (
    AuthenticationError,
    KankaException,
    NotFoundError,
    RateLimitError,
    ValidationError,
)

TOKEN = os.environ.get("KANKA_TOKEN")
CAMPAIGN_ID_STR = os.environ.get("KANKA_CAMPAIGN_ID")
CAMPAIGN_ID = int(CAMPAIGN_ID_STR) if CAMPAIGN_ID_STR else 0


def handle_authentication_error():
    """Demonstrate handling authentication errors."""
    print("\n1. Authentication Error:")
    print("   Attempting to connect with invalid token...")

    try:
        bad_client = KankaClient(token="invalid-token", campaign_id=CAMPAIGN_ID)
        bad_client.characters.list()
    except AuthenticationError as e:
        print(f"   ✓ Caught AuthenticationError: {e}")
        print("   Solution: Check your API token in Kanka settings")


def handle_not_found_error(client):
    """Demonstrate handling not found errors."""
    print("\n2. Not Found Error:")
    print("   Attempting to get non-existent character...")

    try:
        client.characters.get(999999999)
    except NotFoundError as e:
        print(f"   ✓ Caught NotFoundError: {e}")
        print("   Solution: Verify the entity ID exists")


def handle_validation_error(client):
    """Demonstrate handling validation errors."""
    print("\n3. Validation Error:")

    # Empty name
    print("   a) Creating character with empty name...")
    try:
        client.characters.create(name="")
    except ValidationError as e:
        print(f"   ✓ Caught ValidationError: {e}")
        if hasattr(e, "errors"):
            print(f"   Validation errors: {e.errors}")

    # Invalid data type
    print("\n   b) Creating character with invalid data...")
    try:
        # Tags should be a list of IDs, not a string
        client.characters.create(name="Test", tags="invalid")
    except ValidationError as e:
        print(f"   ✓ Caught ValidationError: {e}")

    # Invalid field
    print("\n   c) Updating with invalid field value...")
    char = client.characters.create(name="Temporary Test Character")
    try:
        # location_id should be an integer
        client.characters.update(char, location_id="not-a-number")
    except ValidationError as e:
        print(f"   ✓ Caught ValidationError: {e}")
    finally:
        client.characters.delete(char)


def handle_forbidden_error(client):
    """Demonstrate handling forbidden errors."""
    print("\n4. Forbidden Error:")
    print("   This error occurs when accessing resources without permission")
    print(f"   Current campaign: {client.campaign_id}")
    print("   (Cannot demonstrate without a restricted resource)")
    print("   Common causes:")
    print("   - Accessing private entities from another campaign")
    print("   - Insufficient permissions on shared campaigns")


def handle_rate_limit_error(client):
    """Demonstrate handling rate limit errors."""
    print("\n5. Rate Limit Error:")
    print("   Kanka API has rate limits (30 requests per minute)")
    print("   Making rapid requests to demonstrate...")

    # Note: This is for demonstration only - don't do this in production!
    created_chars = []
    try:
        for i in range(35):  # Try to exceed rate limit
            char = client.characters.create(name=f"RateLimit Test {i}")
            created_chars.append(char)
            if i % 10 == 0:
                print(f"   Created {i} characters...")
    except RateLimitError as e:
        print(f"   ✓ Caught RateLimitError: {e}")
        if hasattr(e, "retry_after"):
            print(f"   Retry after: {e.retry_after} seconds")
        print("   Solution: Implement backoff and retry logic")
    finally:
        # Cleanup
        print("   Cleaning up test characters...")
        for char in created_chars:
            try:
                client.characters.delete(char)
                time.sleep(2)  # Avoid hitting rate limit during cleanup
            except Exception:
                pass


def demonstrate_retry_logic(client):
    """Demonstrate retry logic for rate limits."""
    print("\n6. Implementing Retry Logic:")

    def get_character_with_retry(char_id, max_retries=3):
        """Get a character with automatic retry on rate limit."""
        for attempt in range(max_retries):
            try:
                return client.characters.get(char_id)
            except RateLimitError as e:
                if attempt < max_retries - 1:
                    wait_time = getattr(e, "retry_after", 60)
                    print(f"   Rate limited. Waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    raise

    # Create a test character
    char = client.characters.create(name="Retry Test")
    print(f"   Created test character: {char.name}")

    # Get with retry logic
    try:
        retrieved = get_character_with_retry(char.id)
        print(f"   ✓ Successfully retrieved: {retrieved.name}")
    except RateLimitError:
        print("   × Still rate limited after retries")
    finally:
        client.characters.delete(char)


def demonstrate_generic_error_handling(client):
    """Demonstrate catching generic Kanka exceptions."""
    print("\n7. Generic Error Handling:")
    print("   Using base KankaException for catch-all handling...")

    try:
        # This will cause some kind of error
        client.characters.get(999999999)
    except KankaException as e:
        print(f"   ✓ Caught KankaException: {type(e).__name__}")
        print(f"   Message: {e}")


def demonstrate_safe_operations(client):
    """Demonstrate safe operation patterns."""
    print("\n8. Safe Operation Patterns:")

    def safe_get_character(char_id):
        """Safely get a character, returning None if not found."""
        try:
            return client.characters.get(char_id)
        except NotFoundError:
            return None

    def safe_create_character(name, **kwargs):
        """Safely create a character with validation."""
        try:
            if not name or not name.strip():
                print("   × Name is required")
                return None
            return client.characters.create(name=name, **kwargs)
        except ValidationError as e:
            print(f"   × Validation failed: {e}")
            return None

    # Test safe operations
    print("   Testing safe get...")
    char = safe_get_character(999999)
    if char is None:
        print("   ✓ Safely handled missing character")

    print("\n   Testing safe create...")
    char = safe_create_character("")  # Invalid
    if char is None:
        print("   ✓ Safely handled invalid creation")

    char = safe_create_character("Valid Character")  # Valid
    if char:
        print(f"   ✓ Successfully created: {char.name}")
        client.characters.delete(char)


def main():
    """Run all error handling demonstrations."""

    if not TOKEN or not CAMPAIGN_ID:
        print("Please set KANKA_TOKEN and KANKA_CAMPAIGN_ID environment variables")
        exit(1)

    print("Python-Kanka Error Handling Demo")
    print("=" * 50)

    # Test authentication separately (it will fail to create client)
    handle_authentication_error()

    # Create valid client for other tests
    client = KankaClient(token=TOKEN, campaign_id=CAMPAIGN_ID)

    # Run demonstrations
    handle_not_found_error(client)
    handle_validation_error(client)
    handle_forbidden_error(client)
    # Skip rate limit demo by default (uncomment to test)
    # handle_rate_limit_error(client)
    demonstrate_retry_logic(client)
    demonstrate_generic_error_handling(client)
    demonstrate_safe_operations(client)

    print("\n" + "=" * 50)
    print("Error Handling Best Practices:")
    print("1. Always catch specific exceptions when possible")
    print("2. Implement retry logic for rate limits")
    print("3. Validate data before sending to API")
    print("4. Provide helpful error messages to users")
    print("5. Log errors for debugging")
    print("6. Clean up resources in finally blocks")
    print("7. Use generic KankaException as last resort")


if __name__ == "__main__":
    main()
