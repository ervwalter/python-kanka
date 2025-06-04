"""
Integration tests for entity tagging functionality.
Tests creating entities with tags and updating entities with tags.
"""

from datetime import datetime

# Handle both direct execution and import scenarios
if __name__ == "__main__":
    import setup_test_env

    setup_test_env.setup_environment()

from base import IntegrationTestBase


class TestEntityTagsIntegration(IntegrationTestBase):
    """Integration tests for entity tagging operations."""

    def __init__(self):
        super().__init__()
        self._created_tags = []
        self._created_entities = []

    def _register_tag_cleanup(self, tag_id: int, name: str):
        """Register a tag for cleanup."""
        self._created_tags.append(tag_id)

        def cleanup():
            if self.client:
                self.client.tags.delete(tag_id)

        self.register_cleanup(f"Delete tag '{name}' (ID: {tag_id})", cleanup)

    def _register_entity_cleanup(self, entity_type: str, entity_id: int, name: str):
        """Register an entity for cleanup."""
        self._created_entities.append((entity_type, entity_id))

        def cleanup():
            if self.client:
                manager = getattr(self.client, entity_type)
                manager.delete(entity_id)

        self.register_cleanup(
            f"Delete {entity_type[:-1]} '{name}' (ID: {entity_id})", cleanup
        )

    def _create_test_tags(self):
        """Create test tags to use in entity creation/update tests."""
        tags = []

        # Create category tags
        tag_names = [
            ("Important", "red"),
            ("Quest-Related", "green"),
            ("Secret", "navy"),
            ("Player-Known", "yellow"),
        ]

        for name, color in tag_names:
            tag = self.client.tags.create(
                name=f"{name} - DELETE ME - {datetime.now().isoformat()}",
                type="Category",
                colour=color,
                entry=f"<p>Test tag for {name} items.</p>",
            )
            self._register_tag_cleanup(tag.id, tag.name)
            tags.append(tag)
            self.wait_for_api(0.2)  # Small delay between tag creations

        return tags

    def test_create_character_with_tags(self):
        """Test creating a character with tags."""
        # First create tags
        tags = self._create_test_tags()
        tag_ids = [tag.id for tag in tags[:2]]  # Use first two tags

        self.wait_for_api()

        # Create character with tags
        character_data = {
            "name": f"Tagged Character - DELETE ME - {datetime.now().isoformat()}",
            "type": "NPC",
            "entry": "<p>A character with <strong>multiple tags</strong>.</p>",
            "tags": tag_ids,  # Assign tags
        }

        character = self.client.characters.create(**character_data)
        self._register_entity_cleanup("characters", character.id, character.name)

        # Verify character was created
        self.assert_not_none(character.id, "Character ID should not be None")

        # Note: The API might not return tags in the create response
        # We'd need to fetch with ?related=1 to verify tags
        print(f"  Created character '{character.name}' with {len(tag_ids)} tags")

    def test_create_location_with_tags(self):
        """Test creating a location with tags."""
        # First create tags
        tags = self._create_test_tags()
        tag_ids = [tags[2].id]  # Use "Secret" tag

        self.wait_for_api()

        # Create location with tags
        location_data = {
            "name": f"Secret Location - DELETE ME - {datetime.now().isoformat()}",
            "type": "Hidden Base",
            "entry": "<p>A <em>secret location</em> known only to a few.</p>",
            "tags": tag_ids,
        }

        location = self.client.locations.create(**location_data)
        self._register_entity_cleanup("locations", location.id, location.name)

        print(f"  Created location '{location.name}' with secret tag")

    def test_update_entity_tags(self):
        """Test updating an entity's tags."""
        # Create tags
        tags = self._create_test_tags()

        # Create a journal without tags
        journal_name = f"Journal Entry - DELETE ME - {datetime.now().isoformat()}"
        journal = self.client.journals.create(
            name=journal_name,
            type="Session Log",
            entry="<p>Initially untagged journal entry.</p>",
        )
        self._register_entity_cleanup("journals", journal.id, journal.name)

        self.wait_for_api()

        # Update journal to add tags
        updated_data = {
            "tags": [tags[0].id, tags[1].id],  # Add "Important" and "Quest-Related"
            "entry": "<h2>Updated Entry</h2><p>This journal is now tagged as <strong>important</strong> and quest-related.</p>",
        }
        self.client.journals.update(journal.id, **updated_data)

        print(f"  Updated journal '{journal.name}' with 2 tags")

    def test_create_quest_with_nested_tags(self):
        """Test creating a quest with nested tags (parent-child tags)."""
        # Create parent tag
        parent_tag = self.client.tags.create(
            name=f"Quest Tags - DELETE ME - {datetime.now().isoformat()}",
            type="Parent",
            colour="purple",
            entry="<p>Parent category for quest tags.</p>",
        )
        self._register_tag_cleanup(parent_tag.id, parent_tag.name)

        self.wait_for_api()

        # Create child tags
        main_quest_tag = self.client.tags.create(
            name=f"Main Quest - DELETE ME - {datetime.now().isoformat()}",
            type="Quest Type",
            colour="pink",
            tag_id=parent_tag.id,
            entry="<p>Tag for main story quests.</p>",
        )
        self._register_tag_cleanup(main_quest_tag.id, main_quest_tag.name)

        side_quest_tag = self.client.tags.create(
            name=f"Side Quest - DELETE ME - {datetime.now().isoformat()}",
            type="Quest Type",
            colour="maroon",
            tag_id=parent_tag.id,
            entry="<p>Tag for optional side quests.</p>",
        )
        self._register_tag_cleanup(side_quest_tag.id, side_quest_tag.name)

        self.wait_for_api()

        # Create quest with nested tags
        quest_data = {
            "name": f"Epic Quest - DELETE ME - {datetime.now().isoformat()}",
            "type": "Main Story",
            "entry": "<h2>Save the Kingdom</h2><p>The kingdom needs <strong>heroes</strong>!</p>",
            "tags": [main_quest_tag.id],  # Use child tag
        }

        quest = self.client.quests.create(**quest_data)
        self._register_entity_cleanup("quests", quest.id, quest.name)

        print(f"  Created quest '{quest.name}' with nested tag '{main_quest_tag.name}'")

    def test_multiple_entity_types_same_tags(self):
        """Test using the same tags across different entity types."""
        # Create shared tags
        tags = self._create_test_tags()
        shared_tag_ids = [tags[0].id, tags[3].id]  # "Important" and "Player-Known"

        self.wait_for_api()

        # Create character with tags
        character = self.client.characters.create(
            name=f"Important Character - DELETE ME - {datetime.now().isoformat()}",
            type="PC",
            entry="<p>An important player character.</p>",
            tags=shared_tag_ids,
        )
        self._register_entity_cleanup("characters", character.id, character.name)

        self.wait_for_api()

        # Create note with same tags
        note = self.client.notes.create(
            name=f"Important Note - DELETE ME - {datetime.now().isoformat()}",
            type="Lore",
            entry="<p>Important information that players know.</p>",
            tags=shared_tag_ids,
        )
        self._register_entity_cleanup("notes", note.id, note.name)

        self.wait_for_api()

        # Create organisation with same tags
        organisation = self.client.organisations.create(
            name=f"Important Guild - DELETE ME - {datetime.now().isoformat()}",
            type="Guild",
            entry="<p>An important guild known to players.</p>",
            tags=shared_tag_ids,
        )
        self._register_entity_cleanup(
            "organisations", organisation.id, organisation.name
        )

        print(
            "  Created 3 different entities (character, note, organisation) with same tags"
        )

    def test_remove_tags_from_entity(self):
        """Test removing tags from an entity."""
        # Create tags
        tags = self._create_test_tags()
        all_tag_ids = [tag.id for tag in tags]

        # Create event with all tags
        event_name = f"Tagged Event - DELETE ME - {datetime.now().isoformat()}"
        event = self.client.events.create(
            name=event_name,
            type="Festival",
            date="Summer Solstice",
            entry="<p>A festival with many tags.</p>",
            tags=all_tag_ids,
        )
        self._register_entity_cleanup("events", event.id, event.name)

        self.wait_for_api()

        # Update to remove some tags (keep only first tag)
        self.client.events.update(
            event.id,
            tags=[tags[0].id],  # Keep only "Important" tag
            entry="<p>Updated: Now only marked as important.</p>",
        )

        print(f"  Updated event '{event.name}' - reduced from {len(tags)} to 1 tag")

        # Update again to remove all tags
        self.client.events.update(
            event.id,
            tags=[],  # Remove all tags
            entry="<p>Updated: All tags removed.</p>",
        )

        print(f"  Updated event '{event.name}' - removed all tags")

    def test_entity_filtering_by_tags(self):
        """Test filtering entities by tags using the entities endpoint."""
        # Create a specific tag for filtering
        filter_tag = self.client.tags.create(
            name=f"Filter Test Tag - DELETE ME - {datetime.now().isoformat()}",
            type="Test",
            colour="teal",
            entry="<p>Tag for filter testing.</p>",
        )
        self._register_tag_cleanup(filter_tag.id, filter_tag.name)

        self.wait_for_api()

        # Create multiple entities with this tag
        character = self.client.characters.create(
            name=f"Filter Test Character - DELETE ME - {datetime.now().isoformat()}",
            entry="<p>Character for tag filtering.</p>",
            tags=[filter_tag.id],
        )
        self._register_entity_cleanup("characters", character.id, character.name)

        location = self.client.locations.create(
            name=f"Filter Test Location - DELETE ME - {datetime.now().isoformat()}",
            entry="<p>Location for tag filtering.</p>",
            tags=[filter_tag.id],
        )
        self._register_entity_cleanup("locations", location.id, location.name)

        self.wait_for_api()

        # Use entities endpoint to filter by tag
        entities = self.client.entities(tags=[filter_tag.id])

        # Verify we found our entities
        found_character = False
        found_location = False

        for entity in entities:
            if (
                entity.get("child_id") == character.id
                and entity.get("type") == "character"
            ):
                found_character = True
            elif (
                entity.get("child_id") == location.id
                and entity.get("type") == "location"
            ):
                found_location = True

        self.assert_true(
            found_character and found_location,
            f"Should find both character and location with tag {filter_tag.id}",
        )

        print(f"  Successfully filtered entities by tag '{filter_tag.name}'")

    def run_all_tests(self):
        """Run all entity tag integration tests."""
        tests = [
            ("Character with Tags", self.test_create_character_with_tags),
            ("Location with Tags", self.test_create_location_with_tags),
            ("Update Entity Tags", self.test_update_entity_tags),
            ("Quest with Nested Tags", self.test_create_quest_with_nested_tags),
            ("Multiple Entities Same Tags", self.test_multiple_entity_types_same_tags),
            ("Remove Tags from Entity", self.test_remove_tags_from_entity),
            ("Filter Entities by Tags", self.test_entity_filtering_by_tags),
        ]

        results = []
        for test_name, test_func in tests:
            result = self.run_test(test_name, test_func)
            results.append((test_name, result))

        return results


if __name__ == "__main__":
    # When run directly, execute all tests
    tester = TestEntityTagsIntegration()
    results = tester.run_all_tests()

    print("\n" + "=" * 50)
    print("ENTITY TAGS INTEGRATION TEST RESULTS")
    print("=" * 50)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        print(f"{test_name}: {status}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed < total:
        exit(1)
