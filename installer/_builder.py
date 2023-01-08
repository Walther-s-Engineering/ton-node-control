from __future__ import annotations

import platform
import shutil
import site
import sys
import typing as t

import os
import pathlib
import subprocess

from pathlib import Path

from _typing import Bytes, String
from _exceptions import TonNodeControlInstallationError

SHELL: String = os.getenv('SHELL', '')
TON_NODE_CONTROL_HOME = os.getenv('TON_NODE_CONTROL_HOME')

SOURCES_DIRECTORY = {
    'darwin': Path('/usr/local/src'),
    'linux': Path('/usr/src'),
}

BINARIES_DIRECTORY = {
    'darwin': Path('/usr/local/bin'),
    'linux': Path('/usr/bin'),
}

MODULE_DIRECTORY = {
    'darwin': '~/Library/Application Support',
    'linux': '~/.local/share',
}


def get_ton_node_control_home(*targets: t.Optional[String]) -> Path:
    if not targets:
        return Path(TON_NODE_CONTROL_HOME).expanduser()
    return Path(TON_NODE_CONTROL_HOME, *targets).expanduser()


def get_module_directory() -> Path:
    if TON_NODE_CONTROL_HOME is not None:
        return get_ton_node_control_home()
    path: Bytes = os.path.join(
        os.path.expanduser(MODULE_DIRECTORY[sys.platform]),
        'ton-node-control',
    )
    return Path(path)


def get_binary_directory() -> Path:
    if TON_NODE_CONTROL_HOME is not None:
        return get_ton_node_control_home('bin')
    user_base: String = site.getuserbase()
    binaries_directory = os.path.join(user_base, 'bin')
    return Path(binaries_directory)


def ton_binary_directory() -> Path:
    module_directory = get_ton_node_control_home()
    path = os.path.join(module_directory, 'bin')
    return Path(path)


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
        stdout_buffer = kwargs.pop('buffer', subprocess.PIPE)
        stderr_buffer = kwargs.pop('buffer', subprocess.STDOUT)
        process = subprocess.run(
            args,
            stdout=stdout_buffer,
            stderr=stderr_buffer,
            **kwargs,
        )

        if process.returncode != 0:
            raise TonNodeControlInstallationError(
                log=process.stdout.decode(),
                return_code=process.returncode,
            )
        return process


class Builder:
    def __init__(self, path: Path) -> None:
        self._path: Path = path
        self._binaries_path: Path = self._path.joinpath('bin')
