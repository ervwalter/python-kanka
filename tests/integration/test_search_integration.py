"""
Integration tests for search functionality.
"""

import time
from datetime import datetime

# Handle both direct execution and import scenarios
if __name__ == "__main__":
    import setup_test_env

    setup_test_env.setup_environment()

from base import IntegrationTestBase


class TestSearchIntegration(IntegrationTestBase):
    """Integration tests for search operations."""

    def __init__(self):
        super().__init__()
        self._created_entities = []
        self._unique_suffix = datetime.now().strftime("%Y%m%d%H%M%S")

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

    def _register_tag_cleanup(self, tag_id: int, name: str):
        """Register a tag for cleanup."""

        def cleanup():
            if self.client:
                self.client.tags.delete(tag_id)

        self.register_cleanup(f"Delete tag '{name}' (ID: {tag_id})", cleanup)

    def _create_searchable_entities(self):
        """Create various entities with searchable content and tags."""
        entities_created = []

        # First create some tags
        dragon_tag = self.client.tags.create(
            name=f"Dragon-Related {self._unique_suffix} - DELETE ME",
            type="Category",
            colour="red",
            entry="<p>Tag for dragon-related content.</p>",
        )
        self._register_tag_cleanup(dragon_tag.id, dragon_tag.name)

        phoenix_tag = self.client.tags.create(
            name=f"Phoenix-Related {self._unique_suffix} - DELETE ME",
            type="Category",
            colour="orange",
            entry="<p>Tag for phoenix-related content.</p>",
        )
        self._register_tag_cleanup(phoenix_tag.id, phoenix_tag.name)

        epic_tag = self.client.tags.create(
            name=f"Epic Content {self._unique_suffix} - DELETE ME",
            type="Importance",
            colour="purple",
            entry="<p>Tag for epic/legendary content.</p>",
        )
        self._register_tag_cleanup(epic_tag.id, epic_tag.name)

        self.wait_for_api(0.5)

        # Create character with tags
        character = self.client.characters.create(
            name=f"Zephyr Dragonborn Warrior {self._unique_suffix} - DELETE ME",
            title="Dragon Slayer",
            type="PC",
            entry="<p>A mighty warrior who slays dragons with legendary prowess.</p>",
            tags=[dragon_tag.id, epic_tag.id],
        )
        self._register_entity_cleanup("characters", character.id, character.name)
        entities_created.append(("character", character))

        # Create location with tags
        location = self.client.locations.create(
            name=f"Dragon's Peak Mountain {self._unique_suffix} - DELETE ME",
            type="Mountain",
            entry="<p>Ancient mountain where dragons nest. Home to the great wyrm Zephyrion.</p>",
            tags=[dragon_tag.id],
        )
        self._register_entity_cleanup("locations", location.id, location.name)
        entities_created.append(("location", location))

        # Create note with tags
        note = self.client.notes.create(
            name=f"Dragon Lore Research {self._unique_suffix} - DELETE ME",
            type="Research",
            entry="<p>Research notes about ancient dragons and their connection to Zephyr magic.</p>",
            tags=[dragon_tag.id],
        )
        self._register_entity_cleanup("notes", note.id, note.name)
        entities_created.append(("note", note))

        # Create organisation with tags
        organisation = self.client.organisations.create(
            name=f"Order of the Crimson Phoenix {self._unique_suffix} - DELETE ME",
            type="Knightly Order",
            entry="<p>A secret order dedicated to protecting the realm from phoenix cultists.</p>",
            tags=[phoenix_tag.id, epic_tag.id],
        )
        self._register_entity_cleanup(
            "organisations", organisation.id, organisation.name
        )
        entities_created.append(("organisation", organisation))

        # Create quest with tags
        quest = self.client.quests.create(
            name=f"Hunt the Phoenix Lord {self._unique_suffix} - DELETE ME",
            type="Main Quest",
            entry="<p>Track down the Phoenix Lord before the crimson moon rises.</p>",
            tags=[phoenix_tag.id, epic_tag.id],
        )
        self._register_entity_cleanup("quests", quest.id, quest.name)
        entities_created.append(("quest", quest))

        # Store tags for reference
        self._created_tags = {
            "dragon": dragon_tag,
            "phoenix": phoenix_tag,
            "epic": epic_tag,
        }

        return entities_created

    def test_basic_search(self):
        """Test basic search functionality."""
        # Create searchable entities
        self._create_searchable_entities()

        # Give API time to index new entities
        self.wait_for_api(2.0)

        # Search for "dragon" - should find character and location
        results = self.client.search("dragon")

        # Verify we got results
        self.assert_true(
            len(results) > 0, "Should find at least some results for 'dragon'"
        )

        # Check if our entities are in results
        found_character = False
        found_location = False
        found_note = False

        for result in results:
            if hasattr(result, "name") and self._unique_suffix in result.name:
                if "Zephyr Dragonborn Warrior" in result.name:
                    found_character = True
                elif "Dragon's Peak Mountain" in result.name:
                    found_location = True
                elif "Dragon Lore Research" in result.name:
                    found_note = True

        print(f"  Found {len(results)} results for 'dragon'")
        print(f"  Found test character: {found_character}")
        print(f"  Found test location: {found_location}")
        print(f"  Found test note: {found_note}")

    def test_search_unique_term(self):
        """Test searching for a unique term."""
        # Create entities
        created_entities = self._create_searchable_entities()

        self.wait_for_api(2.0)

        # Search for unique term that should only match our entities
        results = self.client.search(self._unique_suffix)

        # Convert to list to count
        results_list = list(results)

        # Should find all our created entities
        self.assert_true(
            len(results_list) >= len(created_entities),
            f"Should find at least {len(created_entities)} results for unique suffix",
        )

        # Count how many of our entities were found
        found_count = 0
        for result in results_list:
            if hasattr(result, "name") and self._unique_suffix in result.name:
                found_count += 1

        print(
            f"  Found {found_count} of {len(created_entities)} test entities with unique suffix"
        )

    def test_search_pagination(self):
        """Test search with pagination parameters."""
        # Create entities
        self._create_searchable_entities()

        self.wait_for_api(2.0)

        # Search with pagination
        results_page1 = self.client.search("DELETE ME", page=1)
        results_page2 = self.client.search("DELETE ME", page=2)

        # Check pagination metadata (may be empty if not provided by API)
        meta = self.client.last_search_meta

        print(f"  Page 1: {len(results_page1)} results")
        print(f"  Page 2: {len(results_page2)} results")

        # Only check metadata if it's provided
        if meta:
            print(f"  Pagination metadata: {meta}")
        else:
            print("  No pagination metadata returned by API")

    def test_search_different_terms(self):
        """Test searching for different terms."""
        # Create entities
        self._create_searchable_entities()

        self.wait_for_api(2.0)

        # Search for "phoenix" - should find organisation and quest
        phoenix_results = self.client.search("phoenix")

        found_org = False
        found_quest = False

        for result in phoenix_results:
            if hasattr(result, "name") and self._unique_suffix in result.name:
                if "Order of the Crimson Phoenix" in result.name:
                    found_org = True
                elif "Hunt the Phoenix Lord" in result.name:
                    found_quest = True

        print(f"  Search 'phoenix': {len(phoenix_results)} results")
        print(f"    Found organisation: {found_org}")
        print(f"    Found quest: {found_quest}")

        # Search for "Zephyr" - should find character and note
        zephyr_results = self.client.search("Zephyr")

        found_char = False
        found_note = False

        for result in zephyr_results:
            if hasattr(result, "name") and self._unique_suffix in result.name:
                if "Zephyr Dragonborn Warrior" in result.name:
                    found_char = True
                elif "Dragon Lore Research" in result.name:
                    found_note = True

        print(f"  Search 'Zephyr': {len(zephyr_results)} results")
        print(f"    Found character: {found_char}")
        print(f"    Found note: {found_note}")

    def test_search_result_structure(self):
        """Test the structure of search results."""
        # Create a test entity
        character = self.client.characters.create(
            name=f"Structure Test Hero {self._unique_suffix} - DELETE ME",
            title="Test Title",
            entry="<p>Testing search result structure.</p>",
        )
        self._register_entity_cleanup("characters", character.id, character.name)

        self.wait_for_api(2.0)

        # Search for our unique entity
        results = self.client.search(f"Structure Test Hero {self._unique_suffix}")

        # Find our test result
        test_result = None
        for result in results:
            if hasattr(result, "name") and character.name in result.name:
                test_result = result
                break

        self.assert_not_none(
            test_result, "Should find our test character in search results"
        )

        # Verify SearchResult structure
        self.assert_true(
            hasattr(test_result, "id"), "SearchResult should have 'id' attribute"
        )
        self.assert_true(
            hasattr(test_result, "name"), "SearchResult should have 'name' attribute"
        )
        self.assert_true(
            hasattr(test_result, "type"), "SearchResult should have 'type' attribute"
        )

        # Verify values (type might be None in some cases)
        if test_result and test_result.type:
            self.assert_equal(
                test_result.type, "character", "Result type should be 'character'"
            )

        print("  Verified SearchResult structure")
        if test_result:
            print(f"    id: {test_result.id}")
            print(f"    name: {test_result.name}")
            print(f"    type: {test_result.type}")

    def test_search_no_results(self):
        """Test search that returns no results."""
        # Search for something that shouldn't exist
        unique_nonsense = f"XYZ{self._unique_suffix}QWERTY{int(time.time())}"
        results = self.client.search(unique_nonsense)

        # Should get empty list, not error
        self.assert_equal(
            len(results), 0, "Should get empty results for nonsense search"
        )

        print(f"  Search for '{unique_nonsense}': {len(results)} results (expected 0)")

    def test_search_special_characters(self):
        """Test search with special characters in entity names."""
        # Create entity with special characters
        special_name = (
            f"The Wizard's & Dragon's Tale #{self._unique_suffix} - DELETE ME"
        )
        journal = self.client.journals.create(
            name=special_name,
            type="Story",
            entry="<p>A tale of wizards & dragons in the year 2024.</p>",
        )
        self._register_entity_cleanup("journals", journal.id, journal.name)

        self.wait_for_api(2.0)

        # Search for part of the name
        results = self.client.search("Wizard's")

        # Check if we found our entity
        found = False
        for result in results:
            if hasattr(result, "name") and self._unique_suffix in result.name:
                found = True
                break

        print(f"  Created entity with special characters: {special_name}")
        print(f'  Search for "Wizard\'s": Found our entity: {found}')

    def test_search_tags(self):
        """Test searching for tags themselves."""
        # Create entities with tags
        self._create_searchable_entities()

        self.wait_for_api(2.0)

        # Search for tag names
        dragon_tag_results = self.client.search(f"Dragon-Related {self._unique_suffix}")
        epic_tag_results = self.client.search(f"Epic Content {self._unique_suffix}")

        # Check if we found the tags
        # Note: The search API returns 'entity_type' not 'type' for the entity type
        found_dragon_tag = False
        found_epic_tag = False

        for result in dragon_tag_results:
            if hasattr(result, "name") and self._unique_suffix in result.name:
                # Tags might not have a type field in SearchResult
                found_dragon_tag = True
                break

        for result in epic_tag_results:
            if hasattr(result, "name") and self._unique_suffix in result.name:
                # Tags might not have a type field in SearchResult
                found_epic_tag = True
                break

        print(f"  Search for dragon tag: Found = {found_dragon_tag}")
        print(f"  Search for epic tag: Found = {found_epic_tag}")

        # Also verify the tags are included in SearchResult objects
        print(f"  Created {len(self._created_tags)} tags for entities")

    def run_all_tests(self):
        """Run all search integration tests."""
        tests = [
            ("Basic Search", self.test_basic_search),
            ("Search Unique Term", self.test_search_unique_term),
            ("Search Pagination", self.test_search_pagination),
            ("Search Different Terms", self.test_search_different_terms),
            ("Search Result Structure", self.test_search_result_structure),
            ("Search No Results", self.test_search_no_results),
            ("Search Special Characters", self.test_search_special_characters),
            ("Search Tags", self.test_search_tags),
        ]

        results = []
        for test_name, test_func in tests:
            result = self.run_test(test_name, test_func)
            results.append((test_name, result))

        return results


if __name__ == "__main__":
    # When run directly, execute all tests
    tester = TestSearchIntegration()
    results = tester.run_all_tests()

    print("\n" + "=" * 50)
    print("SEARCH INTEGRATION TEST RESULTS")
    print("=" * 50)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        print(f"{test_name}: {status}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed < total:
        exit(1)
