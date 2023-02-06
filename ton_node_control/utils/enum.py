import typing as t
from enum import Enum

from .typing import Integer, String


class AutoNameEnum(Enum):
    def _generate_next_value_(  # type: ignore[override]
        self: Enum,
        start: Integer,
        count: Integer,
        last_values: t.List[t.Any],
    ) -> Enum:
        return self

    def __str__(self) -> String:
        return self.value

    @classmethod
    def pretty_list(cls) -> String:
        return ', '.join(String(item) for item in cls)
