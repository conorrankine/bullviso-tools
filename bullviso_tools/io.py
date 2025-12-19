#!/usr/bin/env python3

# =============================================================================
#                               LIBRARY IMPORTS
# =============================================================================

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

# =============================================================================
#                                   CLASSES
# =============================================================================

@dataclass(frozen = True)
class OutputConfig:

    xyz_f_glob: str
    out_f_glob: str
    energy_line_config: OutputLineConfig

@dataclass(frozen = True)
class OutputLineConfig:

    flag: str
    target_index: int

OUTPUT_CONFIGS: dict[str, OutputConfig] = {
    'xtb': OutputConfig(
        xyz_f_glob = 'xtbopt.xyz',
        out_f_glob = 'xtb.out',
        energy_line_config = OutputLineConfig(
            flag = 'TOTAL ENERGY',
            target_index = 3
        )
    ),
    'orca': OutputConfig(
        xyz_f_glob = '0*[!j].xyz',
        out_f_glob = '0*.out',
        energy_line_config = OutputLineConfig(
            flag = 'FINAL SINGLE POINT ENERGY',
            target_index = 4
        )
    ),
}

# =============================================================================
#                                  FUNCTIONS
# =============================================================================

def iter_results_dirs(
    root_d: Path
) -> Iterator[Path]:
    """
    Yields (sub)directories under the specified root directory that contain
    both .xyz and .out files.

    Args:
        root_d (Path): Root directory.

    Yields:
        Path: Paths to (sub)directories under the specified root directory that
        contain both .xyz and .out files.
    """

    for d, _, files in os.walk(root_d):
        suffixes = {Path(f).suffix for f in files}
        if {'.xyz', '.out'} <= suffixes:
            yield Path(d)

def detect_output_type(
    result_d: Path
) -> str:
    """
    Return the output type matching the files contained in the specified
    result directory; the output type is the key in `OUTPUT_CONFIGS` whose glob
    patterns (`xyz_f_glob` and `out_f_glob`) both resolve succesfully.

    Args:
        result_d (Path): Result directory.

    Returns:
        str: Output type.

    Raises:
        ValueError: If the output type cannot be detected;
        ValueError: If multiple possible output types are detected.
    """

    matches = []
    for output_type, output_config in OUTPUT_CONFIGS.items():
        has_xyz = any(result_d.glob(output_config.xyz_f_glob))
        has_out = any(result_d.glob(output_config.out_f_glob))
        if has_xyz and has_out:
            matches.append(output_type)

    if not matches:
        raise ValueError(
            f'couldn\'t detect the output type for {result_d}'
        )
    if len(matches) > 1:
        raise ValueError(
            f'mutliple possible output types detected for {result_d}: '
            f'candidates = {{{", ".join(matches)}}}'
        )

    return matches[0]

# =============================================================================
#                                     EOF
# =============================================================================
