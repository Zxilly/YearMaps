from pathlib import Path


class ProviderError(Exception):
    pass


def ensure_default_data_dir() -> Path:
    home = Path.home()
    if not home.exists():
        raise ProviderError("No home directory found")
    data_dir = home / ".yearmaps"
    if not data_dir.exists():
        data_dir.mkdir()
        return data_dir
    else:
        if not data_dir.is_dir():
            raise ProviderError("Default data directory is not a directory")
        else:
            return data_dir


def ensure_cache_dir(data_dir: Path = ensure_default_data_dir()) -> Path:
    cache_dir = data_dir / "cache"
    if not cache_dir.exists():
        cache_dir.mkdir()
        return cache_dir
    else:
        if not cache_dir.is_dir():
            raise ProviderError("Cache directory is not a directory")
        else:
            return cache_dir
