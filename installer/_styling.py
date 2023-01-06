from __future__ import annotations

import io
import os
import sys
import typing as t

from tnc_typing import Bool, String, Integer
from tnc_typing import COLOR, OPTION, STYLE

FOREGROUND_COLORS: t.Dict[COLOR, Integer] = dict(
    black=30,
    red=31,
    green=32,
    yellow=33,
    blue=34,
    magenta=35,
    cyan=36,
    white=37,
)
BACKGROUND_COLORS: t.Dict[COLOR, Integer] = dict(
    black=40,
    red=41,
    green=42,
    yellow=43,
    blue=44,
    magenta=45,
    cyan=46,
    white=47,
)
OPTIONS: t.Dict[OPTION, Integer] = dict(
    bold=1, underscore=4, blink=5, reverse=7, conceal=8,
)


def style(
    foreground: String = None,
    background: String = None,
    options: t.List | t.Tuple = None,
) -> String:
    codes = []
    if foreground is not None:
        codes.append(FOREGROUND_COLORS[foreground])
    if background is not None:
        codes.append(FOREGROUND_COLORS[background])
    if options is not None:
        if not isinstance(options, (list, tuple)):
            options: t.List[t.Any] = [options]
        
        for option in options:
            codes.append(OPTIONS[option])
    
    return '\033[{}m'.format(';'.join(map(str, codes)))


STYLES = dict(
    info=style('cyan'),
    comment=style('white'),
    success=style('green'),
    error=style('red'),
    warning=style('yellow'),
    bold=style(options=['bold']),
)


def write_styled_stdout(style_type: STYLE, line: String) -> None:
    sys.stdout.write(colorize(style_type, line) + '\n')


def is_decorated():
    if not hasattr(sys.stdout, 'fileno'):
        return False
    try:
        return os.isatty(sys.stdout.fileno())
    except io.UnsupportedOperation:
        return False


def colorize(style_type: STYLE, text: String) -> String:
    if not is_decorated():
        return text
    return f'{STYLES[style_type]}{text}\033[0m'


def string_to_bool(value: String) -> Bool:
    return value in {'true', '1', 'y', 'yes'}
