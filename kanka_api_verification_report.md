# Kanka API Verification Report

## Summary

This report compares the entity types implemented in the python-kanka SDK against the official Kanka API documentation (v1.0).

## Entity Types Comparison

### Core Entity Types from API Documentation

According to the official Kanka API docs, the following entity types are available:

1. **Characters** ✅ (Implemented)
2. **Locations** ✅ (Implemented)
3. **Families** ✅ (Implemented) 
4. **Organisations** ✅ (Implemented)
5. **Items** ✅ (Implemented)
6. **Notes** ✅ (Implemented)
7. **Events** ✅ (Implemented)
8. **Calendars** ✅ (Implemented)
9. **Timelines** ✅ (Implemented)
10. **Creatures** ✅ (Implemented)
11. **Races** ✅ (Implemented)
12. **Quests** ✅ (Implemented)
13. **Maps** ✅ (Implemented)
14. **Journals** ✅ (Implemented)
15. **Abilities** ⚠️ (Model exists but not registered in client)
16. **Tags** ✅ (Implemented)
17. **Conversations** ⚠️ (Model exists but not registered in client)
18. **Dice Rolls** ❌ (Not implemented)

### Additional Entity-Related Endpoints

The API also includes these entity-related concepts which we have:

- **Posts** ✅ (Implemented as related data)
- **Attributes** ✅ (Implemented)
- **Entity Events** ✅ (Implemented as EntityEvent)
- **Entity Notes** ✅ (Implemented as EntityNote)
- **Entity Inventory** ❓ (Not verified in our SDK)
- **Entity Mentions** ❓ (Not verified in our SDK)
- **Entity Tags** ❓ (Not verified in our SDK)
- **Entity Permissions** ❓ (Not verified in our SDK)
- **Relations** ❓ (Not verified in our SDK)
- **Entity Abilities** ❓ (Not verified in our SDK)
- **Entity Image** ❓ (Not verified in our SDK)
- **Entity Assets** ❓ (Not verified in our SDK)

### Additional Entity Type in SDK

- **Species** ✅ (Implemented - appears to be valid based on API docs)

## Key Findings

### 1. Missing Entity Types
- **Dice Rolls**: Not implemented at all in the SDK

### 2. Incomplete Implementations
- **Abilities**: Model exists in `entities.py` but not imported or registered in `client.py`
- **Conversations**: Model exists in `entities.py` but not imported or registered in `client.py`

### 3. Entity Notes vs Posts
Based on the API documentation:
- **Entity Notes** are a separate endpoint for private annotations on entities
- **Posts** are content entries that can be attached to entities
- These are distinct features, not replacements for each other
- Our SDK correctly implements both as separate concepts

### 4. Property Verification Status
Without detailed API endpoint documentation, we cannot fully verify if all properties match the API exactly. However, the basic entity structures appear to align with typical Kanka entity patterns.

## Recommendations

1. **Add Dice Rolls entity**: Create a new DiceRoll model and register it in the client
2. **Register Abilities manager**: Import Ability in client.py and create an abilities manager
3. **Register Conversations manager**: Import Conversation in client.py and create a conversations manager
4. **Verify additional entity-related endpoints**: Check if we need to implement:
   - Entity Inventory
   - Entity Mentions
   - Entity Tags (different from Tags entity)
   - Entity Permissions
   - Relations
   - Entity Abilities (different from Abilities entity)
   - Entity Image
   - Entity Assets

## Endpoint Naming Patterns

The API uses underscore-separated names for multi-word endpoints:
- `entity_notes` (not entitynotes)
- `entity_events` (not entityevents)

However, based on the API documentation URL structure:
- Dice Rolls appears to use `dice-rolls` (with hyphen) in the docs URL
- The actual API endpoint might be `dice_rolls` (underscore) to match other patterns
- This needs verification with actual API testing

Our SDK correctly follows the underscore pattern for existing entities.