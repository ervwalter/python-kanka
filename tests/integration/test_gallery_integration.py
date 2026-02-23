"""
Integration tests for Campaign Gallery operations.
"""

import contextlib
import os
import tempfile

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


class TestGalleryIntegration(IntegrationTestBase):
    """Integration tests for Campaign Gallery CRUD operations."""

    def __init__(self):
        super().__init__()

    def _create_test_image(self, prefix="test_gallery") -> str:
        """Create a temporary PNG file and return its path."""
        fd, path = tempfile.mkstemp(suffix=".png", prefix=prefix)
        os.write(fd, _TEST_PNG)
        os.close(fd)

        def cleanup():
            with contextlib.suppress(OSError):
                os.unlink(path)

        self.register_cleanup(f"Delete temp file '{path}'", cleanup)
        return path

    def _register_gallery_cleanup(self, image_id: str, name: str):
        """Register a gallery image for cleanup."""

        def cleanup():
            if self.client:
                with contextlib.suppress(Exception):
                    self.client.gallery_delete(image_id)

        self.register_cleanup(
            f"Delete gallery image '{name}' (ID: {image_id})", cleanup
        )

    def test_gallery_upload(self):
        """Test uploading an image to the campaign gallery."""
        image_path = self._create_test_image()

        image = self.client.gallery_upload(image_path)
        self._register_gallery_cleanup(image.id, image.name or "unnamed")

        self.assert_not_none(image.id, "Gallery image ID should not be None")
        self.assert_not_none(image.path, "Gallery image path (URL) should not be None")
        self.assert_equal(image.ext, "png", "Extension should be png")

        print(f"  Uploaded gallery image: {image.name} (ID: {image.id})")

    def test_gallery_get(self):
        """Test retrieving a specific gallery image."""
        image_path = self._create_test_image()

        uploaded = self.client.gallery_upload(image_path)
        self._register_gallery_cleanup(uploaded.id, uploaded.name or "unnamed")

        self.wait_for_api()

        fetched = self.client.gallery_get(uploaded.id)

        self.assert_equal(fetched.id, uploaded.id, "Image ID mismatch")
        self.assert_equal(fetched.ext, "png", "Extension should be png")

        print(f"  Retrieved gallery image: {fetched.id}")

    def test_gallery_list(self):
        """Test listing campaign gallery images."""
        image_path = self._create_test_image()

        uploaded = self.client.gallery_upload(image_path)
        self._register_gallery_cleanup(uploaded.id, uploaded.name or "unnamed")

        self.wait_for_api()

        images = self.client.gallery()

        found = any(img.id == uploaded.id for img in images)
        self.assert_true(
            found, f"Uploaded image {uploaded.id} not found in gallery list"
        )

        print(f"  Found {len(images)} image(s) in gallery")

    def test_gallery_delete(self):
        """Test deleting a gallery image."""
        image_path = self._create_test_image()

        uploaded = self.client.gallery_upload(image_path)
        image_id = uploaded.id

        self.wait_for_api()

        result = self.client.gallery_delete(image_id)
        self.assert_true(result, "gallery_delete should return True")

        self.wait_for_api()

        # Verify it's deleted
        try:
            self.client.gallery_get(image_id)
            self.assert_true(
                False, f"Gallery image {image_id} should have been deleted"
            )
        except Exception:
            pass

        print(f"  Deleted gallery image {image_id}")

    def run_all_tests(self):
        """Run all gallery integration tests."""
        tests = [
            ("Gallery Upload", self.test_gallery_upload),
            ("Gallery Get", self.test_gallery_get),
            ("Gallery List", self.test_gallery_list),
            ("Gallery Delete", self.test_gallery_delete),
        ]

        results = []
        for test_name, test_func in tests:
            result = self.run_test(test_name, test_func)
            results.append((test_name, result))

        return results


if __name__ == "__main__":
    TestGalleryIntegration.run_standalone("GALLERY INTEGRATION TEST")
