"""Tests for EntityManager."""

import hashlib
from unittest.mock import Mock, mock_open, patch

from kanka.managers import EntityManager
from kanka.models.base import Post
from kanka.models.common import EntityAsset, EntityImageInfo
from kanka.models.entities import Character

from .utils import (
    create_api_response,
    create_mock_entity,
    create_mock_entity_asset,
    create_mock_entity_image_info,
    create_mock_post,
)


class TestEntityManager:
    """Test EntityManager class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_client = Mock()
        self.mock_client._request = Mock()
        self.manager = EntityManager(self.mock_client, "characters", Character)

    def test_manager_initialization(self):
        """Test manager initialization."""
        assert self.manager.client == self.mock_client
        assert self.manager.endpoint == "characters"
        assert self.manager.model == Character

    def test_get_entity(self):
        """Test getting a single entity."""
        # Setup mock response
        mock_data = create_mock_entity("character", 1, name="Test Character")
        self.mock_client._request.return_value = {"data": mock_data}

        # Get entity
        character = self.manager.get(1)

        # Verify request
        self.mock_client._request.assert_called_with("GET", "characters/1", params={})

        # Verify result
        assert isinstance(character, Character)
        assert character.id == 1
        assert character.name == "Test Character"

    def test_get_entity_with_related(self):
        """Test getting entity with related data."""
        # Setup mock response with related data
        mock_data = create_mock_entity(
            "character",
            1,
            name="Test Character",
            posts=[create_mock_post(1)],
            attributes=[{"name": "Strength", "value": "18"}],
        )
        self.mock_client._request.return_value = {"data": mock_data}

        # Get entity with related data
        character = self.manager.get(1, related=True)

        # Verify request
        self.mock_client._request.assert_called_with(
            "GET", "characters/1", params={"related": 1}
        )

        # Verify related data
        assert character.posts is not None
        assert len(character.posts) == 1
        assert isinstance(character.posts[0], Post)
        assert character.attributes is not None
        assert len(character.attributes) == 1

    def test_list_entities(self):
        """Test listing entities."""
        # Setup mock response
        mock_data = [
            create_mock_entity("character", 1, name="Character 1"),
            create_mock_entity("character", 2, name="Character 2"),
        ]
        mock_response = create_api_response(mock_data)
        self.mock_client._request.return_value = mock_response

        # List entities
        characters = self.manager.list()

        # Verify request
        self.mock_client._request.assert_called_with(
            "GET", "characters", params={"page": 1, "limit": 30}
        )

        # Verify results
        assert len(characters) == 2
        assert all(isinstance(c, Character) for c in characters)
        assert characters[0].name == "Character 1"
        assert characters[1].name == "Character 2"

        # Check metadata storage
        assert self.manager.last_page_meta["total"] == 2
        assert self.manager.last_page_links is not None

    def test_list_with_filters(self):
        """Test listing with various filters."""
        self.mock_client._request.return_value = create_api_response([])

        # Test with multiple filters
        self.manager.list(
            page=2,
            limit=50,
            name="test",
            tags=[1, 2, 3],
            is_private=False,
            type="NPC",
            created_by=5,
        )

        # Verify request parameters
        self.mock_client._request.assert_called_with(
            "GET",
            "characters",
            params={
                "page": 2,
                "limit": 50,
                "name": "test",
                "tags": "1,2,3",
                "is_private": 0,
                "type": "NPC",
                "created_by": 5,
            },
        )

    def test_list_with_types_filter(self):
        """Test listing with types filter (list)."""
        self.mock_client._request.return_value = create_api_response([])

        # Test with types as list
        self.manager.list(types=["character", "npc"])

        # Verify types are comma-separated
        call_args = self.mock_client._request.call_args
        assert call_args[1]["params"]["types"] == "character,npc"

    def test_create_entity(self):
        """Test creating an entity."""
        # Setup mock response
        mock_data = create_mock_entity(
            "character", 1, name="New Character", title="Knight"
        )
        self.mock_client._request.return_value = {"data": mock_data}

        # Create entity
        character = self.manager.create(
            name="New Character", title="Knight", is_private=True
        )

        # Verify request
        call_args = self.mock_client._request.call_args
        assert call_args[0] == ("POST", "characters")
        assert call_args[1]["json"]["name"] == "New Character"
        assert call_args[1]["json"]["title"] == "Knight"
        assert call_args[1]["json"]["is_private"] is True

        # Verify excluded fields
        assert "id" not in call_args[1]["json"]
        assert "entity_id" not in call_args[1]["json"]
        assert "created_at" not in call_args[1]["json"]

        # Verify result
        assert isinstance(character, Character)
        assert character.name == "New Character"

    def test_update_entity_by_object(self):
        """Test updating an entity by passing entity object."""
        # Create existing entity
        existing = Character(
            id=1,
            entity_id=100,
            name="Old Name",
            title="Old Title",
            created_at="2024-01-01T00:00:00.000000Z",
            created_by=1,
            updated_at="2024-01-01T00:00:00.000000Z",
            updated_by=1,
        )

        # Setup mock response
        mock_data = create_mock_entity(
            "character", 1, name="New Name", title="New Title"
        )
        self.mock_client._request.return_value = {"data": mock_data}

        # Update entity
        updated = self.manager.update(existing, name="New Name", title="New Title")

        # Verify request
        self.mock_client._request.assert_called_with(
            "PATCH", "characters/1", json={"name": "New Name", "title": "New Title"}
        )

        # Verify result
        assert updated.name == "New Name"
        assert updated.title == "New Title"

    def test_update_entity_by_id(self):
        """Test updating an entity by ID."""
        # Setup mock response
        mock_data = create_mock_entity("character", 1, name="Updated Name")
        self.mock_client._request.return_value = {"data": mock_data}

        # Update by ID
        updated = self.manager.update(1, name="Updated Name")

        # Verify request
        self.mock_client._request.assert_called_with(
            "PATCH", "characters/1", json={"name": "Updated Name"}
        )

        # Verify result
        assert updated.name == "Updated Name"

    def test_update_no_changes(self):
        """Test update with no changes."""
        # Create existing entity
        existing = Character(
            id=1,
            entity_id=100,
            name="Name",
            created_at="2024-01-01T00:00:00.000000Z",
            created_by=1,
            updated_at="2024-01-01T00:00:00.000000Z",
            updated_by=1,
        )

        # Update with same name (no change)
        result = self.manager.update(existing, name="Name")

        # Should return original entity without making request
        assert result == existing
        self.mock_client._request.assert_not_called()

    def test_update_validation_error(self):
        """Test update with invalid data."""
        # Since we removed validation in update for flexibility,
        # the validation will happen on the server side
        # This test now checks that we can send the data
        mock_data = create_mock_entity("character", 1)
        self.mock_client._request.return_value = {"data": mock_data}

        # This should not raise an error locally
        self.manager.update(1, created_at="not a date")

        # Verify the invalid data was sent to the server
        self.mock_client._request.assert_called_with(
            "PATCH", "characters/1", json={"created_at": "not a date"}
        )

    def test_delete_entity_by_object(self):
        """Test deleting an entity by object."""
        entity = Character(
            id=1,
            entity_id=100,
            name="Test",
            created_at="2024-01-01T00:00:00.000000Z",
            created_by=1,
            updated_at="2024-01-01T00:00:00.000000Z",
            updated_by=1,
        )

        self.mock_client._request.return_value = {}

        # Delete entity
        result = self.manager.delete(entity)

        # Verify request
        self.mock_client._request.assert_called_with("DELETE", "characters/1")

        assert result is True

    def test_delete_entity_by_id(self):
        """Test deleting an entity by ID."""
        self.mock_client._request.return_value = {}

        # Delete by ID
        result = self.manager.delete(5)

        # Verify request
        self.mock_client._request.assert_called_with("DELETE", "characters/5")

        assert result is True

    def test_list_posts(self):
        """Test listing posts for an entity."""
        # Setup mock response
        mock_posts = [
            create_mock_post(1, name="Post 1"),
            create_mock_post(2, name="Post 2"),
        ]
        mock_response = create_api_response(mock_posts)
        self.mock_client._request.return_value = mock_response

        # List posts - passing entity_id directly
        posts = self.manager.list_posts(100)  # 100 is the entity_id

        # Verify request uses entities endpoint
        self.mock_client._request.assert_called_with(
            "GET", "entities/100/posts", params={"page": 1, "limit": 30}
        )

        # Verify results
        assert len(posts) == 2
        assert all(isinstance(p, Post) for p in posts)
        assert posts[0].name == "Post 1"

        # Check metadata storage
        assert self.manager.last_posts_meta["total"] == 2

    def test_list_posts_with_entity_object(self):
        """Test listing posts by passing entity object."""
        entity = Character(
            id=5,
            entity_id=500,
            name="Test",
            created_at="2024-01-01T00:00:00.000000Z",
            created_by=1,
            updated_at="2024-01-01T00:00:00.000000Z",
            updated_by=1,
        )

        self.mock_client._request.return_value = create_api_response([])

        # List posts
        self.manager.list_posts(entity, page=2, limit=10)

        # Verify it used the entity's entity_id with entities endpoint
        self.mock_client._request.assert_called_with(
            "GET", "entities/500/posts", params={"page": 2, "limit": 10}
        )

    def test_create_post(self):
        """Test creating a post."""
        # Setup mock response
        mock_post = create_mock_post(
            1, name="New Post", entry="<p>Content</p>", is_private=True
        )
        self.mock_client._request.return_value = {"data": mock_post}

        # Create post - passing entity_id
        post = self.manager.create_post(
            100, name="New Post", entry="<p>Content</p>", is_private=True
        )

        # Verify request uses entities endpoint
        self.mock_client._request.assert_called_with(
            "POST",
            "entities/100/posts",
            json={
                "name": "New Post",
                "entry": "<p>Content</p>",
                "is_private": 1,  # Converted to int
            },
        )

        # Verify result
        assert isinstance(post, Post)
        assert post.name == "New Post"

    def test_get_post(self):
        """Test getting a specific post."""
        # Setup mock response
        mock_post = create_mock_post(5, name="Specific Post")
        self.mock_client._request.return_value = {"data": mock_post}

        # Get post - passing entity_id
        post = self.manager.get_post(100, 5)

        # Verify request uses entities endpoint
        self.mock_client._request.assert_called_with("GET", "entities/100/posts/5")

        # Verify result
        assert isinstance(post, Post)
        assert post.id == 5
        assert post.name == "Specific Post"

    def test_update_post(self):
        """Test updating a post."""
        # Setup mock response
        mock_post = create_mock_post(5, name="Updated Post", entry="Updated content")
        self.mock_client._request.return_value = {"data": mock_post}

        # Update post - passing entity_id
        post = self.manager.update_post(
            100, 5, name="Updated Post", entry="Updated content", is_private=False
        )

        # Verify request uses entities endpoint
        self.mock_client._request.assert_called_with(
            "PATCH",
            "entities/100/posts/5",
            json={
                "name": "Updated Post",
                "entry": "Updated content",
                "is_private": 0,  # Converted to int
            },
        )

        # Verify result
        assert post.name == "Updated Post"

    def test_delete_post(self):
        """Test deleting a post."""
        self.mock_client._request.return_value = {}

        # Delete post - passing entity_id
        result = self.manager.delete_post(100, 5)

        # Verify request uses entities endpoint
        self.mock_client._request.assert_called_with("DELETE", "entities/100/posts/5")

        assert result is True

    def test_post_operations_with_entity_object(self):
        """Test all post operations when passing an entity object."""
        # Create an entity with both id and entity_id
        entity = Character(
            id=5,  # The character-specific ID
            entity_id=500,  # The universal entity ID
            name="Test Character",
            created_at="2024-01-01T00:00:00.000000Z",
            created_by=1,
            updated_at="2024-01-01T00:00:00.000000Z",
            updated_by=1,
        )

        # Test create_post with entity object
        self.mock_client._request.return_value = {"data": create_mock_post(1)}
        self.manager.create_post(entity, name="Test", entry="Content", visibility_id=1)
        self.mock_client._request.assert_called_with(
            "POST",
            "entities/500/posts",  # Should use entity_id, not id
            json={"name": "Test", "entry": "Content", "visibility_id": 1},
        )

        # Test get_post with entity object
        self.mock_client._request.return_value = {"data": create_mock_post(1)}
        self.manager.get_post(entity, 1)
        self.mock_client._request.assert_called_with(
            "GET", "entities/500/posts/1"  # Should use entity_id
        )

        # Test update_post with entity object
        self.mock_client._request.return_value = {"data": create_mock_post(1)}
        self.manager.update_post(entity, 1, name="Updated")
        self.mock_client._request.assert_called_with(
            "PATCH", "entities/500/posts/1", json={"name": "Updated"}
        )

        # Test delete_post with entity object
        self.mock_client._request.return_value = {}
        self.manager.delete_post(entity, 1)
        self.mock_client._request.assert_called_with(
            "DELETE", "entities/500/posts/1"  # Should use entity_id
        )

    def test_extract_entity_id_from_int(self):
        """Test _extract_entity_id with an integer."""
        assert self.manager._extract_entity_id(42) == 42

    def test_extract_entity_id_from_entity(self):
        """Test _extract_entity_id with an entity object."""
        entity = Character(
            id=5,
            entity_id=500,
            name="Test",
            created_at="2024-01-01T00:00:00.000000Z",
            created_by=1,
            updated_at="2024-01-01T00:00:00.000000Z",
            updated_by=1,
        )
        assert self.manager._extract_entity_id(entity) == 500


class TestEntityAssets:
    """Test entity asset methods."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_client = Mock()
        self.mock_client._request = Mock()
        self.mock_client._upload_request = Mock()
        self.manager = EntityManager(self.mock_client, "characters", Character)

    def test_list_assets(self):
        """Test listing entity assets."""
        mock_assets = [
            create_mock_entity_asset(1, name="file1.png", type_id=1),
            create_mock_entity_asset(2, name="ref_link", type_id=2),
        ]
        self.mock_client._request.return_value = create_api_response(mock_assets)

        assets = self.manager.list_assets(100)

        self.mock_client._request.assert_called_with(
            "GET", "entities/100/entity_assets", params={"page": 1, "limit": 30}
        )
        assert len(assets) == 2
        assert all(isinstance(a, EntityAsset) for a in assets)
        assert assets[0].name == "file1.png"
        assert assets[1].type_id == 2

    def test_list_assets_with_entity_object(self):
        """Test listing assets with entity object."""
        entity = Character(
            id=5,
            entity_id=500,
            name="Test",
            created_at="2024-01-01T00:00:00.000000Z",
            created_by=1,
            updated_at="2024-01-01T00:00:00.000000Z",
            updated_by=1,
        )
        self.mock_client._request.return_value = create_api_response([])

        self.manager.list_assets(entity)
        self.mock_client._request.assert_called_with(
            "GET", "entities/500/entity_assets", params={"page": 1, "limit": 30}
        )

    def test_get_asset(self):
        """Test getting a specific asset."""
        mock_asset = create_mock_entity_asset(5, name="my_file")
        self.mock_client._request.return_value = {"data": mock_asset}

        asset = self.manager.get_asset(100, 5)

        self.mock_client._request.assert_called_with(
            "GET", "entities/100/entity_assets/5"
        )
        assert isinstance(asset, EntityAsset)
        assert asset.id == 5
        assert asset.name == "my_file"

    @patch("builtins.open", mock_open(read_data=b"fake file data"))
    def test_create_file_asset(self):
        """Test creating a file asset."""
        mock_asset = create_mock_entity_asset(1, name="upload", type_id=1)
        self.mock_client._upload_request.return_value = {"data": mock_asset}

        asset = self.manager.create_file_asset(
            100, "/path/to/file.png", name="upload", visibility_id=1
        )

        call_args = self.mock_client._upload_request.call_args
        assert call_args[0] == ("POST", "entities/100/entity_assets")
        assert call_args[1]["data"]["type_id"] == 1
        assert call_args[1]["data"]["name"] == "upload"
        assert call_args[1]["data"]["visibility_id"] == 1
        assert isinstance(asset, EntityAsset)

    @patch("builtins.open", mock_open(read_data=b"fake file data"))
    def test_create_file_asset_default_name(self):
        """Test file asset uses filename stem as default name."""
        mock_asset = create_mock_entity_asset(1, name="portrait", type_id=1)
        self.mock_client._upload_request.return_value = {"data": mock_asset}

        self.manager.create_file_asset(100, "/path/to/portrait.png")

        call_args = self.mock_client._upload_request.call_args
        assert call_args[1]["data"]["name"] == "portrait"

    def test_create_link_asset(self):
        """Test creating a link asset."""
        mock_asset = create_mock_entity_asset(2, name="Wiki", type_id=2)
        self.mock_client._request.return_value = {"data": mock_asset}

        asset = self.manager.create_link_asset(
            100, "Wiki", "https://example.com", icon="fa-link"
        )

        self.mock_client._request.assert_called_with(
            "POST",
            "entities/100/entity_assets",
            json={
                "type_id": 2,
                "name": "Wiki",
                "metadata": {"url": "https://example.com", "icon": "fa-link"},
            },
        )
        assert isinstance(asset, EntityAsset)
        assert asset.name == "Wiki"

    def test_create_alias_asset(self):
        """Test creating an alias asset."""
        mock_asset = create_mock_entity_asset(3, name="Dragon", type_id=3)
        self.mock_client._request.return_value = {"data": mock_asset}

        asset = self.manager.create_alias_asset(100, "Dragon")

        self.mock_client._request.assert_called_with(
            "POST",
            "entities/100/entity_assets",
            json={"type_id": 3, "name": "Dragon"},
        )
        assert isinstance(asset, EntityAsset)

    def test_delete_asset(self):
        """Test deleting an asset."""
        self.mock_client._request.return_value = {}

        result = self.manager.delete_asset(100, 5)

        self.mock_client._request.assert_called_with(
            "DELETE", "entities/100/entity_assets/5"
        )
        assert result is True

    def test_last_assets_meta(self):
        """Test pagination metadata for assets."""
        mock_assets = [create_mock_entity_asset(1)]
        self.mock_client._request.return_value = create_api_response(mock_assets)

        self.manager.list_assets(100)
        assert self.manager.last_assets_meta["total"] == 1
        assert self.manager.last_assets_links is not None


