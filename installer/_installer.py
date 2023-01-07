import typing as t

import contextlib
import re
import pathlib
import sys
import urllib.request
import json
import functools
import shutil
import subprocess
import time
import tempfile
import tarfile
import os

from datetime import datetime

from _compiler import Compiler
from _cursor import Cursor
from _typing import Bool, Bytes, String, Integer
from _path import module_directory, binary_directory, ton_binary_directory
from _styling import colorize, is_decorated, write_styled_stdout
from _venv import VirtualEnvironment
from _sources import TON_BUILD_REQUIREMENTS
from _exceptions import TonNodeControlInstallationError

PRE_MESSAGE = """Welcome to {ton_node_control}!

This will download and install the latest version of {ton_node_control},
a tool to control/operate a TON validator node for Python.

It will add the `ton-node-control` command to {ton_node_control}'s binaries directory, located at:

{ton_node_control_home_bin}
You can uninstall at any time by executing this script with the `--uninstall` option,
and these changes will be reverted.
"""


class Installer:
    MEDATA_URL: String = 'https://pypi.org/pypi/ton-node-control/json'
    TON_MEDATA_URL: String = 'https://api.github.com/repos/ton-blockchain/ton/commits'
    TON_SOURCES_URL: String = 'https://api.github.com/repos/ton-blockchain/ton/tarball/{version}'
    VERSION_REGEX = re.compile(
        r"v?(\d+)(?:\.(\d+))?(?:\.(\d+))?(?:\.(\d+))?"
        "("
        "[._-]?"
        r"(?:(stable|beta|b|rc|RC|alpha|a|patch|pl|p)((?:[.-]?\d+)*)?)?"
        "([.-]?dev)?"
        ")?"
        r"(?:\+[^\s]+)?"
    )
    COMMIT_REGEX = re.compile(r'[0-9a-fA-F]{40}')
    
    def __init__(
        self,
        force: Bool = False,
        accept_all: Bool = False,
        git: t.Optional[String] = None,
        version: t.Optional[String] = None,
        ton_version: t.Optional[String] = None,
        superuser_password: t.Optional[String] = None,
        preview: Bool = False,
    ) -> None:
        self._force: Bool = force
        self._accept_all: Bool = accept_all
        self._git: t.Optional[String] = git
        self._version: t.Optional[String] = version
        self._ton_version: t.Optional[String] = ton_version
        self._preview: Bool = preview
        self._superuser_password: t.Optional[String] = superuser_password
        
        self._cursor = Cursor()
        self._module_dir: pathlib.Path = module_directory()
        self._binaries_dir: pathlib.Path = binary_directory()
        self._ton_binaries_dir: pathlib.Path = ton_binary_directory()
        self._meta_data: t.Dict[t.Any, t.Any] = {}
        self._ton_meta_data: t.Dict[t.Any, t.Any] = {}
    
    @property
    def binaries_dir(self) -> pathlib.Path:
        if self._binaries_dir is None:
            self._binaries_dir: pathlib.Path = binary_directory()
        return self._binaries_dir
    
    @property
    def module_dir(self) -> pathlib.Path:
        if self._module_dir is None:
            self._module_dir: pathlib.Path = module_directory()
        return self._module_dir
    
    @property
    def ton_binaries_dir(self) -> pathlib.Path:
        if self._ton_binaries_dir is None:
            self._ton_binaries_dir: pathlib.Path = ton_binary_directory()
        return self._ton_binaries_dir
    
    @property
    def version_file(self) -> pathlib.Path:
        return self.module_dir.joinpath('VERSION')
    
    @property
    def ton_version_file(self) -> pathlib.Path:
        return self._ton_binaries_dir.joinpath('VERSION')
    
    @property
    def ton_version(self) -> t.Optional[String]:
        if self._ton_version is None:
            return None
        return self._ton_version[:6]
    
    def _get(self, url: String) -> Bytes:
        request = urllib.request.Request(url, headers={'User-Agent': 'ton-node-control'})
        with contextlib.closing(urllib.request.urlopen(request)) as response:
            return response.read()
    
    def _write(self, line: String) -> None:
        sys.stdout.write(line + '\n')
    
    def _overwrite(self, line) -> None:
        if not is_decorated():
            return self._write(line)
        
        self._cursor.move_up()
        self._cursor.clear_line()
        self._write(line)
    
    def _install_comment(self, version: str, message: str):
        self._overwrite(
            'Installing {} ({}): {}'.format(
                colorize('info', '"ton-node-control"'),
                colorize('bold', version),
                colorize('comment', message),
            ),
        )
    
    def allow_pre_releases(self) -> Bool:
        return self._preview
    
    def ensure_directories(self) -> None:
        self.module_dir.mkdir(parents=True, exist_ok=True)
        self.binaries_dir.mkdir(parents=True, exist_ok=True)
        self.ton_binaries_dir.mkdir(parents=True, exist_ok=True)
    
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
        self._meta_data = json.loads(self._get(self.MEDATA_URL).decode())
        
        def _compare_versions(current: String, lookup: String) -> Integer:
            version_current: re.Match = self.VERSION_REGEX.match(current)
            version_lookup: re.Match = self.VERSION_REGEX.match(lookup)
            version_current: tuple = tuple(
                int(p)
                for p in version_current.groups()[:3] + (version_current.group(5),)
            )
            version_lookup: tuple = tuple(
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
            self._meta_data['releases'].keys(),
            key=functools.cmp_to_key(_compare_versions),
        )
        if self._version is not None and self._version not in releases:
            message = colorize('error', f'Version {self._version} does not exist.')
            self._write(message)
            raise ValueError(message)
        
        version = self._version
        if version is None:
            for release in reversed(releases):
                match = self.VERSION_REGEX.match(release)
                if match.group(5) and self.allow_pre_releases() is False:
                    continue
                version = release
                break
        if current_version == version and self._force is False:
            self._write(
                f'The latest version ({colorize("bold", version)}) is already installed.',
            )
            return None, current_version
        return version, current_version
    
    def get_ton_meta_data(self) -> t.Tuple[t.Optional[String], t.Optional[String]]:
        try:
            date: t.Optional[String] = None
            current_version: t.Optional[String] = None
            if self.ton_version_file.exists():
                current_version, date = self.ton_version_file.read_text().strip().split(':')
                date: datetime = datetime.fromisoformat(date)
            self._write(
                colorize(
                    'info',
                    'Retrieving "ton-blockchain" meta-data',
                ),
            )
            self._ton_meta_data = dict(
                versions=json.loads(self._get(self.TON_MEDATA_URL).decode()),
            )
            self._write('')
            releases: t.List[t.Dict[String, t.Any]] = [
                version for version in reversed(self._ton_meta_data['versions'])
            ]
            commits: t.List[String] = [_version['sha'] for _version in releases]
            if self._ton_version is not None and self._ton_version not in commits:
                message = colorize('error', f'Version {self._ton_version} does not exist.')
                self._write(message)
                raise ValueError(message)
            
            if date is None and current_version is None:
                self._write(
                    colorize(
                        'warning',
                        'No installed versions of "ton-blockchain" '
                        'was found, will use latest.',
                    ),
                )
                version = commits.pop()
                return version, current_version
            version = self._ton_version
            if version is None:
                version = commits.pop()
            # FIXME: Fix this code block
            raise NotImplementedError('FIXME')
        except Exception as err:
            import traceback
            traceback.print_exc()
            print(err)
    
    @contextlib.contextmanager
    def make_environment(self, version: String) -> VirtualEnvironment:
        env_path: pathlib.Path = self.module_dir.joinpath('venv')
        env_path_saved: pathlib.Path = env_path.with_suffix('.save')
        
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
    
    def make_binary(self, version: String, env: VirtualEnvironment) -> None:
        self._install_comment(version, 'Creating executable')
        self.binaries_dir.mkdir(parents=True, exist_ok=True)
        
        script = 'ton-node-control'
        target_script = env.binaries_path.joinpath(script)
        if self.binaries_dir.joinpath(script).exists():
            self.binaries_dir.joinpath(script).unlink()
        symlink = self.binaries_dir.joinpath(script)
        try:
            symlink.symlink_to(target_script)
        except FileExistsError:
            symlink.unlink(missing_ok=True)
            self.make_binary(version, env)
    
    @contextlib.contextmanager
    def make_compiler(self, version: String) -> Compiler:
        sources_backup_path: pathlib.Path = self.ton_binaries_dir.with_suffix('.backup')
        if self.ton_binaries_dir.exists():
            self._install_comment(
                version,
                'Saving existing build',
            )
            if sources_backup_path.exists():
                shutil.rmtree(sources_backup_path)
            shutil.move(self.ton_binaries_dir, sources_backup_path)
        try:
            self._install_comment(
                version,
                'Preparing "ton-blockchain" sources to compilation',
            )
            yield Compiler.make(self.ton_binaries_dir)
        except Exception as err:
            if self.ton_binaries_dir.exists():
                self._install_comment(
                    version,
                    'An error occurred. Removing build directories',
                )
                shutil.rmtree(self.ton_binaries_dir)
            
            if sources_backup_path.exists():
                self._install_comment(
                    version,
                    'Restoring previously saved build',
                )
                shutil.move(sources_backup_path, self.ton_binaries_dir)
            raise err
        else:
            if sources_backup_path.exists():
                shutil.rmtree(sources_backup_path, ignore_errors=True)
    
    def install_ton_node_control(self, version: String, env: VirtualEnvironment) -> None:
        self._install_comment(version, 'Installing "ton-node-control"')
        if self._git is not None:
            specification = f'git+{version}'
        else:
            specification = f'ton-node-control=={version}'
        env.pip('install', specification)
    
    def install_ton(self, version: String) -> None:
        truncated_version = version[:6]
        self._install_comment(
            truncated_version,
            colorize(
                'info',
                f'Cloning "ton-blockchain" sources',
            ),
        )
        with self.make_compiler(truncated_version) as compiler:
            if self._superuser_password is not None:
                compiler.packages_update(input=self._superuser_password.encode())
                for requirement in TON_BUILD_REQUIREMENTS:
                    self._install_comment(
                        truncated_version,
                        colorize(
                            'info',
                            f'Installing ton-blockchain dependency "{requirement}"',
                        ),
                    )
                    compiler.packages_get(requirement, input=self._superuser_password.encode())
            self.compile_ton_sources(truncated_version, compiler)
        time.sleep(5)
    
    def compile_ton_sources(self, version: String, compiler: Compiler) -> None:
        with tempfile.TemporaryDirectory(prefix='ton-blockchain-installer') as temp_dir:
            self._install_comment(
                version,
                colorize('info', f'Cloning ton-blockchain source code'),
            )
            compiler.git_clone('git@github.com:ton-blockchain/ton.git', '--recursive', temp_dir)
            compiler.git_reset(version)
            self._compile_ton(version, compiler, temp_dir)
    
    def _compile_ton(
        self,
        version: String,
        compiler: Compiler,
        sources_path: pathlib.Path,
    ) -> None:
        self._install_comment(
            version,
            'Running cmake',
        )
        compiler.cmake(sources_path)
        compiler.make_build(
            'dht-server',
            'fift',
            'func',
            'lite-client',
            'validator-engine',
            'validator-engine-console',
            'generate-random-id',
            'tonlibjson',
            'rldp-http-proxy',
        )

    def _install_fift(self) -> None:
        pass
    
    def run(self) -> Integer:
        if self._git is True:
            version = self._git
        else:
            try:
                version, current_version = self.get_package_meta_data()
            except ValueError:
                return 1
        if version is None:
            return 0
        try:
            ton_version, ton_current_version = self.get_ton_meta_data()
        except Exception:
            return 1
        if ton_version is None:
            return 0
        self._write(
            PRE_MESSAGE.format(
                ton_node_control=colorize('info', 'ton-node-control'),
                ton_node_control_home_bin=colorize('comment', str(self.binaries_dir)),
            ),
        )
        self.ensure_directories()
        try:
            self.install(version)
        except subprocess.CalledProcessError as err:
            raise TonNodeControlInstallationError(
                log=err.output.decode(),
                return_code=err.returncode,
            ) from err
        try:
            self.install_ton(ton_version)
        except subprocess.CalledProcessError as err:
            raise TonNodeControlInstallationError(
                log=err.output.decode(),
                return_code=err.returncode,
            ) from err
        self._write('')
        self._write(
            colorize(
                'success',
                f'Successfully installed {colorize("bold", "ton-node-control")} '
                f'({colorize("bold", version)})',
            ),
        )
        return 0
    
    def install(self, version: String) -> Integer:
        """
        Installs "ton-node-control" in $TON_NODE_CONTROL_HOME.
        """
        self._write(
            colorize(
                'comment',
                f'Installing {colorize("info", "ton-node-control")} '
                f'({colorize("info", version)})',
            ),
        )
        with self.make_environment(version) as env:
            self.install_ton_node_control(version, env)
            self.make_binary(version, env)
            self.version_file.write_text(version)
            self._install_comment(version, 'Done')
            return 0
    
    def uninstall(self) -> Integer:
        if not self._module_dir.exists():
            write_styled_stdout('warning', '"ton-node-control" is not currently installed.')
            return 1
        
        version = None
        if self._module_dir.joinpath('VERSION').exists():
            version = self._module_dir.joinpath('VERSION').read_text().strip()
        
        if version is not None:
            write_styled_stdout(
                'info',
                'Removing "ton-node-control" ({version})'.format(
                    version=colorize('b', version),
                ),
            )
        else:
            write_styled_stdout('info', 'Removing "ton-node-control"')
        shutil.rmtree(str(self._module_dir))
        
        return 0
