import sys
import typing as t


if sys.version_info < (3, 8):
    print(
        '\033[0;31mThis module cannot be used with a version of "Python" below 3.8.\n'
        f'You are using version {sys.version_info.major}.{sys.version_info.minor}\033[0m',
    )
    sys.exit(1)

try:
    Bool: t.TypeAlias = bool
    Bytes: t.TypeAlias = bytes
    String: t.TypeAlias = str
    Integer: t.TypeAlias = int
    Self = t.Self

    # Styling typing
    STYLE: t.Literal['info', 'comment', 'success', 'error', 'warning']
    COLOR: t.Literal['black', 'blue', 'cyan', 'green', 'magenta', 'red', 'white', 'yellow']
    OPTION: t.Literal['bold', 'underscore', 'blink', 'reverse', 'conceal']

except (AttributeError, ModuleNotFoundError, ImportError):
    Bool = t.TypeVar('Bool', bound=bool)  # noqa: *, 811
    Bytes = t.TypeVar('Bytes', bound=bool)  # noqa: *, 811
    String = t.TypeVar('String', bound=str)  # noqa: *, 811
    Integer = t.TypeVar('Integer', bound=int)  # noqa: *, 811
    STYLE = t.TypeVar('STYLE')
    COLOR = t.TypeVar('COLOR')
    OPTION = t.TypeVar('OPTION')
    Self = t.TypeVar('Self')