class TestEntityImage:
    """Test entity image methods."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_client = Mock()
        self.mock_client._request = Mock()
        self.mock_client._upload_request = Mock()
        self.manager = EntityManager(self.mock_client, "characters", Character)

    def test_get_image(self):
        """Test getting entity image info."""
        mock_info = create_mock_entity_image_info()
        self.mock_client._request.return_value = {"data": mock_info}

        info = self.manager.get_image(100)

        self.mock_client._request.assert_called_with("GET", "entities/100/image")
        assert isinstance(info, EntityImageInfo)
        assert info.image is not None
        assert info.image.uuid == "img-uuid-123"
        assert info.header is not None

    def test_get_image_with_entity_object(self):
        """Test getting image info with entity object."""
        entity = Character(
            id=5,
            entity_id=500,
            name="Test",
            created_at="2024-01-01T00:00:00.000000Z",
            created_by=1,
            updated_at="2024-01-01T00:00:00.000000Z",
            updated_by=1,
        )
        mock_info = create_mock_entity_image_info()
        self.mock_client._request.return_value = {"data": mock_info}

        self.manager.get_image(entity)
        self.mock_client._request.assert_called_with("GET", "entities/500/image")

    @patch("builtins.open", mock_open(read_data=b"fake image data"))
    def test_set_image(self):
        """Test setting entity main image."""
        mock_info = create_mock_entity_image_info()
        self.mock_client._upload_request.return_value = {"data": mock_info}

        info = self.manager.set_image(100, "/path/to/image.png")

        call_args = self.mock_client._upload_request.call_args
        assert call_args[0] == ("POST", "entities/100/image")
        assert "is_header" not in call_args[1]["data"]
        assert isinstance(info, EntityImageInfo)

    @patch("builtins.open", mock_open(read_data=b"fake image data"))
    def test_set_header_image(self):
        """Test setting entity header image."""
        mock_info = create_mock_entity_image_info()
        self.mock_client._upload_request.return_value = {"data": mock_info}

        self.manager.set_image(100, "/path/to/header.png", is_header=True)

        call_args = self.mock_client._upload_request.call_args
        assert call_args[1]["data"]["is_header"] == 1

    def test_delete_image(self):
        """Test deleting entity main image."""
        self.mock_client._request.return_value = {}

        result = self.manager.delete_image(100)

        self.mock_client._request.assert_called_with(
            "DELETE", "entities/100/image", params={}
        )
        assert result is True

    def test_delete_header_image(self):
        """Test deleting entity header image."""
        self.mock_client._request.return_value = {}

        result = self.manager.delete_image(100, is_header=True)

        self.mock_client._request.assert_called_with(
            "DELETE", "entities/100/image", params={"is_header": 1}
        )
        assert result is True


class TestConvenienceHelpers:
    """Test private helper methods for image convenience."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_client = Mock()
        self.mock_client._request = Mock()
        self.mock_client._upload_request = Mock()
        self.manager = EntityManager(self.mock_client, "characters", Character)

    def test_compute_file_hash(self):
        """Test computing file hash."""
        data = b"test file content"
        expected = hashlib.sha256(data).hexdigest()[:12]

        with patch("builtins.open", mock_open(read_data=data)):
            result = self.manager._compute_file_hash("/path/to/file.png")

        assert result == expected
        assert len(result) == 12

    def test_format_managed_asset_name(self):
        """Test formatting managed asset name."""
        result = self.manager._format_managed_asset_name("portrait", "abcdef123456")
        assert result == "portrait:abcdef123456"

    def test_format_managed_asset_name_truncates_long_names(self):
        """Test that long names are truncated to fit 45 char limit."""
        long_name = "a" * 50
        result = self.manager._format_managed_asset_name(long_name, "abcdef123456")
        assert len(result) == 45  # 32 + 1 + 12
        assert result.endswith(":abcdef123456")

    def test_parse_managed_asset_name(self):
        """Test parsing managed asset names."""
        result = self.manager._parse_managed_asset_name("portrait:abcdef123456")
        assert result == ("portrait", "abcdef123456")

    def test_parse_managed_asset_name_not_managed(self):
        """Test that non-managed names return None."""
        assert self.manager._parse_managed_asset_name("regular_name") is None
        assert self.manager._parse_managed_asset_name("name:short") is None
        assert self.manager._parse_managed_asset_name("name:ABCDEF123456") is None
        assert self.manager._parse_managed_asset_name("") is None

    def test_rewrite_image_srcs_double_quotes(self):
        """Test rewriting img src with double quotes."""
        html = '<p><img src="portrait.png" /> Hello</p>'
        result = self.manager._rewrite_image_srcs(
            html, {"portrait.png": "https://cdn.example.com/img.png"}
        )
        assert result == '<p><img src="https://cdn.example.com/img.png" /> Hello</p>'

    def test_rewrite_image_srcs_single_quotes(self):
        """Test rewriting img src with single quotes."""
        html = "<p><img src='portrait.png' /> Hello</p>"
        result = self.manager._rewrite_image_srcs(
            html, {"portrait.png": "https://cdn.example.com/img.png"}
        )
        assert result == "<p><img src='https://cdn.example.com/img.png' /> Hello</p>"

    def test_rewrite_image_srcs_multiple(self):
        """Test rewriting multiple img srcs."""
        html = '<img src="a.png" /><img src="b.png" />'
        result = self.manager._rewrite_image_srcs(
            html,
            {
                "a.png": "https://cdn.example.com/a.png",
                "b.png": "https://cdn.example.com/b.png",
            },
        )
        assert 'src="https://cdn.example.com/a.png"' in result
        assert 'src="https://cdn.example.com/b.png"' in result

    def test_rewrite_image_srcs_no_match(self):
        """Test that non-matching srcs are left unchanged."""
        html = '<img src="other.png" />'
        result = self.manager._rewrite_image_srcs(
            html, {"portrait.png": "https://cdn.example.com/img.png"}
        )
        assert result == html


