#!/usr/bin/env python3

# =============================================================================
#                               LIBRARY IMPORTS
# =============================================================================

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

from .constants import (
    AU_CONVERSION_FACTORS,
    SUBSTITUENT_SITE_LABELS
)

# =============================================================================
#                                   CLASSES
# =============================================================================

@dataclass(frozen = True)
class OutputConfig:

    xyz_f_glob: str
    out_f_glob: str
    out_completion_flag: str
    out_imaginary_frequency_flag: str
    energy_line_config: OutputLineConfig

@dataclass(frozen = True)
class OutputLineConfig:

    flag: str
    target_index: int

# =============================================================================
#                                  FUNCTIONS
# =============================================================================

def iter_results_dirs(
    root_d: Path,
    validate: bool = True
) -> Iterator[Path]:
    """
    Yields (sub)directories under the specified root directory that contain
    both .xyz and .out files, and (optionally) pass a validation check for the
    i) completion and ii) convergence to a real minimum of the computational
    chemical calculation inside.

    If any (sub)directory containing both .xyz and .out files also contains a
    '.ignore' flag file, it is skipped.

    Args:
        root_d (Path): Root directory.
        validate (bool, optional): If True, yield only those (sub)directories
            with computational chemical calculations that pass a validation
            check for i) completeness and ii) convegergence to a real minimum;
            if False, yield all (sub)directories.

    Yields:
        Path: Paths to (sub)directories under the specified root directory that
        contain both .xyz and .out files.
    """

    for d, _, files in os.walk(root_d):
        suffixes = {Path(f).suffix for f in files}
        if {'.xyz', '.out'} <= suffixes:
            results_d = Path(d)
            if not (results_d / '.ignore').exists():
                if validate:
                    try:
                        if validate_results_dir(results_d):
                            yield results_d
                    except ValueError as e:
                        print(f'skipping {results_d}: {e}')
                else:
                    yield results_d
            else:
                print(f'skipping {results_d}: flagged to ignore')

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

def validate_results_dir(
    result_d: Path,
    output_config: OutputConfig | None = None
) -> bool:
    """
    Validates that the specified result directory contains a completed
    computational chemical calculation that has converged to a real minimum,
    i.e., that has no imaginary (negative-valued) frequencies.

    Args:
        result_d (Path): Result directory.
        output_config (OutputConfig, optional): Output configuration to guide
            parsing of the output file; if None, an output configuration is
            inferred from the files in the specified result directory.

    Returns:
        bool: True if validation checks pass.

    Raises:
        ValueError: If the output file is incomplete, i.e., if the expected
            'normal termination' message is not printed to the output file;
        ValueError: If the output file contains imaginary (negative-valued)
            frequencies, i.e., if the 'imaginary frequency' warning message is
            printed to the output file.
    """

    output_config = (
        output_config or OUTPUT_CONFIGS[detect_output_type(result_d)]
    )

    out_f = get_output_file(result_d, output_config)
    with out_f.open('r') as f:
        f_contents = f.read()
    if f_contents.rfind(output_config.out_completion_flag) == -1:
        raise ValueError(
            f'incomplete output detected'
        )
    if f_contents.rfind(output_config.out_imaginary_frequency_flag) != -1:
        raise ValueError(
            f'imaginary frequency detected'
        )
    return True

def get_scf_energy(
    result_d: Path,
    output_config: OutputConfig | None = None,
    units: str = 'au'
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

    try:
        au_conversion_factor = AU_CONVERSION_FACTORS[units]
    except KeyError:
        raise ValueError(
            f'\'{units}\' is not a supported energy unit; supported energy '
            f'units are {{{", ".join(AU_CONVERSION_FACTORS.keys())}}}'
        ) from None
    
    out_f = get_output_file(result_d, output_config)
    energy_line_config = output_config.energy_line_config
    with out_f.open('r') as f:
        lines = f.readlines()
    for line in reversed(lines):
        if energy_line_config.flag in line:
            parts = line.strip().split()
            if not parts:
                continue
            energy_au = float(parts[energy_line_config.target_index])
            return energy_au * au_conversion_factor
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

def parse_results_dir_name(
    result_d: Path
) -> tuple[str, str, str | None]:
    """
    Returns the isomer/conformer/pose labels encoded in the name of the
    specified results directory; expects the result directory name formatted
    as "<ISOMER>_<CONFORMER>[_<POSE>]".

    Args:
        result_d (Path): Result directory.

    Returns:
        tuple[str, str, str | None]: Tuple of isomer/conformer/pose labels.

    Raises:
        ValueError: If the name of the specified results directory does not
            contain two or three underscore-separated tokens.
    """
    
    parts = result_d.name.split('_')
    if len(parts) == 3:
        isomer, conformer, pose = parts
    elif len(parts) == 2:
        isomer, conformer = parts
        pose = None
    else:
        raise ValueError(
            f'expected the result directory name formatted as '
            f'"<ISOMER>_<CONFORMER>[_<POSE>]"; got \'{result_d.name}\''
        )

    return isomer, conformer, pose

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
#                                   CONFIGS
# =============================================================================

OUTPUT_CONFIGS: dict[str, OutputConfig] = {
    'xtb': OutputConfig(
        xyz_f_glob = 'xtbopt.xyz',
        out_f_glob = 'xtb.out',
        out_completion_flag = 'finished run',
        out_imaginary_frequency_flag = 'significant imaginary frequency',
        energy_line_config = OutputLineConfig(
            flag = 'TOTAL ENERGY',
            target_index = 3
        )
    ),
    'orca': OutputConfig(
        xyz_f_glob = '0*[!j].xyz',
        out_f_glob = '0*.out',
        out_completion_flag = 'ORCA TERMINATED NORMALLY',
        out_imaginary_frequency_flag = 'IMAGINARY MODE',
        energy_line_config = OutputLineConfig(
            flag = 'FINAL SINGLE POINT ENERGY',
            target_index = 4
        )
    ),
}

# =============================================================================
#                                     EOF
# =============================================================================
