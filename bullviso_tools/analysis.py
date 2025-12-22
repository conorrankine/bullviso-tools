#!/usr/bin/env python3

# =============================================================================
#                               LIBRARY IMPORTS
# =============================================================================

from __future__ import annotations

import numpy as np
import pandas as pd

from .constants import IDEAL_GAS_CONSTANTS

# =============================================================================
#                                  FUNCTIONS
# =============================================================================

def calculate_boltzmann_populations(
    rel_energy: pd.Series,
    units: str = 'au',
    temperature: float = 298.15
) -> pd.Series:
    """
    Returns Boltzmann populations (%) for conformers with the supplied relative
    energies at the specified temperature.

    Args:
        rel_energy (pd.Series): Relative energies.
        units (str, optional): Energy units. Defaults to 'au'.
        temperature (float, optional): Temperature (K) for the Boltzmann
            population analysis. Defaults to 298.15 K.

    Returns:
        pd.Series: Boltzmann populations (%).

    Raises:
        ValueError: If the energy units are unsupported, i.e., if a compatible
            ideal gas constant value is not defined;
        ValueError: If the temperature is <= 0 K.
    """
    
    if temperature <= 0:
        raise ValueError(
            f'temperature cannot be 0 K or below; got {temperature} K'
        )
    R = IDEAL_GAS_CONSTANTS.get(units, None)
    if R is None:
        raise ValueError(
            f'no compatible ideal gas constant value defined for the energy '
            f'units \'{units}\''
        )
    boltzmann_terms = np.exp((-1.0 * rel_energy) / (R * temperature))
    boltzmann_populations = 100.0 * (boltzmann_terms / boltzmann_terms.sum())

    return boltzmann_populations

# =============================================================================
#                                     EOF
# =============================================================================
