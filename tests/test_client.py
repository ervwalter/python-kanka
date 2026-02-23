"""Tests for KankaClient."""

from unittest.mock import MagicMock, mock_open, patch

import pytest

from kanka import KankaClient
from kanka.exceptions import (
    AuthenticationError,
    ForbiddenError,
    KankaException,
    NotFoundError,
    RateLimitError,
    ValidationError,
)
from kanka.models.common import GalleryImage, SearchResult
from kanka.models.entities import Character, Location

from .utils import (
    MockResponse,
    create_api_response,
    create_mock_gallery_image,
    create_mock_search_result,
)


class TestKankaClient:
    """Test KankaClient class."""

    def test_client_initialization(self):
        """Test client initialization."""
        client = KankaClient(token="test_token", campaign_id=123)

        assert client.token == "test_token"
        assert client.campaign_id == 123
        assert client.session is not None
        assert client.session.headers["Authorization"] == "Bearer test_token"
        assert client.session.headers["Accept"] == "application/json"
        assert client.session.headers["Content-Type"] == "application/json"

    def test_manager_initialization(self):
        """Test that all entity managers are initialized."""
        client = KankaClient(token="test_token", campaign_id=123)

        # Check core entity managers
        assert client.calendars is not None
        assert client.characters is not None
        assert client.creatures is not None
        assert client.events is not None
        assert client.families is not None
        assert client.journals is not None
        assert client.locations is not None
        assert client.notes is not None
        assert client.organisations is not None
        assert client.quests is not None
        assert client.races is not None
        assert client.tags is not None

        # Check manager types
        assert client.characters.endpoint == "characters"
        assert client.characters.model == Character
        assert client.locations.endpoint == "locations"
        assert client.locations.model == Location

    @patch("requests.Session")
    def test_search(self, mock_session_class):
        """Test search functionality."""
        # Setup mock
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        mock_response = MockResponse(
            create_api_response(
                [
                    create_mock_search_result("character", 1, name="Dragon Knight"),
                    create_mock_search_result("location", 2, name="Dragon's Lair"),
                ]
            ),
            status_code=200,
        )
        mock_session.request.return_value = mock_response

        # Create client and search
        client = KankaClient(token="test_token", campaign_id=123)
        results = client.search("dragon")

        # Verify request
        mock_session.request.assert_called_with(
            "GET",
            "https://api.kanka.io/1.0/campaigns/123/search/dragon",
            params={"page": 1},
        )

        # Verify results
        assert len(results) == 2
        assert isinstance(results[0], SearchResult)
        assert results[0].name == "Dragon Knight"
        assert results[0].type == "character"
        assert results[1].name == "Dragon's Lair"
        assert results[1].type == "location"

        # Check metadata storage
        assert client.last_search_meta["total"] == 2
        assert client.last_search_links is not None

    @patch("requests.Session")
    def test_search_with_pagination(self, mock_session_class):
        """Test search with custom pagination."""
        # Setup mock
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        mock_response = MockResponse(create_api_response([]), status_code=200)
        mock_session.request.return_value = mock_response

        # Create client and search
        client = KankaClient(token="test_token", campaign_id=123)
        client.search("test", page=3)

        # Verify request
        mock_session.request.assert_called_with(
            "GET",
            "https://api.kanka.io/1.0/campaigns/123/search/test",
            params={"page": 3},
        )

    @patch("requests.Session")
    def test_entities_endpoint(self, mock_session_class):
        """Test entities endpoint with filters."""
        # Setup mock
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        mock_response = MockResponse(
            create_api_response(
                [
                    {"id": 1, "name": "Test Character", "type": "character"},
                    {"id": 2, "name": "Test Location", "type": "location"},
                ]
            ),
            status_code=200,
        )
        mock_session.request.return_value = mock_response

        # Create client and query entities
        client = KankaClient(token="test_token", campaign_id=123)

        # Test with types filter
        results = client.entities(types=["character", "location"])

        mock_session.request.assert_called_with(
            "GET",
            "https://api.kanka.io/1.0/campaigns/123/entities",
            params={"types": "character,location"},
        )

        assert len(results) == 2

    @patch("requests.Session")
    def test_entities_with_multiple_filters(self, mock_session_class):
        """Test entities endpoint with multiple filter types."""
        # Setup mock
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        mock_response = MockResponse(create_api_response([]), status_code=200)
        mock_session.request.return_value = mock_response

        # Create client and query with multiple filters
        client = KankaClient(token="test_token", campaign_id=123)

        client.entities(
            types=["character"],
            tags=[1, 2, 3],
            name="test",
            is_private=False,
            created_by=5,
        )

        mock_session.request.assert_called_with(
            "GET",
            "https://api.kanka.io/1.0/campaigns/123/entities",
            params={
                "types": "character",
                "tags": "1,2,3",
                "name": "test",
                "is_private": 0,
                "created_by": 5,
            },
        )

    @patch("requests.Session")
    def test_request_error_handling(self, mock_session_class):
        """Test error handling in _request method."""
        # Setup mock
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        client = KankaClient(
            token="test_token", campaign_id=123, enable_rate_limit_retry=False
        )

        # Test 401 Unauthorized
        mock_response = MockResponse({}, status_code=401)
        mock_session.request.return_value = mock_response

        with pytest.raises(AuthenticationError) as exc_info:
            client._request("GET", "test")
        assert "Invalid authentication token" in str(exc_info.value)

        # Test 403 Forbidden
        mock_response = MockResponse({}, status_code=403)
        mock_session.request.return_value = mock_response

        with pytest.raises(ForbiddenError) as exc_info2:
            client._request("GET", "test")
        assert "Access forbidden" in str(exc_info2.value)

        # Test 404 Not Found
        mock_response = MockResponse({}, status_code=404)
        mock_session.request.return_value = mock_response

        with pytest.raises(NotFoundError) as exc_info3:
            client._request("GET", "test")
        assert "Resource not found: test" in str(exc_info3.value)

        # Test 422 Validation Error
        mock_response = MockResponse(
            {"errors": {"name": ["required"]}}, status_code=422
        )
        mock_session.request.return_value = mock_response

        with pytest.raises(ValidationError) as exc_info4:
            client._request("POST", "test")
        assert "Validation error" in str(exc_info4.value)

        # Test 429 Rate Limit
        mock_response = MockResponse({}, status_code=429)
        mock_session.request.return_value = mock_response

        with pytest.raises(RateLimitError) as exc_info5:
            client._request("GET", "test")
        assert "Rate limit exceeded" in str(exc_info5.value)

        # Test generic 500 error
        mock_response = MockResponse({}, status_code=500, text="Server Error")
        mock_session.request.return_value = mock_response

        with pytest.raises(KankaException) as exc_info6:
            client._request("GET", "test")
        assert "API error 500" in str(exc_info6.value)

    @patch("requests.Session")
    def test_delete_request_returns_empty_dict(self, mock_session_class):
        """Test that DELETE requests return empty dict."""
        # Setup mock
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        mock_response = MockResponse({}, status_code=200)
        mock_session.request.return_value = mock_response

        client = KankaClient(token="test_token", campaign_id=123)
        result = client._request("DELETE", "test/1")

        assert result == {}

    @patch("requests.Session")
    def test_handle_response_shared(self, mock_session_class):
        """Test _handle_response is used by both _request and _upload_request."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        client = KankaClient(token="test_token", campaign_id=123)

        # Test 404 via _handle_response
        mock_response = MockResponse({}, status_code=404)
        with pytest.raises(NotFoundError):
            client._handle_response(mock_response, "GET", "test")

        # Test success via _handle_response
        mock_response = MockResponse({"data": {"id": 1}}, status_code=200)
        result = client._handle_response(mock_response, "GET", "test")
        assert result == {"data": {"id": 1}}

        # Test DELETE via _handle_response
        mock_response = MockResponse({}, status_code=200)
        result = client._handle_response(mock_response, "DELETE", "test")
        assert result == {}

    def test_upload_request(self):
        """Test _upload_request sends multipart and restores Content-Type."""
        client = KankaClient(token="test_token", campaign_id=123)

        mock_response = MockResponse(
            {"data": [create_mock_gallery_image()]}, status_code=200
        )

        # Verify Content-Type is set before upload
        assert client.session.headers["Content-Type"] == "application/json"

        with patch.object(client.session, "request", return_value=mock_response):
            result = client._upload_request(
                "POST", "gallery", files={"file[]": ("test.png", b"data")}, data={}
            )

        # Verify Content-Type is restored after upload
        assert client.session.headers["Content-Type"] == "application/json"
        assert "data" in result

    def test_upload_request_restores_content_type_on_error(self):
        """Test Content-Type is restored even if upload fails."""
        client = KankaClient(token="test_token", campaign_id=123)

        mock_response = MockResponse({}, status_code=422)

        with (
            patch.object(client.session, "request", return_value=mock_response),
            pytest.raises(ValidationError),
        ):
            client._upload_request(
                "POST", "gallery", files={"file[]": ("test.png", b"data")}
            )

        # Content-Type must still be restored
        assert client.session.headers["Content-Type"] == "application/json"


class TestGalleryMethods:
    """Test campaign gallery methods."""

    @patch("requests.Session")
    def test_gallery_list(self, mock_session_class):
        """Test listing gallery images."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        mock_response = MockResponse(
            create_api_response(
                [
                    create_mock_gallery_image("uuid-1", name="image1.png"),
                    create_mock_gallery_image("uuid-2", name="image2.png"),
                ]
            ),
            status_code=200,
        )
        mock_session.request.return_value = mock_response

        client = KankaClient(token="test_token", campaign_id=123)
        images = client.gallery()

        mock_session.request.assert_called_with(
            "GET",
            "https://api.kanka.io/1.0/campaigns/123/images",
            params={"page": 1, "limit": 30},
        )

        assert len(images) == 2
        assert all(isinstance(img, GalleryImage) for img in images)
        assert images[0].name == "image1.png"
        assert client.last_gallery_meta["total"] == 2

    @patch("requests.Session")
    def test_gallery_get(self, mock_session_class):
        """Test getting a specific gallery image."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        mock_response = MockResponse(
            {"data": create_mock_gallery_image("uuid-1", name="test.png")},
            status_code=200,
        )
        mock_session.request.return_value = mock_response

        client = KankaClient(token="test_token", campaign_id=123)
        image = client.gallery_get("uuid-1")

        assert isinstance(image, GalleryImage)
        assert image.id == "uuid-1"
        assert image.name == "test.png"

    @patch("builtins.open", mock_open(read_data=b"fake image data"))
    @patch("requests.Session")
    def test_gallery_upload(self, mock_session_class):
        """Test uploading a gallery image."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        mock_response = MockResponse(
            {"data": [create_mock_gallery_image("new-uuid", name="upload.png")]},
            status_code=200,
        )
        mock_session.request.return_value = mock_response

        client = KankaClient(token="test_token", campaign_id=123)
        image = client.gallery_upload("/path/to/upload.png", folder_id="folder-uuid")

        assert isinstance(image, GalleryImage)
        assert image.id == "new-uuid"

    @patch("requests.Session")
    def test_gallery_delete(self, mock_session_class):
        """Test deleting a gallery image."""
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session

        mock_response = MockResponse({}, status_code=200)
        mock_session.request.return_value = mock_response

        client = KankaClient(token="test_token", campaign_id=123)
        result = client.gallery_delete("uuid-1")

        mock_session.request.assert_called_with(
            "DELETE",
            "https://api.kanka.io/1.0/campaigns/123/images/uuid-1",
        )
        assert result is True
