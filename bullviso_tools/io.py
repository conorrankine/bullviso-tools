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

OUTPUT_CONFIGS: dict[str, OutputConfig] = {
    'xtb': OutputConfig(
        xyz_f_glob = 'xtbopt.xyz',
        out_f_glob = 'xtb.out'
    ),
    'orca': OutputConfig(
        xyz_f_glob = '0*[!j].xyz',
        out_f_glob = '0*.out'
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

# =============================================================================
#                                     EOF
# =============================================================================
