from __future__ import annotations

import contextlib
import subprocess
import sys
import tempfile

from pathlib import Path
from urllib.request import Request, urlopen

from installer.builder import Builder
from installer.typing import String


class VirtualEnvironment(Builder):
    def __init__(self, path: Path) -> None:
        super().__init__(path)
        self._python: String = str(self._path.joinpath(self._binaries_path, 'python'))
        self._git: String = str(self._path.joinpath(self._binaries_path, 'git'))

    @classmethod
    def make(cls, target: Path) -> VirtualEnvironment:
        if sys.executable is None:
            raise ValueError(
                'Unable to determine sys.executable. '
                'Set PATH to a sane value or set it explicitly with PYTHONEXECUTABLE.'
            )
        try:
            # on some linux distributions (eg: debian), the distribution provided python
            # installation might not include ensurepip, causing the venv module to
            # fail when attempting to create a virtual environment
            # we import ensurepip but do not use it explicitly here
            import ensurepip  # noqa: F401
            import venv
    
            builder = venv.EnvBuilder(clear=True, with_pip=True, symlinks=False)
            builder.ensure_directories(target)
            builder.create(target)
        except ImportError:
            python_version = f'{sys.version_info.major}.{sys.version_info.minor}'
            virtual_env_bootstrap_url: String = (
                f"https://bootstrap.pypa.io/virtualenv/{python_version}/virtualenv.pyz"
            )
            with tempfile.TemporaryDirectory(prefix='tnc-installer') as temp_dir:
                virtualenv_pyz = Path(temp_dir) / 'virtualenv.pyz'
                request = Request(
                    virtual_env_bootstrap_url,
                    headers={'User-Agent': 'ton-node-control'},
                )
                with contextlib.closing(urlopen(request)) as response:
                    virtualenv_pyz.write_bytes(response.read())
                cls.run(
                    sys.executable, virtualenv_pyz, '--clear', '--always-copy', target,
                )
        target.joinpath('ton_node_controller').touch()
        env: VirtualEnvironment = cls(target)
        env.pip('install', '--disable-pip-version-check', '--upgrade', 'pip')
        return env
    
    def python(self, *args, **kwargs) -> subprocess.CompletedProcess:
        return self.run(self._python, *args, **kwargs)
    
    def pip(self, *args, **kwargs) -> subprocess.CompletedProcess:
        return self.python('-m', 'pip', *args, **kwargs)
