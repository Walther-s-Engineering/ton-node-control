#!/usr/bin/env python3
# Partially copied from https://github.com/python-poetry/install.python-poetry.org
from __future__ import annotations

import argparse
import contextlib
import functools
import getpass
import io
import json
import os
import pathlib
import platform
import shutil
import site
import subprocess
import sys
import re
import tempfile
import time
import typing as t
import tarfile
import urllib.request

from datetime import datetime

if sys.version_info < (3, 8):
    print(
        '\033[0;31mThis module cannot be used with a version of "Python" below 3.10.\n'
        f'You are using version {sys.version_info.major}.{sys.version_info.minor}\033[0m',
    )
    sys.exit(1)

# Typing
try:
    Bool: t.TypeAlias = bool
    Bytes: t.TypeAlias = bytes
    String: t.TypeAlias = str
    Integer: t.TypeAlias = int
    
    # Styling typing
    STYLE: t.Literal['info', 'comment', 'success', 'error', 'warning']
    COLOR: t.Literal['black', 'blue', 'cyan', 'green', 'magenta', 'red', 'white', 'yellow']
    OPTION: t.Literal['bold', 'underscore', 'blink', 'reverse', 'conceal']

except AttributeError:
    Bool = t.TypeVar('Bool', bound=bool)  # noqa: *, 811
    Bytes = t.TypeVar('Bytes', bound=bool)  # noqa: *, 811
    String = t.TypeVar('String', bound=str)  # noqa: *, 811
    Integer = t.TypeVar('Integer', bound=int)  # noqa: *, 811

# Installation required variables
SHELL: String = os.getenv('SHELL', '')
WINDOWS = sys.platform.startswith('win') or (sys.platform == 'cli' and os.name == 'nt')
MACOS = sys.platform == 'darwin'

TON_NODE_CONTROL_HOME = os.getenv('TON_NODE_CONTROL_HOME')
TON_BUILD_REQUIREMENTS = [
    'build-essential',
    'git',
    'make',
    'cmake',
    'clang',
    'libgflags-dev',
    'zlib1g-dev',
    'libssl-dev',
    'libreadline-dev',
    'libmicrohttpd-dev',
    'pkg-config',
    'libgsl-dev',
    'python3',
    'python3-dev',
    'python3-pip',
]

# Script utils
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


def write_styled_stdout(style: STYLE, line: String) -> None:
    sys.stdout.write(colorize(style, line) + '\n')


def is_decorated():
    if not hasattr(sys.stdout, 'fileno'):
        return False
    try:
        return os.isatty(sys.stdout.fileno())
    except io.UnsupportedOperation:
        return False


def colorize(style: STYLE, text: String) -> String:
    if not is_decorated():
        return text
    return f'{STYLES[style]}{text}\033[0m'


def string_to_bool(value: String) -> Bool:
    return value in {'true', '1', 'y', 'yes'}


# Messages
PRE_MESSAGE = """Welcome to {ton_node_control}!

This will download and install the latest version of {ton_node_control},
a tool to control/operate a TON validator node for Python.

It will add the `ton-node-control` command to {ton_node_control}'s binaries directory, located at:

{ton_node_control_home_bin}
You can uninstall at any time by executing this script with the `--uninstall` option,
and these changes will be reverted.
"""


# Path and system operations
def module_directory() -> pathlib.Path:
    if TON_NODE_CONTROL_HOME is not None:
        return pathlib.Path(TON_NODE_CONTROL_HOME).expanduser()
    
    if MACOS is True:
        path = os.path.expanduser('~/Library/Application Support/ton-node-control')
    else:
        path = os.getenv('XDG_DATA_HOME', os.path.expanduser('~/.local/share'))
        path = os.path.join(path, 'ton-node-control')
    return pathlib.Path(path)


def binary_directory() -> pathlib.Path:
    if TON_NODE_CONTROL_HOME is not None:
        return pathlib.Path(TON_NODE_CONTROL_HOME, 'bin').expanduser()
    user_base: String = site.getuserbase()
    bin_dir = os.path.join(user_base, 'bin')
    return pathlib.Path(bin_dir)


