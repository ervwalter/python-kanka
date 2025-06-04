# Entity Types Update Summary

## Changes Made

### Removed Entity Types (For SDK Simplification)
- **Conversation** - Removed for simplification
- **Bookmark** - Removed for simplification
- **AttributeTemplate** - Removed for simplification  
- **DiceRoll** - Removed for simplification
- **Timeline** - Removed for simplification
- **Map** - Removed for simplification
- **Ability** - Removed for simplification
- **Item** - Removed for simplification

### Removed Entity Types (Not Top-Level Entities)
- **EntityNote** - This is a sub-resource, not a top-level entity
- **EntityEvent** - This is a sub-resource, not a top-level entity  
- **Attribute** - Attributes are sub-resources attached to entities
- **Species** - This doesn't exist in the Kanka API routes

### Files Updated
1. **kanka/models/entities.py**
   - Removed: EntityNote, EntityEvent, Attribute, Species classes
   - Added: DiceRoll, AttributeTemplate, Bookmark classes
   - Added entity_type property overrides for DiceRoll and AttributeTemplate
   - Updated model rebuild list

2. **kanka/client.py**
   - Updated imports to remove deleted classes and add new ones
   - Removed managers: species, attributes, entity_notes, entity_events
   - Added managers: abilities, conversations, dice_rolls, attribute_templates, bookmarks
   - Updated docstring to reflect correct managers

3. **kanka/models/__init__.py**
   - Updated imports and __all__ list to reflect changes

4. **kanka/__init__.py**
   - Updated imports and __all__ list to include new entity types

5. **tests/test_models.py**
   - Removed tests for Attribute and EntityEvent classes

6. **tests/test_client.py**
   - Updated manager initialization test to check for correct managers

## Verification
All tests pass successfully after these changes. The entity types now correctly match the Kanka API routes specification.