class TestConvenienceImagesCreate:
    """Test images parameter on create()."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_client = Mock()
        self.mock_client._request = Mock()
        self.mock_client._upload_request = Mock()
        self.manager = EntityManager(self.mock_client, "characters", Character)

    def test_create_without_images(self):
        """Test create without images works as before."""
        mock_data = create_mock_entity("character", 1, name="Hero")
        self.mock_client._request.return_value = {"data": mock_data}

        self.manager.create(name="Hero")

        self.mock_client._request.assert_called_once_with(
            "POST", "characters", json={"name": "Hero"}
        )

    @patch("builtins.open", mock_open(read_data=b"fake image"))
    def test_create_with_images(self):
        """Test create with images uploads assets and rewrites entry."""
        # First call: create entity
        mock_entity = create_mock_entity(
            "character",
            1,
            entry='<p><img src="portrait.png" /></p>',
        )
        # Second call: update with rewritten entry
        mock_updated = create_mock_entity(
            "character",
            1,
            entry='<p><img src="https://cdn.example.com/asset.png" /></p>',
        )

        # File asset upload response
        file_hash = hashlib.sha256(b"fake image").hexdigest()[:12]
        managed_name = f"portrait.png:{file_hash}"
        mock_asset = create_mock_entity_asset(
            1,
            name=managed_name,
            type_id=1,
            _url="https://cdn.example.com/asset.png",
        )

        self.mock_client._request.side_effect = [
            {"data": mock_entity},  # POST create
            {"data": mock_updated},  # PATCH update with rewritten entry
        ]
        self.mock_client._upload_request.return_value = {"data": mock_asset}

        self.manager.create(
            name="Hero",
            entry='<p><img src="portrait.png" /></p>',
            images={"portrait.png": "/path/to/portrait.png"},
        )

        # Should have called create, then upload, then update
        assert self.mock_client._request.call_count == 2
        assert self.mock_client._upload_request.call_count == 1

    @patch("builtins.open", mock_open(read_data=b"fake image"))
    def test_create_with_images_no_entry(self):
        """Test create with images but no entry skips image processing."""
        mock_entity = create_mock_entity("character", 1, name="Hero", entry=None)
        self.mock_client._request.return_value = {"data": mock_entity}

        self.manager.create(
            name="Hero",
            images={"portrait.png": "/path/to/portrait.png"},
        )

        # Should only call create, no upload
        self.mock_client._request.assert_called_once()
        self.mock_client._upload_request.assert_not_called()


class TestConvenienceImagesUpdate:
    """Test images parameter on update()."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_client = Mock()
        self.mock_client._request = Mock()
        self.mock_client._upload_request = Mock()
        self.manager = EntityManager(self.mock_client, "characters", Character)

    @patch("builtins.open", mock_open(read_data=b"fake image"))
    def test_update_with_images_reuses_unchanged(self):
        """Test update with unchanged image reuses existing asset URL."""
        file_hash = hashlib.sha256(b"fake image").hexdigest()[:12]
        managed_name = f"portrait.png:{file_hash}"

        # Existing asset with same hash
        existing_asset = create_mock_entity_asset(
            10,
            name=managed_name,
            type_id=1,
            _url="https://cdn.example.com/existing.png",
        )

        entity = Character(
            id=5,
            entity_id=500,
            name="Hero",
            entry='<p><img src="portrait.png" /></p>',
            created_at="2024-01-01T00:00:00.000000Z",
            created_by=1,
            updated_at="2024-01-01T00:00:00.000000Z",
            updated_by=1,
        )

        self.mock_client._request.side_effect = [
            create_api_response([existing_asset]),  # list_assets
            {"data": create_mock_entity("character", 5)},  # PATCH update
        ]

        self.manager.update(
            entity,
            entry='<p><img src="portrait.png" /></p>',
            images={"portrait.png": "/path/to/portrait.png"},
        )

        # Should NOT have uploaded a new file
        self.mock_client._upload_request.assert_not_called()

    @patch("builtins.open", mock_open(read_data=b"new image data"))
    def test_update_with_images_replaces_changed(self):
        """Test update replaces asset when file hash differs."""
        old_hash = "aaaaaaaaaaaa"
        managed_name = f"portrait.png:{old_hash}"

        existing_asset = create_mock_entity_asset(10, name=managed_name, type_id=1)

        entity = Character(
            id=5,
            entity_id=500,
            name="Hero",
            entry='<p><img src="portrait.png" /></p>',
            created_at="2024-01-01T00:00:00.000000Z",
            created_by=1,
            updated_at="2024-01-01T00:00:00.000000Z",
            updated_by=1,
        )

        new_hash = hashlib.sha256(b"new image data").hexdigest()[:12]
        new_managed_name = f"portrait.png:{new_hash}"
        new_asset = create_mock_entity_asset(
            11,
            name=new_managed_name,
            type_id=1,
            _url="https://cdn.example.com/new.png",
        )

        self.mock_client._request.side_effect = [
            create_api_response([existing_asset]),  # list_assets
            {},  # delete old asset
            {"data": create_mock_entity("character", 5)},  # PATCH update
        ]
        self.mock_client._upload_request.return_value = {"data": new_asset}

        self.manager.update(
            entity,
            entry='<p><img src="portrait.png" /></p>',
            images={"portrait.png": "/path/to/portrait.png"},
        )

        # Should have uploaded new file and deleted old
        self.mock_client._upload_request.assert_called_once()

    @patch("builtins.open", mock_open(read_data=b"fake image"))
    def test_update_with_images_cleans_orphans(self):
        """Test update cleans up orphaned managed assets."""
        file_hash = hashlib.sha256(b"fake image").hexdigest()[:12]

        orphan_asset = create_mock_entity_asset(
            10, name=f"old_image.png:{file_hash}", type_id=1
        )
        new_asset = create_mock_entity_asset(
            11,
            name=f"new_image.png:{file_hash}",
            type_id=1,
            _url="https://cdn.example.com/new.png",
        )

        entity = Character(
            id=5,
            entity_id=500,
            name="Hero",
            entry='<p><img src="new_image.png" /></p>',
            created_at="2024-01-01T00:00:00.000000Z",
            created_by=1,
            updated_at="2024-01-01T00:00:00.000000Z",
            updated_by=1,
        )

        self.mock_client._request.side_effect = [
            create_api_response([orphan_asset]),  # list_assets
            {},  # delete orphan
            {"data": create_mock_entity("character", 5)},  # PATCH update
        ]
        self.mock_client._upload_request.return_value = {"data": new_asset}

        self.manager.update(
            entity,
            entry='<p><img src="new_image.png" /></p>',
            images={"new_image.png": "/path/to/new_image.png"},
        )

        # Orphan should have been deleted
        delete_calls = [
            c for c in self.mock_client._request.call_args_list if c[0][0] == "DELETE"
        ]
        assert len(delete_calls) == 1


