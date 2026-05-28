#!/usr/bin/env python3

# =============================================================================
#                               LIBRARY IMPORTS
# =============================================================================

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd

from .labels import isomer_barcode_to_label

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure

# =============================================================================
#                                  FUNCTIONS
# =============================================================================

def plot_pop_by_isomer(
    input_csv: Path,
    ax: Axes | None = None,
    population_column: str | None = None,
    top_n: int | None = None,
    label_isomers: bool = True,
    **kwargs
) -> tuple[Figure, Axes]:
    """
    Plots a bar chart of the population of each isomer from a
    `pop_by_isomer.csv` file.

    Args:
        input_csv (Path): Input `pop_by_isomer.csv` file to read.
        ax (matplotlib.axes.Axes, optional): Axes to plot on. If None, a new
            figure and axes are created.
        population_column (str, optional): Population column to plot. If None,
            the single column beginning with `pop` is inferred.
        top_n (int, optional): Number of most-populated isomers to plot. If
            None, all isomers are plotted.
        label_isomers (bool, optional): If True, convert isomer barcodes to
            alpha/beta/gamma/delta labels for x tick labels.
        **kwargs: Additional keyword arguments passed to `DataFrame.plot.bar`.

    Returns:
        tuple[matplotlib.figure.Figure, matplotlib.axes.Axes]: Matplotlib
        figure and axes objects.
    """

    df = pd.read_csv(
        input_csv,
        dtype = {'isomer': str}
    )

    if population_column is None:
        population_column = _population_column(df)
    elif population_column not in df.columns:
        raise ValueError(
            f'population column \'{population_column}\' was not found in '
            f'{input_csv}; columns = {{{", ".join(df.columns)}}}'
        )

    if top_n is not None:
        if top_n <= 0:
            raise ValueError(f'top_n must be greater than 0; got {top_n}')
        df = df.head(top_n)

    x_column = 'isomer'
    if label_isomers:
        x_column = '_isomer_label'
        df[x_column] = df['isomer'].map(isomer_barcode_to_label)

    kwargs.setdefault('xlabel', 'Isomer')
    kwargs.setdefault('ylabel', 'Population (%)')
    kwargs.setdefault('rot', 90)
    kwargs.setdefault('legend', False)
    kwargs.setdefault('figsize', (8.0, 4.8))
    kwargs.setdefault('color', '#4C78A8')

    ax = df.plot.bar(
        x = x_column,
        y = population_column,
        ax = ax,
        **kwargs
    )

    return ax.figure, ax

def _population_column(
    df: pd.DataFrame
) -> str:

    population_columns = [
        column for column in df.columns if column.startswith('pop')
    ]
    if not population_columns:
        raise ValueError(
            f'expected exactly one `pop(<TEMPERATURE>K)` column; found no '
            f'candidate in {{{", ".join(df.columns)}}}'
        )
    if len(population_columns) > 1:
        raise ValueError(
            f'expected exactly one `pop(<TEMPERATURE>K)` column; found '
            f'multiple candidates: {", ".join(population_columns)}'
        )

    return population_columns[0]

# =============================================================================
#                                     EOF
# =============================================================================
