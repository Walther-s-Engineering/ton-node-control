from __future__ import annotations

import sys

if sys.version_info < (3, 8):
    print(
        '\033[0;31mThis module cannot be used with a version of "Python" below 3.8.\n'
        f'You are using version {sys.version_info.major}.{sys.version_info.minor}\033[0m',
    )
    sys.exit(1)

import typing as t

import argparse
import os
import io
import contextlib
import tempfile

from urllib.request import Request, urlopen


class InstallerMetadata(t.NamedTuple):
    link: str
    dependencies: t.List[str]
    

class Installers(t.NamedTuple):
    linux: InstallerMetadata
    darwin: InstallerMetadata


TEMPORARY_DIRECTORY = tempfile.TemporaryDirectory()
sys.path.append(TEMPORARY_DIRECTORY.name)

BASE_DEPENDENCIES = [
    'https://raw.githubusercontent.com/Walther-s-Engineering/ton-node-control/master/installer/base_installer.py',
    'https://raw.githubusercontent.com/Walther-s-Engineering/ton-node-control/master/installer/styling.py',
    'https://raw.githubusercontent.com/Walther-s-Engineering/ton-node-control/master/installer/typing.py',
]
INSTALLERS_BY_SYSTEM = Installers(
    linux=InstallerMetadata(
        link=('https://raw.githubusercontent.com/'
              'Walther-s-Engineering/ton-node-control/'
              'master/installer/linux_installer.py'),
        dependencies=BASE_DEPENDENCIES,
    ),
    darwin=InstallerMetadata(
        link=('https://raw.githubusercontent.com/'
              'Walther-s-Engineering/ton-node-control/'
              'master/installer/linux_installer.py'),
        dependencies=BASE_DEPENDENCIES,
    ),
)

INSTALLER_META_DATA: t.Optional[InstallerMetadata] = getattr(INSTALLERS_BY_SYSTEM, sys.platform, None)

if INSTALLER_META_DATA is None:
    print('Your operating system is not supported yet. Installation cannot be processed.')
    sys.exit(1)


def download_requirement(url: str) -> bytes:
    request = Request(url, headers={'User-Agent': 'ton-node-control'})
    with contextlib.closing(urlopen(request)) as response:
        return response.read()


def build_directory_and_module(dependency: str, dependency_code: bytes) -> str:
    installer_module_path: str = os.path.join(TEMPORARY_DIRECTORY.name, 'installer')
    with contextlib.suppress(FileExistsError):
        os.mkdir(installer_module_path)
    dependency_name: str = os.path.basename(dependency)
    with open(os.path.join(installer_module_path, dependency_name), 'w+b') as file:
        file.write(dependency_code)
    return os.path.basename(file.name).strip('.py')


for dependency_url in INSTALLER_META_DATA.dependencies:
    dependency_data = download_requirement(dependency_url)
    dependency_module = build_directory_and_module(dependency_url, dependency_data)

file_data: bytes = download_requirement(INSTALLER_META_DATA.link)
module_name: str = build_directory_and_module(INSTALLER_META_DATA.link, file_data)

module = getattr(__import__(f'installer.{module_name}'), module_name)

from installer.typing import Bool, String, Integer  # noqa: E402
from installer.typing import COLOR, OPTION, STYLE  # noqa: E402


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


def main() -> int:
    parser = argparse.ArgumentParser(
        description='Installs the latest (or given) version of "ton-node-control".',
    )
    parser.add_argument('--version', dest='version', help='install specific version.')
    parser.add_argument('--ton-version', dest='ton_version', help='install specific version.')
    arguments: argparse.Namespace = parser.parse_args()
    installer = module.Installer(
        version=arguments.version,
        ton_version=arguments.ton_version,
    )
    try:
        installer.install()
    except Exception as err:
        raise err
    return 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(0)
    finally:
        TEMPORARY_DIRECTORY.cleanup()
