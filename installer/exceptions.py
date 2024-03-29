import typing as t

from installer.typing import String, Integer


class TonNodeControlInstallationError(RuntimeError):
    def __init__(self, return_code: Integer = 0, log: t.Optional[String] = None) -> None:
        super().__init__()
        self.return_code: Integer = return_code
        self.log: t.Optional[String] = log
