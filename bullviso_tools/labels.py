#!/usr/bin/env python3

# =============================================================================
#                                  CONSTANTS
# =============================================================================

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
#                                  FUNCTIONS
# =============================================================================

def isomer_barcode_to_label(
    isomer_barcode: str
) -> str:
    """
    Returns a comma-separated label defining the bullvalene substitution sites
    encoded by the supplied isomer barcode in alpha/beta/gamma/delta notation.

    Args:
        isomer_barcode (str): Isomer barcode.

    Returns:
        str: Comma-separated label in alpha/beta/gamma/delta notation.

    Raises:
        ValueError: If the isomer barcode is not exactly 10 bits in length;
        ValueError: If the isomer barcode contains non-decimal bits with values
            outside the range [0-9].
    """

    if len(isomer_barcode) != 10:
        raise ValueError(
            f'isomer barcodes should contain exactly 10 bits; got '
            f'\'{isomer_barcode}\' ({len(isomer_barcode)} bits)'
        )
    if not isomer_barcode.isdigit():
        raise ValueError(
            f'isomer barcodes should contain only decimal bits with values in '
            f'the range [0-9]; got \'{isomer_barcode}\''
        )

    labels = []
    for i, bit in enumerate(isomer_barcode):
        if bit != '0':
            labels.append(SUBSTITUENT_SITE_LABELS[i])

    return ','.join(labels)

# =============================================================================
#                                     EOF
# =============================================================================
