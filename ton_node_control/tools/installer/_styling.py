from __future__ import annotations

import io
import os
import sys
import typing as t

from collections import UserDict
from enum import auto, Enum
from typing import Any

from ton_node_control.utils.enum import AutoNameEnum
from installer.typing import Bool, String, Integer
from installer.typing import COLOR, OPTION


class Colors(AutoNameEnum):
    black = auto()
    red = auto()
    green = auto()
    yellow = auto()
    blue = auto()
    magenta = auto()
    cyan = auto()
    white = auto()


class Options(AutoNameEnum):
    bold = auto()
    underscore = auto()
    blink = auto()
    reverse = auto()
    conceal = auto()


class Styles(AutoNameEnum):
    info = auto()
    comment = auto()
    success = auto()
    error = auto()
    warning = auto()
    bold = auto()


FOREGROUND_COLORS: t.Dict[COLOR, Integer] = {
    Colors.black: 30,
    Colors.red: 31,
    Colors.green: 32,
    Colors.yellow: 33,
    Colors.blue: 34,
    Colors.magenta: 35,
    Colors.cyan: 36,
    Colors.white: 37,
}

BACKGROUND_COLORS: t.Dict[COLOR, Integer] = {
    Colors.black: 40,
    Colors.red: 41,
    Colors.green: 42,
    Colors.yellow: 43,
    Colors.blue: 44,
    Colors.magenta: 45,
    Colors.cyan: 46,
    Colors.white: 47,
}

OPTIONS: t.Dict[OPTION, Integer] = {
    Options.bold: 1,
    Options.underscore: 4,
    Options.blink: 5,
    Options.reverse: 7,
    Options.conceal: 8,
}


def style(
    foreground: String = None,
    background: String = None,
    options: t.List | t.Tuple = None,
) -> String:
    codes = []
    if foreground is not None:
        codes.append(FOREGROUND_COLORS[Colors(foreground)])
    if background is not None:
        codes.append(FOREGROUND_COLORS[Colors(background)])
    if options is not None:
        if not isinstance(options, (list, tuple)):
            options: t.List[t.Any] = [Options(options)]

        for option in options:
            codes.append(OPTIONS[Options(option)])

    return '\033[{}m'.format(';'.join(map(str, codes)))


STYLES_COLLECTION: t.Dict[Any, str] = {
    Styles.info: style('cyan'),
    Styles.comment: style('white'),
    Styles.success: style('green'),
    Styles.error: style('red'),
    Styles.warning: style('yellow'),
    Styles.bold: style(options=['bold'])
}


def write_styled_stdout(style_type: Styles, line: String) -> None:
    sys.stdout.write(colorize(style_type, line) + '\n')


def is_decorated():
    if not hasattr(sys.stdout, 'fileno'):
        return False
    try:
        return os.isatty(sys.stdout.fileno())
    except io.UnsupportedOperation:
        return False


def colorize(style_type: Styles, text: String) -> String:
    if not is_decorated():
        return text
    return f'{STYLES_COLLECTION[style_type]}{text}\033[0m'


def string_to_bool(value: String) -> Bool:
    return value in {'true', '1', 'y', 'yes'}
