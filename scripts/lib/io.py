"""
Shared I/O functions for CyclicChamp MCP scripts.

These functions are extracted and simplified from the original use cases
to handle common file operations.
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple, Union, Optional


def load_pnear_data(input_file: Union[str, Path]) -> Tuple[List[str], List[float], List[float], List[float], List[str]]:
    """
    Load P_near data from CyclicChamp results file.

    Args:
        input_file: Path to Pnear_values_*.txt file

    Returns:
        Tuple of (designs, energies, pnear_rosetta, pnear_ga, sequences)

    Raises:
        FileNotFoundError: If input file doesn't exist
        ValueError: If no valid data found in file
    """
    input_file = Path(input_file)

    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    designs = []
    energies = []
    pnear_rosetta = []
    pnear_ga = []
    sequences = []

    with open(input_file, 'r') as f:
        lines = f.readlines()

    # Parse the file (skip header and empty lines)
    for line in lines:
        if line.strip() and not line.startswith('Name'):
            parts = [p for p in line.strip().split('\t') if p.strip()]  # Remove empty parts
            if len(parts) >= 5:  # Ensure we have all columns
                try:
                    designs.append(parts[0])
                    energies.append(float(parts[1]))
                    pnear_rosetta.append(float(parts[2]))
                    pnear_ga.append(float(parts[3]))
                    sequences.append(parts[4])
                except ValueError:
                    continue  # Skip malformed lines

    if len(designs) == 0:
        raise ValueError("No valid designs found in the input file!")

    return designs, energies, pnear_rosetta, pnear_ga, sequences


def save_output_file(data: Union[Dict, List, str], file_path: Union[str, Path], format_type: str = "auto") -> None:
    """
    Save data to file in the appropriate format.

    Args:
        data: Data to save
        file_path: Output file path
        format_type: Format type ('json', 'txt', 'auto')
    """
    file_path = Path(file_path)

    # Auto-detect format from extension
    if format_type == "auto":
        suffix = file_path.suffix.lower()
        if suffix == ".json":
            format_type = "json"
        elif suffix in [".txt", ".md", ".log"]:
            format_type = "txt"
        else:
            format_type = "txt"  # Default

    # Create parent directory if needed
    file_path.parent.mkdir(parents=True, exist_ok=True)

    if format_type == "json":
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    elif format_type == "txt":
        with open(file_path, 'w') as f:
            if isinstance(data, str):
                f.write(data)
            elif isinstance(data, (list, dict)):
                f.write(str(data))
            else:
                f.write(repr(data))


def load_config_file(config_file: Union[str, Path]) -> Dict:
    """
    Load configuration from JSON file.

    Args:
        config_file: Path to configuration file

    Returns:
        Configuration dictionary

    Raises:
        FileNotFoundError: If config file doesn't exist
        json.JSONDecodeError: If config file is malformed
    """
    config_file = Path(config_file)

    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_file}")

    with open(config_file, 'r') as f:
        config = json.load(f)

    return config


def get_input_files_from_pattern(pattern: str, base_dir: Union[str, Path] = ".") -> List[Path]:
    """
    Get list of input files matching a pattern.

    Args:
        pattern: Glob pattern (e.g., "Pnear_values_*.txt")
        base_dir: Base directory to search in

    Returns:
        List of matching file paths
    """
    base_dir = Path(base_dir)
    return list(base_dir.glob(pattern))


def create_output_filename(input_file: Union[str, Path], suffix: str, extension: str = None) -> Path:
    """
    Create standardized output filename based on input file.

    Args:
        input_file: Input file path
        suffix: Suffix to add to filename
        extension: New extension (keep original if None)

    Returns:
        New file path

    Example:
        >>> create_output_filename("Pnear_values_15res.txt", "_analysis", ".png")
        Path("Pnear_values_15res_analysis.png")
    """
    input_path = Path(input_file)

    if extension is None:
        new_name = f"{input_path.stem}{suffix}{input_path.suffix}"
    else:
        new_name = f"{input_path.stem}{suffix}{extension}"

    return input_path.parent / new_name