#!/usr/bin/env python3

# =============================================================================
#                               LIBRARY IMPORTS
# =============================================================================

import typer
import pandas as pd
from pathlib import Path

from bullviso_tools.analysis import calculate_boltzmann_populations

# =============================================================================
#                                     APP
# =============================================================================

app = typer.Typer()

# =============================================================================
#                                  FUNCTIONS
# =============================================================================

def main(
    input_csv: Path,
    temperature: float,
    output_csv: Path,
    float_format: str
):

    df = pd.read_csv(
        input_csv,
        dtype = {'isomer': str, 'conformer': str, 'pose': str}
    )

    df[f'pop({temperature}K)'] = calculate_boltzmann_populations(
        df['rel_energy_kjmol'],
        temperature = temperature
    )

    df.drop(['energy_kjmol', 'rel_energy_kjmol'], inplace = True)

    df.to_csv(
        output_csv,
        index = False,
        float_format = float_format
    )

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
    temperature: float = typer.Option(
        298.15,
        help = 'temperature (K) for Boltzmann population analysis'
    ),
    output_csv: Path = typer.Option(
        './pop.csv',
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
        input_csv = input_csv,
        temperature = temperature,
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
