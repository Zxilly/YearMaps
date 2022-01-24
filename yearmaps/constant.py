from datetime import timedelta
from enum import Enum, unique


@unique
class Config(Enum):
    DATA_DIR = "data_dir"  # necessary
    OUTPUT_DIR = "output_dir"  # necessary
    MODE = "mode"  # necessary
    YEAR = "year"  # optional
    FILE_TYPE = "file_type"  # necessary
    COLOR = "color"  # optional

    SERVER = "server"  # optional


ONE_DAY = timedelta(days=1)
