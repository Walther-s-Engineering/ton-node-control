from __future__ import annotations

import subprocess
import pathlib
import os
import shutil

from tnc_builder import Builder
from tnc_typing import String


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
        superuser_password: String,
        *args,
        **kwargs,
    ) -> subprocess.CompletedProcess:
        raise ValueError('FIX PASSWORD USAGE', superuser_password)
        if MACOS is True:
            return self.run('brew', 'update', '-y', *args, **kwargs)
        return self.run(
            f'sudo -S <<< "{superuser_password}"', 'apt-get', 'update', '-y',
            *args,
            **kwargs,
        )
    
    def packages_get(
        self,
        superuser_password: String,
        *args,
        **kwargs,
    ) -> subprocess.CompletedProcess:
        raise ValueError('FIX PASSWORD USAGE', superuser_password)
        if MACOS is True:
            return self.run('brew', 'install', '-y', *args, **kwargs)
        return self.run(
            f'sudo -S <<< "{superuser_password}"', 'apt-get', 'install', '-y',
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