def ton_binary_directory() -> pathlib.Path:
    if TON_NODE_CONTROL_HOME is not None:
        return pathlib.Path(TON_NODE_CONTROL_HOME).expanduser()

    if MACOS is True:
        path = os.path.expanduser('~/Library/Application Support/ton-node-control')
    else:
        path = os.getenv('XDG_DATA_HOME', os.path.expanduser('~/.local/share'))
        path = os.path.join(path, 'ton-node-control')

    bin_dir = os.path.join(path, 'bin')
    return pathlib.Path(bin_dir)


def prompt_sudo_password() -> t.Optional[String]:
    if MACOS is True:
        dependencies = colorize('info', 'brew install ')
    else:
        dependencies = colorize('info', 'sudo apt-get install ')
    dependencies += ' '.join(TON_BUILD_REQUIREMENTS)
    if os.getuid() != 0:
        write_styled_stdout(
            'warning',
            'The installer is not running with superuser privileges.\n'
            'But during the installation process it will be necessary.\n'
            'You can enter your superuser password, '
            'or you can install the packages yourself.\n'
            f'Packages required for installation:',
        )
        sys.stdout.write('\t' + dependencies + '\n')
        use_installer: Bool = string_to_bool(input('Use installer?\n Answer: '))
        if use_installer is True:
            write_styled_stdout(
                'warning',
                'The installer will be used to install the required packages.'
            )
            password: String = getpass.getpass(' Type your password: ')
            return password
        return None
    return None


def prompt_package_installation() -> Bool:
    if MACOS is True:
        dependencies = colorize('info', 'brew install ')
    else:
        dependencies = colorize('info', 'sudo apt-get install ')
    dependencies += ' '.join(TON_BUILD_REQUIREMENTS)
    write_styled_stdout(
        'warning',
        'Make sure you have installed the required packages for the installation.'
    )
    return string_to_bool(input('Proceed?\n Answer: '))


# Installing instances
class TonNodeControlInstallationError(RuntimeError):
    def __init__(self, return_code: Integer = 0, log: t.Optional[String] = None) -> None:
        super().__init__()
        self.return_code: Integer = return_code
        self.log: t.Optional[String] = log


class Cursor:
    def __init__(self) -> None:
        self._output = sys.stdout

    def move_up(self, lines: int = 1) -> "Cursor":
        self._output.write(f"\x1b[{lines}A")

        return self

    def move_down(self, lines: int = 1) -> "Cursor":
        self._output.write(f"\x1b[{lines}B")

        return self

    def move_right(self, columns: int = 1) -> "Cursor":
        self._output.write(f"\x1b[{columns}C")

        return self

    def move_left(self, columns: int = 1) -> "Cursor":
        self._output.write(f"\x1b[{columns}D")

        return self

    def move_to_column(self, column: int) -> "Cursor":
        self._output.write(f"\x1b[{column}G")

        return self

    def move_to_position(self, column: int, row: int) -> "Cursor":
        self._output.write(f"\x1b[{row + 1};{column}H")

        return self

    def save_position(self) -> "Cursor":
        self._output.write("\x1b7")

        return self

    def restore_position(self) -> "Cursor":
        self._output.write("\x1b8")

        return self

    def hide(self) -> "Cursor":
        self._output.write("\x1b[?25l")

        return self

    def show(self) -> "Cursor":
        self._output.write("\x1b[?25h\x1b[?0c")

        return self

    def clear_line(self) -> "Cursor":
        """
        Clears all the output from the current line.
        """
        self._output.write("\x1b[2K")

        return self

    def clear_line_after(self) -> "Cursor":
        """
        Clears all the output from the current line after the current position.
        """
        self._output.write("\x1b[K")

        return self

    def clear_output(self) -> "Cursor":
        """
        Clears all the output from the cursors' current position
        to the end of the screen.
        """
        self._output.write("\x1b[0J")

        return self

    def clear_screen(self) -> "Cursor":
        """
        Clears the entire screen.
        """
        self._output.write("\x1b[2J")

        return self


