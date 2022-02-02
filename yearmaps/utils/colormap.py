from typing import List

import click
import numpy as np
from matplotlib.colors import ListedColormap, to_rgba_array

no_value_color = to_rgba_array("#f6f6f6")


class PolarisationColorMap(ListedColormap):
    def __init__(self, colors: List[str], color_need: int, no_grey_index: List[int]):
        colors = colors.copy()
        self.zero_color = to_rgba_array(colors[0])
        self.no_grey_index = no_grey_index
        colors.pop(0)
        if color_need != -1:
            if color_need == 0:
                colors = colors[:1]
            else:
                colors = colors[:color_need]
        super().__init__(colors)

    # noinspection PyShadowingBuiltins
    def __call__(self, X, alpha=None, bytes=False):
        if isinstance(X, np.ma.core.MaskedArray):
            index = np.where(X == 0)
            mask_index = np.where(X.mask)
            color = super(ListedColormap, self).__call__(X, alpha=alpha, bytes=bytes)
            for i in index:
                color[i] = self.zero_color
            for i in mask_index[0]:
                if i in self.no_grey_index:
                    continue
                color[i] = no_value_color
            return color
        click.echo(f"Unhandled situation {type(X)}", err=True)
        return super(ListedColormap, self).__call__(X, alpha=alpha, bytes=bytes)


class WithBlankListedColorMap(ListedColormap):  # TODO: support color need
    def __init__(self, colors: List[str], no_grey_index: List[int]):
        self.no_grey_index = no_grey_index
        super().__init__(colors)

    # noinspection PyShadowingBuiltins
    def __call__(self, X, alpha=None, bytes=False):
        if isinstance(X, np.ma.core.MaskedArray):
            mask_index = np.where(X.mask)
            color = super(ListedColormap, self).__call__(X, alpha=alpha, bytes=bytes)
            for i in mask_index[0]:
                if i in self.no_grey_index:
                    continue
                color[i] = no_value_color
            return color
        click.echo(f"Unhandled situation {type(X)}", err=True)
        return super(ListedColormap, self).__call__(X, alpha=alpha, bytes=bytes)
