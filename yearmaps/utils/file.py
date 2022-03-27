import tempfile
from pathlib import Path
from typing import Union

from yearmaps.utils.error import ProviderError


def ensure_dir(dir_: Union[Path, str]) -> str:
    if isinstance(dir_, str):
        dir_ = Path(dir_)
    if not dir_.exists():
        if not dir_.parent.exists():
            raise FileExistsError(f"Parent directory of {dir_.absolute().__str__()} does not exist")
        dir_.mkdir()
        return str(dir_)
    if not dir_.is_dir():
        raise ProviderError(f"{dir_.absolute().__str__()} is not a directory")
    return str(dir_)


def default_data_dir() -> Path:
    home = Path.home()
    if not home.exists():
        raise ProviderError("No home directory found")
    data_dir = home / ".yearmaps"
    return Path(ensure_dir(data_dir))


def default_cache_dir() -> Path:
    return Path(tempfile.gettempdir()) / "yearmaps-cache"
