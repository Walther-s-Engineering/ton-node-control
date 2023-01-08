import typing as t

from _typing import Integer, String


class TonNodeControlInstallationError(RuntimeError):
    def __init__(self, return_code: Integer = 0, log: t.Optional[String] = None) -> None:
        super().__init__()
        self.return_code: Integer = return_code
        self.log: t.Optional[String] = log
