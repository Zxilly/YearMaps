from pathlib import Path

from yearmaps.utils.error import ProviderError


def ensure_dir(dir_: Path) -> Path:
    if not dir_.exists():
        dir_.mkdir()
        return dir_
    else:
        if not dir_.is_dir():
            raise ProviderError("Default utils directory is not a directory")
        else:
            return dir_


def default_data_dir() -> Path:
    home = Path.home()
    if not home.exists():
        raise ProviderError("No home directory found")
    data_dir = home / ".yearmaps"
    return ensure_dir(data_dir)


def default_cache_dir() -> Path:
    data_dir = default_data_dir()
    cache_dir = data_dir / "cache"
    return ensure_dir(cache_dir)
