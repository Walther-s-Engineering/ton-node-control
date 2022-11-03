from enum import Enum

from .base_enum import EnumHelper


class MainMenuEntries(str, EnumHelper, Enum):
    status = 'status'