class Builder:
    def __init__(self, path: pathlib.Path) -> None:
        self._path: pathlib.Path = path
        self._binaries_path: pathlib.Path = self._path.joinpath('bin')

    @property
    def path(self) -> pathlib.Path:
        return self._path

    @property
    def binaries_path(self) -> pathlib.Path:
        return self._binaries_path

    @classmethod
    def make(cls, target: pathlib.Path) -> Builder:
        raise NotImplementedError

    @staticmethod
    def run(*args: t.Any, **kwargs: t.Dict[String, t.Any]) -> subprocess.CompletedProcess:
        process = subprocess.run(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            **kwargs,
        )
        if process.returncode != 0:
            raise TonNodeControlInstallationError(
                log=process.stdout.decode(),
                return_code=process.returncode,
            )
        return process


class VirtualEnvironment(Builder):
    def __init__(self, path: pathlib.Path) -> None:
        super().__init__(path)
        self._python: String = str(self._path.joinpath(self._binaries_path, 'python'))
        self._git: String = str(self._path.joinpath(self._binaries_path, 'git'))
    
    @classmethod
    def make(cls, target: pathlib.Path) -> VirtualEnvironment:
        if sys.executable is None:
            raise ValueError(
                "Unable to determine sys.executable. "
                "Set PATH to a sane value or set it explicitly with PYTHONEXECUTABLE.",
            )
        try:
            # on some linux distributions (eg: debian), the distribution provided python
            # installation might not include ensurepip, causing the venv module to
            # fail when attempting to create a virtual environment
            # we import ensurepip but do not use it explicitly here
            import ensurepip  # noqa: F401
            import venv

            builder = venv.EnvBuilder(clear=True, with_pip=True, symlinks=False)
            builder.ensure_directories(target)
            builder.create(target)
        except ImportError:
            python_version = f'{sys.version_info.major}.{sys.version_info.minor}'
            virtual_env_bootstrap_url: String = (
                f"https://bootstrap.pypa.io/virtualenv/{python_version}/virtualenv.pyz"
            )
            with tempfile.TemporaryDirectory(prefix='tnc-installer') as temp_dir:
                virtualenv_pyz = pathlib.Path(temp_dir) / 'virtualenv.pyz'
                request = urllib.request.Request(
                    virtual_env_bootstrap_url,
                    headers={'User-Agent': 'ton-node-control'},
                )
                with contextlib.closing(urllib.request.urlopen(request)) as response:
                    virtualenv_pyz.write_bytes(response.read())
                cls.run(
                    sys.executable, virtualenv_pyz, '--clear', '--always-copy', target,
                )
        target.joinpath('tnc_env').touch()
        env: VirtualEnvironment = cls(target)

        env.pip('install', '--disable-pip-version-check', '--upgrade', 'pip')
        return env

    def python(self, *args, **kwargs) -> subprocess.CompletedProcess:
        return self.run(self._python, *args, **kwargs)

    def pip(self, *args, **kwargs) -> subprocess.CompletedProcess:
        return self.python('-m', 'pip', *args, **kwargs)


