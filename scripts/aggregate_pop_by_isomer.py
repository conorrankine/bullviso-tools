#!/usr/bin/env python3

# =============================================================================
#                               LIBRARY IMPORTS
# =============================================================================

import typer
import pandas as pd
from pathlib import Path

from bullviso_tools.io import isomer_barcode_to_label

# =============================================================================
#                                     APP
# =============================================================================

app = typer.Typer()

# =============================================================================
#                                  FUNCTIONS
# =============================================================================

def main(
    input_csv: Path,
    output_csv: Path,
    output_float_format: str
):

    df = pd.read_csv(
        input_csv,
        dtype = {'isomer': str, 'conformer': str, 'pose': str}
    )

    population_column = _population_column(df)

    grouped_df = (
        df.groupby('isomer', as_index = False)[population_column].sum()
    )
    
    grouped_df['isomer_label'] = (
        grouped_df['isomer'].apply(isomer_barcode_to_label)
    )
    
    ordered_columns = ['isomer', 'isomer_label', population_column]
    grouped_df = grouped_df[ordered_columns]

    grouped_df.sort_values(
        population_column,
        ascending = False,
        inplace = True
    )

    grouped_df.to_csv(
        output_csv,
        index = False,
        float_format = output_float_format
    )

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

@app.command()
def run(
    input_csv: Path = typer.Argument(
        './pop.csv',
        exists = True,
        file_okay = True,
        dir_okay = False,
        readable = True,
        resolve_path = True,
        help = 'input (population analysis) .csv file to read'
    ),
    output_csv: Path = typer.Option(
        './pop_by_isomer.csv',
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
