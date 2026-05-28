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

def plot_rel_energy_by_isomer(
    input_csv: Path,
    ax: Axes | None = None,
    rel_energy_column: str | None = None,
    top_n: int | None = None,
    label_isomers: bool = True,
    **kwargs
) -> tuple[Figure, Axes]:
    """
    Plots box-and-whisker plots of relative energies grouped by isomer from an
    `energy.csv` file.

    Args:
        input_csv (Path): Input `energy.csv` file to read.
        ax (matplotlib.axes.Axes, optional): Axes to plot on. If None, a new
            figure and axes are created.
        rel_energy_column (str, optional): Relative energy column to plot. If
            None, the single column beginning with `rel_energy_` is inferred.
        top_n (int, optional): Number of lowest-energy isomer groups to plot,
            ranked by the minimum relative energy for each isomer. Plotted
            groups are sorted by isomer barcode. If None, all isomers are
            plotted.
        label_isomers (bool, optional): If True, convert isomer barcodes to
            alpha/beta/gamma/delta labels for x tick labels.
        **kwargs: Additional keyword arguments passed to `DataFrame.boxplot`.

    Returns:
        tuple[matplotlib.figure.Figure, matplotlib.axes.Axes]: Matplotlib
        figure and axes objects.
    """

    df = pd.read_csv(
        input_csv,
        dtype = {'isomer': str, 'conformer': str, 'pose': str}
    )

    if rel_energy_column is None:
        rel_energy_column = _rel_energy_column(df)
    elif rel_energy_column not in df.columns:
        raise ValueError(
            f'relative energy column \'{rel_energy_column}\' was not found in '
            f'{input_csv}; columns = {{{", ".join(df.columns)}}}'
        )

    if top_n is not None:
        if top_n <= 0:
            raise ValueError(f'top_n must be greater than 0; got {top_n}')
        selected_isomers = (
            df.groupby('isomer')[rel_energy_column]
            .min()
            .sort_values()
            .head(top_n)
            .index
        )
        df = df[df['isomer'].isin(selected_isomers)]

    isomer_order = sorted(df['isomer'].unique())

    x_column = 'isomer'
    group_order = list(isomer_order)
    if label_isomers:
        x_column = '_isomer_label'
        df[x_column] = df['isomer'].map(isomer_barcode_to_label)
        group_order = [
            isomer_barcode_to_label(isomer)
            for isomer in group_order
        ]
    df[x_column] = pd.Categorical(
        df[x_column],
        categories = group_order,
        ordered = True
    )

    units = rel_energy_column.removeprefix('rel_energy_')

    kwargs.setdefault('xlabel', 'Isomer')
    kwargs.setdefault('ylabel', f'Relative Energy / {units}')
    kwargs.setdefault('rot', 90)
    kwargs.setdefault('grid', False)
    kwargs.setdefault('figsize', (8.0, 4.8))

    ax = df.boxplot(
        column = rel_energy_column,
        by = x_column,
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

def _rel_energy_column(
    df: pd.DataFrame
) -> str:

    rel_energy_columns = [
        column for column in df.columns if column.startswith('rel_energy_')
    ]
    if not rel_energy_columns:
        raise ValueError(
            f'expected exactly one `rel_energy_<UNITS>` column; found no '
            f'candidate in {{{", ".join(df.columns)}}}'
        )
    if len(rel_energy_columns) > 1:
        raise ValueError(
            f'expected exactly one `rel_energy_<UNITS>` column; found '
            f'multiple candidates: {", ".join(rel_energy_columns)}'
        )

    return rel_energy_columns[0]

# =============================================================================
#                                     EOF
# =============================================================================
