import calendar
import datetime
import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, List, Callable

import click
import matplotlib as mpl
import matplotlib.axes
import matplotlib.colors
import matplotlib.figure
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.ticker import ScalarFormatter
from matplotlib.transforms import Bbox

from yearmaps import utils
from yearmaps.constant import Config, ONE_DAY
from yearmaps.utils import YearData
from yearmaps.utils.colors import PolarisationColorMap
from yearmaps.utils.util import date_range


class ProviderInfo(ABC):

    # Component unit.
    @property
    @abstractmethod
    def unit(self) -> str:
        pass

    @property
    def dtype(self) -> Callable:
        return int

    # Provider name
    @property
    def name(self) -> str:
        return self.id.upper()

    # Provider id
    @property
    @abstractmethod
    def id(self) -> str:
        pass

    # Render colors, should have 10 items
    @property
    @abstractmethod
    def colors(self) -> List[str]:
        pass

    # Global group options
    options: Dict[str, Any] = None


class ProviderInterface(ABC):
    # Get raw utils from utils source.
    @abstractmethod
    def access(self) -> Any:
        pass

    # Parse raw utils to standard format.
    @abstractmethod
    def process(self, raw: Any) -> YearData:
        pass

    # Register command to click
    @staticmethod
    @abstractmethod
    def command():
        pass


