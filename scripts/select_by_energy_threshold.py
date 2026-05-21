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
    get_xyz_file,
    parse_results_dir_name
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
    units: str = 'kjmol',
    min_per_isomer: int = 0
):

    records = []
    for result_d in iter_results_dirs(root_d):
        isomer, _, _ = parse_results_dir_name(result_d)
        energy = get_scf_energy(result_d, units = units)
        records.append({
            'result_d': result_d,
            'isomer': isomer,
            'energy': energy
        })

    min_energy = min(record['energy'] for record in records)

    selected_result_dirs = set()
    
    for record in records:
        if (record['energy'] - min_energy) < energy_threshold:
            selected_result_dirs.add(record['result_d'])

    records_by_isomer = {}
    for record in records:
        records_by_isomer.setdefault(record['isomer'], []).append(record)
    for isomer_records in records_by_isomer.values():
        isomer_records.sort(key = lambda record: record['energy'])
        for record in isomer_records[:min_per_isomer]:
            selected_result_dirs.add(record['result_d'])

    for src_d in sorted(selected_result_dirs):
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
    ),
    min_per_isomer: int = typer.Option(
        0,
        min = 0,
        help = 'minimum number of structures to select per isomer'
    )
):
    
    main(
        root_d = root_d,
        output_d = output_d,
        energy_threshold = energy_threshold,
        units = units,
        min_per_isomer = min_per_isomer
    )

# =============================================================================
#                                 ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    app()

# =============================================================================
#                                     EOF
# =============================================================================
