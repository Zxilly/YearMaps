from pathlib import Path


class ProviderError(Exception):
    pass


def default_data_dir() -> Path:
    home = Path.home()
    if not home.exists():
        raise ProviderError("No home directory found")
    data_dir = home / ".yearmaps"
    return ensure_dir(data_dir)


def cache_dir(data_dir: Path = default_data_dir()) -> Path:
    cache_dir = data_dir / "cache"
    return ensure_dir(cache_dir)


def ensure_dir(dir_: Path) -> Path:
    if not dir_.exists():
        dir_.mkdir()
        return dir_
    else:
        if not dir_.is_dir():
            raise ProviderError("Default data directory is not a directory")
        else:
            return dir_
