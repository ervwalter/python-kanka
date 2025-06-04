#!/usr/bin/env python3
"""Test script to debug API response validation issues."""

import json
from kanka.models.entities import Character

# Simulate the API response that's causing issues
api_response = {
    "id": 123,
    "entity_id": 456,
    "name": "Test Character",
    "created_at": "2024-01-01T00:00:00.000000Z",
    "created_by": 1,
    "updated_at": "2024-01-01T00:00:00.000000Z",
    "updated_by": None,  # This is causing the issue
    "traits": [],  # This is also causing issues
    "is_private": False,
    "tags": []
}

print("Testing API response parsing...")
print(f"API Response: {json.dumps(api_response, indent=2)}")

try:
    character = Character(**api_response)
    print(f"\n✅ Success! Character created: {character.name}")
except Exception as e:
    print(f"\n❌ Error: {type(e).__name__}")
    print(f"Details: {e}")