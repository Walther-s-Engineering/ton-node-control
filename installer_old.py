from __future__ import annotations

import typing as t

import argparse
import contextlib
import urllib.request
import os
import io
import sys
import pathlib
import tempfile

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
    COLOR = t.TypeVar('COLOR', bound=str)
    OPTION = t.TypeVar('OPTION')
    Self = t.TypeVar('Self')


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


try:
    from _installer import Installer  # noqa: E402
    from _exceptions import TonNodeControlInstallationError  # noqa: E402
    from _prompts import prompt_package_installation, prompt_use_installer  # noqa: E402
    from _path import WINDOWS  # noqa: E402
except ImportError as err:
    print(err)
    def download_requirement(url: str) -> bytes:
        request = urllib.request.Request(url, headers={'User-Agent': 'ton-node-control'})
        with contextlib.closing(urllib.request.urlopen(request)) as response:
            return response.read()
    
    
    def write_file(data: bytes, file: str) -> None:
        with open(f'./{file}', 'w+b') as file:
            file.write(data)

    write_styled_stdout(
        'warning',
        'Not found required modules to process installation.\n'
        'Required modules will be downloaded.',
    )
    REQUIREMENTS_BEFORE_FULL_INSTALLATION: t.List[str] = [
        'https://raw.githubusercontent.com/Walther-s-Engineering/ton-node-control/master/installer/_typing.py',
    ]
    
    INSTALLER_REQUIREMENTS: t.List[str] = [
        'https://raw.githubusercontent.com/Walther-s-Engineering/ton-node-control/master/installer/_path.py',
        'https://raw.githubusercontent.com/Walther-s-Engineering/ton-node-control/master/installer/_sources.py',
        'https://raw.githubusercontent.com/Walther-s-Engineering/ton-node-control/master/installer/_prompts.py',
        'https://raw.githubusercontent.com/Walther-s-Engineering/ton-node-control/master/installer/_cursor.py',
        'https://raw.githubusercontent.com/Walther-s-Engineering/ton-node-control/master/installer/_exceptions.py',
        'https://raw.githubusercontent.com/Walther-s-Engineering/ton-node-control/master/installer/_compiler.py',
        'https://raw.githubusercontent.com/Walther-s-Engineering/ton-node-control/master/installer/_builder.py',
        'https://raw.githubusercontent.com/Walther-s-Engineering/ton-node-control/master/installer/_venv.py',
        'https://raw.githubusercontent.com/Walther-s-Engineering/ton-node-control/master/installer/_installer.py',
        'https://raw.githubusercontent.com/Walther-s-Engineering/ton-node-control/master/installer/_styling.py',
    ]
    pre_dependencies = enumerate(REQUIREMENTS_BEFORE_FULL_INSTALLATION, start=1)
    full_dependencies = enumerate(INSTALLER_REQUIREMENTS, start=1)
    for dependency_index, dependencies in enumerate([pre_dependencies, full_dependencies]):
        if dependency_index == 0:
            write_before = lambda: write_styled_stdout(  # noqa: E731
                'warning',
                'Preparing installation process. Downloading required dependencies.',
            )
            write_after = lambda: write_styled_stdout(  # noqa: E731
                'info',
                'Successfully downloaded base dependencies for installation process.\n',
            )
        else:
            write_before = lambda: write_styled_stdout(  # noqa: E731
                'warning',
                'Downloading installer dependencies for full installation.',
            )
            write_after = lambda: write_styled_stdout(  # noqa: E731
                'info',
                'Successfully downloaded full dependencies for installation process.'
            )
        write_before()
        for index, dependency_url in dependencies:
            file_name: str = os.path.basename(dependency_url)
            write_styled_stdout(
                'comment',
                f'\tDownloading dependency {index}): "{file_name.strip(".py").lstrip("_")}"',
            )
            data: bytes = download_requirement(dependency_url)
            write_file(data, file_name)
        write_after()
    os.execv(sys.executable, ['python'] + sys.argv)


def main() -> Integer:
    parser = argparse.ArgumentParser(
        description='Installs the latest (or given) version of "ton-node-control".',
    )
    parser.add_argument('--version', dest='version', help='install specific version.')
    parser.add_argument('--ton-version', dest='ton_version', help='install specific version.')
    # parser.add_argument(
    #     '--git',
    #     action='store',
    #     dest='git',
    #     help='Install from a git repository instead of fetching the latest version '
    #          'of "ton-node-control" available online.'
    # )
    # parser.add_argument(
    #     '-y',
    #     '--yes',
    #     action='store_true',
    #     dest='accept_all',
    #     help='accept all prompts',
    # )
    # parser.add_argument(
    #     '-f',
    #     '--force',
    #     action='store_true',
    #     dest='force',
    #     default=False,
    #     help='install on top of existing version',
    # )
    # parser.add_argument(
    #     '--uninstall',
    #     action='store_true',
    #     dest='uninstall',
    #     default=False,
    #     help='uninstall ton-node-control',
    # )
    # parser.add_argument(
    #     '--use-installer',
    #     action='store_true',
    #     dest='use_installer',
    #     default=False,
    #     help=''
    # )

    args: argparse.Namespace = parser.parse_args()
    # superuser_password: t.Optional[String] = prompt_use_installer(args)
    # if superuser_password is None:
    #     write_styled_stdout(
    #         'error',
    #         'If you want to run installer without prompting super-user password '
    #         'run it with super-user privileges.',
    #     )
    #     proceed: Bool = prompt_package_installation()
    #     if proceed is False:
    #         write_styled_stdout(
    #             'info',
    #             'Installation process stopped.\n'
    #         )
    #         return 13
    #
    # write_styled_stdout('info', '\nStarting installation process.\n')
    installer = Installer(
        version=args.version,
        ton_version=args.ton_version,
    )
    # if args.uninstall is True:
    #     return installer.uninstall()
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
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        write_styled_stdout('info', '\nExited.')
        sys.exit(0)
