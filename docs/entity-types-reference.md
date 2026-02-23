# Entity Types Reference

All entity types inherit from the `Entity` base class. This page documents the common fields and the type-specific fields for each of the 12 supported entity types.

## Common Fields (Entity Base)

Every entity type inherits these fields:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `id` | `int` | — | Type-specific entity ID (used for CRUD operations) |
| `entity_id` | `int` | — | Universal entity ID (used for posts, assets, images) |
| `name` | `str` | — | Entity name (required for creation) |
| `entry` | `str \| None` | `None` | Main text/description content (supports HTML) |
| `image` | `str \| None` | `None` | Image URL |
| `image_full` | `str \| None` | `None` | Full-size image URL |
| `image_thumb` | `str \| None` | `None` | Thumbnail image URL |
| `is_private` | `bool` | `False` | Whether entity is private |
| `tags` | `list[int]` | `[]` | List of tag IDs |
| `created_at` | `datetime` | — | Creation timestamp |
| `created_by` | `int` | — | Creator user ID |
| `updated_at` | `datetime` | — | Last update timestamp |
| `updated_by` | `int \| None` | `None` | Last updater user ID |
| `posts` | `list[Post] \| None` | `None` | Related posts (populated when `related=True`) |
| `attributes` | `list[dict] \| None` | `None` | Custom attributes (populated when `related=True`) |

### Property

- `entity_type` → `str` — Returns the lowercase class name (e.g., `"character"`, `"location"`)

---

## Calendar

Custom calendar systems for tracking campaign time.

**Manager:** `client.calendars`

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `type` | `str \| None` | `None` | Calendar type |
| `date` | `str \| None` | `None` | Current date in the calendar |
| `parameters` | `str \| None` | `None` | Calendar configuration parameters |
| `months` | `list[dict] \| None` | `None` | Month definitions |
| `weekdays` | `list[str] \| None` | `None` | Weekday names |
| `years` | `dict \| list \| None` | `None` | Year configuration |
| `seasons` | `list[dict] \| None` | `None` | Season definitions |
| `moons` | `list[dict] \| None` | `None` | Moon/celestial body definitions |
| `suffix` | `str \| None` | `None` | Year suffix format |
| `has_leap_year` | `bool \| None` | `None` | Whether calendar has leap years |
| `leap_year_amount` | `int \| None` | `None` | Frequency of leap years |
| `leap_year_month` | `int \| None` | `None` | Which month gets the extra day |
| `leap_year_offset` | `int \| None` | `None` | Leap year calculation offset |
| `leap_year_start` | `int \| None` | `None` | Starting year for leap calculations |

```python
calendar = client.calendars.create(
    name="Shire Reckoning",
    type="Regional Calendar",
    suffix="SR",
    weekdays=["Sterday", "Sunday", "Monday", "Trewsday", "Hevensday", "Mersday", "Highday"],
)
```

---

## Character

Player characters, NPCs, and other persons.

**Manager:** `client.characters`

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `type` | `str \| None` | `None` | Character type/class (e.g., "NPC", "Wizard") |
| `title` | `str \| None` | `None` | Character's title or role |
| `age` | `str \| None` | `None` | Character's age |
| `sex` | `str \| None` | `None` | Character's sex/gender |
| `pronouns` | `str \| None` | `None` | Character's pronouns |
| `race_id` | `int \| None` | `None` | Link to a Race entity |
| `family_id` | `int \| None` | `None` | Link to a Family entity |
| `location_id` | `int \| None` | `None` | Link to a Location entity |
| `is_dead` | `bool` | `False` | Whether character is deceased |

```python
character = client.characters.create(
    name="Gandalf the Grey",
    type="Wizard",
    title="Istari",
    age="2000+",
    sex="Male",
    pronouns="he/him",
    location_id=rivendell.id,
    is_dead=False,
)
```

---

## Creature

Monsters, animals, and non-character beings.

**Manager:** `client.creatures`

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `type` | `str \| None` | `None` | Creature type |
| `location_id` | `int \| None` | `None` | Creature's habitat/location |

```python
creature = client.creatures.create(
    name="Balrog",
    type="Demon",
    entry="<p>Ancient evil of Morgoth</p>",
    location_id=moria.id,
)
```

---

## Event

Historical or campaign events.

**Manager:** `client.events`

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `type` | `str \| None` | `None` | Event type/category |
| `date` | `str \| None` | `None` | When the event occurred |
| `location_id` | `int \| None` | `None` | Where the event took place |

```python
event = client.events.create(
    name="Battle of Pelennor Fields",
    type="Battle",
    date="March 15, 3019",
    location_id=minas_tirith.id,
)
```

