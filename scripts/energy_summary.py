#!/usr/bin/env python3

# =============================================================================
#                               LIBRARY IMPORTS
# =============================================================================

import typer
import pandas as pd
from pathlib import Path

from bullviso_tools.io import (
    iter_results_dirs,
    parse_results_dir_name,
    get_scf_energy
)

# =============================================================================
#                                     APP
# =============================================================================

app = typer.Typer()

# =============================================================================
#                                  FUNCTIONS
# =============================================================================

def main(
    root_d: Path,
    output_csv: Path,
    output_units: str,
    output_float_format: str
):

    records = []
    for result_d in iter_results_dirs(root_d):
        isomer, conformer, pose = parse_results_dir_name(result_d)
        energy = get_scf_energy(result_d, units = output_units)
        records.append({
            'isomer': isomer,
            'conformer': conformer,
            'pose': pose,
            f'energy_{output_units}': energy
        })

    df = pd.DataFrame.from_records(
        records,
        columns = [
            'isomer',
            'conformer',
            'pose',
            f'energy_{output_units}'
        ]
    )

    df[f'rel_energy_{output_units}'] = (
        df[f'energy_{output_units}'] - df[f'energy_{output_units}'].min()
    )

    df.sort_values(
        f'rel_energy_{output_units}',
        inplace = True
    )

    df.to_csv(
        output_csv,
        index = False,
        float_format = output_float_format
    )

@app.command()
def run(
    root_d: Path = typer.Argument(
        'minima',
        exists = True,
        file_okay = False,
        dir_okay = True,
        readable = True,
        resolve_path = True,
        help = 'root/\'top-level\' directory to process'
    ),
    output_csv: Path = typer.Option(
        './energy.csv',
        file_okay = True,
        dir_okay = False,
        writable = True,
        resolve_path = True,
        help = 'output .csv file to write'
    ),
    output_units: str = typer.Option(
        'kjmol',
        help = 'output energy units'
    ),
    output_float_format: str = typer.Option(
        '%.2f',
        help = 'output float format'
    )
):
    
    main(
        root_d = root_d,
        output_csv = output_csv,
        output_units = output_units,
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
