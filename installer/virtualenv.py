from pathlib import Path

from installer.builder import Builder
from installer.typing import String


class VirtualEnvironment(Builder):
    def __init__(self, path: Path) -> None:
        super().__init__(path)
        self._python: String = str(self._pa)
