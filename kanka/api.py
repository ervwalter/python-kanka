"""
Main Kanka API functions and classes
"""
from datetime import datetime
from dacite import from_dict, Config
import kanka.objects.stored as stored
from .exceptions import KankaError
from .utils import to_datetime, create_entity, KankaSession
from .objects.user import Profile, Campaign

entitylist = ["character", "location", "organisation", "note",
              "race", "quest", "journal", "family"]

def bind_method(entity):
    def _method(self, entity_id):
        if entity_id:
            endpoint = f'{entity}s/{str(entity_id)}'
            data = self.session.api_request(endpoint)["data"]
            classname = getattr(stored, f'Stored{entity.title()}')
            return from_dict(
                data_class=classname,
                data=data,
                config=Config(type_hooks={datetime: to_datetime}))
        raise KankaError("No character ID provided.")
    return _method

class KankaClient(object):
    """ Interact with kanka API with this client.
    
    This class stores the kanka API token in a session object (see `~utils.KankaSession`).
    Also provides methods to retrieve campain and profile data.
    """
    def __init__(self, token=''):
        self.session = KankaSession(api_token=token)

    def get_profile(self):
        """ Get Profile information."""
        profile = Profile(self.session.api_request("profile")["data"])

        return profile

    def get_campaigns(self):
        """ Get list of campaigns.

        This function requests data from https://kanka.io/api/1.0/campaigns.
        :return: Array with campaigns
        :rtype: List of `~objects.user.Campaign`
        """
        data = self.session.api_request("campaigns")["data"]
        campaigns = [create_entity(Campaign, cdata) for cdata in data]
        return campaigns

    def campaign(self, c_id=None):
        """ Get information about a campaign."""
        if c_id is None:
            raise KankaError("Campaign id not specified.")

        for entity in entitylist:
            _method = bind_method(entity)
            setattr(Campaign, entity, _method)
        endpoint = f'campaigns/{str(c_id)}'
        campaign = create_entity(Campaign, self.session.api_request(endpoint)["data"])
        campaign.__post_init__(api_token=self.session.token)

        return campaign

    def import_campaign(self, c_id=None):
        if c_id is None:
            raise KankaError("Campaign id not specified.")

        data = self.session.api_request(f'campaigns/{str(c_id)}')
        for entity in entitylist:
            if entity[-1] == "y":
                entity = entity.replace("y", "ie")
            endpoint = f'{entity}s'
            data["data"][endpoint] = self.session.api_request(f'campaigns/{str(c_id)}/{endpoint}')["data"]

        imported = create_entity(Entity_object=stored.StoredCampaign, data=data["data"])
        return imported
