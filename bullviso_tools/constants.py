#!/usr/bin/env python3

# =============================================================================
#                                  CONSTANTS
# =============================================================================

AU_CONVERSION_FACTORS: dict[str, float] = {
    'au': 1.000,
    'kjmol': 2625.500,
    'kcalmol': 627.510
}

IDEAL_GAS_CONSTANTS: dict[str, float] = {
    'au': None,
    'kjmol': 8.314E-3,
    'kcalmol': 1.987E-3
}

SUBSTITUENT_SITE_LABELS: dict[int, str] = {
    0: r'$\delta^{\prime\prime}$',
    1: r'$\gamma^{\prime\prime}$',
    2: r'$\beta^{\prime\prime}$',
    3: r'$\delta^{\prime}$',
    4: r'$\gamma^{\prime}$',
    5: r'$\beta^{\prime}$',
    6: r'$\delta$',
    7: r'$\gamma$',
    8: r'$\beta$',
    9: r'$\alpha$'
}

# =============================================================================
#                                     EOF
# =============================================================================
