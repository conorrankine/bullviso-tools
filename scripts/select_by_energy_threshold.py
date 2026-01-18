#!/usr/bin/env python3

# =============================================================================
#                               LIBRARY IMPORTS
# =============================================================================

import typer
import shutil
from pathlib import Path

from bullviso_tools.io import (
    iter_results_dirs,
    get_scf_energy,
    get_output_file,
    get_xyz_file
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
    output_d: Path,
    energy_threshold: float,
    units: str = 'kjmol'
):

    records = []
    for result_d in iter_results_dirs(root_d):
        energy = get_scf_energy(result_d, units = units)
        records.append({
            'result_d': result_d,
            'energy': energy
        })

    min_energy = min(record['energy'] for record in records)
    
    for record in records:
        if (record['energy'] - min_energy) < energy_threshold:
            src_d = record['result_d']
            dst_d = output_d / src_d.relative_to(root_d)
            dst_d.mkdir(parents = True, exist_ok = True)
            src_f = get_xyz_file(src_d)
            dst_f = dst_d / f'{dst_d.name}.xyz'
            shutil.copy(src_f, dst_f)

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
    output_d: Path = typer.Option(
        'selected',
        file_okay = False,
        dir_okay = True,
        writable = True,
        resolve_path = True,
        help = 'output directory to copy selected structures to'
    ),
    energy_threshold: float = typer.Option(
        10.0,
        min = 0.0,
        help = 'energy threshold'
    ),
    units: str = typer.Option(
        'kjmol',
        help = 'energy units (e.g., \'kjmol\', \'kcalmol\', etc.)'
    )
):
    
    main(
        root_d = root_d,
        output_d = output_d,
        energy_threshold = energy_threshold,
        units = units
    )

# =============================================================================
#                                 ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    app()

# =============================================================================
#                                     EOF
# =============================================================================
