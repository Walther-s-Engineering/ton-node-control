from __future__ import annotations

import subprocess
from pathlib import Path

from installer.builder import Builder
from installer.sources import
# TODO: Complete arguments getter based on system with dict trick in source.py file

class Compiler(Builder):
    def __init__(self, path: Path) -> None:
        super().__init__(path)
        self._path: Path = path

    @classmethod
    def make(cls, target: Path) -> Compiler:
        compiler: Compiler = cls(target)
        return compiler

    def packages_update(
        self,
        *args,
        **kwargs,
    ) -> subprocess.CompletedProcess:
        return self.run()

    def packages_get(
        self,
        *args,
        **kwargs,
    ) -> subprocess.CompletedProcess:
        pass
    
    def cmake(
        self,
        *args,
        **kwargs,
    ) -> subprocess.CompletedProcess:
        pass
    
    def make_build(
        self,
        *args,
        **kwargs,
    ) -> subprocess.CompletedProcess:
        pass
    
    def git(
        self,
        *args,
        **kwargs,
    ) -> subprocess.CompletedProcess:
        pass
    
    def git_clone(
        self,
        *args,
        **kwargs,
    ) -> subprocess.CompletedProcess:
        pass
