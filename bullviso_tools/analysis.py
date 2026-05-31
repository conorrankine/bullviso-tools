#!/usr/bin/env python3

# =============================================================================
#                               LIBRARY IMPORTS
# =============================================================================

from __future__ import annotations

import numpy as np
import pandas as pd

# =============================================================================
#                                  CONSTANTS
# =============================================================================

R = 8.314

# =============================================================================
#                                  FUNCTIONS
# =============================================================================

def calculate_boltzmann_populations(
    rel_energy: pd.Series,
    temperature: float = 298.15
) -> pd.Series:
    """
    Returns Boltzmann populations (%) for conformers with the supplied relative
    energies (kJ mol^{-1}) at the specified temperature.

    Args:
        rel_energy (pd.Series): Relative energies (kJ mol^{-1}).
        temperature (float, optional): Temperature (K) for the Boltzmann
            population analysis. Defaults to 298.15 K.

    Returns:
        pd.Series: Boltzmann populations (%).

    Raises:
        ValueError: If the specified temperature is <= 0 K.
    """
    
    if temperature <= 0:
        raise ValueError(
            f'temperature cannot be 0 K or below; got {temperature} K'
        )

    boltzmann_terms = np.exp((-1.0 * rel_energy) / (R * temperature))
    boltzmann_populations = 100.0 * (boltzmann_terms / boltzmann_terms.sum())

    return boltzmann_populations

# =============================================================================
#                                     EOF
# =============================================================================
