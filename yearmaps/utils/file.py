from pathlib import Path
from typing import Union

from yearmaps.utils.error import ProviderError


def ensure_dir(dir_: Union[Path, str]) -> Path:
    if isinstance(dir_, str):
        dir_ = Path(dir_)
    if not dir_.exists():
        if not dir_.parent.exists():
            raise FileExistsError(f"Parent directory of {dir_} does not exist")
        dir_.mkdir()
        return dir_
    if not dir_.is_dir():
        raise ProviderError("Default utils directory is not a directory")
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