class TestConvenienceImagesPost:
    """Test images parameter on create_post() and update_post()."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_client = Mock()
        self.mock_client._request = Mock()
        self.mock_client._upload_request = Mock()
        self.manager = EntityManager(self.mock_client, "characters", Character)

    @patch("builtins.open", mock_open(read_data=b"fake image"))
    def test_create_post_with_images(self):
        """Test create_post with images uploads and rewrites."""
        file_hash = hashlib.sha256(b"fake image").hexdigest()[:12]
        managed_name = f"portrait.png:{file_hash}"
        mock_asset = create_mock_entity_asset(
            1,
            name=managed_name,
            type_id=1,
            _url="https://cdn.example.com/asset.png",
        )
        mock_post = create_mock_post(
            1,
            entry='<p><img src="https://cdn.example.com/asset.png" /></p>',
        )

        self.mock_client._upload_request.return_value = {"data": mock_asset}
        self.mock_client._request.return_value = {"data": mock_post}

        post = self.manager.create_post(
            100,
            "Test Post",
            '<p><img src="portrait.png" /></p>',
            images={"portrait.png": "/path/to/portrait.png"},
        )

        assert isinstance(post, Post)
        # Asset should have been uploaded
        self.mock_client._upload_request.assert_called_once()

    @patch("builtins.open", mock_open(read_data=b"fake image"))
    def test_update_post_with_images(self):
        """Test update_post with images."""
        file_hash = hashlib.sha256(b"fake image").hexdigest()[:12]
        managed_name = f"portrait.png:{file_hash}"
        mock_asset = create_mock_entity_asset(
            1,
            name=managed_name,
            type_id=1,
            _url="https://cdn.example.com/asset.png",
        )

        self.mock_client._request.side_effect = [
            create_api_response([]),  # list_assets (no existing)
            {"data": create_mock_post(5)},  # PATCH update
        ]
        self.mock_client._upload_request.return_value = {"data": mock_asset}

        self.manager.update_post(
            100,
            5,
            entry='<p><img src="portrait.png" /></p>',
            images={"portrait.png": "/path/to/portrait.png"},
        )

        self.mock_client._upload_request.assert_called_once()

    @patch("builtins.open", mock_open(read_data=b"fake image"))
    def test_update_post_with_images_fetches_entry_if_missing(self):
        """Test update_post fetches existing post entry when not provided."""
        file_hash = hashlib.sha256(b"fake image").hexdigest()[:12]
        managed_name = f"portrait.png:{file_hash}"
        mock_asset = create_mock_entity_asset(
            1,
            name=managed_name,
            type_id=1,
            _url="https://cdn.example.com/asset.png",
        )

        existing_post = create_mock_post(5, entry='<p><img src="portrait.png" /></p>')

        self.mock_client._request.side_effect = [
            {"data": existing_post},  # get_post (fetch entry)
            create_api_response([]),  # list_assets
            {"data": create_mock_post(5)},  # PATCH update
        ]
        self.mock_client._upload_request.return_value = {"data": mock_asset}

        self.manager.update_post(
            100,
            5,
            name="Keep Name",
            images={"portrait.png": "/path/to/portrait.png"},
        )

        # Should have fetched the post to get entry
        first_call = self.mock_client._request.call_args_list[0]
        assert first_call[0] == ("GET", "entities/100/posts/5")
