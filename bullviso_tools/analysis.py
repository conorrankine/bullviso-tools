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

R = 8.314E-3

# =============================================================================
#                                  FUNCTIONS
# =============================================================================

def calculate_boltzmann_populations(
    rel_energy: pd.Series[float],
    temperature: float = 298.15
) -> pd.Series[float]:
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
        ValueError: If the specified temperature is not finite or is <= 0 K.
        ValueError: If no relative energies are supplied.
        ValueError: If the supplied relative energies contain NaN values.
        ValueError: If the supplied relative energies contain infinite values.
    """
    
    if not np.isfinite(temperature) or temperature <= 0:
        raise ValueError(
            f'`temperature` should be finite and > 0 K; got {temperature} K'
        )

    if rel_energy.empty:
        raise ValueError(
            '`rel_energy` cannot be an empty series'
        )

    if rel_energy.isna().any():
        raise ValueError(
            '`rel_energy` cannot contain NaN values'
        )

    if not np.isfinite(rel_energy).all():
        raise ValueError(
            '`rel_energy` cannot contain infinite values'
        )

    boltzmann_terms = np.exp((-1.0 * rel_energy) / (R * temperature))
    boltzmann_populations = 100.0 * (boltzmann_terms / boltzmann_terms.sum())

    return boltzmann_populations

# =============================================================================
#                                     EOF
# =============================================================================
