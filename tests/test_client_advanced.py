"""Advanced tests for KankaClient features."""

import json
import os
import time
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

from kanka import KankaClient
from kanka.models.entities import (
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

from .utils import MockResponse


class TestDebugMode:
    """Test debug mode functionality."""

    def setup_method(self):
        """Setup for each test."""
        # Clean up any existing debug environment variables
        for key in ["KANKA_DEBUG_MODE", "KANKA_DEBUG_DIR"]:
            if key in os.environ:
                del os.environ[key]

    @patch("requests.Session")
    def test_debug_mode_disabled_by_default(self, mock_session_class):
        """Test that debug mode is disabled by default."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        client = KankaClient(token="test", campaign_id=123)

        assert client._debug_mode is False
        assert not client._debug_dir.exists()

    @patch("requests.Session")
    def test_debug_mode_enabled_via_env(self, mock_session_class):
        """Test enabling debug mode via environment variable."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        os.environ["KANKA_DEBUG_MODE"] = "true"
        os.environ["KANKA_DEBUG_DIR"] = "test_debug"

        try:
            client = KankaClient(token="test", campaign_id=123)

            assert client._debug_mode is True
            assert client._debug_dir == Path("test_debug")
            assert client._debug_dir.exists()

            # Clean up
            if client._debug_dir.exists():
                import shutil

                shutil.rmtree(client._debug_dir)
        finally:
            del os.environ["KANKA_DEBUG_MODE"]
            del os.environ["KANKA_DEBUG_DIR"]

    @patch("requests.Session")
    def test_debug_logging_request(self, mock_session_class):
        """Test that debug mode logs requests and responses."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        # Setup response
        mock_response = MockResponse(
            {"data": {"id": 1, "name": "Test Character"}},
            status_code=200,
            headers={"X-RateLimit-Remaining": "100"},
        )
        mock_session.request.return_value = mock_response

        os.environ["KANKA_DEBUG_MODE"] = "true"
        os.environ["KANKA_DEBUG_DIR"] = "test_debug_logs"

        try:
            client = KankaClient(token="test", campaign_id=123)

            # Make a request
            client._request("GET", "characters/1")

            # Check that debug file was created
            debug_files = list(client._debug_dir.glob("*.json"))
            assert len(debug_files) == 1

            # Verify debug file contents
            with open(debug_files[0]) as f:
                debug_data = json.load(f)

            assert debug_data["request"]["method"] == "GET"
            assert "characters/1" in debug_data["request"]["url"]
            assert debug_data["response"]["status_code"] == 200
            assert debug_data["response"]["body"]["data"]["name"] == "Test Character"

            # Clean up
            if client._debug_dir.exists():
                import shutil

                shutil.rmtree(client._debug_dir)
        finally:
            del os.environ["KANKA_DEBUG_MODE"]
            del os.environ["KANKA_DEBUG_DIR"]

    @patch("requests.Session")
    def test_debug_file_naming(self, mock_session_class):
        """Test debug file naming convention."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        mock_response = MockResponse({"data": []}, status_code=200)
        mock_session.request.return_value = mock_response

        os.environ["KANKA_DEBUG_MODE"] = "true"
        os.environ["KANKA_DEBUG_DIR"] = "test_debug_naming"

        try:
            client = KankaClient(token="test", campaign_id=123)

            # Make different types of requests
            client._request("GET", "characters")
            client._request("POST", "locations")
            client._request("GET", "search/dragon")

            debug_files = sorted(client._debug_dir.glob("*.json"))
            assert len(debug_files) == 3

            # Check file naming pattern
            assert "GET_characters" in str(debug_files[0])
            assert "POST_locations" in str(debug_files[1])
            assert "GET_search_dragon" in str(debug_files[2])

            # Clean up
            if client._debug_dir.exists():
                import shutil

                shutil.rmtree(client._debug_dir)
        finally:
            del os.environ["KANKA_DEBUG_MODE"]
            del os.environ["KANKA_DEBUG_DIR"]


class TestRateLimitParsing:
    """Test rate limit header parsing."""

    @patch("requests.Session")
    def test_parse_retry_after_seconds(self, mock_session_class):
        """Test parsing Retry-After header with seconds."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        client = KankaClient(token="test", campaign_id=123)

        # Mock response with Retry-After in seconds
        mock_response = Mock()
        mock_response.headers = {"Retry-After": "30"}

        delay = client._parse_rate_limit_headers(mock_response)
        assert delay == 30.0

    @patch("requests.Session")
    def test_parse_retry_after_date(self, mock_session_class):
        """Test parsing Retry-After header with HTTP date."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        client = KankaClient(token="test", campaign_id=123)

        # Mock response with Retry-After as HTTP date
        future_time = "Wed, 21 Oct 2025 07:28:00 GMT"
        current_time = "Wed, 21 Oct 2025 07:27:30 GMT"

        mock_response = Mock()
        mock_response.headers = {"Retry-After": future_time, "Date": current_time}

        delay = client._parse_rate_limit_headers(mock_response)
        assert delay == 30.0  # 30 seconds difference

    @patch("requests.Session")
    def test_parse_x_ratelimit_headers(self, mock_session_class):
        """Test parsing X-RateLimit headers."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        client = KankaClient(token="test", campaign_id=123)

        # Mock response with X-RateLimit headers
        current_time = int(time.time())
        reset_time = current_time + 45

        mock_response = Mock()
        mock_response.headers = {
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": str(reset_time),
        }

        with patch("time.time", return_value=current_time):
            delay = client._parse_rate_limit_headers(mock_response)
            assert delay == 45.0

    @patch("requests.Session")
    def test_parse_no_rate_limit_headers(self, mock_session_class):
        """Test handling response without rate limit headers."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        client = KankaClient(token="test", campaign_id=123)

        mock_response = Mock()
        mock_response.headers = {}

        delay = client._parse_rate_limit_headers(mock_response)
        assert delay is None

    @patch("requests.Session")
    def test_parse_invalid_headers(self, mock_session_class):
        """Test handling invalid rate limit headers."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        client = KankaClient(token="test", campaign_id=123)

        # Invalid Retry-After
        mock_response = Mock()
        mock_response.headers = {"Retry-After": "invalid"}
        delay = client._parse_rate_limit_headers(mock_response)
        assert delay is None

        # Invalid X-RateLimit headers
        mock_response.headers = {
            "X-RateLimit-Remaining": "invalid",
            "X-RateLimit-Reset": "invalid",
        }
        delay = client._parse_rate_limit_headers(mock_response)
        assert delay is None


class TestEntityManagerProperties:
    """Test all entity manager properties."""

    @patch("requests.Session")
    def test_all_manager_properties(self, mock_session_class):
        """Test that all entity manager properties are properly initialized."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        client = KankaClient(token="test", campaign_id=123)

        # Test each manager property
        managers_and_types = [
            (client.calendars, "calendars", Calendar),
            (client.characters, "characters", Character),
            (client.creatures, "creatures", Creature),
            (client.events, "events", Event),
            (client.families, "families", Family),
            (client.journals, "journals", Journal),
            (client.locations, "locations", Location),
            (client.notes, "notes", Note),
            (client.organisations, "organisations", Organisation),
            (client.quests, "quests", Quest),
            (client.races, "races", Race),
            (client.tags, "tags", Tag),
        ]

        for manager, endpoint, model in managers_and_types:
            assert manager is not None
            assert manager.endpoint == endpoint  # type: ignore
            assert manager.model == model  # type: ignore
            assert manager.client == client  # type: ignore

    @patch("requests.Session")
    def test_manager_properties_are_stable(self, mock_session_class):
        """Test that manager properties return the same instance."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        client = KankaClient(token="test", campaign_id=123)

        # Get managers twice and verify they're the same instance
        chars1 = client.characters
        chars2 = client.characters
        assert chars1 is chars2

        locs1 = client.locations
        locs2 = client.locations
        assert locs1 is locs2


class TestEntitiesMethodFiltering:
    """Test entities() method with various filters."""

    @patch("requests.Session")
    def test_entities_single_type_filter(self, mock_session_class):
        """Test entities() with single type filter."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        mock_response = MockResponse({"data": []}, status_code=200)
        mock_session.request.return_value = mock_response

        client = KankaClient(token="test", campaign_id=123)

        # Test with single type as string
        client.entities(types="character")

        call_args = mock_session.request.call_args
        assert call_args[1]["params"]["types"] == "character"

    @patch("requests.Session")
    def test_entities_date_filtering(self, mock_session_class):
        """Test entities() with date filters."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        mock_response = MockResponse({"data": []}, status_code=200)
        mock_session.request.return_value = mock_response

        client = KankaClient(token="test", campaign_id=123)

        # Test with date filters (these get passed through as-is)
        client.entities(created_at=">=2024-01-01", updated_at="<=2024-12-31")

        # The client doesn't parse these, just passes them
        call_args = mock_session.request.call_args
        assert "created_at" not in call_args[1]["params"]  # Not in standard filters
        assert "updated_at" not in call_args[1]["params"]

    @patch("requests.Session")
    def test_entities_boolean_conversion(self, mock_session_class):
        """Test entities() converts boolean to int."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        mock_response = MockResponse({"data": []}, status_code=200)
        mock_session.request.return_value = mock_response

        client = KankaClient(token="test", campaign_id=123)

        # Test boolean conversion
        client.entities(is_private=True)

        call_args = mock_session.request.call_args
        assert call_args[1]["params"]["is_private"] == 1

        client.entities(is_private=False)

        call_args = mock_session.request.call_args
        assert call_args[1]["params"]["is_private"] == 0


class TestPaginationMetadata:
    """Test pagination metadata properties."""

    @patch("requests.Session")
    def test_search_metadata_storage(self, mock_session_class):
        """Test that search metadata is stored and accessible."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        mock_response = MockResponse(
            {
                "data": [],
                "meta": {
                    "current_page": 2,
                    "from": 31,
                    "to": 60,
                    "per_page": 30,
                    "last_page": 5,
                    "total": 150,
                },
                "links": {
                    "first": "http://api.kanka.io/...",
                    "prev": "http://api.kanka.io/...",
                    "next": "http://api.kanka.io/...",
                    "last": "http://api.kanka.io/...",
                },
            },
            status_code=200,
        )
        mock_session.request.return_value = mock_response

        client = KankaClient(token="test", campaign_id=123)

        # Perform search
        client.search("test", page=2)

        # Check metadata
        assert client.last_search_meta["current_page"] == 2
        assert client.last_search_meta["total"] == 150
        assert client.last_search_meta["last_page"] == 5

        # Check links
        assert "first" in client.last_search_links
        assert "next" in client.last_search_links

    @patch("requests.Session")
    def test_metadata_empty_before_search(self, mock_session_class):
        """Test that metadata is empty before any search."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        client = KankaClient(token="test", campaign_id=123)

        # Should return empty dicts before any search
        assert client.last_search_meta == {}
        assert client.last_search_links == {}


class TestSearchResultOptionalType:
    """Test SearchResult with optional type field."""

    def test_search_result_without_type(self):
        """Test SearchResult can be created without type field."""
        from kanka.models.common import SearchResult

        # Create without type
        result = SearchResult(
            id=1,
            entity_id=100,
            name="Test Entity",
            url="https://api.kanka.io/campaigns/123/entities/100",
            is_private=False,
            tags=[],
            created_at="2024-01-01T00:00:00.000000Z",
            updated_at="2024-01-01T00:00:00.000000Z",
        )

        assert result.type is None
        assert result.name == "Test Entity"

    def test_search_result_with_type(self):
        """Test SearchResult with type field."""
        from kanka.models.common import SearchResult

        # Create with type
        result = SearchResult(
            id=1,
            entity_id=100,
            name="Test Character",
            type="character",
            url="https://api.kanka.io/campaigns/123/characters/1",
            is_private=False,
            tags=[1, 2],
            created_at="2024-01-01T00:00:00.000000Z",
            updated_at="2024-01-01T00:00:00.000000Z",
        )

        assert result.type == "character"
        assert result.tags == [1, 2]
