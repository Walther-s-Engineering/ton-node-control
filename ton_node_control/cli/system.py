import os


def get_cpu_count() -> int:
    return os.cpu_count()
