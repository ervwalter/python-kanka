# python-kanka
This is a python client for https://kanka.io. It's still early development so use it at your own risk.

To get started you need an API token. Create the client with
```python
import kanka
token = {your_api_token_string}
client = kanka.api.KankaClient(token)
```

With this you can get a list of campaigns or import a campaign and get entities:
```python
client.get_campaigns()
my_campaign = client.campaign({campaign_id})
my_campaign.get_characters()
char = my_campaign.character({character_id)
```
