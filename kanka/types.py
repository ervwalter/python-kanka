"""Type aliases and custom types for the Kanka SDK."""

from datetime import datetime
from typing import Union

# Pydantic accepts both datetime objects and ISO format strings for datetime fields
# This type alias helps mypy understand that both are valid
DateTimeField = Union[datetime, str]
