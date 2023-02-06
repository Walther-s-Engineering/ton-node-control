import re
import typing as t

from pathlib import Path

from ton_node_control.tools.installer._sources import (
    get_binaries_directory,
    get_ton_binaries_directory,
    get_module_directory,
)
from ton_node_control.utils.typing import String


from ._cursor import Cursor
from ._styling import Styles, is_decorated, colorize


class BaseInstaller:
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
        /,
        cursor: Cursor,
        *,
        ton_version: t.Optional[String] = None,
    ) -> None:
        self.ton_version: t.Optional[String] = ton_version

        self.cursor = cursor

        self._module_directory: Path = get_module_directory()
        self._binaries_directory: Path = get_binaries_directory()
        self._ton_binaries_directory: Path = get_ton_binaries_directory()

        self._meda_data: t.Dict[t.Any, t.Any] = {}

    @property
    def module_directory(self) -> Path:
        return self._module_directory

    @property
    def binaries_directory(self) -> Path:
        return self._binaries_directory

    @property
    def ton_binaries_directory(self) -> Path:
        return self._ton_binaries_directory

    @property
    def version_file(self) -> Path:
        return self.module_directory.joinpath('VERSION')

    @property
    def ton_version_file(self) -> Path:
        return self.ton_binaries_directory.joinpath('VERSION')

    def _overwrite(self, line: String) -> None:
        if not is_decorated():
            return self.cursor.write(line)
        self.cursor.move_up()
        self.cursor.clear_line()
        self.cursor.write(line)

    def write_styled_output(self, style_type: Styles, line: String) -> None:
        self.cursor.write_styled_output(style_type, line)

    def install_comment(self, message: String, version: t.Optional[String] = None) -> None:
        if version is None:
            text = 'Installing {}: {}'.format(
                colorize(Styles.info, '"ton-node-control"'),
                colorize(Styles.comment, message)
            )
        else:
            text = 'Installing {} ({}): {}'.format(
                colorize(Styles.info, '"ton-node-control"'),
                colorize(Styles.bold, version),
                colorize(Styles.comment, message),
            )
        self._overwrite(text)
