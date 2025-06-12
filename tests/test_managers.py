"""Tests for EntityManager."""

from unittest.mock import Mock

from kanka.managers import EntityManager
from kanka.models.base import Post
from kanka.models.entities import Character

from .utils import create_api_response, create_mock_entity, create_mock_post


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
