"""
General utility functions for CyclicChamp MCP scripts.

These functions provide common utilities extracted from the use cases.
"""

import json
from pathlib import Path
from typing import Dict, Any, Union, Optional


def setup_output_directory(output_dir: Union[str, Path], input_file: Optional[Union[str, Path]] = None) -> Path:
    """
    Setup output directory with a sensible default based on input file.

    Args:
        output_dir: Desired output directory (or None for auto)
        input_file: Input file path for auto-generation

    Returns:
        Path to output directory
    """
    if output_dir is None:
        if input_file is not None:
            input_path = Path(input_file)
            output_dir = input_path.parent / f"{input_path.stem}_results"
        else:
            output_dir = Path("results")

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    return output_path


def merge_configs(default_config: Dict[str, Any], user_config: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
    """
    Merge configuration dictionaries with override priority.

    Args:
        default_config: Default configuration
        user_config: User configuration (can be None)
        **kwargs: Additional overrides

    Returns:
        Merged configuration dictionary

    Priority: kwargs > user_config > default_config
    """
    merged = default_config.copy()

    if user_config:
        merged.update(user_config)

    merged.update(kwargs)

    return merged


def load_config_with_defaults(config_file: Optional[Union[str, Path]], default_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Load config file with fallback to defaults.

    Args:
        config_file: Path to config file (can be None)
        default_config: Default configuration

    Returns:
        Configuration dictionary
    """
    if config_file is None:
        return default_config.copy()

    config_path = Path(config_file)

    if not config_path.exists():
        return default_config.copy()

    try:
        with open(config_path, 'r') as f:
            user_config = json.load(f)
        return merge_configs(default_config, user_config)
    except (json.JSONDecodeError, IOError):
        return default_config.copy()


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def get_file_info(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Get basic file information.

    Args:
        file_path: Path to file

    Returns:
        Dictionary with file information
    """
    file_path = Path(file_path)

    if not file_path.exists():
        return {"exists": False}

    stat = file_path.stat()

    return {
        "exists": True,
        "size_bytes": stat.st_size,
        "size_formatted": format_file_size(stat.st_size),
        "modified": stat.st_mtime,
        "is_file": file_path.is_file(),
        "is_dir": file_path.is_dir(),
        "extension": file_path.suffix,
        "name": file_path.name,
        "stem": file_path.stem
    }


def create_summary_dict(script_name: str, input_file: str, output_dir: str, **metadata) -> Dict[str, Any]:
    """
    Create standardized summary dictionary for script results.

    Args:
        script_name: Name of the script
        input_file: Input file path
        output_dir: Output directory path
        **metadata: Additional metadata

    Returns:
        Summary dictionary
    """
    return {
        "script": script_name,
        "input_file": str(input_file),
        "output_dir": str(output_dir),
        "input_info": get_file_info(input_file),
        "output_info": get_file_info(output_dir),
        **metadata
    }


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers, returning default on zero division.

    Args:
        numerator: Numerator
        denominator: Denominator
        default: Value to return on zero division

    Returns:
        Division result or default
    """
    try:
        return numerator / denominator if denominator != 0 else default
    except (ZeroDivisionError, TypeError):
        return default


def clamp(value: float, min_val: float, max_val: float) -> float:
    """
    Clamp value between min and max.

    Args:
        value: Value to clamp
        min_val: Minimum value
        max_val: Maximum value

    Returns:
        Clamped value
    """
    return max(min_val, min(value, max_val))