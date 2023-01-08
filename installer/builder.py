from __future__ import annotations

import typing as t

import subprocess

from pathlib import Path

from installer.exceptions import TonNodeControlInstallationError
from installer.typing import String


class Builder:
    def __init__(self, path: Path) -> None:
        self._path: Path = path
        self._binaries_path: Path = self._path.joinpath('bin')
    
    @property
    def path(self) -> Path:
        return self._path
    
    @property
    def binaries_path(self) -> Path:
        return self._binaries_path

    @classmethod
    def make(cls, target: Path) -> Builder:
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
