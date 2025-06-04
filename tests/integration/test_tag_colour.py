"""
Integration test for Tag colour field functionality.
"""

from datetime import datetime

# Handle both direct execution and import scenarios
if __name__ == "__main__":
    import setup_test_env

    setup_test_env.setup_environment()

from base import IntegrationTestBase


class TestTagColourIntegration(IntegrationTestBase):
    """Integration tests for Tag colour field functionality."""

    def __init__(self):
        super().__init__()

    def _register_tag_cleanup(self, tag_id: int, name: str):
        """Register a tag for cleanup."""

        def cleanup():
            if self.client:
                self.client.tags.delete(tag_id)

        self.register_cleanup(f"Delete tag '{name}' (ID: {tag_id})", cleanup)

    def test_tag_with_valid_colour(self):
        """Test creating a tag with a valid named colour."""
        # Valid colours based on testing: red, green, yellow, orange, purple, pink, brown, black, grey, navy, teal, aqua, maroon
        tag_data = {
            "name": f"Red Tag - DELETE ME - {datetime.now().isoformat()}",
            "type": "Coloured Category",
            "entry": "<p>This tag has a red colour.</p>",
            "colour": "red",
        }

        # Create the tag
        tag = self.client.tags.create(**tag_data)
        self._register_tag_cleanup(tag.id, tag.name)

        # Verify the tag was created with the colour
        self.assert_not_none(tag.id, "Tag ID should not be None")
        self.assert_equal(tag.name, tag_data["name"], "Tag name mismatch")
        self.assert_equal(tag.colour, "red", "Tag colour mismatch")

        print(
            f"  Created tag with colour: {tag.name} (ID: {tag.id}, colour: {tag.colour})"
        )

    def test_tag_without_colour(self):
        """Test creating a tag without specifying colour."""
        tag_data = {
            "name": f"No Colour Tag - DELETE ME - {datetime.now().isoformat()}",
            "type": "Plain Category",
            "entry": "<p>This tag has no colour specified.</p>",
        }

        # Create the tag
        tag = self.client.tags.create(**tag_data)
        self._register_tag_cleanup(tag.id, tag.name)

        # Verify the tag was created
        self.assert_not_none(tag.id, "Tag ID should not be None")
        self.assert_equal(tag.name, tag_data["name"], "Tag name mismatch")

        print(f"  Created tag without colour: {tag.name} (ID: {tag.id})")

    def test_tag_colour_update(self):
        """Test updating a tag's colour."""
        # Create a tag without colour
        original_name = f"Colour Update Test - DELETE ME - {datetime.now().isoformat()}"
        tag = self.client.tags.create(
            name=original_name,
            type="Test Type",
            entry="<p>Tag for colour update testing.</p>",
        )
        self._register_tag_cleanup(tag.id, tag.name)

        self.wait_for_api()

        # Update the tag with a colour
        updated_tag = self.client.tags.update(tag.id, colour="green")

        # Verify the colour was updated
        self.assert_equal(updated_tag.colour, "green", "Tag colour not updated")

        print(f"  Updated tag {tag.id} colour to: {updated_tag.colour}")

    def test_multiple_coloured_tags(self):
        """Test creating multiple tags with different valid colours."""
        valid_colours = ["red", "green", "yellow", "orange", "purple"]
        created_tags = []

        for colour in valid_colours:
            tag_data = {
                "name": f"{colour.capitalize()} Tag - DELETE ME - {datetime.now().isoformat()}",
                "type": f"{colour.capitalize()} Category",
                "entry": f"<p>This tag is {colour}.</p>",
                "colour": colour,
            }

            tag = self.client.tags.create(**tag_data)
            self._register_tag_cleanup(tag.id, tag.name)
            created_tags.append(tag)

            self.assert_equal(tag.colour, colour, f"Tag colour mismatch for {colour}")

            self.wait_for_api()

        print(f"  Created {len(created_tags)} coloured tags successfully")

    def run_all_tests(self):
        """Run all tag colour integration tests."""
        tests = [
            ("Tag with Valid Colour", self.test_tag_with_valid_colour),
            ("Tag without Colour", self.test_tag_without_colour),
            ("Tag Colour Update", self.test_tag_colour_update),
            ("Multiple Coloured Tags", self.test_multiple_coloured_tags),
        ]

        results = []
        for test_name, test_func in tests:
            result = self.run_test(test_name, test_func)
            results.append((test_name, result))

        return results


if __name__ == "__main__":
    # When run directly, execute all tests
    tester = TestTagColourIntegration()
    results = tester.run_all_tests()

    print("\n" + "=" * 50)
    print("TAG COLOUR INTEGRATION TEST RESULTS")
    print("=" * 50)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        print(f"{test_name}: {status}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed < total:
        exit(1)
