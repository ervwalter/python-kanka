"""
Integration tests for mentions between entities.
"""

from datetime import datetime

# Handle both direct execution and import scenarios
if __name__ == "__main__":
    import setup_test_env

    setup_test_env.setup_environment()

from base import IntegrationTestBase


class TestMentionsIntegration(IntegrationTestBase):
    """Integration tests for entity mentions."""

    def __init__(self):
        super().__init__()

    def _register_character_cleanup(self, character_id: int, name: str):
        """Register a character for cleanup."""

        def cleanup():
            if self.client:
                self.client.characters.delete(character_id)

        self.register_cleanup(
            f"Delete character '{name}' (ID: {character_id})", cleanup
        )

    def _register_journal_cleanup(self, journal_id: int, name: str):
        """Register a journal for cleanup."""

        def cleanup():
            if self.client:
                self.client.journals.delete(journal_id)

        self.register_cleanup(f"Delete journal '{name}' (ID: {journal_id})", cleanup)

    def test_character_mention_in_journal(self):
        """Test mentioning a character in a journal entry."""
        # Create a character first
        character_name = (
            f"Integration Test Character - DELETE ME - {datetime.now().isoformat()}"
        )
        character = self.client.characters.create(
            name=character_name,
            title="The Mentioned Hero",
            entry="<p>This character will be mentioned in a journal.</p>",
        )
        self._register_character_cleanup(character.id, character.name)
        print(f"  Created character: {character.name} (ID: {character.id})")

        self.wait_for_api()

        # Create a journal that mentions the character using the mention syntax
        journal_name = (
            f"Integration Test Journal - DELETE ME - {datetime.now().isoformat()}"
        )
        # Kanka uses [entity:ID] syntax for mentions
        journal_entry = f"<p>Today I met [entity:{character.entity_id}], who is known as {character.title}.</p>"
        journal = self.client.journals.create(
            name=journal_name,
            type="Journal",
            entry=journal_entry,
        )
        self._register_journal_cleanup(journal.id, journal.name)
        print(f"  Created journal: {journal.name} (ID: {journal.id})")

        self.wait_for_api()

        # Fetch the journal with relations
        journal_with_relations = self.client.journals.get(journal.id, related=True)

        # Check if the character is mentioned in the journal's related entities
        if (
            hasattr(journal_with_relations, "relations")
            and journal_with_relations.relations
        ):
            found_mention = False
            for relation in journal_with_relations.relations:
                if (
                    hasattr(relation, "target_id")
                    and relation.target_id == character.entity_id
                ):
                    found_mention = True
                    print("  Found character mention in journal relations")
                    break

            if not found_mention:
                print("  Character mention not found in journal relations")
        else:
            print("  No relations found on journal")

        # Fetch the character with relations
        character_with_relations = self.client.characters.get(
            character.id, related=True
        )

        # Check if the journal mentions the character
        if (
            hasattr(character_with_relations, "relations")
            and character_with_relations.relations
        ):
            found_mention = False
            for relation in character_with_relations.relations:
                if (
                    hasattr(relation, "owner_id")
                    and relation.owner_id == journal.entity_id
                ):
                    found_mention = True
                    print("  Found journal mentioning character in character relations")
                    break

            if not found_mention:
                print("  Journal mention not found in character relations")
        else:
            print("  No relations found on character")

        # Alternative: Check if the mention is preserved in the journal entry
        self.assert_in(
            f"[entity:{character.entity_id}]",
            journal.entry,
            "Character mention should be preserved in journal entry",
        )
        print("  Verified character mention syntax in journal entry")

    def test_multiple_mentions_in_entry(self):
        """Test multiple entity mentions in a single entry."""
        # Create two characters
        character1_name = (
            f"Integration Test Character 1 - DELETE ME - {datetime.now().isoformat()}"
        )
        character1 = self.client.characters.create(
            name=character1_name,
            title="The First Hero",
            entry="<p>First character to be mentioned.</p>",
        )
        self._register_character_cleanup(character1.id, character1.name)

        character2_name = (
            f"Integration Test Character 2 - DELETE ME - {datetime.now().isoformat()}"
        )
        character2 = self.client.characters.create(
            name=character2_name,
            title="The Second Hero",
            entry="<p>Second character to be mentioned.</p>",
        )
        self._register_character_cleanup(character2.id, character2.name)

        self.wait_for_api()

        # Create a journal mentioning both characters
        journal_name = (
            f"Integration Test Journal Multi - DELETE ME - {datetime.now().isoformat()}"
        )
        journal_entry = (
            f"<p>The party consists of [entity:{character1.entity_id}] and "
            f"[entity:{character2.entity_id}]. They work together well.</p>"
        )
        journal = self.client.journals.create(
            name=journal_name,
            type="Chronicle",
            entry=journal_entry,
        )
        self._register_journal_cleanup(journal.id, journal.name)

        self.wait_for_api()

        # Verify both mentions are in the journal entry
        self.assert_in(
            f"[entity:{character1.entity_id}]",
            journal.entry,
            "First character mention should be in journal",
        )
        self.assert_in(
            f"[entity:{character2.entity_id}]",
            journal.entry,
            "Second character mention should be in journal",
        )
        print("  Verified multiple character mentions in journal entry")

    def run_all_tests(self):
        """Run all mention integration tests."""
        tests = [
            ("Character Mention in Journal", self.test_character_mention_in_journal),
            ("Multiple Mentions in Entry", self.test_multiple_mentions_in_entry),
        ]

        results = []
        for test_name, test_func in tests:
            result = self.run_test(test_name, test_func)
            results.append((test_name, result))

        return results


if __name__ == "__main__":
    # When run directly, execute all tests
    tester = TestMentionsIntegration()
    results = tester.run_all_tests()

    print("\n" + "=" * 50)
    print("MENTIONS INTEGRATION TEST RESULTS")
    print("=" * 50)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        print(f"{test_name}: {status}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed < total:
        exit(1)
