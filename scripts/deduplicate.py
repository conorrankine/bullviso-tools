#!/usr/bin/env python3

# =============================================================================
#                               LIBRARY IMPORTS
# =============================================================================

import typer
from pathlib import Path
from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit.ML.Cluster import Butina

from bullviso_tools.io import (
    iter_results_dirs,
    get_scf_energy,
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
    rms_threshold: float = 0.1
):
    
    isomers = [d.name for d in root_d.iterdir() if d.is_dir()]
    for isomer in isomers:
        mol = _load_confs_from_dir(root_d / isomer)
        if mol is None:
            continue

        rms_matrix = AllChem.GetConformerRMSMatrix(mol)
        clusters = Butina.ClusterData(
            rms_matrix,
            mol.GetNumConformers(),
            rms_threshold,
            isDistData = True
        )

        conf_ids = [conf.GetId() for conf in mol.GetConformers()]
        
        for cluster in clusters:
            min_energy_conf_idx = min(
                cluster,
                key = lambda idx: (
                    mol.GetConformer(conf_ids[idx]).GetDoubleProp('energy')
                )
            )
            for idx in (i for i in cluster if i != min_energy_conf_idx):
                result_d = Path(
                    mol.GetConformer(conf_ids[idx]).GetProp('result_d')
                )
                print(f'writing .ignore to {result_d}')
                with open(result_d / '.ignore', 'w') as f:
                    pass

def _load_confs_from_dir(
    root_d: Path,
    set_properties: bool = True
) -> Chem.Mol | None:
    
    mol: Chem.Mol = None
    for result_d in iter_results_dirs(root_d):
        result_d_mol = get_mol(result_d)
        result_d_conf = result_d_mol.GetConformer()
        if set_properties:
            energy = get_scf_energy(result_d, units = 'au')
            result_d_conf.SetProp('result_d', str(result_d))
            result_d_conf.SetDoubleProp('energy', energy)
        if mol is None:
            mol = result_d_mol
        else:
            mol.AddConformer(result_d_conf, assignId = True)
    return mol

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
    rms_threshold: float = typer.Option(
        0.1,
        min = 0.0,
        help = 'RMS threshold for distance-based clustering/deduplication'
    )
):
    
    main(
        root_d = root_d,
        rms_threshold = rms_threshold
    )

# =============================================================================
#                                 ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    app()

# =============================================================================
#                                     EOF
# =============================================================================