---

## Family

Dynasties, houses, clans, and family structures.

**Manager:** `client.families`

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `location_id` | `int \| None` | `None` | Family seat/home location |
| `family_id` | `int \| None` | `None` | Parent family (for family trees) |

```python
family = client.families.create(
    name="House Baggins",
    type="Hobbit Family",
    location_id=the_shire.id,
)

# Create a sub-family
branch = client.families.create(
    name="Baggins of Hobbiton",
    family_id=family.id,
)
```

---

## Journal

Session notes, chronicles, and logs.

**Manager:** `client.journals`

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `type` | `str \| None` | `None` | Journal type |
| `date` | `str \| None` | `None` | In-game date of journal entry |
| `character_id` | `int \| None` | `None` | Character who wrote the journal |

```python
journal = client.journals.create(
    name="Session 12 Notes",
    type="Session Log",
    date="3019-03-25",
    character_id=frodo.id,
    entry="<p>The party entered Mordor...</p>",
)
```

---

## Location

Places, regions, buildings, and geographic features.

**Manager:** `client.locations`

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `type` | `str \| None` | `None` | Location type (e.g., "City", "Country", "Building") |
| `parent_location_id` | `int \| None` | `None` | Parent location (for hierarchies) |
| `map` | `str \| None` | `None` | Map image filename |
| `map_url` | `str \| None` | `None` | Full URL to map image |
| `is_map_private` | `int \| None` | `None` | Map privacy setting |

```python
middle_earth = client.locations.create(
    name="Middle-earth",
    type="Continent",
)

rivendell = client.locations.create(
    name="Rivendell",
    type="City",
    parent_location_id=middle_earth.id,
    entry="<p>The Last Homely House East of the Sea</p>",
)
```

---

## Note

General notes and campaign documentation.

**Manager:** `client.notes`

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `type` | `str \| None` | `None` | Note type/category |
| `location_id` | `int \| None` | `None` | Associated location |

```python
note = client.notes.create(
    name="DM Plot Notes",
    type="Plot Point",
    entry="<p>Remember: the eagles are coming!</p>",
    is_private=True,
)
```

---

## Organisation

Guilds, governments, companies, and other groups.

**Manager:** `client.organisations`

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `type` | `str \| None` | `None` | Organisation type |
| `location_id` | `int \| None` | `None` | Organisation's headquarters/location |
| `organisation_id` | `int \| None` | `None` | Parent organisation (for hierarchies) |

```python
council = client.organisations.create(
    name="The White Council",
    type="Council",
    location_id=rivendell.id,
)

# Create a sub-organisation
committee = client.organisations.create(
    name="Ring Committee",
    organisation_id=council.id,
)
```

---

## Quest

Missions, objectives, and goals.

**Manager:** `client.quests`

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `type` | `str \| None` | `None` | Quest type (e.g., "Main", "Side") |
| `quest_id` | `int \| None` | `None` | Parent quest (for sub-quests) |
| `character_id` | `int \| None` | `None` | Quest giver or related character |

```python
main_quest = client.quests.create(
    name="Destroy the One Ring",
    type="Main Quest",
    character_id=gandalf.id,
)

sub_quest = client.quests.create(
    name="Cross the Mines of Moria",
    type="Sub-quest",
    quest_id=main_quest.id,
)
```

---

## Race

Species, ethnicities, and racial templates.

**Manager:** `client.races`

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `type` | `str \| None` | `None` | Race type/category |
| `race_id` | `int \| None` | `None` | Parent race (for sub-races) |

```python
elves = client.races.create(
    name="Elves",
    type="Immortal Race",
)

# Create a sub-race
noldor = client.races.create(
    name="Noldor",
    type="Elven Kindred",
    race_id=elves.id,
)
```

---

## Tag

Labels for organizing and categorizing content.

**Manager:** `client.tags`

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `type` | `str \| None` | `None` | Tag type/category |
| `colour` | `str \| None` | `None` | Tag color (see valid values below) |
| `tag_id` | `int \| None` | `None` | Parent tag (for tag hierarchies) |

**Valid `colour` values:** `aqua`, `black`, `brown`, `grey`, `green`, `light-blue`, `maroon`, `navy`, `orange`, `pink`, `purple`, `red`, `teal`, `yellow`, or `None` for no color.

```python
tag = client.tags.create(
    name="Important NPC",
    colour="red",
)

# Create a child tag
sub_tag = client.tags.create(
    name="Quest Giver",
    tag_id=tag.id,
    colour="orange",
)

# Apply tags when creating or updating entities
character = client.characters.create(
    name="Gandalf",
    tags=[tag.id, sub_tag.id],
)
```
