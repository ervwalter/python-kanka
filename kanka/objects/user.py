"""
:mod:`kanka.user` - User Profile and Campaigns
"""

from datetime import datetime
from typing import Optional

from ..exceptions import KankaError
from ..models import entities
from ..models.base import KankaModel
from ..utils import KankaSession, append_from


class Profile(KankaModel):
    """Kanka user profile information."""

    id: int
    name: str
    avatar: str
    avatar_thumb: str
    locale: str
    timezone: str
    date_format: str  # Fixed typo from date_formate
    default_pagination: int
    last_campaign_id: int
    is_patreon: bool


class Campaign(KankaModel):
    """Holds information about a campaign."""

    id: int
    name: str
    locale: str
    entry: str
    image: str
    image_full: str
    image_thumb: str
    visibility: str
    created_at: datetime
    updated_at: datetime

    # Session management for backward compatibility
    _session: Optional[KankaSession] = None

    def __post_init__(self, api_token=""):
        """Backward compatibility method - called after object creation."""
        if api_token:
            self.session = KankaSession(api_token=api_token)
            self.session.base_url += f"campaigns/{str(self.id)}/"
        elif hasattr(self, "_session") and self._session:
            self.session = self._session
            self.session.base_url += f"campaigns/{str(self.id)}/"

    def get_list_of(self, endpoint):
        charlist = append_from(self.session, [], self.session.base_url + endpoint)
        return [(item["name"], item["id"]) for item in charlist]

    def search(self, expression=None):
        """Search for entities in the campaign.
        This function uses the /search/{expression} endpoint of the kanka API.
        Requesting from this endpoint returns entities with matching expressions
        inside the name field. It seemes that a maximum of ten matching entites are
        returned with every request (todo: verify). The search is not case sensitive.

        :param expression: Term to search for. Doesn't need to match the entity name
                            commpletly, can contain parts of the name
        :type expression: string
        :return: List of entities with matched names
        """
        if expression:
            match = []
            data = self.session.api_request(f"search/{str(expression)}")
            for item in data["data"]:
                match.extend([getattr(self, item["type"])(item["id"])])
            return match
        raise KankaError("An error occured.")

    def delete(self, entity=None, id=None):
        """Deletes an entity."""
        for attr in [entity, id]:
            if attr is None:
                raise KankaError("Missing either entity type or entity id.")
        url = self.session.base_url + f"{entity}s/{str(id)}"
        r = self.session.delete(url=url, headers=self.session.headers)
        if r.status_code == 204:
            return True
        return False

    def new_entity(self, entity=None):
        """Creates new entity."""
        if entity:
            entity_class = getattr(entities, entity.title())
            # Create with minimal required fields - will be filled later
            spawn = entity_class(
                name=f"New {entity}",
                id=0,  # Temporary ID
                entity_id=0,
                created_at=datetime.now(),
                created_by=0,
                updated_at=datetime.now(),
                updated_by=0,
            )
            # Set up session for backward compatibility
            spawn._session = KankaSession(api_token=self.session.token)
            spawn._session.base_url = self.session.base_url + f"{entity}s"
            return spawn
        raise KankaError(
            'No entity type given. Specify a type, ie new_entity(entity="location"'
        )
