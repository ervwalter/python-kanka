# Error Handling

The SDK provides specific exception types for different API error scenarios. All exceptions inherit from `KankaException`.

## Exception Hierarchy

```
KankaException           ← Base exception (catch-all)
├── AuthenticationError   ← HTTP 401 (invalid token)
├── ForbiddenError        ← HTTP 403 (insufficient permissions)
├── NotFoundError         ← HTTP 404 (entity doesn't exist)
├── ValidationError       ← HTTP 422 (invalid request data)
└── RateLimitError        ← HTTP 429 (rate limit exceeded)
```

## Importing Exceptions

```python
# Import specific exceptions
from kanka.exceptions import NotFoundError, ValidationError

# Or import from the top-level package
from kanka import NotFoundError, ValidationError, KankaException
```

## Exception Details

### AuthenticationError (401)

Raised when the API token is invalid, expired, or missing.

```python
from kanka import KankaClient, AuthenticationError

try:
    client = KankaClient(token="invalid-token", campaign_id=123)
    client.characters.list()
except AuthenticationError:
    print("Invalid API token — check your token at https://app.kanka.io/settings/api")
```

### ForbiddenError (403)

Raised when you don't have permission to access a resource.

```python
from kanka import ForbiddenError

try:
    client.characters.get(private_char_id)
except ForbiddenError:
    print("You don't have permission to view this entity")
```

Common causes:
- Accessing private entities in a campaign you're not a member of
- Insufficient permissions on shared campaigns
- Admin-only operations without admin rights

### NotFoundError (404)

Raised when the requested entity doesn't exist or has been deleted.

```python
from kanka import NotFoundError

try:
    character = client.characters.get(999999)
except NotFoundError:
    print("Character not found")
```

### ValidationError (422)

Raised when the API rejects your request data. The error message includes details about which fields failed validation.

```python
from kanka import ValidationError

try:
    client.characters.create(name="")  # Empty name
except ValidationError as e:
    print(f"Validation error: {e}")
```

### RateLimitError (429)

Raised when the API rate limit is exceeded. By default, the SDK automatically retries rate-limited requests, so this exception is only raised when:

- Auto-retry is disabled (`enable_rate_limit_retry=False`)
- All retry attempts have been exhausted

```python
from kanka import RateLimitError

try:
    for i in range(1000):
        client.characters.list()
except RateLimitError:
    print("Rate limit exceeded after all retries")
```

See [Rate Limiting](rate-limiting.md) for details on the retry behavior.

### KankaException (catch-all)

Raised for any other API errors (other 4xx/5xx status codes). Also serves as the base class for catching any SDK exception.

```python
from kanka import KankaException

try:
    client.characters.get(123)
except KankaException as e:
    print(f"API error: {e}")
```

## Recommended Pattern

Order your `except` clauses from most specific to least specific:

```python
from kanka import (
    KankaException,
    NotFoundError,
    ValidationError,
    RateLimitError,
    AuthenticationError,
    ForbiddenError,
)

try:
    character = client.characters.get(123)
    updated = client.characters.update(character, name="New Name")
except NotFoundError:
    print("Character not found")
except ValidationError as e:
    print(f"Invalid data: {e}")
except AuthenticationError:
    print("Check your API token")
except ForbiddenError:
    print("Insufficient permissions")
except RateLimitError:
    print("Rate limit exceeded after retries")
except KankaException as e:
    print(f"Other API error: {e}")
```

## Safe Operation Helpers

A useful pattern for optional lookups:

```python
def safe_get(manager, entity_id):
    """Get an entity, returning None if not found."""
    try:
        return manager.get(entity_id)
    except NotFoundError:
        return None

character = safe_get(client.characters, 123)
if character:
    print(character.name)
else:
    print("Not found")
```
