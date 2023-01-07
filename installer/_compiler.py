from __future__ import annotations

import subprocess
import pathlib
import os

from _builder import Builder, set_build_env_variables, get_build_variables
from _path import MACOS


class Compiler(Builder):
    def __init__(self, path: pathlib.Path) -> None:
        super().__init__(path)
        self._path: pathlib.Path = path
    
    @classmethod
    def make(cls, target: pathlib.Path) -> Compiler:
        compiler: Compiler = cls(target)
        set_build_env_variables()
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
            return self.run('sudo', '-S', 'brew', 'install', '-y', *args, **kwargs)
        return self.run(
            'sudo', '-S', 'apt-get', 'install', '-y',
            *args,
            **kwargs,
        )
    
    def cmake(self, *args, **kwargs) -> subprocess.CompletedProcess:
        return self.run(
            'sudo', '-S', 'cmake', '-B', self.path, *get_build_variables(),
            *args,
            **kwargs,
        )
    
    def make_build(self, *args, **kwargs) -> subprocess.CompletedProcess:
        return self.run('ninja', '-j', os.cpu_count(), *args, **kwargs)

    def git(self, *args, **kwargs) -> subprocess.CompletedProcess:
        return self.run('git', *args, **kwargs)

    def git_clone(self, *args, **kwargs) -> subprocess.CompletedProcess:
        return self.git('clone', *args, **kwargs)

    def git_reset(self, *args, **kwargs) -> subprocess.CompletedProcess:
        return self.git('reset', '--hard', *args, **kwargs)
