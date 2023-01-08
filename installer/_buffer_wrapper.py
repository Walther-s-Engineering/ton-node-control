from __future__ import annotations

import io
import typing as t

from _typing import Bytes, String

Installer = t.TypeVar('Installer')


class BufferWrapper(io.IOBase):
    def __init__(self, installer: Installer, version: String) -> None:
        self.installer: Installer = installer
        self.version: String = version

    def write(self, text: String | Bytes) -> None:
        for line in text.read():
            self.installer._install_comment(self.version, line)

    def fileno(self) -> int:
        return self.fileno()
