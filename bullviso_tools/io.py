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
    Returns the output type matching the files contained in the specified
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
            f'multiple possible output types detected for {result_d}: '
            f'candidates = {{{", ".join(matches)}}}'
        )

    return matches[0]

def get_scf_energy(
    result_d: Path,
    output_config: OutputConfig | None = None
) -> float:
    """
    Returns the SCF energy in Hartree extracted from the output file contained
    in the specified result directory.

    Args:
        result_d (Path): Result directory.
        output_config (OutputConfig, optional): Output configuration to guide
            parsing of the output file; if None, an output configuration is
            inferred from the files in the specified result directory.

    Returns:
        float: SCF energy (Hartree).

    Raises:
        ValueError: If the SCF energy cannot be found in the output file.
    """
    
    output_config = (
        output_config or OUTPUT_CONFIGS[detect_output_type(result_d)]
    )
    
    out_f = get_output_file(result_d, output_config)
    energy_line_config = output_config.energy_line_config
    with out_f.open('r') as f:
        for line in f:
            if energy_line_config.flag in line:
                parts = line.strip().split()
                if not parts:
                    continue
                return float(parts[energy_line_config.target_index])
    raise ValueError(
        f'couldn\'t get the SCF energy from {out_f}; no lines containing the '
        f'target string flag \'{energy_line_config.flag}\''
    )

def get_output_file(
    result_d: Path,
    output_config: OutputConfig
) -> Path:
    """
    Returns the output file path from the specified result directory that
    matches the specified output configuration.

    Args:
        result_d (Path): Result directory.
        output_config (OutputConfig): Output configuration.

    Returns:
        Path: Path to the output file in the specified result directory.
    """

    return _get_file_matching_glob(result_d, output_config.out_f_glob)

def get_xyz_file(
    result_d: Path,
    output_config: OutputConfig
) -> Path:
    """
    Returns the .xyz file path from the specified result directory that matches
    the specified output configuration.

    Args:
        result_d (Path): Result directory.
        output_config (OutputConfig): Output configuration.

    Returns:
        Path: Path to the .xyz file in the specified result directory.
    """

    return _get_file_matching_glob(result_d, output_config.xyz_f_glob)

def _get_file_matching_glob(
    result_d: Path,
    glob_pattern: str
) -> Path:
    """
    Returns the single file matching the supplied glob pattern inside the
    specified result directory.

    Args:
        result_d (Path): Result directory.
        glob_pattern (str): Glob pattern to match the target file.

    Returns:
        Path: Path to the matched file in the specified result directory.

    Raises:
        FileNotFoundError: If a matching file cannot be found;
        ValueError: If multiple possible matching files are found.
    """

    matches = list(result_d.glob(glob_pattern))

    if not matches:
        raise FileNotFoundError(
            f'no files matching \'{glob_pattern}\' found in {result_d}'
        )
    if len(matches) > 1:
        raise ValueError(
            f'multiple files matching \'{glob_pattern}\' found in {result_d}: '
            f'matches = {{{", ".join(matches)}}}'
        )

    return matches[0]

# =============================================================================
#                                     EOF
# =============================================================================
