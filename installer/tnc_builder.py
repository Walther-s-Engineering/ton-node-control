from __future__ import annotations

import typing as t

import pathlib
import subprocess

from tnc_typing import String
from tnc_exceptions import TonNodeControlInstallationError


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
            **kwargs,
        )
        if process.returncode != 0:
            raise TonNodeControlInstallationError(
                log=process.stdout.decode(),
                return_code=process.returncode,
            )
        return process
