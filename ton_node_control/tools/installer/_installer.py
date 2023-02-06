import typing as t

from pathlib import Path

from ._base_installer import BaseInstaller


class Installer(BaseInstaller):
    def ensure_directories(self) -> None:
        self.module_directory.mkdir(parents=True, exist_ok=True)
        self.binaries_directory.mkdir(parents=True, exist_ok=True)
        self.ton_binaries_directory.mkdir(parents=True, exist_ok=True)

    def install(self) -> None:
        directories_to_ensure: t.List[Path] = [
            self.module_directory,
            self.ton_binaries_directory,
            self.binaries_directory,
        ]
        for directory in directories_to_ensure:
            if directory.exists() is True:
                self.install_comment(f'directory "{directory}" is found!')
            else:
                self.install_comment(f'directory "{directory}" is not found!')
            self.cursor.write('')
        self.install_comment('creating missing directories')
        self.ensure_directories()
        self.install_comment('missing directories successfully created')
