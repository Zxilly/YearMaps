from abc import ABC, abstractmethod
from typing import Dict, Any

from yearmaps.data import YearData


class ProviderInfo(ABC):
    """
    Component unit.
    """

    @abstractmethod
    @property
    def unit(self) -> str:
        pass

    """
    Provider name
    """

    @property
    @abstractmethod
    def name(self) -> str:
        pass


class ProviderWithoutSlot(ProviderInfo, ABC):
    """
    Get raw data from data source.
    """

    @abstractmethod
    def fetch(self) -> Any:
        pass

    """
    Parse raw data to standard format.
    """

    @abstractmethod
    def parse(self, raw: Any) -> Dict[int, YearData]:
        pass

    """
    Register command to click
    """

    @staticmethod
    @abstractmethod
    def command():
        pass


class Provider(ProviderWithoutSlot, ABC):

    @abstractmethod
    @property
    def provider(self) -> ProviderWithoutSlot:
        pass

    """
        Render data to output
    """

    def render(self):
        raw = self.fetch()
        data = self.parse(raw)
