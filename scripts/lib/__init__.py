"""
Shared library for CyclicChamp MCP scripts.

This library contains common functions extracted from the use cases
to minimize code duplication while maintaining independence.
"""

__version__ = "1.0.0"
__author__ = "CyclicChamp MCP"

from .io import load_pnear_data, save_output_file
from .validation import validate_input_file, validate_peptide_size
from .utils import setup_output_directory, merge_configs

__all__ = [
    'load_pnear_data',
    'save_output_file',
    'validate_input_file',
    'validate_peptide_size',
    'setup_output_directory',
    'merge_configs'
]