import getpass
import typing as t
import os
import sys

from tnc_path import MACOS
from tnc_styling import colorize, string_to_bool, write_styled_stdout
from tnc_typing import Bool, String
from tnc_sources import TON_BUILD_REQUIREMENTS


def get_input(prompt: String) -> String:
    return input(prompt)


def prompt_use_installer() -> t.Optional[String]:
    use_installer: Bool = string_to_bool(get_input('Use installer?\n Answer: '))
    if use_installer is True:
        write_styled_stdout(
            'warning',
            'The installer will be used to install the required packages.'
        )
        password: String = getpass.getpass(' Type your password: ')
        return password


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
        sys.stdout.write('>>>\t' + dependencies + '\n')
    use_installer: Bool = string_to_bool(get_input('Use installer?\n Answer: '))
    if use_installer is True:
        write_styled_stdout(
            'warning',
            'The installer will be used to install the required packages.'
        )
        password: String = getpass.getpass(' Type your password: ')
        return password
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
    return string_to_bool(get_input('Proceed?\n Answer: '))

