
class EnumHelper:
    @classmethod
    def choices(cls) -> list:
        return [str(entry.value) for entry in cls]  # noqa:
