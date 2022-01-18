import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any

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


class Provider(ProviderInfo, ABC):

    # Read cache
    def read_data(self) -> Any:
        data_file = Path(self.options[config.DATA_DIR]) / f"{self.name}.json"
        if not data_file.exists():
            return {}
        with open(data_file, "r", encoding='UTF-8') as f:
            data = json.load(f)
        return data

    # Write cache
    def write_data(self, cache: Any):
        cache_file = Path(self.options[config.DATA_DIR]) / f"{self.name}.json"
        with open(cache_file, "w", encoding='UTF-8') as f:
            json.dump(cache, f)

    # Get raw data from data source.
    @abstractmethod
    def fetch(self) -> Any:
        pass

    # Parse raw data to standard format.
    @abstractmethod
    def process(self, raw: Any) -> Dict[int, YearData]:
        pass

    # Register command to click
    @staticmethod
    @abstractmethod
    def command():
        pass

    # Render data to output
    def render(self, options: Dict[str, Any]):
        self.options = options
        raw = self.fetch()
        data = self.process(raw)
        # TODO: render data to picture
