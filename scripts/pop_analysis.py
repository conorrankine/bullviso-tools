#!/usr/bin/env python3

# =============================================================================
#                               LIBRARY IMPORTS
# =============================================================================

import typer
import pandas as pd
from pathlib import Path

from bullviso_tools.analysis import calculate_boltzmann_populations

# =============================================================================
#                                     APP
# =============================================================================

app = typer.Typer()

# =============================================================================
#                                  FUNCTIONS
# =============================================================================

def main(
    input_csv: Path,
    temperature: float,
    output_csv: Path,
    output_float_format: str
):

    df = pd.read_csv(
        input_csv,
        dtype = {'isomer': str, 'conformer': str, 'pose': str}
    )

    rel_energy_col = _rel_energy_column(df)
    units = rel_energy_col.removeprefix('rel_energy_')

    df[f'pop({temperature}K)'] = calculate_boltzmann_populations(
        df[rel_energy_col],
        units = units,
        temperature = temperature
    )

    df.drop(
        columns = [col for col in df.columns if 'energy' in col],
        inplace = True
    )

    df.to_csv(
        output_csv,
        index = False,
        float_format = output_float_format
    )

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

@app.command()
def run(
    input_csv: Path = typer.Argument(
        './energy.csv',
        exists = True,
        file_okay = True,
        dir_okay = False,
        readable = True,
        resolve_path = True,
        help = 'input (energy summary) .csv file to read'
    ),
    temperature: float = typer.Option(
        298.15,
        help = 'temperature (K) for Boltzmann population analysis'
    ),
    output_csv: Path = typer.Option(
        './pop.csv',
        file_okay = True,
        dir_okay = False,
        writable = True,
        resolve_path = True,
        help = 'output .csv file to write'
    ),
    output_float_format: str = typer.Option(
        '%.2f',
        help = 'output float format'
    )
):
    
    main(
        input_csv = input_csv,
        temperature = temperature,
        output_csv = output_csv,
        output_float_format = output_float_format
    )

# =============================================================================
#                                 ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    app()

# =============================================================================
#                                     EOF
# =============================================================================
