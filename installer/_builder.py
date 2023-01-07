from __future__ import annotations

import platform
import shutil
import typing as t

import os
import pathlib
import subprocess

from _path import MACOS
from _typing import String
from _exceptions import TonNodeControlInstallationError


CLANG_PATH = shutil.which('clang')
CLANG_XX_PATH = shutil.which('clang++')
ENV_CCACHE_DISABLE = '1'

ENV_MACOS_CPU = '-mcpu=apple-a14'
ENV_MACOS_CC = f'{CLANG_PATH} {ENV_MACOS_CPU}'
ENV_MACOS_CXX = f'{CLANG_XX_PATH} {ENV_MACOS_CPU}'


def set_build_env_variables() -> None:
    if MACOS is True:
        os.environ.setdefault('CC', ENV_MACOS_CC)
        os.environ.setdefault('CXX', ENV_MACOS_CXX)
        os.environ.setdefault('CCACHE_DISABLE', ENV_CCACHE_DISABLE)
        os.environ.setdefault('CMAKE_C_COMPILER', CLANG_PATH)
        os.environ.setdefault('CMAKE_CXX_COMPILE', CLANG_XX_PATH)
    else:
        os.environ.setdefault('CC', ENV_MACOS_CC)
        os.environ.setdefault('CXX', ENV_MACOS_CXX)
        os.environ.setdefault('CCACHE_DISABLE', ENV_CCACHE_DISABLE)


def get_build_variables() -> t.List[str]:
    architecture: str = platform.machine()
    default_arguments = ['-DCMAKE_BUILD_TYPE=Release', '-GNinja']
    if 'arm' == architecture:
        return ['-DTON_ARCH=', '-Wno-dev', *default_arguments]
    else:
        return [*default_arguments]


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
        process = subprocess.run(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
            **kwargs,
        )
        for line in iter(process.stdout.readline, 'b'):
            print(line)

        if process.returncode != 0:
            raise TonNodeControlInstallationError(
                log=process.stdout.decode(),
                return_code=process.returncode,
            )
        return process
