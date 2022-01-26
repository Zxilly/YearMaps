from dataclasses import dataclass
from datetime import timedelta


@dataclass
class Configs:
    data_dir: str
    output_dir: str
    mode: str
    file_type: str
    year: int = None
    color: str = None
    server: bool = None


ONE_DAY = timedelta(days=1)
