import datetime
import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, List

import click

from yearmaps.constant import config
from yearmaps.data import YearData


class ProviderInfo(ABC):

    # Component unit.
    @property
    @abstractmethod
    def unit(self) -> str:
        pass

    # Provider name
    @property
    def name(self) -> str:
        return self.id.upper()

    # Provider id
    @property
    @abstractmethod
    def id(self) -> str:
        pass

    # Global group options
    options: Dict[str, Any] = None


class ProviderInterface(ABC):
    # Get raw data from data source.
    @abstractmethod
    def access(self) -> Any:
        pass

    # Parse raw data to standard format.
    @abstractmethod
    def process(self, raw: Any) -> List[YearData]:
        pass

    # Register command to click
    @staticmethod
    @abstractmethod
    def command():
        pass


class Provider(ProviderInfo, ProviderInterface, ABC):

    # Read cache
    def read_data_file(self) -> Dict:
        data_file = Path(self.options[config.DATA_DIR]) / f"{self.id}.json"
        if not data_file.exists():
            return {}
        with open(data_file, "r", encoding='UTF-8') as f:
            data = json.load(f)
        return data

    # Write cache
    def write_data_file(self, cache: Any):
        cache_file = Path(self.options[config.DATA_DIR]) / f"{self.id}.json"
        with open(cache_file, "w", encoding='UTF-8') as f:
            json.dump(cache, f)

    # Judge a date should be rendered or not.
    def is_date_valid(self, date: datetime.date):
        return self.start_date() <= date <= self.end_date()

    # The start date under current mode
    def start_date(self):
        mode = self.options[config.MODE]
        if mode == 'year':
            return datetime.date(self.options[config.YEAR], 1, 1)
        else:
            return datetime.date.today() - datetime.timedelta(days=366)

    # The end date under current mode
    def end_date(self):
        mode = self.options[config.MODE]
        if mode == 'year':
            return datetime.date(self.options[config.YEAR], 12, 31)
        else:
            return datetime.date.today()

    # Render data to output
    def render(self, options: Dict[str, Any]):
        self.options = options
        click.echo("Start access data...")
        raw = self.access()
        click.echo("End access data.")
        click.echo("Start process data...")
        data = self.process(raw)
        # TODO: render data to picture
