# MCP Scripts for CyclicChamp

Clean, self-contained scripts extracted from verified use cases for MCP tool wrapping.

## Design Principles

1. **Minimal Dependencies**: Only essential packages imported (numpy, matplotlib, pandas)
2. **Self-Contained**: Functions inlined where possible
3. **Configurable**: Parameters in config files, not hardcoded
4. **MCP-Ready**: Each script has a main function ready for MCP wrapping

## Scripts

| Script | Description | Repo Dependent | Config |
|--------|-------------|----------------|--------|
| `pnear_analysis.py` | Analyze P_near stability values | No | `configs/pnear_analysis_config.json` |
| `sequence_analysis.py` | Analyze sequence composition & properties | No | `configs/sequence_analysis_config.json` |
| `backbone_sampling_params.py` | Generate backbone sampling parameters | No | `configs/backbone_sampling_config.json` |

## Dependencies

All scripts use only standard scientific packages:
- **Essential**: numpy, matplotlib, pandas
- **Standard Library**: argparse, json, pathlib, collections, sys, os
- **No Repo Dependencies**: All scripts are fully self-contained

## Usage

```bash
# Activate environment
mamba activate ./env  # or: conda activate ./env

# P_near analysis
python scripts/pnear_analysis.py --input examples/data/results/Pnear_values_15res.txt --output-dir results/

# Sequence analysis
python scripts/sequence_analysis.py --input examples/data/results/Pnear_values_15res.txt --output-dir results/

# Backbone sampling parameters
python scripts/backbone_sampling_params.py --size 15 --output-dir results/

# With custom config
python scripts/pnear_analysis.py --input FILE --output-dir DIR --config configs/pnear_analysis_config.json
```

## Configuration Files

Located in `configs/`:
- `pnear_analysis_config.json`: P_near analysis settings
- `sequence_analysis_config.json`: Sequence analysis settings
- `backbone_sampling_config.json`: Backbone parameter settings
- `default_config.json`: Global default settings

## Shared Library

Common functions are in `scripts/lib/`:
- `io.py`: File loading/saving utilities
- `validation.py`: Input validation functions
- `utils.py`: General utility functions

## For MCP Wrapping (Step 6)

Each script exports a main function that can be wrapped as an MCP tool:

```python
# Example for P_near analysis
from scripts.pnear_analysis import run_pnear_analysis

@mcp.tool()
def analyze_cyclic_peptide_stability(input_file: str, output_dir: str = None) -> dict:
    """Analyze P_near stability values for cyclic peptide designs."""
    return run_pnear_analysis(input_file, output_dir)
```

### Main Functions

| Script | Main Function | Returns |
|--------|---------------|---------|
| `pnear_analysis.py` | `run_pnear_analysis(input_file, output_dir, config, **kwargs)` | Analysis results dict |
| `sequence_analysis.py` | `run_sequence_analysis(input_file, output_dir, config, **kwargs)` | Sequence data DataFrame + metadata |
| `backbone_sampling_params.py` | `run_backbone_sampling_params(peptide_size, output_dir, config, **kwargs)` | Parameter sets + metadata |

## Testing

All scripts have been tested with example data:

```bash
# Test all scripts
mamba run -p ./env python scripts/pnear_analysis.py --input examples/data/results/Pnear_values_15res.txt --output-dir test_results/
mamba run -p ./env python scripts/sequence_analysis.py --input examples/data/results/Pnear_values_15res.txt --output-dir test_results/
mamba run -p ./env python scripts/backbone_sampling_params.py --size 15 --output-dir test_results/
```

✅ All tests pass successfully.

## File Structure

```
scripts/
├── lib/                           # Shared utilities
│   ├── __init__.py               # Package initialization
│   ├── io.py                     # File I/O utilities
│   ├── validation.py             # Input validation
│   └── utils.py                  # General utilities
├── pnear_analysis.py             # P_near stability analysis
├── sequence_analysis.py          # Sequence composition analysis
├── backbone_sampling_params.py   # Backbone parameter generation
└── README.md                     # This file

configs/
├── pnear_analysis_config.json    # P_near analysis config
├── sequence_analysis_config.json # Sequence analysis config
├── backbone_sampling_config.json # Backbone parameters config
└── default_config.json          # Global defaults
```

## Next Step (Step 6)

These scripts are ready to be wrapped as MCP tools. Each script:
- Has a clear main function interface
- Returns structured data suitable for MCP
- Handles errors gracefully
- Is fully documented
- Is independently tested and working