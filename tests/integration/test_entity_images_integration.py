"""
Integration tests for Entity Image operations and convenience images parameter.
"""

import contextlib
import os
import tempfile
from datetime import datetime

# Handle both direct execution and import scenarios
if __name__ == "__main__":
    import setup_test_env

    setup_test_env.setup_environment()

from base import IntegrationTestBase

# 16x16 red square PNG (80 bytes) — large enough to visually confirm in Kanka UI
_TEST_PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
    b"\x00\x00\x00\x10\x00\x00\x00\x10\x08\x02\x00\x00\x00\x90\x91h"
    b"6\x00\x00\x00\x17IDATx\x9cc\xf8\xcf\xc0@"
    b'\x12"M\xf5\xa8\x86Q\rCJ\x03\x00\x90\xf9\xff\x01'
    b"\xf9\xe1\xfax\x00\x00\x00\x00IEND\xaeB`\x82"
)


class TestEntityImageIntegration(IntegrationTestBase):
    """Integration tests for Entity Image and convenience images operations."""

    def __init__(self):
        super().__init__()

    def _create_test_image(self, prefix="test_entimg") -> str:
        """Create a temporary PNG file and return its path."""
        fd, path = tempfile.mkstemp(suffix=".png", prefix=prefix)
        os.write(fd, _TEST_PNG)
        os.close(fd)

        def cleanup():
            with contextlib.suppress(OSError):
                os.unlink(path)

        self.register_cleanup(f"Delete temp file '{path}'", cleanup)
        return path

    def _register_character_cleanup(self, character_id: int, name: str):
        """Register a character for cleanup."""

        def cleanup():
            if self.client:
                self.client.characters.delete(character_id)

        self.register_cleanup(
            f"Delete character '{name}' (ID: {character_id})", cleanup
        )

    def test_set_image(self):
        """Test setting the main image for an entity."""
        character = self.client.characters.create(
            name=f"Integration Test Image - DELETE ME - {datetime.now().isoformat()}"
        )
        self._register_character_cleanup(character.id, character.name)

        self.wait_for_api()

        image_path = self._create_test_image()
        result = self.client.characters.set_image(character, image_path)

        self.assert_not_none(result, "set_image should return EntityImageInfo")
        self.assert_not_none(result.image, "Image data should not be None")
        self.assert_not_none(result.image.full, "Image full URL should not be None")

        print(f"  Set image for character: {result.image.full}")

    def test_get_image(self):
        """Test getting image information for an entity."""
        character = self.client.characters.create(
            name=f"Integration Test Image - DELETE ME - {datetime.now().isoformat()}"
        )
        self._register_character_cleanup(character.id, character.name)

        self.wait_for_api()

        image_path = self._create_test_image()
        self.client.characters.set_image(character, image_path)

        self.wait_for_api()

        info = self.client.characters.get_image(character)

        self.assert_not_none(info, "get_image should return EntityImageInfo")
        self.assert_not_none(info.image, "Image data should not be None after set")

        print(
            f"  Got image info: image={info.image is not None}, header={info.header is not None}"
        )

    def test_delete_image(self):
        """Test deleting the main image for an entity."""
        character = self.client.characters.create(
            name=f"Integration Test Image - DELETE ME - {datetime.now().isoformat()}"
        )
        self._register_character_cleanup(character.id, character.name)

        self.wait_for_api()

        image_path = self._create_test_image()
        self.client.characters.set_image(character, image_path)

        self.wait_for_api()

        result = self.client.characters.delete_image(character)
        self.assert_true(result, "delete_image should return True")

        self.wait_for_api()

        # Verify the image is unlinked (uuid cleared, full becomes empty string)
        info = self.client.characters.get_image(character)
        self.assert_true(
            info.image is None or not info.image.uuid,
            f"Image uuid should be cleared after delete, got: {info.image}",
        )

        print("  Deleted main image successfully")

    def test_set_header_image(self):
        """Test setting the header image for an entity."""
        character = self.client.characters.create(
            name=f"Integration Test Image - DELETE ME - {datetime.now().isoformat()}"
        )
        self._register_character_cleanup(character.id, character.name)

        self.wait_for_api()

        image_path = self._create_test_image()
        result = self.client.characters.set_image(character, image_path, is_header=True)

        self.assert_not_none(result, "set_image should return EntityImageInfo")
        self.assert_not_none(result.header, "Header data should not be None")
        self.assert_not_none(result.header.full, "Header full URL should not be None")

        print(f"  Set header image: {result.header.full}")

    def test_delete_header_image(self):
        """Test deleting the header image for an entity."""
        character = self.client.characters.create(
            name=f"Integration Test Image - DELETE ME - {datetime.now().isoformat()}"
        )
        self._register_character_cleanup(character.id, character.name)

        self.wait_for_api()

        image_path = self._create_test_image()
        self.client.characters.set_image(character, image_path, is_header=True)

        self.wait_for_api()

        result = self.client.characters.delete_image(character, is_header=True)
        self.assert_true(result, "delete_image(is_header=True) should return True")

        self.wait_for_api()

        info = self.client.characters.get_image(character)
        self.assert_true(
            info.header is None or info.header.full is None,
            "Header should be cleared after delete",
        )

        print("  Deleted header image successfully")

    def test_convenience_images_on_create(self):
        """Test the convenience images parameter on entity create."""
        image_path = self._create_test_image()

        character = self.client.characters.create(
            name=f"Integration Test Convenience - DELETE ME - {datetime.now().isoformat()}",
            entry='<p><img src="portrait.png"> A brave hero.</p>',
            images={"portrait.png": image_path},
        )
        self._register_character_cleanup(character.id, character.name)

        # Verify the entry was rewritten — src should be a CDN URL, not the placeholder
        self.assert_not_none(character.entry, "Entry should not be None")
        self.assert_true(
            'src="portrait.png"' not in character.entry,
            f"Entry src should have CDN URL, not placeholder. Got: {character.entry}",
        )
        self.assert_true(
            "<img" in character.entry,
            "Entry should still contain an img tag",
        )

        # Verify the managed asset was created
        self.wait_for_api()
        assets = self.client.characters.list_assets(character)
        managed_assets = [a for a in assets if a.type_id == 1 and ":" in a.name]
        self.assert_true(
            len(managed_assets) >= 1,
            f"Expected at least 1 managed asset, got {len(managed_assets)}",
        )

        print(
            f"  Created character with convenience images, entry: {character.entry[:80]}..."
        )

    def test_convenience_images_on_update(self):
        """Test the convenience images parameter on entity update."""
        # Create character first without images
        character = self.client.characters.create(
            name=f"Integration Test Convenience - DELETE ME - {datetime.now().isoformat()}",
            entry="<p>Original entry with no images.</p>",
        )
        self._register_character_cleanup(character.id, character.name)

        self.wait_for_api()

        # Now update with an image
        image_path = self._create_test_image()
        updated = self.client.characters.update(
            character,
            entry='<p><img src="avatar.png"> Updated with image.</p>',
            images={"avatar.png": image_path},
        )

        self.assert_not_none(updated.entry, "Entry should not be None")
        self.assert_true(
            'src="avatar.png"' not in updated.entry,
            f"Entry src should have CDN URL, not placeholder. Got: {updated.entry}",
        )

        # Verify asset was created
        self.wait_for_api()
        assets = self.client.characters.list_assets(updated)
        managed_assets = [a for a in assets if a.type_id == 1 and ":" in a.name]
        self.assert_true(
            len(managed_assets) >= 1,
            f"Expected at least 1 managed asset, got {len(managed_assets)}",
        )

        print(
            f"  Updated character with convenience images, entry: {updated.entry[:80]}..."
        )

    def test_convenience_images_on_post(self):
        """Test the convenience images parameter on post create."""
        character = self.client.characters.create(
            name=f"Integration Test Convenience - DELETE ME - {datetime.now().isoformat()}"
        )
        self._register_character_cleanup(character.id, character.name)

        self.wait_for_api()

        image_path = self._create_test_image()
        post = self.client.characters.create_post(
            character,
            name=f"Integration Test Post - DELETE ME - {datetime.now().isoformat()}",
            entry='<p><img src="map.png"> A detailed map.</p>',
            images={"map.png": image_path},
        )

        self.assert_not_none(post.entry, "Post entry should not be None")
        self.assert_true(
            'src="map.png"' not in post.entry,
            f"Post entry src should have CDN URL, not placeholder. Got: {post.entry}",
        )

        print(f"  Created post with convenience images, entry: {post.entry[:80]}...")

    def run_all_tests(self):
        """Run all entity image integration tests."""
        tests = [
            ("Entity Image - Set", self.test_set_image),
            ("Entity Image - Get", self.test_get_image),
            ("Entity Image - Delete", self.test_delete_image),
            ("Entity Image - Set Header", self.test_set_header_image),
            ("Entity Image - Delete Header", self.test_delete_header_image),
            ("Convenience Images - Create", self.test_convenience_images_on_create),
            ("Convenience Images - Update", self.test_convenience_images_on_update),
            ("Convenience Images - Post", self.test_convenience_images_on_post),
        ]

        results = []
        for test_name, test_func in tests:
            result = self.run_test(test_name, test_func)
            results.append((test_name, result))

        return results


if __name__ == "__main__":
    TestEntityImageIntegration.run_standalone("ENTITY IMAGE INTEGRATION TEST")