class Compiler(Builder):
    def __init__(self, path: pathlib.Path) -> None:
        super().__init__(path)
        self._path: pathlib.Path = path

    @classmethod
    def make(cls, target: pathlib.Path) -> Compiler:
        compiler: Compiler = cls(target)
        compiler.apt_update()
        for requirement in TON_BUILD_REQUIREMENTS:
            path: t.Optional[String] = shutil.which(requirement)
            if path is None:
                compiler.apt_get(requirement)
        os.environ.setdefault('CC', shutil.which('clang'))
        os.environ.setdefault('CXX', shutil.which('clang++'))
        os.environ.setdefault('CCACHE_DISABLE', '1')
        return compiler
    
    def apt_update(self, *args, **kwargs) -> subprocess.CompletedProcess:
        return self.run('apt-get', 'update', '-y', *args, **kwargs)

    def apt_get(self, *args, **kwargs) -> subprocess.CompletedProcess:
        return self.run('apt-get', 'install', '-y', *args, **kwargs)
    
    def cmake(self, *args, **kwargs) -> subprocess.CompletedProcess:
        return self.run(
            'cmake', '-DCMAKE_BUILD_TYPE=Release', '-B', self.path,
            *args, **kwargs,
        )

    def make_build(self, *args, **kwargs) -> subprocess.CompletedProcess:
        return self.run('make', '-j', os.cpu_count(), *args, **kwargs)


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
            )
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
            self.compile_ton_sources(truncated_version, compiler)
        time.sleep(5)

    def compile_ton_sources(self, version: String, compiler: Compiler) -> None:
        data: Bytes = self._get(self.TON_SOURCES_URL.format(version=version))
        with tempfile.TemporaryDirectory(prefix='ton-blockchain-installer') as temp_dir:
            tarball_path = pathlib.Path(temp_dir)
            archive_path: pathlib.Path = tarball_path.joinpath('sources.tar.gz')
            with open(archive_path, 'w+b') as file:
                file.write(data)
            self._install_comment(
                version,
                colorize(
                    'info',
                    f'Unpacking "ton-blockchain" sources to compile',
                ),
            )
            tarfile.open(file.name).extractall(tarball_path)
            os.remove(archive_path)
            sources_dir: String = os.listdir(tarball_path).pop()
            sources_path: pathlib.Path = tarball_path.joinpath(sources_dir)
            self._compile_ton(version, compiler, sources_path)

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
        compiler.cmake('-S', sources_path)

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
        # try:
        #     self.install(version)
        # except subprocess.CalledProcessError as err:
        #     raise TonNodeControlInstallationError(
        #         log=err.output.decode(),
        #         return_code=err.returncode,
        #     ) from err
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


def main() -> Integer:
    if WINDOWS is True:
        write_styled_stdout(
            'error',
            colorize('bold', 'Windows system is not supported yet.'),
        )
        return 1

    parser = argparse.ArgumentParser(
        description='Installs the latest (or given) version of "ton-node-control".',
    )
    parser.add_argument('--version', dest='version', help='install specific version.')
    parser.add_argument('--ton-version', dest='ton_version', help='install specific version.')
    parser.add_argument(
        '--git',
        action='store',
        dest='git',
        help='Install from a git repository instead of fetching the latest version '
             'of "ton-node-control" available online.'
    )
    parser.add_argument(
        '-y',
        '--yes',
        action='store_true',
        dest='accept_all',
        help='accept all prompts',
    )
    parser.add_argument(
        '-f',
        '--force',
        action='store_true',
        dest='force',
        default=False,
        help='install on top of existing version',
    )
    parser.add_argument(
        '--uninstall',
        action='store_true',
        dest='uninstall',
        default=False,
        help='uninstall ton-node-control',
    )
    args: argparse.Namespace = parser.parse_args()

    superuser_password: t.Optional[String] = prompt_sudo_password()
    proceed: Bool = prompt_package_installation()
    if proceed is False:
        write_styled_stdout(
            'info',
            'Installation process stopped.\n'
        )
        return 13

    write_styled_stdout('info', '\nStarting installation process.\n')
    installer = Installer(
        accept_all=args.accept_all,
        force=args.force,
        git=args.git,
        version=args.version,
        ton_version=args.ton_version,
        superuser_password=superuser_password,
    )
    if args.uninstall is True:
        return installer.uninstall()
    try:
        return installer.run()
    except TonNodeControlInstallationError as err:
        write_styled_stdout('error', 'Installation of "ton-node-control" is failed!')
        
        if err.log is not None:
            import traceback
            
            _, path = tempfile.mkstemp(
                suffix='.log',
                prefix='tnc-installer-error-',
                dir=str(pathlib.Path.cwd()),
                text=True,
            )
            write_styled_stdout('error', f'See "{path}" for error logs.')
            pathlib.Path(path).write_text(
                f'{err.log}\n'
                f'Traceback:\n\n{str().join(traceback.format_tb(err.__traceback__))}',
            )
            print(str().join(traceback.format_tb(err.__traceback__)))
        return err.return_code


if __name__ == '__main__':
    sys.exit(main())
