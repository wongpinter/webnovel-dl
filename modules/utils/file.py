from pathlib import Path


def create_directory(path, with_filename=False):
    if with_filename:
        path = Path(path).parent

    Path(path).mkdir(parents=True, exist_ok=True)

    return path


def exists(path):
    return Path(path).exists()


def remove(path):
    if exists(path):
        Path(path).unlink()
