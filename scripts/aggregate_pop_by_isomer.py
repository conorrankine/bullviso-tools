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
    input_csv: Path = Path('./energy.csv'),
    output_csv: Path = Path('./pop_by_isomer.csv')
):

    df = pd.read_csv(
        input_csv,
        dtype = {
            'isomer': str,
            'conformer': str,
            'pose': str
        }
    )

    population_columns = _population_columns(df)

    aggregated_df = (
        df.groupby('isomer', as_index = False)
        .agg({column: 'sum' for column in population_columns})
    )
    
    aggregated_df['isomer_label'] = (
        aggregated_df['isomer'].apply(isomer_barcode_to_label)
    )
    
    ordered_columns = ['isomer', 'isomer_label', *population_columns]
    aggregated_df = aggregated_df[ordered_columns]

    aggregated_df.sort_values(
        population_columns[-1],
        ascending = False,
        inplace = True
    )

    aggregated_df.to_csv(
        output_csv,
        index = False,
        float_format = '%.6f'
    )

def _population_columns(
    df: pd.DataFrame
) -> list[str]:
    
    population_columns = [
        column for column in df.columns
        if column.startswith('pop(') and column.endswith('K)')
    ]
    if not population_columns:
        raise ValueError(
            f'expected column(s) named like `pop(<TEMP>K)`; found no '
            f'candidates in {{{", ".join(df.columns)}}}'
        )

    return population_columns

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
    output_csv: Path = typer.Option(
        './pop_by_isomer.csv',
        file_okay = True,
        dir_okay = False,
        writable = True,
        resolve_path = True,
        help = 'output .csv file to write'
    )
):
    
    main(
        input_csv,
        output_csv = output_csv
    )

# =============================================================================
#                                 ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    app()

# =============================================================================
#                                     EOF
# =============================================================================
