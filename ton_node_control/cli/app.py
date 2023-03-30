import typing as t

import click

from pathlib import Path

from ton_node_control.tools.installer import Installer
from ton_node_control.tools.installer._cursor import Cursor
from ton_node_control.utils.typing import Integer

main = click.Group()
wallet_commands = click.Group()
cmds = click.CommandCollection(
    sources=[main, wallet_commands]
)

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


@wallet_commands.command
def test_wallet_command():
    pass
