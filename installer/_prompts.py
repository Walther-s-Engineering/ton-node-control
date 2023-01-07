import argparse
import getpass
import typing as t
import os
import sys

from _path import MACOS
from _styling import colorize, string_to_bool, write_styled_stdout
from _typing import Bool, String
from _sources import TON_BUILD_REQUIREMENTS


def get_input(prompt: String) -> String:
    return input(prompt)


def prompt_use_installer(args: argparse.Namespace) -> t.Optional[String]:
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
        sys.stdout.write('>>>\t' + dependencies + '\n')
    if args.accept_all is True:
        return prompt_sudo_password()

    use_installer: Bool = string_to_bool(get_input('Use installer?\n Answer: '))
    if use_installer is True:
        write_styled_stdout(
            'warning',
            'The installer will be used to install the required packages.',
        )
        return prompt_sudo_password()


def prompt_sudo_password() -> t.Optional[String]:
    return getpass.getpass(' Type your password: ')


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
    return string_to_bool(get_input('Proceed?\n Answer: '))

