"""
Integration tests for the generic entities API endpoint.
"""

from datetime import datetime

# Handle both direct execution and import scenarios
if __name__ == "__main__":
    import setup_test_env

    setup_test_env.setup_environment()

from base import IntegrationTestBase


class TestEntitiesApiIntegration(IntegrationTestBase):
    """Integration tests for the generic entities API endpoint."""

    def __init__(self):
        super().__init__()
        self._created_entities = []

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

    def _create_test_entities(self):
        """Create various test entities for testing the entities API."""
        entities_created = []

        # Create a character
        character = self.client.characters.create(
            name=f"Entities API Test Character - DELETE ME - {datetime.now().isoformat()}",
            title="Test Hero",
            type="PC",
            entry="<p>Character for entities API testing.</p>",
            is_private=False,
        )
        self._register_entity_cleanup("characters", character.id, character.name)
        entities_created.append(("character", character))

        # Create a location
        location = self.client.locations.create(
            name=f"Entities API Test Location - DELETE ME - {datetime.now().isoformat()}",
            type="City",
            entry="<p>Location for entities API testing.</p>",
            is_private=True,  # Private entity
        )
        self._register_entity_cleanup("locations", location.id, location.name)
        entities_created.append(("location", location))

        # Create a note
        note = self.client.notes.create(
            name=f"Entities API Test Note - DELETE ME - {datetime.now().isoformat()}",
            type="Secret",
            entry="<p>Note for entities API testing.</p>",
            is_private=False,
        )
        self._register_entity_cleanup("notes", note.id, note.name)
        entities_created.append(("note", note))

        # Create an organisation
        organisation = self.client.organisations.create(
            name=f"Entities API Test Guild - DELETE ME - {datetime.now().isoformat()}",
            type="Guild",
            entry="<p>Organisation for entities API testing.</p>",
            is_private=False,
        )
        self._register_entity_cleanup(
            "organisations", organisation.id, organisation.name
        )
        entities_created.append(("organisation", organisation))

        # Create a quest
        quest = self.client.quests.create(
            name=f"Entities API Test Quest - DELETE ME - {datetime.now().isoformat()}",
            type="Main",
            entry="<p>Quest for entities API testing.</p>",
            is_private=True,  # Another private entity
        )
        self._register_entity_cleanup("quests", quest.id, quest.name)
        entities_created.append(("quest", quest))

        return entities_created

    def test_list_all_entities(self):
        """Test listing all entities without filters."""
        # Create test entities
        created_entities = self._create_test_entities()

        self.wait_for_api()

        # List entities with a name filter to limit results
        # (listing truly ALL entities might be too much data)
        test_entities = self.client.entities(name="Entities API Test")

        # Convert to list to ensure we can iterate multiple times
        test_entities_list = list(test_entities)

        # Verify we get entities
        self.assert_true(
            len(test_entities_list) > 0, "Should have at least some entities"
        )

        # Verify our created entities are in the list
        created_entity_ids = {entity.entity_id for _, entity in created_entities}
        found_ids = {entity.get("id") for entity in test_entities_list}

        found_count = 0
        for entity_id in created_entity_ids:
            if entity_id in found_ids:
                found_count += 1

        self.assert_equal(
            found_count,
            len(created_entities),
            f"Should find all {len(created_entities)} created test entities",
        )

        print(f"  Listed {len(test_entities_list)} test entities")
        print(f"  Found all {len(created_entities)} created test entities")

    def test_filter_by_single_type(self):
        """Test filtering entities by a single type."""
        # Create test entities
        created_entities = self._create_test_entities()

        self.wait_for_api()

        # Filter for only characters
        character_entities = self.client.entities(types="character")

        # Verify all returned entities are characters
        for entity in character_entities:
            self.assert_equal(
                entity.get("type"),
                "character",
                f"Entity {entity.get('id')} should be type 'character'",
            )

        # Find our test character
        test_character = next(
            (e for t, e in created_entities if t == "character"), None
        )
        found = False
        if test_character:
            found = any(
                e.get("id") == test_character.entity_id for e in character_entities
            )
        self.assert_true(found, "Test character should be in filtered results")

        print(f"  Found {len(character_entities)} character entities")

    def test_filter_by_multiple_types(self):
        """Test filtering entities by multiple types."""
        # Create test entities
        self._create_test_entities()

        self.wait_for_api()

        # Filter for characters and locations
        entities = self.client.entities(types=["character", "location"])

        # Verify all returned entities are of the requested types
        valid_types = {"character", "location"}
        for entity in entities:
            self.assert_in(
                entity.get("type"),
                valid_types,
                "Entity type should be character or location",
            )

        # Count entities by type
        type_counts: dict[str, int] = {}
        for entity in entities:
            entity_type = entity.get("type", "unknown")
            type_counts[entity_type] = type_counts.get(entity_type, 0) + 1

        print(f"  Found {len(entities)} entities of types character/location")
        for entity_type, count in type_counts.items():
            print(f"    - {entity_type}: {count}")

    def test_filter_by_name(self):
        """Test filtering entities by name."""
        # Create test entities
        created_entities = self._create_test_entities()

        self.wait_for_api()

        # Filter by our test prefix
        test_entities = self.client.entities(name="Entities API Test")

        # Verify all returned entities have our test prefix in the name
        for entity in test_entities:
            entity_name = entity.get("name", "")
            self.assert_in(
                "Entities API Test",
                entity_name,
                "Entity name should contain 'Entities API Test'",
            )

        # Should find all our created entities
        self.assert_true(
            len(test_entities) >= len(created_entities),
            f"Should find at least {len(created_entities)} test entities",
        )

        print(f"  Found {len(test_entities)} entities with name filter")

    def test_filter_by_is_private(self):
        """Test filtering entities by privacy status."""
        # Create test entities (some private, some public)
        self._create_test_entities()

        self.wait_for_api()

        # Filter for private entities only
        private_entities = self.client.entities(
            is_private=1,
            name="Entities API Test",  # Add name filter to focus on our test entities
        )

        # Verify all returned entities are private
        for entity in private_entities:
            self.assert_equal(
                entity.get("is_private"),
                1,
                f"Entity {entity.get('id')} should be private",
            )

        # We created 2 private entities (location and quest)
        private_count = sum(1 for entity in private_entities)
        self.assert_true(
            private_count >= 2,
            f"Should find at least 2 private test entities, found {private_count}",
        )

        print(f"  Found {private_count} private entities")

        # Filter for public entities only
        public_entities = self.client.entities(is_private=0, name="Entities API Test")

        # Verify all returned entities are public
        for entity in public_entities:
            self.assert_equal(
                entity.get("is_private"),
                0,
                f"Entity {entity.get('id')} should be public",
            )

        public_count = sum(1 for entity in public_entities)
        print(f"  Found {public_count} public entities")

    def test_filter_with_tags(self):
        """Test filtering entities by tags."""
        # Create a tag first
        tag = self.client.tags.create(
            name=f"Entities API Filter Tag - DELETE ME - {datetime.now().isoformat()}",
            type="Test",
            colour="teal",
        )

        def cleanup_tag():
            if self.client:
                self.client.tags.delete(tag.id)

        self.register_cleanup(f"Delete tag '{tag.name}' (ID: {tag.id})", cleanup_tag)

        self.wait_for_api()

        # Create entities with this tag
        character_with_tag = self.client.characters.create(
            name=f"Tagged Character - DELETE ME - {datetime.now().isoformat()}",
            type="NPC",
            tags=[tag.id],
        )
        self._register_entity_cleanup(
            "characters", character_with_tag.id, character_with_tag.name
        )

        journal_with_tag = self.client.journals.create(
            name=f"Tagged Journal - DELETE ME - {datetime.now().isoformat()}",
            type="Session",
            tags=[tag.id],
        )
        self._register_entity_cleanup(
            "journals", journal_with_tag.id, journal_with_tag.name
        )

        self.wait_for_api()

        # Filter entities by tag
        tagged_entities = self.client.entities(tags=[tag.id])

        # Verify we found our tagged entities
        found_character = False
        found_journal = False

        for entity in tagged_entities:
            if (
                entity.get("child_id") == character_with_tag.id
                and entity.get("type") == "character"
            ):
                found_character = True
            elif (
                entity.get("child_id") == journal_with_tag.id
                and entity.get("type") == "journal"
            ):
                found_journal = True

        self.assert_true(found_character, "Should find tagged character")
        self.assert_true(found_journal, "Should find tagged journal")

        print(f"  Found {len(tagged_entities)} entities with tag filter")

    def test_combined_filters(self):
        """Test combining multiple filters."""
        # Create test entities
        self._create_test_entities()

        self.wait_for_api()

        # Filter for public characters and notes with our test prefix
        filtered_entities = list(
            self.client.entities(
                types=["character", "note"], is_private=0, name="Entities API Test"
            )
        )

        # Verify all returned entities match all criteria
        for entity in filtered_entities:
            # Should be character or note
            self.assert_in(
                entity.get("type"),
                ["character", "note"],
                "Entity type should be character or note",
            )

            # Should be public
            self.assert_equal(entity.get("is_private"), 0, "Entity should be public")

            # Should have our test prefix
            self.assert_in(
                "Entities API Test",
                entity.get("name", ""),
                "Entity name should contain test prefix",
            )

        entity_count = len(filtered_entities)
        print(f"  Found {entity_count} entities matching combined filters")

    def test_entity_response_structure(self):
        """Test the structure of entity responses from the generic API."""
        # Create a test entity
        character = self.client.characters.create(
            name=f"Structure Test Character - DELETE ME - {datetime.now().isoformat()}",
            title="Test Title",
            entry="<p>Testing entity structure.</p>",
        )
        self._register_entity_cleanup("characters", character.id, character.name)

        self.wait_for_api()

        # Get entities and find our character
        entities = self.client.entities(name="Structure Test Character")

        test_entity = None
        for entity in entities:
            if entity.get("child_id") == character.id:
                test_entity = entity
                break

        self.assert_not_none(test_entity, "Should find our test character")

        # Verify expected fields in generic entity response
        expected_fields = ["id", "name", "type", "child_id"]
        for field in expected_fields:
            self.assert_in(field, test_entity, f"Entity should have '{field}' field")

        # Verify values
        if test_entity:
            self.assert_equal(
                test_entity["id"], character.entity_id, "Entity ID mismatch"
            )
            self.assert_equal(test_entity["type"], "character", "Entity type mismatch")
            self.assert_equal(
                test_entity["child_id"], character.id, "Child ID mismatch"
            )

        print("  Verified entity structure for generic API response")

    def run_all_tests(self):
        """Run all entities API integration tests."""
        tests = [
            ("List All Entities", self.test_list_all_entities),
            ("Filter by Single Type", self.test_filter_by_single_type),
            ("Filter by Multiple Types", self.test_filter_by_multiple_types),
            ("Filter by Name", self.test_filter_by_name),
            ("Filter by Privacy Status", self.test_filter_by_is_private),
            ("Filter by Tags", self.test_filter_with_tags),
            ("Combined Filters", self.test_combined_filters),
            ("Entity Response Structure", self.test_entity_response_structure),
        ]

        results = []
        for test_name, test_func in tests:
            result = self.run_test(test_name, test_func)
            results.append((test_name, result))

        return results


if __name__ == "__main__":
    # When run directly, execute all tests
    tester = TestEntitiesApiIntegration()
    results = tester.run_all_tests()

    print("\n" + "=" * 50)
    print("ENTITIES API INTEGRATION TEST RESULTS")
    print("=" * 50)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        print(f"{test_name}: {status}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed < total:
        exit(1)
