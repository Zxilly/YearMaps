from enum import Enum, unique


@unique
class Config(Enum):
    DATA_DIR = "data_dir"
    OUTPUT_DIR = "output_dir"
