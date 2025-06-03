"""
:mod: kanka.base
Base objects. Every object is derived from KankaObject,
every core entity is derived from Entity
"""

# Re-export from new models location for backward compatibility
from ..models.base import Entity
from ..models.base import KankaModel as KankaObject
from ..models.common import Trait

# For backward compatibility with the old API
__all__ = ["KankaObject", "Entity", "Trait"]
