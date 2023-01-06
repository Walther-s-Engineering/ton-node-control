#!/usr/bin/env python3
# Partially copied from https://github.com/python-poetry/install.python-poetry.org
from __future__ import annotations

import typing as t

import argparse
import contextlib
import os
import pathlib
import sys
import tempfile
import urllib.request


INSTALLER_REQUIREMENTS: t.List[str] = [
    'https://raw.githubusercontent.com/Walther-s-Engineering/ton-node-control/master/installer/tnc_typing.py',
    'https://raw.githubusercontent.com/Walther-s-Engineering/ton-node-control/master/installer/tnc_styling.py',
    'https://raw.githubusercontent.com/Walther-s-Engineering/ton-node-control/master/installer/tnc_path.py',
    'https://raw.githubusercontent.com/Walther-s-Engineering/ton-node-control/master/installer/tnc_sources.py',
    'https://raw.githubusercontent.com/Walther-s-Engineering/ton-node-control/master/installer/tnc_prompts.py',
    'https://raw.githubusercontent.com/Walther-s-Engineering/ton-node-control/master/installer/tnc_cursor.py',
    'https://raw.githubusercontent.com/Walther-s-Engineering/ton-node-control/master/installer/tnc_exceptions.py',
    'https://raw.githubusercontent.com/Walther-s-Engineering/ton-node-control/master/installer/tnc_compiler.py',
    'https://raw.githubusercontent.com/Walther-s-Engineering/ton-node-control/master/installer/tnc_builder.py',
    'https://raw.githubusercontent.com/Walther-s-Engineering/ton-node-control/master/installer/tnc_venv.py',
    'https://raw.githubusercontent.com/Walther-s-Engineering/ton-node-control/master/installer/tnc_installer.py',
]


def download_requirements(url: str) -> bytes:
    request = urllib.request.Request(url, headers={'User-Agent': 'ton-node-control'})
    with contextlib.closing(urllib.request.urlopen(request)) as response:
        return response.read()


def write_file(data: bytes, file: str) -> None:
    with open(f'./{file}', 'wb+') as file:
        file.write(data)


for requirement_file_url in INSTALLER_REQUIREMENTS:
    file_data: bytes = download_requirements(requirement_file_url)
    write_file(file_data, os.path.basename(requirement_file_url))


from tnc_installer import Installer  # noqa: E402
from tnc_exceptions import TonNodeControlInstallationError  # noqa: E402
from tnc_prompts import prompt_sudo_password, prompt_package_installation  # noqa: E402
from tnc_path import WINDOWS  # noqa: E402
from tnc_typing import Bool, String, Integer  # noqa: E402
from tnc_styling import write_styled_stdout, colorize  # noqa: E402


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
    parser.add_argument(
        '--use-installer',
        action='store_true',
        dest='use_installer',
        default=False,
        help=''
    )
    args: argparse.Namespace = parser.parse_args()

    superuser_password: t.Optional[String] = prompt_sudo_password()
    if superuser_password is None:
        write_styled_stdout(
            'error',
            'If you want to run installer without prompting super-user password '
            'run it with super-user privileges.',
        )
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
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        write_styled_stdout('info', '\nExited.')
        sys.exit(0)
