"""
Integration tests for Post sub-resource operations.
"""

from datetime import datetime

# Handle both direct execution and import scenarios
if __name__ == "__main__":
    import setup_test_env

    setup_test_env.setup_environment()

from base import IntegrationTestBase

# Character and Post types are imported implicitly through the client


class TestPostIntegration(IntegrationTestBase):
    """Integration tests for Post CRUD operations as sub-resources."""

    def __init__(self):
        super().__init__()

    def _register_post_cleanup(
        self,
        entity_id: int,
        post_id: int,
        post_name: str,
        entity_type: str = "character",
    ):
        """Register a post for cleanup."""

        def cleanup():
            if self.client:
                try:
                    if entity_type == "character":
                        self.client.characters.delete_post(entity_id, post_id)
                    elif entity_type == "location":
                        self.client.locations.delete_post(entity_id, post_id)
                except Exception:
                    # Post may already be deleted if parent entity was deleted
                    pass

        self.register_cleanup(
            f"Delete post '{post_name}' (ID: {post_id}) from {entity_type}", cleanup
        )

    def _register_character_cleanup(self, character_id: int, name: str):
        """Register a character for cleanup."""

        def cleanup():
            if self.client:
                self.client.characters.delete(character_id)

        self.register_cleanup(
            f"Delete character '{name}' (ID: {character_id})", cleanup
        )

    def _register_location_cleanup(self, location_id: int, name: str):
        """Register a location for cleanup."""

        def cleanup():
            if self.client:
                self.client.locations.delete(location_id)

        self.register_cleanup(f"Delete location '{name}' (ID: {location_id})", cleanup)

    def test_create_post_on_character(self):
        """Test creating a post on a character."""
        # First create a character
        character_name = f"Integration Test Character for Posts - DELETE ME - {datetime.now().isoformat()}"
        character = self.client.characters.create(name=character_name)
        self._register_character_cleanup(character.id, character.name)

        self.wait_for_api()

        # Create post data
        post_data = {
            "name": f"Integration Test Post - DELETE ME - {datetime.now().isoformat()}",
            "entry": "<h3>Character Journal Entry</h3><p>Today's <strong>adventures</strong> included:</p><ul><li>Meeting with the guild</li><li>Exploring the dungeon</li><li>Finding mysterious artifact</li></ul><p><em>More details to follow...</em></p>",
            "visibility": "all",
        }

        # Create the post on the character (pass the character object, not just ID)
        post = self.client.characters.create_post(character, **post_data)
        self._register_post_cleanup(character.entity_id, post.id, post.name)

        # Verify the post was created
        self.assert_not_none(post.id, "Post ID should not be None")
        self.assert_equal(post.name, post_data["name"], "Post name mismatch")
        self.assert_equal(post.entry, post_data["entry"], "Post entry mismatch")
        # Note: visibility is not returned in the Post model, it's only used during creation

        print(
            f"  Created post: {post.name} (ID: {post.id}) on character {character.id}"
        )

    def test_list_posts_for_character(self):
        """Test listing posts for a character."""
        # Create a character
        character = self.client.characters.create(
            name=f"Integration Test Character for Posts - DELETE ME - {datetime.now().isoformat()}"
        )
        self._register_character_cleanup(character.id, character.name)

        self.wait_for_api()

        # Create a post on the character
        post_name = f"Integration Test Post - DELETE ME - {datetime.now().isoformat()}"
        post = self.client.characters.create_post(
            character,
            name=post_name,
            entry="<p>A brief <strong>post</strong> with <em>simple HTML</em> content.</p>",
        )
        self._register_post_cleanup(character.entity_id, post.id, post.name)

        self.wait_for_api()

        # List all posts for the character
        posts = list(self.client.characters.list_posts(character))

        # Verify our post appears in the list
        found = False
        for p in posts:
            if p.id == post.id:
                found = True
                break

        self.assert_true(
            found, f"Created post {post.id} not found in character's posts"
        )
        print(f"  Found {len(posts)} post(s) for character {character.id}")

    def test_update_post(self):
        """Test updating a post."""
        # Create a character
        character = self.client.characters.create(
            name=f"Integration Test Character for Posts - DELETE ME - {datetime.now().isoformat()}"
        )
        self._register_character_cleanup(character.id, character.name)

        self.wait_for_api()

        # Create a post
        original_name = (
            f"Integration Test Post - DELETE ME - {datetime.now().isoformat()}"
        )
        post = self.client.characters.create_post(
            character,
            name=original_name,
            entry="<p>Original post with <strong>basic formatting</strong>.</p>",
            visibility="all",
        )
        self._register_post_cleanup(character.entity_id, post.id, post.name)

        self.wait_for_api()

        # Update the post (API requires name field even if not changing)
        updated_data = {
            "name": original_name,  # API requires this even if not changing
            "entry": "<h3>Updated Journal Entry</h3><p>This post has been <em>updated</em> with new information:</p><ol><li>Quest completed successfully</li><li>Rewards collected</li><li>New quest received</li></ol><blockquote>The journey continues...</blockquote>",
            "visibility": "members",
        }
        updated_post = self.client.characters.update_post(
            character, post.id, **updated_data
        )

        # Verify updates
        self.assert_equal(updated_post.name, original_name, "Name should not change")
        self.assert_equal(
            updated_post.entry, updated_data["entry"], "Entry not updated"
        )
        # Note: visibility is not returned in the Post model

        print(f"  Updated post {post.id} successfully")

    def test_get_post(self):
        """Test getting a specific post."""
        # Create a character
        character = self.client.characters.create(
            name=f"Integration Test Character for Posts - DELETE ME - {datetime.now().isoformat()}"
        )
        self._register_character_cleanup(character.id, character.name)

        self.wait_for_api()

        # Create a post
        post_name = f"Integration Test Post - DELETE ME - {datetime.now().isoformat()}"
        created = self.client.characters.create_post(
            character,
            name=post_name,
            entry="<p>Test post with <strong>HTML tags</strong> to <em>retrieve</em>.</p>",
        )
        self._register_post_cleanup(character.entity_id, created.id, created.name)

        self.wait_for_api()

        # Get the post by ID
        post = self.client.characters.get_post(character, created.id)

        # Verify we got the right post
        self.assert_equal(post.id, created.id, "Post ID mismatch")
        self.assert_equal(post.name, post_name, "Post name mismatch")
        self.assert_equal(
            post.entry,
            "<p>Test post with <strong>HTML tags</strong> to <em>retrieve</em>.</p>",
            "Post entry mismatch",
        )

        print(f"  Retrieved post {post.id} successfully")

    def test_delete_post(self):
        """Test deleting a post."""
        # Create a character
        character = self.client.characters.create(
            name=f"Integration Test Character for Posts - DELETE ME - {datetime.now().isoformat()}"
        )
        self._register_character_cleanup(character.id, character.name)

        self.wait_for_api()

        # Create a post
        post = self.client.characters.create_post(
            character,
            name=f"Integration Test Post TO DELETE - {datetime.now().isoformat()}",
            entry="<p>This post will be <del>deleted</del> shortly.</p>",
        )
        post_id = post.id

        self.wait_for_api()

        # Delete the post
        self.client.characters.delete_post(character, post_id)
        # No need to register cleanup since we're testing deletion

        self.wait_for_api()

        # Verify it's deleted by trying to get it
        try:
            self.client.characters.get_post(character, post_id)
            self.assert_true(False, f"Post {post_id} should have been deleted")
        except Exception:
            # Expected - post should not be found
            pass

        print(f"  Deleted post {post_id} successfully")

    def run_all_tests(self):
        """Run all post integration tests."""
        tests = [
            ("Post Creation on Character", self.test_create_post_on_character),
            ("Post Listing for Character", self.test_list_posts_for_character),
            ("Post Update", self.test_update_post),
            ("Post Retrieval", self.test_get_post),
            ("Post Deletion", self.test_delete_post),
        ]

        results = []
        for test_name, test_func in tests:
            result = self.run_test(test_name, test_func)
            results.append((test_name, result))

        return results


if __name__ == "__main__":
    tester = TestPostIntegration()
    results = tester.run_all_tests()

    print("\n" + "=" * 50)
    print("POST INTEGRATION TEST RESULTS")
    print("=" * 50)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        print(f"{test_name}: {status}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed < total:
        exit(1)