class Provider(ProviderInfo, ProviderInterface, ABC):

    # Read cache
    def read_data_file(self) -> Dict:
        data_file = Path(self.options[Config.DATA_DIR]) / f"{self.id}.json"
        if not data_file.exists():
            return {}
        with open(data_file, "r", encoding='UTF-8') as f:
            data = json.load(f)
        return data

    # Write cache
    def write_data_file(self, cache: Any):
        cache_file = Path(self.options[Config.DATA_DIR]) / f"{self.id}.json"
        with open(cache_file, "w", encoding='UTF-8') as f:
            json.dump(cache, f)

    # Judge a date should be rendered or not.
    def is_date_valid(self, date: datetime.date):
        return self.start_date() <= date <= self.end_date()

    # The start date under current mode
    def start_date(self):
        mode = self.options[Config.MODE]
        if mode == 'year':
            return datetime.date(self.options[Config.YEAR], 1, 1)
        else:
            return datetime.date.today() - datetime.timedelta(days=366)

    # The end date under current mode
    def end_date(self):
        mode = self.options[Config.MODE]
        if mode == 'year':
            return datetime.date(self.options[Config.YEAR], 12, 31)
        else:
            return datetime.date.today()

    # Render utils to output
    def render(self, options: Dict[str, Any]):
        self.options = options
        click.echo(f"Start access {self.name} data...")
        raw = self.access()
        click.echo("End access data.")
        click.echo(f"Start process {self.name} data...")
        data = self.process(raw)
        click.echo("End process data.")

        def fulfill_data() -> np:
            start = self.start_date()
            end = self.end_date()
            graph_start = start
            graph_end = end

            while graph_start.weekday() != 0:
                graph_start -= ONE_DAY
            while graph_end.weekday() != 6:
                graph_end += ONE_DAY

            days = (graph_end - graph_start).days
            weeks = days // 7
            if weeks * 7 < days:
                weeks += 1

            empty_grid = np.empty((7, weeks), dtype="float64")
            empty_grid = np.nan * empty_grid

            def get_day(i_: datetime.date) -> int:
                return i_.weekday()

            def get_week(i_: datetime.date) -> int:
                return (i_ - graph_start).days // 7

            for date, value in data.items():
                if date < start:
                    continue
                if date > end:
                    continue

                empty_grid[get_day(date)][get_week(date)] = value

            month_list = np.linspace(-1, -1, weeks, dtype=int)
            year_tuple = (0, 0)
            current_year = None
            for date in date_range(start, end):
                date: datetime.date
                if np.isnan(empty_grid[get_day(date)][get_week(date)]):
                    empty_grid[get_day(date)][get_week(date)] = 0
                if date.weekday() == 0:
                    month_list[get_week(date)] = date.month
                if date.weekday() == 6:
                    if current_year is None:
                        current_year = date.year
                    elif current_year != date.year:
                        year_tuple = (date.year, get_week(date))
            return empty_grid, month_list, year_tuple

        grid, months, (year, year_loc) = fulfill_data()

        mpl.rcParams['font.family'] = 'Consolas'
        mpl.rcParams['svg.fonttype'] = 'none'

        grid_max = np.nanmax(grid)
        grid_sum = np.nansum(grid)

        c_map = PolarisationColorMap(self.colors, grid_max == 0)

        fig_size = (10, 3)
        fig, ax = plt.subplots(figsize=fig_size, dpi=400)
        fig: matplotlib.figure.Figure
        ax: matplotlib.axes.Axes

        pc = ax.pcolormesh(grid, edgecolors=ax.get_facecolor(), linewidth=1, cmap=c_map)
        pc.set_clim(0, grid_max)
        ax.invert_yaxis()
        ax.set_aspect("equal")

        # add weekdays label
        ax.tick_params(axis="y", which="major", pad=1, width=0, colors='#24292f')

        ax.set_yticks([x + 0.5 for x in range(1, 6, 2)])
        ax.set_yticklabels(
            ['Tue', 'Thu', 'Sat'],
        )

        # add months label
        current_month = -1
        month_locs = []
        month_labels = []
        for i, month in enumerate(months):
            if month != current_month:
                month_locs.append(i + 0.5)
                month_labels.append(calendar.month_abbr[int(month)])
                current_month = month

        # trick to remove too close labels
        if month_locs[1] - month_locs[0] < 4:
            month_locs.pop(0)
            month_labels.pop(0)
        if month_locs[-1] - month_locs[-2] < 4:
            month_locs.pop()
            month_labels.pop()

        ax.tick_params(axis="x", which="major", pad=1, width=0, color='#24292f')
        ax.set_xticks(month_locs)
        ax.set_xticklabels(month_labels, ha="center")
        ax.xaxis.tick_top()

        if self.options[Config.MODE] == 'till_now':
            se_cax = ax.secondary_xaxis('bottom')
            se_cax.set_xticks([year_loc])
            se_cax.set_xticklabels([year])
            se_cax.tick_params(axis="x", pad=0, width=0, color='#24292f')
            se_cax.set_frame_on(False)

        ax.set_frame_on(False)

        bbox: Bbox = ax.get_position()
        cax: Axes = fig.add_axes(
            [
                bbox.x1 + 0.015,
                bbox.y0,
                0.015,
                bbox.height
            ]
        )
        cax.set_frame_on(False)
        plt.colorbar(pc, cax=cax, format=ScalarFormatter())

        cax.set_yticks([0 + (grid_max / 9), grid_max - (grid_max / 9)])
        cax.set_yticklabels(["0", str(int(grid_max))])
        cax.tick_params(axis="y", which="major", pad=0, width=0)

        title_font_dict = {'fontsize': 30,
                           'fontfamily': 'Microsoft YaHei',
                           'fontweight': 'bold'}
        ax.set_title(self.name, fontdict=title_font_dict, pad=15, loc='left')

        hint_font_dict = {
            'fontfamily': 'Microsoft YaHei',
        }

        year_font_dict = {
            **hint_font_dict,
            'fontsize': 28,
            'color': '#A9A9A9',
            'fontweight': 'bold'
        }

        ax.text(1, 1.25, f"{self.dtype(grid_sum)} {self.unit}",
                horizontalalignment='right',
                verticalalignment='bottom',
                fontdict=hint_font_dict,
                transform=ax.transAxes)

        if self.options[Config.MODE] == 'year':
            ax.text(-0.075, 0.6, f"{self.options[Config.YEAR]}",
                    horizontalalignment='center',
                    verticalalignment='center',
                    fontdict=year_font_dict,
                    rotation=90,
                    transform=ax.transAxes)

        file_type = self.options[Config.FILE_TYPE]

        if utils.util.is_debug():
            plt.show()

        path = Path(self.options[Config.OUTPUT_DIR]) / f"{self.id}.{file_type}"
        plt.savefig(str(path), bbox_inches='tight', pad_inches=0.1, format=file_type)
