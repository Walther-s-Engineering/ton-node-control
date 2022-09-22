import toml

from typing import Any, AnyStr, Dict, Union
from pathlib import Path


PathLike = Union[str, Path]


def read_file(path: PathLike) -> AnyStr:
    with open(path, 'r') as file:
        return file.read()


def read_toml_file(path: PathLike) -> Dict[str, Any]:
    with open(path, 'r') as file:
        data: Dict[str, Any] = toml.load(file)
    return data
