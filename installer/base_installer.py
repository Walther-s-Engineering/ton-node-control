from __future__ import annotations

import contextlib
import functools
import json
import typing as t

import re
import sys
import shutil

from pathlib import Path
from urllib.request import Request, urlopen

from installer.compiler import Compiler
from installer.virtualenv import VirtualEnvironment
from ton_node_control.tools.installer._styling import colorize, is_decorated
from ton_node_control.tools.installer._sources import get_binaries_directory, get_module_directory, get_ton_binaries_directory
from ton_node_control.tools.installer._cursor import Cursor
from installer.typing import Bytes, String, Integer


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
        /,
        cursor: Cursor,
        *,
        version: t.Optional[String] = None,
        ton_version: t.Optional[String] = None,
    ) -> None:
        self.version: t.Optional[String] = version
        self.ton_version: t.Optional[String] = ton_version
        
        self.cursor = Cursor()
        
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

    @staticmethod
    def _get(url: String) -> Bytes:
        request = Request(url, headers={'User-Agent': 'ton-node-control'})
        with contextlib.closing(urlopen(request)) as response:
            return response.read()

    @staticmethod
    def _write(line: String) -> None:
        sys.stdout.write(line + '\n')

    def _overwrite(self, line: String) -> None:
        if not is_decorated():
            return self._write(line)
        self.cursor.move_up()
        self.cursor.clear_line()
        self._write(line)

    def _install_comment(self, version: String, message: String) -> None:
        self._overwrite(
            'Installing {} ({}): {}'.format(
                colorize('info', '"ton-node-control"'),
                colorize('bold', version),
                colorize('comment', message),
            ),
        )

    def ensure_directories(self) -> None:
        self.module_directory.mkdir(parents=True, exist_ok=True)
        self.binaries_directory.mkdir(parents=True, exist_ok=True)
        self.ton_binaries_directory.mkdir(parents=True, exist_ok=True)

    def get_package_meta_data(self) -> t.Tuple[t.Optional[String], t.Optional[String]]:
        current_version = None
        if self.version_file.exists():
            current_version = self.version_file.read_text().strip()
        self._write(
            colorize(
                'info',
                f'Retrieving "ton-node-control" meta-data',
            ),
        )
        self._meda_data = json.loads(self._get(self.MEDATA_URL).decode())
        
        def _compare_versions(current: String, lookup: String) -> Integer:
            version_current: re.Match = self.VERSION_REGEX.match(current)
            version_lookup: re.Match = self.VERSION_REGEX.match(lookup)
            version_current: t.Tuple[Integer] = tuple(
                int(p)
                for p in version_current.groups()[:3] + (version_current.group(5),)
            )
            version_lookup: t.Tuple[Integer] = tuple(
                int(p)
                for p in version_lookup.groups()[:3] + (version_lookup.group(5),)
            )
            if version_current < version_lookup:
                return -1
            if version_current > version_lookup:
                return 1
            return 0
        
        self._write('')
        releases = sorted(
            self._meda_data['releases'].keys(),
            key=functools.cmp_to_key(_compare_versions),
        )
        if self.version is not None and self.version not in releases:
            message = colorize('error', f'Version "{self.version} does not exists."')
            self._write(message)
            raise ValueError(message)
        
        version = self.version
        if version is None:
            for release in reversed(releases):
                match = self.VERSION_REGEX.match(release)
                if match.group(5):  # FIXME: and self.allow_pre_releases() is False:
                    continue
                version = release
                break
        if current_version == version:  # FIXME: and self._force is False:
            self._write(
                f'The latest version ({colorize("bold", version)}) is already installed.',
            )
            return None, current_version
        return version, current_version

    @contextlib.contextmanager
    def make_environment(self, version: String) -> VirtualEnvironment:
        env_path: Path = self.module_directory.joinpath('venv')
        env_path_saved: Path = env_path.with_suffix('.save')

        if env_path.exists():
            self._install_comment(
                version,
                'Saving existing environment',
            )
            if env_path_saved.exists():
                shutil.rmtree(env_path_saved)
            shutil.move(env_path, env_path_saved)
        try:
            self._install_comment(
                version,
                'Creating environment',
            )
            yield VirtualEnvironment.make(env_path)
        except Exception as err:
            if env_path.exists():
                self._install_comment(
                    version, 'An error occurred. Removing partial environment.'
                )
                shutil.rmtree(env_path)
        
            if env_path_saved.exists():
                self._install_comment(
                    version, 'Restoring previously saved environment.'
                )
                shutil.move(env_path_saved, env_path)
            raise err
        else:
            if env_path_saved.exists():
                shutil.rmtree(env_path_saved, ignore_errors=True)

    @contextlib.contextmanager
    def make_compiler(self, version: String) -> 'Compiler':
        sources_backup_path: Path = self.ton_binaries_directory.with_suffix('.backup')
        if self.ton_binaries_directory.exists():
            self._install_comment(
                version,
                'Saving existing build',
            )
            if sources_backup_path.exists():
                shutil.rmtree(sources_backup_path)
            shutil.move(self.ton_binaries_directory, sources_backup_path)
        try:
            self._install_comment(
                version,
                'Preparing \'ton-blockchain\' sources to compilation process',
            )
            yield Compiler.make()
        except Exception as err:
            pass

    def install(self) -> Integer:
        self._write('Installing')
        return 1
