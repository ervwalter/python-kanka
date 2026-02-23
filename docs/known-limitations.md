# Known Limitations

These are known quirks and limitations of the Kanka API that affect SDK behavior.

## Search Endpoint Ignores `limit`

The search endpoint (`client.search()`) does not respect the `limit` parameter. The API returns a fixed number of results per page. Pagination is only available through the `page` parameter.

## Post Updates Require `name`

The Kanka API requires the `name` field when updating a post, even if you're not changing it. If you omit `name`, the API will return a validation error.

```python
# Must include name even if not changing it
client.characters.update_post(
    character,
    post.id,
    name=post.name,  # Required!
    entry="Updated content...",
)
```

## Unknown Fields Are Silently Ignored

The API silently ignores field names it doesn't recognize when creating or updating entities. This means typos in field names won't produce an error — the field will simply be ignored.

```python
# 'locaton_id' is a typo — no error, just silently ignored
client.characters.create(name="Test", locaton_id=5)
```

## `updated_by` Can Be Null

The `updated_by` field on entities and posts can be `null` from the API, even though `created_by` is always populated.

## HTML Content Normalization

The API normalizes HTML content in `entry` fields. For example, quote characters may be converted. Don't rely on exact string matching of HTML content returned by the API.

## Entity Types Not Yet in SDK

The following Kanka API entity types are available in the API but not yet implemented in this SDK:

- Timeline
- Item
- Relation
- DiceRoll
- Conversation
- AttributeTemplate
- Bookmark
- Ability
- Map
- Inventory

## Custom Fields

True custom fields on entities are handled through Kanka's "attributes" system (accessible via `related=True`), not as direct fields on create/update. Entity-specific fields like `sex` on characters are supported, but arbitrary custom field names are silently ignored by the API.
