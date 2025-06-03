"""
Integration tests for Post sub-resource operations.
"""
from datetime import datetime
from typing import Optional

from .base import IntegrationTestBase
# Character and Post types are imported implicitly through the client


class TestPostIntegration(IntegrationTestBase):
    """Integration tests for Post CRUD operations as sub-resources."""
    
    def __init__(self):
        super().__init__()
        self.created_character_id: Optional[int] = None
        self.created_post_id: Optional[int] = None
        
    def teardown(self):
        """Clean up any created posts and characters."""
        if self.created_post_id and self.created_character_id and self.client:
            try:
                self.client.characters.posts(self.created_character_id).delete(self.created_post_id)
                print(f"  Cleaned up post {self.created_post_id}")
            except Exception:
                pass  # Already deleted or doesn't exist
                
        if self.created_character_id and self.client:
            try:
                self.client.characters.delete(self.created_character_id)
                print(f"  Cleaned up character {self.created_character_id}")
            except Exception:
                pass  # Already deleted or doesn't exist
        super().teardown()
        
    def test_create_post_on_character(self):
        """Test creating a post on a character."""
        # First create a character
        character_name = f"Integration Test Character for Posts - DELETE ME - {datetime.now().isoformat()}"
        character = self.client.characters.create(name=character_name)
        self.created_character_id = character.id
        
        self.wait_for_api()
        
        # Create post data
        post_data = {
            "name": f"Integration Test Post - DELETE ME - {datetime.now().isoformat()}",
            "entry": "<h3>Character Journal Entry</h3><p>Today's <strong>adventures</strong> included:</p><ul><li>Meeting with the guild</li><li>Exploring the dungeon</li><li>Finding mysterious artifact</li></ul><p><em>More details to follow...</em></p>",
            "visibility": "all"
        }
        
        # Create the post on the character
        post = self.client.characters.posts(character.id).create(**post_data)
        self.created_post_id = post.id
        
        # Verify the post was created
        self.assert_not_none(post.id, "Post ID should not be None")
        self.assert_equal(post.name, post_data["name"], "Post name mismatch")
        self.assert_equal(post.entry, post_data["entry"], "Post entry mismatch")
        self.assert_equal(post.visibility, post_data["visibility"], "Post visibility mismatch")
        
        print(f"  Created post: {post.name} (ID: {post.id}) on character {character.id}")
        
    def test_list_posts_for_character(self):
        """Test listing posts for a character."""
        # Create a character
        character = self.client.characters.create(
            name=f"Integration Test Character for Posts - DELETE ME - {datetime.now().isoformat()}"
        )
        self.created_character_id = character.id
        
        self.wait_for_api()
        
        # Create a post on the character
        post_name = f"Integration Test Post - DELETE ME - {datetime.now().isoformat()}"
        post = self.client.characters.posts(character.id).create(
            name=post_name,
            entry="<p>A brief <strong>post</strong> with <em>simple HTML</em> content.</p>"
        )
        self.created_post_id = post.id
        
        self.wait_for_api()
        
        # List all posts for the character
        posts = list(self.client.characters.posts(character.id).list())
        
        # Verify our post appears in the list
        found = False
        for p in posts:
            if p.id == post.id:
                found = True
                break
                
        self.assert_true(found, f"Created post {post.id} not found in character's posts")
        print(f"  Found {len(posts)} post(s) for character {character.id}")
        
    def test_update_post(self):
        """Test updating a post."""
        # Create a character
        character = self.client.characters.create(
            name=f"Integration Test Character for Posts - DELETE ME - {datetime.now().isoformat()}"
        )
        self.created_character_id = character.id
        
        self.wait_for_api()
        
        # Create a post
        original_name = f"Integration Test Post - DELETE ME - {datetime.now().isoformat()}"
        post = self.client.characters.posts(character.id).create(
            name=original_name,
            entry="<p>Original post with <strong>basic formatting</strong>.</p>",
            visibility="all"
        )
        self.created_post_id = post.id
        
        self.wait_for_api()
        
        # Update the post
        updated_data = {
            "entry": "<h3>Updated Journal Entry</h3><p>This post has been <em>updated</em> with new information:</p><ol><li>Quest completed successfully</li><li>Rewards collected</li><li>New quest received</li></ol><blockquote>The journey continues...</blockquote>",
            "visibility": "members"
        }
        updated_post = self.client.characters.posts(character.id).update(post.id, **updated_data)
        
        # Verify updates
        self.assert_equal(updated_post.name, original_name, "Name should not change")
        self.assert_equal(updated_post.entry, updated_data["entry"], "Entry not updated")
        self.assert_equal(updated_post.visibility, "members", "Visibility not updated")
        
        print(f"  Updated post {post.id} successfully")
        
    def test_get_post(self):
        """Test getting a specific post."""
        # Create a character
        character = self.client.characters.create(
            name=f"Integration Test Character for Posts - DELETE ME - {datetime.now().isoformat()}"
        )
        self.created_character_id = character.id
        
        self.wait_for_api()
        
        # Create a post
        post_name = f"Integration Test Post - DELETE ME - {datetime.now().isoformat()}"
        created = self.client.characters.posts(character.id).create(
            name=post_name,
            entry="<p>Test post with <strong>HTML tags</strong> to <em>retrieve</em>.</p>"
        )
        self.created_post_id = created.id
        
        self.wait_for_api()
        
        # Get the post by ID
        post = self.client.characters.posts(character.id).get(created.id)
        
        # Verify we got the right post
        self.assert_equal(post.id, created.id, "Post ID mismatch")
        self.assert_equal(post.name, post_name, "Post name mismatch")
        self.assert_equal(post.entry, "<p>Test post with <strong>HTML tags</strong> to <em>retrieve</em>.</p>", "Post entry mismatch")
        
        print(f"  Retrieved post {post.id} successfully")
        
    def test_delete_post(self):
        """Test deleting a post."""
        # Create a character
        character = self.client.characters.create(
            name=f"Integration Test Character for Posts - DELETE ME - {datetime.now().isoformat()}"
        )
        self.created_character_id = character.id
        
        self.wait_for_api()
        
        # Create a post
        post = self.client.characters.posts(character.id).create(
            name=f"Integration Test Post TO DELETE - {datetime.now().isoformat()}",
            entry="<p>This post will be <del>deleted</del> shortly.</p>"
        )
        post_id = post.id
        
        self.wait_for_api()
        
        # Delete the post
        self.client.characters.posts(character.id).delete(post_id)
        self.created_post_id = None  # Already deleted
        
        self.wait_for_api()
        
        # Verify it's deleted by trying to get it
        try:
            self.client.characters.posts(character.id).get(post_id)
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
    
    print("\n" + "="*50)
    print("POST INTEGRATION TEST RESULTS")
    print("="*50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        print(f"{test_name}: {status}")
        
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed < total:
        exit(1)