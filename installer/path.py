import typing as t
import pathlib
import os
import sys
import site

from tnc_typing import String

SHELL: String = os.getenv('SHELL', '')
WINDOWS = sys.platform.startswith('win') or (sys.platform == 'cli' and os.name == 'nt')
TON_NODE_CONTROL_HOME = os.getenv('TON_NODE_CONTROL_HOME')
MACOS = sys.platform == 'darwin'


def get_ton_node_control_home(*targets: t.Optional[String]) -> pathlib.Path:
    if not targets:
        return pathlib.Path(TON_NODE_CONTROL_HOME).expanduser()
    return pathlib.Path(TON_NODE_CONTROL_HOME, *targets).expanduser()


def module_directory() -> pathlib.Path:
    if TON_NODE_CONTROL_HOME is not None:
        return get_ton_node_control_home()
    
    if MACOS is True:
        path = os.path.expanduser('~/Library/Application Support/ton-node-control')
    else:
        path = os.getenv('XDG_DATA_HOME', os.path.expanduser('~/.local/share'))
        path = os.path.join(path, 'ton-node-control')
    return pathlib.Path(path)


def binary_directory() -> pathlib.Path:
    if TON_NODE_CONTROL_HOME is not None:
        return get_ton_node_control_home('bin')
    user_base: String = site.getuserbase()
    bin_dir = os.path.join(user_base, 'bin')
    return pathlib.Path(bin_dir)


def ton_binary_directory() -> pathlib.Path:
    if TON_NODE_CONTROL_HOME is not None:
        return get_ton_node_control_home()
    
    if MACOS is True:
        path = os.path.expanduser('~/Library/Application Support/ton-node-control')
    else:
        path = os.getenv('XDG_DATA_HOME', os.path.expanduser('~/.local/share'))
        path = os.path.join(path, 'ton-node-control')
    
    bin_dir = os.path.join(path, 'bin')
    return pathlib.Path(bin_dir)
