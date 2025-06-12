"""Main Kanka API client for interacting with the Kanka API.

This module provides the primary interface for working with Kanka's RESTful API.
It handles authentication, request management, and provides convenient access to
all entity types through manager objects.

Example:
    Basic usage of the KankaClient:

    >>> from kanka import KankaClient
    >>> client = KankaClient(token="your-api-token", campaign_id=12345)
    >>> characters = client.characters.list()
    >>> dragon = client.search("dragon")
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Union

from .exceptions import (
    AuthenticationError,
    ForbiddenError,
    KankaException,
    NotFoundError,
    RateLimitError,
    ValidationError,
)
from .managers import EntityManager
from .models.common import SearchResult
from .models.entities import (
    Calendar,
    Character,
    Creature,
    Event,
    Family,
    Journal,
    Location,
    Note,
    Organisation,
    Quest,
    Race,
    Tag,
)


class KankaClient:
    """Main client for Kanka API interaction with automatic rate limit handling.

    This client provides a unified interface to access all Kanka entities
    within a specific campaign. It handles authentication, request management,
    automatic retry on rate limits, and provides entity-specific managers
    for CRUD operations.

    The client automatically handles rate limiting by:
    - Retrying requests that receive 429 (Rate Limit) responses
    - Using exponential backoff between retries
    - Parsing rate limit headers to determine optimal retry delays
    - Respecting the API's rate limit reset times

    Attributes:
        BASE_URL (str): The base URL for the Kanka API
        token (str): Authentication token for API access
        campaign_id (int): ID of the campaign to work with
        session: Configured requests.Session instance
        enable_rate_limit_retry (bool): Whether to automatically retry on rate limits
        max_retries (int): Maximum number of retries for rate limited requests
        retry_delay (float): Initial delay between retries in seconds
        max_retry_delay (float): Maximum delay between retries in seconds

    Entity Managers:
        calendars: Access to Calendar entities
        characters: Access to Character entities
        creatures: Access to Creature entities
        events: Access to Event entities
        families: Access to Family entities
        journals: Access to Journal entities
        locations: Access to Location entities
        notes: Access to Note entities
        organisations: Access to Organisation entities
        quests: Access to Quest entities
        races: Access to Race entities
        tags: Access to Tag entities

    Example:
        >>> # Basic usage with automatic rate limit handling
        >>> client = KankaClient("your-token", 12345)
        >>>
        >>> # Disable automatic retry for rate limits
        >>> client = KankaClient("your-token", 12345, enable_rate_limit_retry=False)
        >>>
        >>> # Customize retry behavior
        >>> client = KankaClient(
        ...     "your-token", 12345,
        ...     max_retries=5,
        ...     retry_delay=2.0,
        ...     max_retry_delay=120.0
        ... )
    """

    BASE_URL = "https://api.kanka.io/1.0"

    def __init__(
        self,
        token: str,
        campaign_id: int,
        *,
        enable_rate_limit_retry: bool = True,
        max_retries: int = 8,
        retry_delay: float = 1.0,
        max_retry_delay: float = 15.0,
    ):
        """Initialize the Kanka client.

        Args:
            token: API authentication token
            campaign_id: Campaign ID to work with
            enable_rate_limit_retry: Whether to automatically retry on rate limits
            max_retries: Maximum number of retries for rate limited requests
            retry_delay: Initial delay between retries in seconds
            max_retry_delay: Maximum delay between retries in seconds
        """
        self.token = token
        self.campaign_id = campaign_id
        self.enable_rate_limit_retry = enable_rate_limit_retry
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.max_retry_delay = max_retry_delay

        # Debug mode configuration
        self._debug_mode = os.environ.get("KANKA_DEBUG_MODE", "").lower() == "true"
        self._debug_dir = Path(os.environ.get("KANKA_DEBUG_DIR", "kanka_debug"))
        self._request_counter = 0

        # Create debug directory if in debug mode
        if self._debug_mode:
            self._debug_dir.mkdir(exist_ok=True)

        # Set up session with default headers
        # Import requests here to avoid import issues
        import requests

        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )

        # Initialize entity managers
        self._init_managers()

    def _init_managers(self):
        """Initialize entity managers for each entity type."""
        # Core entities
        self._calendars = EntityManager(self, "calendars", Calendar)
        self._characters = EntityManager(self, "characters", Character)
        self._creatures = EntityManager(self, "creatures", Creature)
        self._events = EntityManager(self, "events", Event)
        self._families = EntityManager(self, "families", Family)
        self._journals = EntityManager(self, "journals", Journal)
        self._locations = EntityManager(self, "locations", Location)
        self._notes = EntityManager(self, "notes", Note)
        self._organisations = EntityManager(self, "organisations", Organisation)
        self._quests = EntityManager(self, "quests", Quest)
        self._races = EntityManager(self, "races", Race)
        self._tags = EntityManager(self, "tags", Tag)

    @property
    def calendars(self) -> EntityManager[Calendar]:
        """Access calendar entities.

        Returns:
            EntityManager[Calendar]: Manager for Calendar entity operations
        """
        return self._calendars

    @property
    def characters(self) -> EntityManager[Character]:
        """Access character entities.

        Returns:
            EntityManager[Character]: Manager for Character entity operations
        """
        return self._characters

    @property
    def creatures(self) -> EntityManager[Creature]:
        """Access creature entities.

        Returns:
            EntityManager[Creature]: Manager for Creature entity operations
        """
        return self._creatures

    @property
    def events(self) -> EntityManager[Event]:
        """Access event entities.

        Returns:
            EntityManager[Event]: Manager for Event entity operations
        """
        return self._events

    @property
    def families(self) -> EntityManager[Family]:
        """Access family entities.

        Returns:
            EntityManager[Family]: Manager for Family entity operations
        """
        return self._families

    @property
    def journals(self) -> EntityManager[Journal]:
        """Access journal entities.

        Returns:
            EntityManager[Journal]: Manager for Journal entity operations
        """
        return self._journals

    @property
    def locations(self) -> EntityManager[Location]:
        """Access location entities.

        Returns:
            EntityManager[Location]: Manager for Location entity operations
        """
        return self._locations

    @property
    def notes(self) -> EntityManager[Note]:
        """Access note entities.

        Returns:
            EntityManager[Note]: Manager for Note entity operations
        """
        return self._notes

    @property
    def organisations(self) -> EntityManager[Organisation]:
        """Access organisation entities.

        Returns:
            EntityManager[Organisation]: Manager for Organisation entity operations
        """
        return self._organisations

    @property
    def quests(self) -> EntityManager[Quest]:
        """Access quest entities.

        Returns:
            EntityManager[Quest]: Manager for Quest entity operations
        """
        return self._quests

    @property
    def races(self) -> EntityManager[Race]:
        """Access race entities.

        Returns:
            EntityManager[Race]: Manager for Race entity operations
        """
        return self._races

    @property
    def tags(self) -> EntityManager[Tag]:
        """Access tag entities.

        Returns:
            EntityManager[Tag]: Manager for Tag entity operations
        """
        return self._tags

    def search(self, term: str, page: int = 1) -> list[SearchResult]:
        """Search across all entity types.

        Note: The Kanka API search endpoint does not respect limit parameters,
        so pagination control is limited to page selection only.

        Args:
            term: Search term
            page: Page number (default: 1)

        Returns:
            List of search results

        Example:
            results = client.search("dragon")
            results = client.search("dragon", page=2)
        """
        params: dict[str, Union[int, str]] = {"page": page}
        response = self._request("GET", f"search/{term}", params=params)

        # Store pagination metadata for access if needed
        self._last_search_meta = response.get("meta", {})
        self._last_search_links = response.get("links", {})

        return [SearchResult(**item) for item in response["data"]]

    def entity(self, entity_id: int) -> dict[str, Any]:
        """Get a single entity by entity_id.

        This endpoint provides direct access to any entity regardless of type.

        Args:
            entity_id: The entity ID

        Returns:
            Entity data dictionary

        Raises:
            NotFoundError: If entity doesn't exist
        """
        response = self._request("GET", f"entities/{entity_id}")
        return response["data"]  # type: ignore[no-any-return]

    def entities(self, **filters) -> list[dict[str, Any]]:
        """Access the /entities endpoint with filters.

        This endpoint provides a unified way to query entities across all types
        with various filtering options.

        Args:
            **filters: Filter parameters like types, name, is_private, tags

        Returns:
            List of entity data
        """
        params: dict[str, Union[int, str]] = {}

        # Handle special filters
        if "types" in filters and isinstance(filters["types"], list):
            params["types"] = ",".join(filters["types"])
        elif "types" in filters:
            params["types"] = filters["types"]

        if "tags" in filters and isinstance(filters["tags"], list):
            params["tags"] = ",".join(map(str, filters["tags"]))
        elif "tags" in filters:
            params["tags"] = filters["tags"]

        # Add other filters
        for key in ["name", "is_private", "created_by", "updated_by"]:
            if key in filters and filters[key] is not None:
                if isinstance(filters[key], bool):
                    params[key] = int(filters[key])
                else:
                    params[key] = filters[key]

        response = self._request("GET", "entities", params=params)
        return response["data"]  # type: ignore[no-any-return]

    def _parse_rate_limit_headers(self, response) -> Optional[float]:
        """Parse rate limit headers from response.

        Returns:
            Suggested retry delay in seconds, or None if not available
        """
        # Common rate limit headers
        retry_after = response.headers.get("Retry-After")
        if retry_after:
            try:
                # Could be seconds or a date
                return float(retry_after)
            except ValueError:
                # Try parsing as date
                from email.utils import parsedate_to_datetime

                try:
                    retry_date = parsedate_to_datetime(retry_after)
                    return (
                        retry_date
                        - parsedate_to_datetime(response.headers.get("Date", ""))
                    ).total_seconds()
                except Exception:
                    pass

        # Check X-RateLimit headers
        remaining = response.headers.get("X-RateLimit-Remaining")
        reset = response.headers.get("X-RateLimit-Reset")

        if remaining and reset:
            try:
                if int(remaining) == 0:
                    # Calculate seconds until reset
                    reset_time = int(reset)
                    current_time = int(time.time())
                    return max(0, reset_time - current_time)
            except (ValueError, TypeError):
                pass

        return None

    def _log_debug_request(
        self, method: str, url: str, request_data: dict, response, response_time: float
    ):
        """Log request and response to debug file."""
        if not self._debug_mode:
            return

        self._request_counter += 1
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Extract endpoint info from URL for filename
        endpoint_parts = url.replace(self.BASE_URL, "").strip("/").split("/")
        endpoint_name = "_".join(endpoint_parts[2:])  # Skip 'campaigns/{id}/'
        if not endpoint_name:
            endpoint_name = "root"

        # Create descriptive filename
        filename = (
            f"{self._request_counter:04d}_{timestamp}_{method}_{endpoint_name}.json"
        )
        filepath = self._debug_dir / filename

        # Prepare debug data
        debug_data = {
            "timestamp": datetime.now().isoformat(),
            "request_number": self._request_counter,
            "request": {
                "method": method,
                "url": url,
                "headers": dict(self.session.headers),
                "params": request_data.get("params", {}),
                "json": request_data.get("json", {}),
            },
            "response": {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "time_seconds": response_time,
                "body": None,
            },
        }

        # Try to parse response body
        try:
            response_body = response.json()
            if "response" in debug_data and isinstance(debug_data["response"], dict):
                debug_data["response"]["body"] = response_body
        except Exception:
            if "response" in debug_data and isinstance(debug_data["response"], dict):
                debug_data["response"]["body"] = response.text

        # Write to file
        with open(filepath, "w") as f:
            json.dump(debug_data, f, indent=2, default=str)

    def _request(self, method: str, endpoint: str, **kwargs) -> dict[str, Any]:
        """Make HTTP request to Kanka API with automatic retry on rate limits.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (relative to campaign)
            **kwargs: Additional request parameters

        Returns:
            Response data

        Raises:
            Various exceptions based on status code
        """
        # Build full URL
        url = f"{self.BASE_URL}/campaigns/{self.campaign_id}/{endpoint}"

        attempts = 0
        delay = self.retry_delay
        last_exception = None

        while attempts <= self.max_retries:
            try:
                # Track request time
                start_time = time.time()

                # Make request
                response = self.session.request(method, url, **kwargs)

                # Calculate response time
                response_time = time.time() - start_time

                # Log to debug file if enabled
                self._log_debug_request(method, url, kwargs, response, response_time)

                # Handle errors
                if response.status_code == 401:
                    raise AuthenticationError("Invalid authentication token")
                elif response.status_code == 403:
                    raise ForbiddenError("Access forbidden")
                elif response.status_code == 404:
                    raise NotFoundError(f"Resource not found: {endpoint}")
                elif response.status_code == 422:
                    error_data = response.json() if response.text else {}
                    raise ValidationError(f"Validation error: {error_data}")
                elif response.status_code == 429:
                    # Rate limit exceeded
                    attempts += 1
                    if not self.enable_rate_limit_retry or attempts > self.max_retries:
                        raise RateLimitError(
                            f"Rate limit exceeded after {attempts-1} retries"
                        )

                    # Parse rate limit headers for smart retry
                    suggested_delay = self._parse_rate_limit_headers(response)
                    if suggested_delay is not None:
                        delay = min(suggested_delay, self.max_retry_delay)

                    time.sleep(delay)
                    # Exponential backoff for next attempt
                    delay = min(delay * 2, self.max_retry_delay)
                    continue

                elif response.status_code >= 400:
                    raise KankaException(
                        f"API error {response.status_code}: {response.text}"
                    )

                # Success - return response
                # Return empty dict for DELETE requests
                if method == "DELETE":
                    return {}

                return response.json()  # type: ignore[no-any-return]

            except RateLimitError as e:
                last_exception = e
                if attempts >= self.max_retries:
                    raise

        # Should not reach here, but just in case
        if last_exception:
            raise last_exception
        raise KankaException("Unexpected error in request retry logic")

    @property
    def last_search_meta(self) -> dict[str, Any]:
        """Get metadata from the last search() call.

        Returns:
            Dict[str, Any]: Pagination metadata including current_page, from, to,
                           last_page, per_page, total
        """
        return getattr(self, "_last_search_meta", {})

    @property
    def last_search_links(self) -> dict[str, Any]:
        """Get pagination links from the last search() call.

        Returns:
            Dict[str, Any]: Links for pagination including first, last, prev, next URLs
        """
        return getattr(self, "_last_search_links", {})
