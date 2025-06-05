"""Tests for all entity model types."""

from kanka.models.entities import (
    Calendar,
    Character,
    Creature,
    Event,
    Family,
    Journal,
    Location,
    Note,
    Organisation,
    Quest,
    Race,
    Tag,
)


class TestCreature:
    """Test Creature model."""

    def test_creature_creation(self):
        """Test creating a creature."""
        creature = Creature(
            id=1,
            entity_id=100,
            name="Red Dragon",
            created_at="2024-01-01T00:00:00.000000Z",
            created_by=1,
            updated_at="2024-01-01T00:00:00.000000Z",
            updated_by=1,
            type="Dragon",
            location_id=5,
            entry="<p>A fearsome red dragon</p>",
        )

        assert creature.name == "Red Dragon"
        assert creature.type == "Dragon"
        assert creature.location_id == 5
        assert creature.entity_type == "creature"


class TestEvent:
    """Test Event model."""

    def test_event_creation(self):
        """Test creating an event."""
        event = Event(
            id=1,
            entity_id=100,
            name="Battle of Five Armies",
            created_at="2024-01-01T00:00:00.000000Z",
            created_by=1,
            updated_at="2024-01-01T00:00:00.000000Z",
            updated_by=1,
            type="Battle",
            date="941 TA",
            location_id=3,
        )

        assert event.name == "Battle of Five Armies"
        assert event.type == "Battle"
        assert event.date == "941 TA"
        assert event.location_id == 3
        assert event.entity_type == "event"


class TestFamily:
    """Test Family model."""

    def test_family_creation(self):
        """Test creating a family."""
        family = Family(
            id=1,
            entity_id=100,
            name="House Stark",
            created_at="2024-01-01T00:00:00.000000Z",
            created_by=1,
            updated_at="2024-01-01T00:00:00.000000Z",
            updated_by=1,
            family_id=None,  # No parent family
            location_id=7,  # Winterfell
        )

        assert family.name == "House Stark"
        assert family.family_id is None
        assert family.location_id == 7
        assert family.entity_type == "family"

    def test_family_with_parent(self):
        """Test family with parent family."""
        family = Family(
            id=2,
            entity_id=101,
            name="Stark Bannermen",
            created_at="2024-01-01T00:00:00.000000Z",
            created_by=1,
            updated_at="2024-01-01T00:00:00.000000Z",
            updated_by=1,
            family_id=1,  # Parent is House Stark
        )

        assert family.family_id == 1


class TestJournal:
    """Test Journal model."""

    def test_journal_creation(self):
        """Test creating a journal."""
        journal = Journal(
            id=1,
            entity_id=100,
            name="Campaign Session 1",
            created_at="2024-01-01T00:00:00.000000Z",
            created_by=1,
            updated_at="2024-01-01T00:00:00.000000Z",
            updated_by=1,
            type="Session",
            date="3019-03-25",
            character_id=5,  # Author
            entry="<p>The party met in a tavern...</p>",
        )

        assert journal.name == "Campaign Session 1"
        assert journal.type == "Session"
        assert journal.date == "3019-03-25"
        assert journal.character_id == 5
        assert journal.entity_type == "journal"


class TestNote:
    """Test Note model."""

    def test_note_creation(self):
        """Test creating a note."""
        note = Note(
            id=1,
            entity_id=100,
            name="DM Notes - Secret Plot",
            created_at="2024-01-01T00:00:00.000000Z",
            created_by=1,
            updated_at="2024-01-01T00:00:00.000000Z",
            updated_by=1,
            type="Plot",
            is_private=True,
            entry="<p>The villain is actually...</p>",
        )

        assert note.name == "DM Notes - Secret Plot"
        assert note.type == "Plot"
        assert note.is_private is True
        assert note.entity_type == "note"


class TestOrganisation:
    """Test Organisation model."""

    def test_organisation_creation(self):
        """Test creating an organisation."""
        org = Organisation(
            id=1,
            entity_id=100,
            name="The Harpers",
            created_at="2024-01-01T00:00:00.000000Z",
            created_by=1,
            updated_at="2024-01-01T00:00:00.000000Z",
            updated_by=1,
            type="Secret Society",
            organisation_id=None,  # No parent org
            location_id=2,  # Headquarters
        )

        assert org.name == "The Harpers"
        assert org.type == "Secret Society"
        assert org.organisation_id is None
        assert org.location_id == 2
        assert org.entity_type == "organisation"

    def test_organisation_with_parent(self):
        """Test organisation with parent organisation."""
        org = Organisation(
            id=2,
            entity_id=101,
            name="Harper Cell - Waterdeep",
            created_at="2024-01-01T00:00:00.000000Z",
            created_by=1,
            updated_at="2024-01-01T00:00:00.000000Z",
            updated_by=1,
            organisation_id=1,  # Parent is The Harpers
        )

        assert org.organisation_id == 1


