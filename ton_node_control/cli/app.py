import typing as t

import click

from pathlib import Path

from ton_node_control.tools.installer import Installer
from ton_node_control.tools.installer._cursor import Cursor
from ton_node_control.utils.typing import Integer

main = click.Group()
wallet_commands = click.Group()
cursor = Cursor()


@main.command
def control() -> Integer:
    print('test')
    return 1


@main.command
def installer() -> Integer:
    _installer = Installer(cursor)
    _installer.install()
    return 1
