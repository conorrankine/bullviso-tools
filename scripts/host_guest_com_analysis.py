#!/usr/bin/env python3

# =============================================================================
#                               LIBRARY IMPORTS
# =============================================================================

import typer
import numpy as np
import pandas as pd
from rdkit import Chem
from pathlib import Path

from bullviso_tools.io import (
    iter_results_dirs,
    parse_results_dir_name,
    get_mol
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
    n_host_atoms: int = 0,
    n_guest_atoms: int = 0,
    output_csv: Path = Path('./com.csv')
):
    
    total_atoms = n_host_atoms + n_guest_atoms

    records = []
    for result_d in iter_results_dirs(root_d):
        isomer, conformer, pose = parse_results_dir_name(result_d)
        mol = get_mol(result_d)
        if total_atoms > mol.GetNumAtoms():
            raise ValueError(
                f'too many atoms passed; `n_host_atoms` ({n_host_atoms}) + '
                f'`n_guest_atoms` ({n_guest_atoms}) should be less than or '
                f'equal to {mol.GetNumAtoms()} (current total = {total_atoms})'
            )
        host_com_x, host_com_y, host_com_z = calc_com(
            mol, atom_idxs = range(0, n_host_atoms)
        )
        guest_com_x, guest_com_y, guest_com_z = calc_com(
            mol, atom_idxs = range(n_host_atoms, n_host_atoms + n_guest_atoms)
        )
        records.append({
            'isomer': isomer,
            'conformer': conformer,
            'pose': pose,
            'host_com_x': host_com_x,
            'host_com_y': host_com_y,
            'host_com_z': host_com_z,
            'guest_com_x': guest_com_x,
            'guest_com_y': guest_com_y,
            'guest_com_z': guest_com_z
        })

    df = pd.DataFrame.from_records(
        records,
        columns = [
            'isomer',
            'conformer',
            'pose',
            'host_com_x',
            'host_com_y',
            'host_com_z',
            'guest_com_x',
            'guest_com_y',
            'guest_com_z'
        ]
    )

    df.sort_values(
        ['isomer', 'conformer', 'pose'],
        inplace = True
    )

    df.to_csv(
        output_csv,
        index = False,
        float_format = '%.6f'
    )

def calc_com(
    mol: Chem.Mol,
    atom_idxs: list | None = None,
    use_atom_masses: bool = True,
    conf_id: int = -1
) -> tuple[int] | tuple[None]:
    
    conf = mol.GetConformer(conf_id)

    if atom_idxs is None:
        atom_idxs = range(conf.GetNumAtoms())
    atom_idxs = np.fromiter(atom_idxs, dtype = np.int32)
    if atom_idxs.size == 0:
        return tuple([None, None, None])
    
    if use_atom_masses:
        atom_masses = np.array(
            [mol.GetAtomWithIdx(int(i)).GetMass() for i in atom_idxs],
            dtype = np.float32
        )
    else:
        atom_masses = np.ones(atom_idxs.size)
    
    atom_coords = np.array(
        [conf.GetAtomPosition(int(idx)) for idx in atom_idxs],
        dtype = np.float32
    )

    com_coords = (
        (atom_coords * atom_masses[:, None]).sum(axis = 0) / atom_masses.sum()
    )

    return tuple([coord for coord in com_coords])

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
    n_host_atoms: int = typer.Option(
        0,
        min = 0,
        help = 'number of atoms in the host molecule'
    ),
    n_guest_atoms: int = typer.Option(
        0,
        min = 0,
        help = 'number of atoms in the guest molecule'
    ),
    output_csv: Path = typer.Option(
        './com.csv',
        file_okay = True,
        dir_okay = False,
        writable = True,
        resolve_path = True,
        help = 'output .csv file to write'
    )
):
    
    main(
        root_d = root_d,
        n_host_atoms = n_host_atoms,
        n_guest_atoms = n_guest_atoms,
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
