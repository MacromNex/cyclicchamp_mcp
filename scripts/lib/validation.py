"""
Input validation utilities for CyclicChamp MCP scripts.

These functions provide common validation logic extracted from the use cases.
"""

from pathlib import Path
from typing import Union, List, Optional


def validate_input_file(input_file: Union[str, Path], required_extensions: Optional[List[str]] = None) -> Path:
    """
    Validate that input file exists and has correct extension.

    Args:
        input_file: Path to input file
        required_extensions: List of allowed extensions (e.g., ['.txt', '.tsv'])

    Returns:
        Validated Path object

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file has wrong extension
    """
    input_path = Path(input_file)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    if not input_path.is_file():
        raise ValueError(f"Path is not a file: {input_path}")

    if required_extensions:
        if input_path.suffix.lower() not in [ext.lower() for ext in required_extensions]:
            raise ValueError(f"File must have one of these extensions: {required_extensions}")

    return input_path


def validate_peptide_size(size: int, supported_sizes: Optional[List[int]] = None) -> int:
    """
    Validate peptide size parameter.

    Args:
        size: Peptide size in residues
        supported_sizes: List of supported sizes (default: [7, 15, 20, 24])

    Returns:
        Validated size

    Raises:
        ValueError: If size is not supported
    """
    if supported_sizes is None:
        supported_sizes = [7, 15, 20, 24]

    if size not in supported_sizes:
        raise ValueError(f"Peptide size {size} not supported. Supported sizes: {supported_sizes}")

    return size


def validate_pnear_threshold(threshold: float) -> float:
    """
    Validate P_near threshold value.

    Args:
        threshold: P_near threshold (should be 0-1)

    Returns:
        Validated threshold

    Raises:
        ValueError: If threshold is out of range
    """
    if not (0.0 <= threshold <= 1.0):
        raise ValueError(f"P_near threshold must be between 0.0 and 1.0, got: {threshold}")

    return threshold


def validate_config_keys(config: dict, required_keys: List[str], context: str = "config") -> dict:
    """
    Validate that config dictionary contains required keys.

    Args:
        config: Configuration dictionary
        required_keys: List of required keys
        context: Context name for error messages

    Returns:
        Validated config

    Raises:
        ValueError: If required keys are missing
    """
    missing_keys = [key for key in required_keys if key not in config]

    if missing_keys:
        raise ValueError(f"Missing required keys in {context}: {missing_keys}")

    return config


def validate_output_directory(output_dir: Union[str, Path], create: bool = True) -> Path:
    """
    Validate output directory and optionally create it.

    Args:
        output_dir: Output directory path
        create: Whether to create directory if it doesn't exist

    Returns:
        Validated Path object

    Raises:
        ValueError: If directory validation fails
    """
    output_path = Path(output_dir)

    if output_path.exists() and not output_path.is_dir():
        raise ValueError(f"Output path exists but is not a directory: {output_path}")

    if create:
        output_path.mkdir(parents=True, exist_ok=True)

    return output_path


def validate_file_readable(file_path: Union[str, Path]) -> Path:
    """
    Check if file is readable.

    Args:
        file_path: File to check

    Returns:
        Validated Path object

    Raises:
        PermissionError: If file is not readable
    """
    file_path = Path(file_path)

    try:
        with open(file_path, 'r') as f:
            f.read(1)  # Try to read one character
    except PermissionError:
        raise PermissionError(f"Cannot read file: {file_path}")
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")

    return file_path