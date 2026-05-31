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
    float_format: str
):

    records = []
    for result_d in iter_results_dirs(root_d):
        isomer, conformer, pose = parse_results_dir_name(result_d)
        energy = get_scf_energy(result_d)
        records.append({
            'result_d': result_d,
            'isomer': isomer,
            'conformer': conformer,
            'pose': pose,
            'energy_kjmol': energy
        })

    df = pd.DataFrame.from_records(
        records,
        columns = [
            'result_d',
            'isomer',
            'conformer',
            'pose',
            'energy_kjmol'
        ]
    )

    df['rel_energy_kjmol'] = df['energy_kjmol'] - df['energy_kjmol'].min()

    df.sort_values('rel_energy_kjmol', inplace = True)

    df.to_csv(
        output_csv,
        index = False,
        float_format = float_format
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
    float_format: str = typer.Option(
        '%.2f',
        help = 'float format specifying the output floating point precision'
    )
):
    
    main(
        root_d = root_d,
        output_csv = output_csv,
        float_format = float_format
    )

# =============================================================================
#                                 ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    app()

# =============================================================================
#                                     EOF
# =============================================================================
