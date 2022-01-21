from datetime import timedelta
from enum import Enum, unique


@unique
class Config(Enum):
    DATA_DIR = "data_dir"
    OUTPUT_DIR = "output_dir"
    MODE = "mode"
    YEAR = "year"
    FILE_TYPE = "file_type"


ONE_DAY = timedelta(days=1)
