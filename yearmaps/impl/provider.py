import calendar
import datetime
from abc import ABC
from pathlib import Path

import matplotlib as mpl
import matplotlib.axes
import matplotlib.figure
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.ticker import ScalarFormatter
from matplotlib.transforms import Bbox

from yearmaps.constant import Configs, ONE_DAY
from yearmaps.interface.provider import ProviderInterface, date_range, ProviderUtils
from yearmaps.utils.colors import color_list
from yearmaps.utils.colormap import PolarisationColorMap, WithBlankListedColorMap


class Provider(ProviderInterface, ProviderUtils, ABC):

    # Render utils to output
    def render(self, options: Configs):
        self.options = options
        self.echo(f"Initializing {self.name} provider...")
        self.init()
        self.echo(f"Initialized {self.name} provider.")
        self.echo(f"Start access {self.name} data...")
        raw = self.access()
        self.echo("End access data.")
        self.echo(f"Start process {self.name} data...")
        data = self.process(raw)
        self.echo("End process data.")

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

            _no_grey_index = []  # FIXME: too ugly implementation, remove it later

            def fill_no_grey(d: datetime.date):
                day = get_day(d)
                week = get_week(d)
                index = day * weeks + week
                _no_grey_index.append(index)

            for date in date_range(graph_start, start - ONE_DAY):
                fill_no_grey(date)
            for date in date_range(end + ONE_DAY, graph_end):
                fill_no_grey(date)

            for date, value in data.items():
                if not self.is_date_valid(date):
                    continue

                empty_grid[get_day(date)][get_week(date)] = value

            month_list = np.linspace(-1, -1, weeks, dtype=int)
            year_tuple = (start.year, get_week(start))
            current_year = None
            for date in date_range(start, end):
                date: datetime.date
                if date.weekday() == 0:
                    month_list[get_week(date)] = date.month
                if date.weekday() == 6:
                    if current_year is None:
                        current_year = date.year
                    elif current_year != date.year:
                        if year_tuple[0] != date.year:
                            year_tuple = (date.year, get_week(date))
            return empty_grid, month_list, year_tuple, _no_grey_index

        grid, months, (year, year_loc), no_grey_index = fulfill_data()
        grid: np.ndarray

        mpl.rcParams['font.family'] = 'monospace'
        mpl.rcParams['svg.fonttype'] = 'none'
        mpl.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'Noto Sans CJK SC', 'Noto Sans CJK JP', 'Noto Sans CJK']

        grid_max = self.value_type(np.nanmax(grid))
        grid_min = self.value_type(np.nanmin(grid))

        if grid_max == grid_min:
            raise ValueError("No data to collected.")

        color = self.options.color
        if color is None:
            color = self.color
        else:
            color = color_list[color]

        if self.value_type == int:
            color_need = int(grid_max)
        else:
            color_need = -1

        if grid_min == 0:
            c_map = PolarisationColorMap(color, color_need, no_grey_index)
        else:
            c_map = WithBlankListedColorMap(color, no_grey_index)

        fig_size = (10, 3)
        fig, ax = plt.subplots(figsize=fig_size, dpi=400)
        fig: matplotlib.figure.Figure
        ax: matplotlib.axes.Axes

        pc = ax.pcolormesh(grid, edgecolors=ax.get_facecolor(), linewidth=1, cmap=c_map)
        pc.set_clim(grid_min, grid_max)
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

        if self.options.mode == 'till_now':
            se_cax = ax.secondary_xaxis('bottom')
            se_cax.set_xticks([year_loc])
            se_cax.set_xticklabels([year], ha="left")
            se_cax.tick_params(axis="x", pad=0, width=0, color='#24292f')
            se_cax.set_frame_on(False)

        # Remove the axis spines
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

        font_family = 'sans-serif'
        hint_font_dict = {
            'fontfamily': font_family,
        }
        label_font_dict = {
            'fontfamily': 'monospace',
        }

        # Color bar label
        offset = grid_max - grid_min
        cax.set_yticks([grid_min + offset / 9, grid_max - offset / 9])
        cax.set_yticklabels(labels=[self.label_format(grid_min), self.label_format(grid_max)], fontdict=label_font_dict)
        cax.tick_params(axis="y", which="major", pad=0, width=0)

        title_font_dict = {'fontsize': 30,
                           'fontfamily': font_family,
                           'fontweight': 'bold'}
        ax.set_title(self.name, fontdict=title_font_dict, pad=15, loc='left')

        year_font_dict = {
            **hint_font_dict,
            'fontsize': 28,
            'color': '#A9A9A9',
            'fontweight': 'bold'
        }

        if isinstance(self.unit, str):
            analysis = f"{self.value_type(self.analysis(grid))} {self.unit}"
        else:
            analysis = self.unit(self.value_type(self.analysis(grid)))

        # overall analysis
        ax.text(1, 1.25, analysis,
                horizontalalignment='right',
                verticalalignment='bottom',
                fontdict=hint_font_dict,
                transform=ax.transAxes)

        # year analysis on the left
        if self.options.mode == 'year':
            ax.text(-0.075, 0.6, f"{self.options.year}",
                    horizontalalignment='center',
                    verticalalignment='center',
                    fontdict=year_font_dict,
                    rotation=90,
                    transform=ax.transAxes)

        # save the figure
        file_type = self.options.file_type

        if self.options.server:
            path = Path(self.options.output)
        else:
            path = Path(self.options.output) / f"{self.id}.{file_type}"
        plt.savefig(str(path), bbox_inches='tight', pad_inches=0.1, format=file_type)
