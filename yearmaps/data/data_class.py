from abc import ABC, abstractmethod
from typing import List


class YearData:
    year: int
    data: List[int]

    def __init__(self, year: int, data: List[int]):
        self.year = year
        self.data = data