class TestQuest:
    """Test Quest model."""

    def test_quest_creation(self):
        """Test creating a quest."""
        quest = Quest(
            id=1,
            entity_id=100,
            name="Find the Lost Artifact",
            created_at="2024-01-01T00:00:00.000000Z",
            created_by=1,
            updated_at="2024-01-01T00:00:00.000000Z",
            updated_by=1,
            type="Main Quest",
            quest_id=None,  # No parent quest
            character_id=3,  # Quest giver
        )

        assert quest.name == "Find the Lost Artifact"
        assert quest.type == "Main Quest"
        assert quest.quest_id is None
        assert quest.character_id == 3
        assert quest.entity_type == "quest"

    def test_quest_completed(self):
        """Test completed quest."""
        quest = Quest(
            id=2,
            entity_id=101,
            name="Delivered the Message",
            created_at="2024-01-01T00:00:00.000000Z",
            created_by=1,
            updated_at="2024-01-01T00:00:00.000000Z",
            updated_by=1,
            # Note: is_completed is not in the model, but could be stored as extra field
        )

        assert quest.name == "Delivered the Message"

    def test_quest_with_parent(self):
        """Test quest with parent quest."""
        quest = Quest(
            id=3,
            entity_id=102,
            name="Talk to the Sage",
            created_at="2024-01-01T00:00:00.000000Z",
            created_by=1,
            updated_at="2024-01-01T00:00:00.000000Z",
            updated_by=1,
            quest_id=1,  # Part of "Find the Lost Artifact"
        )

        assert quest.quest_id == 1


class TestRace:
    """Test Race model."""

    def test_race_creation(self):
        """Test creating a race."""
        race = Race(
            id=1,
            entity_id=100,
            name="Elves",
            created_at="2024-01-01T00:00:00.000000Z",
            created_by=1,
            updated_at="2024-01-01T00:00:00.000000Z",
            updated_by=1,
            type="Species",
            race_id=None,  # No parent race
        )

        assert race.name == "Elves"
        assert race.type == "Species"
        assert race.race_id is None
        assert race.entity_type == "race"

    def test_race_with_parent(self):
        """Test race with parent race (subrace)."""
        race = Race(
            id=2,
            entity_id=101,
            name="High Elves",
            created_at="2024-01-01T00:00:00.000000Z",
            created_by=1,
            updated_at="2024-01-01T00:00:00.000000Z",
            updated_by=1,
            race_id=1,  # Parent is Elves
        )

        assert race.race_id == 1


class TestTag:
    """Test Tag model."""

    def test_tag_creation(self):
        """Test creating a tag."""
        tag = Tag(
            id=1,
            entity_id=100,
            name="Important NPC",
            created_at="2024-01-01T00:00:00.000000Z",
            created_by=1,
            updated_at="2024-01-01T00:00:00.000000Z",
            updated_by=1,
            type="Category",
            colour="red",
            tag_id=None,  # No parent tag
        )

        assert tag.name == "Important NPC"
        assert tag.type == "Category"
        assert tag.colour == "red"
        assert tag.tag_id is None
        assert tag.entity_type == "tag"

    def test_tag_without_colour(self):
        """Test tag without colour."""
        tag = Tag(
            id=2,
            entity_id=101,
            name="Plot Device",
            created_at="2024-01-01T00:00:00.000000Z",
            created_by=1,
            updated_at="2024-01-01T00:00:00.000000Z",
            updated_by=1,
            colour=None,
        )

        assert tag.colour is None

    def test_tag_with_parent(self):
        """Test tag with parent tag."""
        tag = Tag(
            id=3,
            entity_id=102,
            name="Main Villain",
            created_at="2024-01-01T00:00:00.000000Z",
            created_by=1,
            updated_at="2024-01-01T00:00:00.000000Z",
            updated_by=1,
            tag_id=1,  # Parent is "Important NPC"
        )

        assert tag.tag_id == 1


class TestEntityTypeProperties:
    """Test entity_type property for all models."""

    def test_all_entity_types(self):
        """Test that all entity models return correct entity_type."""
        # Common fields for all entities
        common_fields = {
            "id": 1,
            "entity_id": 100,
            "name": "Test",
            "created_at": "2024-01-01T00:00:00.000000Z",
            "created_by": 1,
            "updated_at": "2024-01-01T00:00:00.000000Z",
            "updated_by": 1,
        }

        # Test each entity type
        entities_and_types = [
            (Calendar(**common_fields), "calendar"),
            (Character(**common_fields), "character"),
            (Creature(**common_fields), "creature"),
            (Event(**common_fields), "event"),
            (Family(**common_fields), "family"),
            (Journal(**common_fields), "journal"),
            (Location(**common_fields), "location"),
            (Note(**common_fields), "note"),
            (Organisation(**common_fields), "organisation"),
            (Quest(**common_fields), "quest"),
            (Race(**common_fields), "race"),
            (Tag(**common_fields), "tag"),
        ]

        for entity, expected_type in entities_and_types:
            assert entity.entity_type == expected_type
