from __future__ import annotations

import sys

from ton_node_control.utils.typing import Bytes, String, Integer

from ton_node_control.tools.installer._styling import colorize, Styles


class Cursor:
    def __init__(self) -> None:
        self._output = sys.stdout

    def write(self, line: String) -> None:
        self._output.write(line + '\n')

    def write_styled_output(self, style_type: Styles, text: String) -> None:
        self._output.write(colorize(style_type, text) + '\n')

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
