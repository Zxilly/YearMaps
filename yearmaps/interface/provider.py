from abc import ABC, abstractmethod
from typing import Dict, Any

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
    def read_cache(self):
        cache_file = self.options

        # Write cache

    def write_cache(self):
        pass

    # Get raw data from data source.
    @abstractmethod
    def fetch(self) -> Any:
        pass

    # Parse raw data to standard format.
    @abstractmethod
    def parse(self, raw: Any) -> Dict[int, YearData]:
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
        data = self.parse(raw)
        # TODO: render data to picture
