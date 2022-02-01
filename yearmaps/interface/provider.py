import datetime
import json
from abc import ABC, abstractmethod
from contextlib import contextmanager
from pathlib import Path
from typing import Any, List, Callable, Union, Dict

import click
import numpy as np

from yearmaps.constant import Configs
from yearmaps.utils import YearData


class ProviderInfo(ABC):

    # Label formatter
    @staticmethod
    def label_format(value: Union[int, float]) -> str:
        return f"{value}"

    # Component unit.
    @property
    @abstractmethod
    def unit(self) -> Union[str, Callable]:
        pass

    @property
    def value_type(self) -> Callable:
        return int

    @staticmethod
    def analysis(data: np.ndarray):
        return np.nansum(data)

    # Provider name
    @property
    def name(self) -> str:
        return self.id.upper()

    # Provider id
    @property
    @abstractmethod
    def id(self) -> str:
        pass

    # Render color, should have 10 items
    @property
    @abstractmethod
    def color(self) -> List[str]:
        pass

    # Global group options
    options: Configs = None


class ProviderInterface(ABC):
    # Get raw utils from utils source.
    @abstractmethod
    def access(self) -> Any:
        pass

    # Parse raw utils to standard format.
    @abstractmethod
    def process(self, raw: Any) -> YearData:
        pass

    def init(self):
        pass

    # Register command to click
    @staticmethod
    @abstractmethod
    def command():
        pass


class ProviderUtils(ProviderInfo, ABC):
    # Read cache
    def __read_data_file(self) -> Dict:
        data_file = Path(self.options.data_dir) / f"{self.id}.json"
        if not data_file.exists():
            return {}
        with open(data_file, "r", encoding='UTF-8') as f:
            data = json.load(f)
        return data

    # Write cache
    def __write_data_file(self, cache: Any):
        cache_file = Path(self.options.data_dir) / f"{self.id}.json"
        with open(cache_file, "w", encoding='UTF-8') as f:
            json.dump(cache, f)

    @contextmanager
    def data_file(self):
        data = self.__read_data_file()
        yield data
        self.__write_data_file(data)

    # Judge a date should be rendered or not.
    def is_date_valid(self, date: datetime.date):
        return self.start_date() <= date <= self.end_date()

    # The start date under current mode
    def start_date(self):
        mode = self.options.mode
        if mode == 'year':
            return datetime.date(self.options.year, 1, 1)
        return datetime.date.today() - datetime.timedelta(days=366)

    # The end date under current mode
    def end_date(self):
        mode = self.options.mode
        if mode == 'year':
            return datetime.date(self.options.year, 12, 31)
        return datetime.date.today()

    def echo(self, msg: str):
        if not self.options.server:
            click.echo(msg)


def date_range(start_date: datetime.date, end_date: datetime.date):
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + datetime.timedelta(n)
