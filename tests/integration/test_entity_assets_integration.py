"""
Integration tests for Entity Asset operations.
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


class TestEntityAssetIntegration(IntegrationTestBase):
    """Integration tests for Entity Asset CRUD operations."""

    def __init__(self):
        super().__init__()

    def _create_test_image(self, prefix="test_asset") -> str:
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

    def test_create_file_asset(self):
        """Test creating a file asset on an entity."""
        character = self.client.characters.create(
            name=f"Integration Test Assets - DELETE ME - {datetime.now().isoformat()}"
        )
        self._register_character_cleanup(character.id, character.name)

        self.wait_for_api()

        image_path = self._create_test_image()
        asset = self.client.characters.create_file_asset(
            character, image_path, name="test-file-asset"
        )

        self.assert_not_none(asset.id, "Asset ID should not be None")
        self.assert_equal(asset.type_id, 1, "File asset type_id should be 1")
        self.assert_equal(asset.name, "test-file-asset", "Asset name mismatch")
        self.assert_not_none(asset.url, "File asset should have a URL")

        print(f"  Created file asset: {asset.name} (ID: {asset.id}, URL: {asset.url})")

    def test_create_link_asset(self):
        """Test creating a link asset on an entity."""
        character = self.client.characters.create(
            name=f"Integration Test Assets - DELETE ME - {datetime.now().isoformat()}"
        )
        self._register_character_cleanup(character.id, character.name)

        self.wait_for_api()

        asset = self.client.characters.create_link_asset(
            character,
            name="Example Link",
            url="https://example.com",
            icon="fa-link",
        )

        self.assert_not_none(asset.id, "Asset ID should not be None")
        self.assert_equal(asset.type_id, 2, "Link asset type_id should be 2")
        self.assert_equal(asset.name, "Example Link", "Asset name mismatch")

        print(f"  Created link asset: {asset.name} (ID: {asset.id})")

    def test_create_alias_asset(self):
        """Test creating an alias asset on an entity."""
        character = self.client.characters.create(
            name=f"Integration Test Assets - DELETE ME - {datetime.now().isoformat()}"
        )
        self._register_character_cleanup(character.id, character.name)

        self.wait_for_api()

        asset = self.client.characters.create_alias_asset(
            character, name="The Dragon Slayer"
        )

        self.assert_not_none(asset.id, "Asset ID should not be None")
        self.assert_equal(asset.type_id, 3, "Alias asset type_id should be 3")
        self.assert_equal(asset.name, "The Dragon Slayer", "Asset name mismatch")

        print(f"  Created alias asset: {asset.name} (ID: {asset.id})")

    def test_list_assets(self):
        """Test listing assets for an entity."""
        character = self.client.characters.create(
            name=f"Integration Test Assets - DELETE ME - {datetime.now().isoformat()}"
        )
        self._register_character_cleanup(character.id, character.name)

        self.wait_for_api()

        # Create multiple asset types
        image_path = self._create_test_image()
        file_asset = self.client.characters.create_file_asset(
            character, image_path, name="list-test-file"
        )

        self.wait_for_api()

        link_asset = self.client.characters.create_link_asset(
            character, name="list-test-link", url="https://example.com"
        )

        self.wait_for_api()

        alias_asset = self.client.characters.create_alias_asset(
            character, name="list-test-alias"
        )

        self.wait_for_api()

        assets = self.client.characters.list_assets(character)

        asset_ids = {a.id for a in assets}
        self.assert_true(
            file_asset.id in asset_ids,
            f"File asset {file_asset.id} not found in list",
        )
        self.assert_true(
            link_asset.id in asset_ids,
            f"Link asset {link_asset.id} not found in list",
        )
        self.assert_true(
            alias_asset.id in asset_ids,
            f"Alias asset {alias_asset.id} not found in list",
        )

        print(f"  Listed {len(assets)} asset(s) for character")

    def test_get_asset(self):
        """Test getting a specific asset."""
        character = self.client.characters.create(
            name=f"Integration Test Assets - DELETE ME - {datetime.now().isoformat()}"
        )
        self._register_character_cleanup(character.id, character.name)

        self.wait_for_api()

        image_path = self._create_test_image()
        created = self.client.characters.create_file_asset(
            character, image_path, name="get-test-asset"
        )

        self.wait_for_api()

        fetched = self.client.characters.get_asset(character, created.id)

        self.assert_equal(fetched.id, created.id, "Asset ID mismatch")
        self.assert_equal(fetched.name, "get-test-asset", "Asset name mismatch")
        self.assert_equal(fetched.type_id, 1, "Asset type_id mismatch")

        print(f"  Retrieved asset: {fetched.name} (ID: {fetched.id})")

    def test_delete_asset(self):
        """Test deleting an asset."""
        character = self.client.characters.create(
            name=f"Integration Test Assets - DELETE ME - {datetime.now().isoformat()}"
        )
        self._register_character_cleanup(character.id, character.name)

        self.wait_for_api()

        image_path = self._create_test_image()
        asset = self.client.characters.create_file_asset(
            character, image_path, name="delete-test-asset"
        )
        asset_id = asset.id

        self.wait_for_api()

        result = self.client.characters.delete_asset(character, asset_id)
        self.assert_true(result, "delete_asset should return True")

        self.wait_for_api()

        # Verify it's deleted by checking the list
        assets = self.client.characters.list_assets(character)
        asset_ids = {a.id for a in assets}
        self.assert_true(
            asset_id not in asset_ids,
            f"Deleted asset {asset_id} should not appear in list",
        )

        print(f"  Deleted asset {asset_id}")

    def run_all_tests(self):
        """Run all entity asset integration tests."""
        tests = [
            ("Entity Asset - Create File", self.test_create_file_asset),
            ("Entity Asset - Create Link", self.test_create_link_asset),
            ("Entity Asset - Create Alias", self.test_create_alias_asset),
            ("Entity Asset - List", self.test_list_assets),
            ("Entity Asset - Get", self.test_get_asset),
            ("Entity Asset - Delete", self.test_delete_asset),
        ]

        results = []
        for test_name, test_func in tests:
            result = self.run_test(test_name, test_func)
            results.append((test_name, result))

        return results


if __name__ == "__main__":
    TestEntityAssetIntegration.run_standalone("ENTITY ASSET INTEGRATION TEST")
