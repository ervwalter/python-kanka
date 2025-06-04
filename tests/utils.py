"""Test utilities and mock factories."""

from typing import Any, Optional


def create_mock_entity(
    entity_type: str, entity_id: int = 1, **kwargs
) -> dict[str, Any]:
    """Create a mock entity response.

    Args:
        entity_type: The type of entity (e.g., 'character', 'location')
        entity_id: The entity ID
        **kwargs: Additional fields to override defaults

    Returns:
        Dict representing an entity from the API
    """
    base_entity = {
        "id": entity_id,
        "entity_id": entity_id * 100,  # Usually different from ID
        "name": kwargs.get("name", f"Test {entity_type.title()} {entity_id}"),
        "entry": kwargs.get("entry", f"<p>This is a test {entity_type}.</p>"),
        "image": kwargs.get("image"),
        "image_full": kwargs.get("image_full"),
        "image_thumb": kwargs.get("image_thumb"),
        "is_private": kwargs.get("is_private", False),
        "tags": kwargs.get("tags", []),
        "created_at": kwargs.get("created_at", "2024-01-01T00:00:00.000000Z"),
        "created_by": kwargs.get("created_by", 1),
        "updated_at": kwargs.get("updated_at", "2024-01-01T00:00:00.000000Z"),
        "updated_by": kwargs.get("updated_by", 1),
    }

    # Add entity-specific fields
    if entity_type == "character":
        base_entity.update(
            {
                "location_id": kwargs.get("location_id"),
                "title": kwargs.get("title"),
                "age": kwargs.get("age"),
                "sex": kwargs.get("sex"),
                "race_id": kwargs.get("race_id"),
                "type": kwargs.get("type"),
                "family_id": kwargs.get("family_id"),
                "is_dead": kwargs.get("is_dead", False),
                "traits": kwargs.get("traits"),
            }
        )
    elif entity_type == "location":
        base_entity.update(
            {
                "type": kwargs.get("type"),
                "map": kwargs.get("map"),
                "map_url": kwargs.get("map_url"),
                "is_map_private": kwargs.get("is_map_private"),
                "parent_location_id": kwargs.get("parent_location_id"),
            }
        )
    elif entity_type == "organisation":
        base_entity.update(
            {
                "location_id": kwargs.get("location_id"),
                "type": kwargs.get("type"),
                "organisation_id": kwargs.get("organisation_id"),
            }
        )
    elif entity_type == "note":
        base_entity.update(
            {
                "type": kwargs.get("type"),
            }
        )
    elif entity_type == "calendar":
        base_entity.update(
            {
                "type": kwargs.get("type"),
                "date": kwargs.get("date"),
                "parameters": kwargs.get("parameters"),
                "months": kwargs.get("months", []),
                "weekdays": kwargs.get("weekdays", []),
                "years": kwargs.get("years", {}),
                "seasons": kwargs.get("seasons", []),
                "moons": kwargs.get("moons", []),
                "suffix": kwargs.get("suffix"),
                "has_leap_year": kwargs.get("has_leap_year"),
                "leap_year_amount": kwargs.get("leap_year_amount"),
                "leap_year_month": kwargs.get("leap_year_month"),
                "leap_year_offset": kwargs.get("leap_year_offset"),
                "leap_year_start": kwargs.get("leap_year_start"),
            }
        )

    # Allow additional custom fields
    for key, value in kwargs.items():
        if key not in base_entity:
            base_entity[key] = value

    return base_entity


def create_mock_post(post_id: int = 1, **kwargs) -> dict[str, Any]:
    """Create a mock post response.

    Args:
        post_id: The post ID
        **kwargs: Additional fields to override defaults

    Returns:
        Dict representing a post from the API
    """
    return {
        "id": post_id,
        "entity_id": kwargs.get("entity_id", 100),
        "name": kwargs.get("name", f"Test Post {post_id}"),
        "entry": kwargs.get("entry", "<p>This is a test post content.</p>"),
        "created_at": kwargs.get("created_at", "2024-01-01T00:00:00.000000Z"),
        "created_by": kwargs.get("created_by", 1),
        "updated_at": kwargs.get("updated_at", "2024-01-01T00:00:00.000000Z"),
        "updated_by": kwargs.get("updated_by", 1),
        "is_private": kwargs.get("is_private", False),
        "is_pinned": kwargs.get("is_pinned", False),
        "visibility": kwargs.get("visibility", "all"),
        "position": kwargs.get("position"),
    }


def create_mock_search_result(
    entity_type: str, entity_id: int = 1, **kwargs
) -> dict[str, Any]:
    """Create a mock search result.

    Args:
        entity_type: The type of entity
        entity_id: The entity ID
        **kwargs: Additional fields

    Returns:
        Dict representing a search result
    """
    return {
        "id": entity_id,
        "entity_id": entity_id * 100,
        "name": kwargs.get("name", f"Search Result {entity_id}"),
        "type": entity_type,
        "url": kwargs.get(
            "url", f"https://app.kanka.io/w/1/entities/{entity_id * 100}"
        ),
        "is_private": kwargs.get("is_private", False),
        "tags": kwargs.get("tags", []),
        "created_at": kwargs.get("created_at", "2024-01-01T00:00:00.000000Z"),
        "updated_at": kwargs.get("updated_at", "2024-01-01T00:00:00.000000Z"),
    }


def create_api_response(
    data: Any, meta: Optional[dict] = None, links: Optional[dict] = None
) -> dict[str, Any]:
    """Create a mock API response with standard structure.

    Args:
        data: The response data (single item or list)
        meta: Pagination metadata
        links: Pagination links

    Returns:
        Dict representing an API response
    """
    response: dict[str, Any] = {
        "data": data if isinstance(data, list) else [data] if data else []
    }

    if meta is not None:
        response["meta"] = meta
    else:
        # Default pagination meta for lists
        if isinstance(data, list):
            response["meta"] = {
                "total": len(data),
                "current_page": 1,
                "per_page": 30,
                "last_page": 1,
                "from": 1 if data else None,
                "to": len(data) if data else None,
            }

    if links is not None:
        response["links"] = links
    else:
        # Default pagination links for lists
        if isinstance(data, list):
            response["links"] = {
                "first": "https://api.kanka.io/1.0/campaigns/1/entities?page=1",
                "last": "https://api.kanka.io/1.0/campaigns/1/entities?page=1",
                "prev": None,
                "next": None,
            }

    return response


def create_error_response(
    status_code: int, message: str, errors: Optional[dict] = None
) -> dict[str, Any]:
    """Create a mock error response.

    Args:
        status_code: HTTP status code
        message: Error message
        errors: Validation errors dict

    Returns:
        Dict representing an error response
    """
    response = {
        "message": message,
        "status_code": status_code,
    }

    if errors:
        response["errors"] = errors

    return response


class MockResponse:
    """Mock HTTP response for testing."""

    def __init__(
        self,
        json_data: dict[str, Any],
        status_code: int = 200,
        text: str = "",
        headers: Optional[dict[str, str]] = None,
    ):
        self.json_data = json_data
        self.status_code = status_code
        self.text = text or str(json_data)
        self.headers = headers or {}

    def json(self):
        """Return JSON data."""
        return self.json_data
