#!/usr/bin/env python3

# =============================================================================
#                               LIBRARY IMPORTS
# =============================================================================

import typer
import shutil
import pandas as pd
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
    min_per_isomer: int,
    energy_csv: Path | None
):

    if energy_csv is None:
        df = _load_energy_df_from_results(root_d)
    else:
        df = _load_energy_df_from_csv(energy_csv)

    selected_df = df[df['rel_energy_kjmol'] < energy_threshold]
    
    if min_per_isomer > 0:
        min_per_isomer_df = (
            df.sort_values('rel_energy_kjmol')
            .groupby('isomer', as_index = False)
            .head(min_per_isomer)
        )
        selected_df = pd.concat(
            [selected_df, min_per_isomer_df],
            ignore_index = True
        )

    selected_result_dirs = {
        Path(result_d) for result_d in selected_df['result_d']
    }

    for src_d in sorted(selected_result_dirs):
        dst_d = output_d / src_d.relative_to(root_d)
        dst_d.mkdir(parents = True, exist_ok = True)
        src_f = get_xyz_file(src_d)
        dst_f = dst_d / f'{dst_d.name}.xyz'
        shutil.copy(src_f, dst_f)

def _load_energy_df_from_results(
    root_d: Path
) -> pd.DataFrame:

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

    return df

def _load_energy_df_from_csv(
    energy_csv: Path
) -> pd.DataFrame:

    return pd.read_csv(
        energy_csv,
        dtype = {'isomer': str, 'conformer': str, 'pose': str}
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
    min_per_isomer: int = typer.Option(
        0,
        min = 0,
        help = 'minimum number of structures to select per isomer'
    ),
    energy_csv: Path | None = typer.Option(
        None,
        exists = True,
        file_okay = True,
        dir_okay = False,
        readable = True,
        resolve_path = True,
        help = 'energy summary .csv to read as a source of energy data'
    )
):
    
    main(
        root_d = root_d,
        output_d = output_d,
        energy_threshold = energy_threshold,
        min_per_isomer = min_per_isomer,
        energy_csv = energy_csv
    )

# =============================================================================
#                                 ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    app()

# =============================================================================
#                                     EOF
# =============================================================================
