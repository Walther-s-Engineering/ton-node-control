from abc import ABC


class ExternalSystemDataSource(ABC):
    client: None

    def __init__(self) -> None:
        client = None
