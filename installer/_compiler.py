from __future__ import annotations

import subprocess
import pathlib
import os
import shutil

from _builder import Builder
from _path import MACOS


class Compiler(Builder):
    def __init__(self, path: pathlib.Path) -> None:
        super().__init__(path)
        self._path: pathlib.Path = path
    
    @classmethod
    def make(cls, target: pathlib.Path) -> Compiler:
        compiler: Compiler = cls(target)
        os.environ.setdefault('CC', shutil.which('clang'))
        os.environ.setdefault('CXX', shutil.which('clang++'))
        os.environ.setdefault('CCACHE_DISABLE', '1')
        return compiler
    
    def packages_update(
        self,
        *args,
        **kwargs,
    ) -> subprocess.CompletedProcess:
        if MACOS is True:
            return self.run('sudo', '-S', 'brew', 'update', '-y', *args, **kwargs)
        return self.run(
            'sudo', '-S', 'apt-get', 'update', '-y',
            *args,
            **kwargs,
        )
    
    def packages_get(
        self,
        *args,
        **kwargs,
    ) -> subprocess.CompletedProcess:
        if MACOS is True:
            return self.run('sudo', '-S','brew', 'install', '-y', *args, **kwargs)
        return self.run(
            'sudo', '-S', 'apt-get', 'install', '-y',
            *args,
            **kwargs,
        )
    
    def cmake(self, *args, **kwargs) -> subprocess.CompletedProcess:
        return self.run(
            'cmake', '-DCMAKE_BUILD_TYPE=Release', '-B', self.path,
            *args, **kwargs,
        )
    
    def make_build(self, *args, **kwargs) -> subprocess.CompletedProcess:
        return self.run('make', '-j', os.cpu_count(), *args, **kwargs)
