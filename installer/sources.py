import site
import sys
import typing as t

import os

from pathlib import Path

from installer.typing import String

TON_NODE_CONTROL_HOME: Path = Path(os.getenv('TON_NODE_CONTROL_HOME'))

SOURCES_PATH: t.Dict[String, Path] = {
    'linux': Path('/usr/src'),
    # TODO: Improve this for MacOS
    'darwin': Path('/usr/src'),
}

BINARIES_PATH: t.Dict[String, Path] = {
    'linux': Path('/usr/bin'),
    # TODO: Improve this for MacOS
    'darwin': Path('/usr/bin'),
}

MODULE_PATH: t.Dict[String, Path] = {
    'linux': Path(site.getuserbase()).joinpath('share'),
    # TODO: Improve this for MacOS
    'darwin': Path('~/Library/Application Support'),
}


def get_ton_node_control_home(*targets: t.Optional[String]) -> Path:
    if not targets:
        return TON_NODE_CONTROL_HOME.expanduser()
    return Path(TON_NODE_CONTROL_HOME, *targets).expanduser()


def get_module_directory():
    if TON_NODE_CONTROL_HOME is not None:
        return get_ton_node_control_home()
    return MODULE_PATH[sys.platform].joinpath('ton-node-control')


def get_binaries_directory():
    if TON_NODE_CONTROL_HOME is not None:
        return get_ton_node_control_home('bin')
    return get_module_directory().joinpath('bin')


def get_ton_binaries_directory():
    if TON_NODE_CONTROL_HOME is not None:
        return get_ton_node_control_home()
    return get_module_directory().joinpath('bin')
