from __future__ import annotations

import typing as t

import re
import sys

from installer.typing import String, Integer
from installer.styling import is_decorated


class Cursor:
    def __init__(self) -> None:
        self._output = sys.stdout

    def move_up(self, lines: Integer = 1) -> Cursor:
        self._output.write(f"\x1b[{lines}A")

        return self

    def move_down(self, lines: Integer = 1) -> Cursor:
        self._output.write(f"\x1b[{lines}B")

        return self

    def move_right(self, columns: Integer = 1) -> Cursor:
        self._output.write(f"\x1b[{columns}C")

        return self

    def move_left(self, columns: Integer = 1) -> Cursor:
        self._output.write(f"\x1b[{columns}D")

        return self

    def move_to_column(self, column: Integer) -> Cursor:
        self._output.write(f"\x1b[{column}G")

        return self

    def move_to_position(self, column: Integer, row: Integer) -> Cursor:
        self._output.write(f"\x1b[{row + 1};{column}H")

        return self

    def save_position(self) -> Cursor:
        self._output.write("\x1b7")

        return self

    def restore_position(self) -> Cursor:
        self._output.write("\x1b8")

        return self

    def hide(self) -> Cursor:
        self._output.write("\x1b[?25l")

        return self

    def show(self) -> Cursor:
        self._output.write("\x1b[?25h\x1b[?0c")

        return self

    def clear_line(self) -> Cursor:
        """
        Clears all the output from the current line.
        """
        self._output.write("\x1b[2K")

        return self

    def clear_line_after(self) -> Cursor:
        """
        Clears all the output from the current line after the current position.
        """
        self._output.write("\x1b[K")

        return self

    def clear_output(self) -> Cursor:
        """
        Clears all the output from the cursors' current position
        to the end of the screen.
        """
        self._output.write("\x1b[0J")

        return self

    def clear_screen(self) -> Cursor:
        """
        Clears the entire screen.
        """
        self._output.write("\x1b[2J")

        return self


class Installer:
    MEDATA_URL: String = 'https://pypi.org/pypi/ton-node-control/json'
    TON_MEDATA_URL: String = 'https://api.github.com/repos/ton-blockchain/ton/commits'
    TON_SOURCES_URL: String = 'https://api.github.com/repos/ton-blockchain/ton/tarball/{version}'
    VERSION_REGEX = re.compile(
        r'v?(\d+)(?:\.(\d+))?(?:\.(\d+))?(?:\.(\d+))?'
        '('
        '[._-]?'
        r'(?:(stable|beta|b|rc|RC|alpha|a|patch|pl|p)((?:[.-]?\d+)*)?)?'
        '([.-]?dev)?'
        ')?'
        r'(?:\+\S+)?'
    )

    def __init__(
        self,
        version: t.Optional[String] = None,
        ton_version: t.Optional[String] = None,
    ) -> None:
        self.version: t.Optional[String] = version
        self.ton_version: t.Optional[String] = ton_version
        self.cursor = Cursor()

    @staticmethod
    def _write(line: String) -> None:
        sys.stdout.write(line + '\n')

    def _overwrite(self, line: String) -> None:
        if not is_decorated():
            return self._write(line)
