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

from bullviso_tools.analysis import (
    calculate_boltzmann_populations
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
    units: str = 'kjmol',
    temperature: float = 298.15,
    output_csv: Path = Path('./energy.csv')
):

    records = []
    for result_d in iter_results_dirs(root_d):
        isomer, conformer, pose = parse_results_dir_name(result_d)
        energy = get_scf_energy(result_d, units = units)
        records.append({
            'isomer': isomer,
            'conformer': conformer,
            'pose': pose,
            f'energy_{units}': energy
        })

    df = pd.DataFrame.from_records(
        records,
        columns = [
            'isomer',
            'conformer',
            'pose',
            f'energy_{units}'
        ]
    )

    df[f'rel_energy_{units}'] = (
        df[f'energy_{units}'] - df[f'energy_{units}'].min()
    )

    df[f'pop({temperature}K)'] = calculate_boltzmann_populations(
        df[f'rel_energy_{units}'],
        units = units,
        temperature = temperature
    )

    df.sort_values(
        f'rel_energy_{units}',
        inplace = True
    )

    df.to_csv(
        output_csv,
        index = False,
        float_format = '%.6f'
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
        help = 'text here'
    ),
    units: str = typer.Option(
        'kjmol',
        help = 'text here'
    ),
    temperature: float = typer.Option(
        298.15,
        min = 0.0,
        help = 'temperature (K) for Boltzmann population analysis'
    ),
    output_csv: Path = typer.Option(
        './energy.csv',
        file_okay = True,
        dir_okay = False,
        writable = True,
        resolve_path = True,
        help = 'output (.csv) file'
    )
):
    
    main(
        root_d = root_d,
        units = units,
        temperature = temperature,
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
