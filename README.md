# CyclicChamp MCP Tools

> MCP tools for cyclic peptide computational analysis using CyclicChamp backbone sampling algorithms

## Table of Contents
- [Overview](#overview)
- [Installation](#installation)
- [Local Usage (Scripts)](#local-usage-scripts)
- [MCP Server Installation](#mcp-server-installation)
- [Using with Claude Code](#using-with-claude-code)
- [Using with Gemini CLI](#using-with-gemini-cli)
- [Available Tools](#available-tools)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

## Overview

CyclicChamp MCP Tools provides a comprehensive suite for cyclic peptide computational analysis, specifically designed for backbone sampling and stability assessment of cyclic peptides from 7 to 24 residues. The tools implement the CyclicChamp methodology for simulated annealing-based peptide design with mixed L/D chirality support.

### Features
- **P_near Stability Analysis**: Analyzes stability metrics combining RMSD and energy assessments (P_near > 0.9 = stable designs)
- **Sequence Composition Analysis**: Comprehensive amino acid and chirality pattern analysis with physicochemical properties
- **Backbone Parameter Generation**: Optimized CyclicChamp simulated annealing parameters for different peptide sizes
- **Batch Processing**: High-throughput analysis for virtual screening and parameter optimization studies
- **Mixed Chirality Support**: Native support for L/D amino acid combinations in cyclic peptide designs

### Directory Structure
```
./
├── README.md               # This file
├── env/                    # Conda environment
├── src/
│   └── server.py           # MCP server with 16 tools
├── scripts/
│   ├── pnear_analysis.py              # P_near stability analysis
│   ├── sequence_analysis.py           # Sequence composition and properties
│   ├── backbone_sampling_params.py   # CyclicChamp parameter generation
│   └── lib/                           # Shared utilities (io, validation, utils)
├── examples/
│   └── data/               # Demo data
│       ├── results/        # P_near analysis results (15, 20, 24 residue samples)
│       ├── sequences/      # Amino acid type definitions (L/D residues)
│       └── structures/     # Sample cluster center PDB structures
├── configs/                # Configuration files
│   ├── pnear_analysis_config.json     # P_near analysis settings
│   ├── sequence_analysis_config.json  # Sequence analysis parameters
│   ├── backbone_sampling_config.json  # Parameter generation formulas
│   └── default_config.json            # Global defaults
└── repo/                   # Original CyclicChamp repository
```

---

## Installation

### Quick Setup

Run the automated setup script:

```bash
./quick_setup.sh
```

This will create the environment and install all dependencies automatically.

### Manual Setup (Advanced)

For manual installation or customization, follow these steps.

#### Prerequisites
- Conda or Mamba (mamba recommended for faster installation)
- Python 3.10+
- Scientific Python stack (numpy, matplotlib, pandas, scipy)
- MCP framework (fastmcp, loguru)

#### Create Environment

Please follow the information in `reports/step3_environment.md` for the complete setup procedure. A typical workflow:

```bash
# Navigate to the MCP directory
cd /home/xux/Desktop/CycPepMCP/CycPepMCP/tool-mcps/cyclicchamp_mcp

# Create conda environment (use mamba if available)
mamba create -p ./env python=3.12 pip -y
# or: conda create -p ./env python=3.12 pip -y

# Activate environment
mamba activate ./env
# or: conda activate ./env

# Install core dependencies
mamba run -p ./env pip install matplotlib numpy scipy loguru click pandas tqdm

# Install MCP dependencies
mamba run -p ./env pip install --force-reinstall --no-cache-dir fastmcp

# Test installation
mamba run -p ./env python -c "import numpy; import matplotlib; import scipy; import fastmcp; print('Core imports successful')"
```

---

## Local Usage (Scripts)

You can use the scripts directly without MCP for local processing.

### Available Scripts

| Script | Description | Example |
|--------|-------------|---------|
| `scripts/pnear_analysis.py` | Analyze P_near stability values for cyclic peptides from CyclicChamp results | See below |
| `scripts/sequence_analysis.py` | Analyze sequence composition, chirality patterns, and physicochemical properties | See below |
| `scripts/backbone_sampling_params.py` | Generate backbone sampling parameters for CyclicChamp simulated annealing | See below |

### Script Examples

#### P_near Stability Analysis

```bash
# Activate environment
mamba activate ./env

# Analyze P_near stability for 15-residue peptides
python scripts/pnear_analysis.py \
  --input examples/data/results/Pnear_values_15res.txt \
  --output-dir results/pnear_analysis \
  --min-pnear 0.9

# Analyze with custom configuration
python scripts/pnear_analysis.py \
  --input examples/data/20res_Pnear_list.txt \
  --config configs/pnear_analysis_config.json \
  --output-dir results/20res_analysis
```

**Parameters:**
- `--input, -i`: Path to Pnear_values_*.txt file (required)
- `--output-dir, -o`: Output directory for plots and reports (optional)
- `--min-pnear`: Minimum P_near threshold for stable designs (default: 0.9)
- `--config`: Path to JSON config file (optional)

#### Sequence Composition Analysis

```bash
# Analyze all designs in dataset
python scripts/sequence_analysis.py \
  --input examples/data/results/Pnear_values_20res.txt \
  --output-dir results/sequence_analysis

# Analyze only stable designs (P_near > 0.9)
python scripts/sequence_analysis.py \
  --input examples/data/24res_Pnear_list.txt \
  --stable-only \
  --min-pnear 0.95 \
  --output-dir results/stable_sequences
```

**Parameters:**
- `--input, -i`: Path to Pnear_values_*.txt file (required)
- `--output-dir, -o`: Output directory (optional)
- `--stable-only`: Analyze only stable designs above threshold (flag)
- `--min-pnear`: P_near threshold for stable designs (default: 0.9)
- `--config`: Path to JSON config file (optional)

#### Backbone Parameter Generation

```bash
# Generate parameters for 15-residue peptides
python scripts/backbone_sampling_params.py \
  --size 15 \
  --output-dir results/parameters_15res

# Generate optimization parameter combinations
python scripts/backbone_sampling_params.py \
  --size 24 \
  --optimize \
  --output-dir results/optimization_24res
```

**Parameters:**
- `--size, -s`: Peptide size - must be 7, 15, 20, or 24 residues (required)
- `--output-dir, -o`: Output directory (optional)
- `--optimize`: Generate parameter combinations for optimization (flag)
- `--config`: Path to JSON config file (optional)

---

## MCP Server Installation

### Option 1: Using fastmcp (Recommended)

```bash
# Install MCP server for Claude Code
fastmcp install src/server.py --name cyclicchamp-tools
```

### Option 2: Manual Installation for Claude Code

```bash
# Add MCP server to Claude Code
claude mcp add cyclicchamp-tools -- $(pwd)/env/bin/python $(pwd)/src/server.py

# Verify installation
claude mcp list
```

### Option 3: Configure in settings.json

Add to `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "cyclicchamp-tools": {
      "command": "/home/xux/Desktop/CycPepMCP/CycPepMCP/tool-mcps/cyclicchamp_mcp/env/bin/python",
      "args": ["/home/xux/Desktop/CycPepMCP/CycPepMCP/tool-mcps/cyclicchamp_mcp/src/server.py"]
    }
  }
}
```

---

## Using with Claude Code

After installing the MCP server, you can use it directly in Claude Code.

### Quick Start

```bash
# Start Claude Code
claude
```

### Example Prompts

#### Tool Discovery
```
What tools are available from cyclicchamp-tools MCP server? Use get_tool_info to show me all available tools and their categories.
```

#### P_near Analysis (Fast - ~1-2 seconds)
```
Use analyze_pnear_stability to analyze @examples/data/20res_Pnear_list.txt with min_pnear=0.9 and show me the stable designs.
```

#### Sequence Analysis (Fast - ~1-3 seconds)
```
Analyze peptide sequences from @examples/data/results/Pnear_values_15res.txt using analyze_peptide_sequences. Focus only on stable designs and show me amino acid composition patterns.
```

#### Parameter Generation (Fast - <1 second)
```
Generate backbone sampling parameters for 20-residue cyclic peptides using generate_backbone_parameters with optimization enabled.
```

#### Background Job Processing (Submit API)
```
Submit a P_near analysis job for @examples/data/24res_Pnear_list.txt using submit_pnear_analysis with job_name="large_dataset_analysis". Then check the status and get results when completed.
```

#### Batch Processing
```
Process multiple datasets: use submit_batch_pnear_analysis with these files:
- @examples/data/20res_Pnear_list.txt
- @examples/data/24res_Pnear_list.txt
Set output_base_dir to "batch_analysis" and track all jobs.
```

### Using @ References

In Claude Code, use `@` to reference files and directories:

| Reference | Description |
|-----------|-------------|
| `@examples/data/20res_Pnear_list.txt` | Reference 20-residue P_near results |
| `@examples/data/results/Pnear_values_15res.txt` | Reference 15-residue sample data |
| `@configs/pnear_analysis_config.json` | Reference P_near config file |
| `@results/` | Reference output directory |

---

## Using with Gemini CLI

### Configuration

Add to `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "cyclicchamp-tools": {
      "command": "/home/xux/Desktop/CycPepMCP/CycPepMCP/tool-mcps/cyclicchamp_mcp/env/bin/python",
      "args": ["/home/xux/Desktop/CycPepMCP/CycPepMCP/tool-mcps/cyclicchamp_mcp/src/server.py"]
    }
  }
}
```

### Example Prompts

```bash
# Start Gemini CLI
gemini

# Example prompts (same as Claude Code)
> What tools are available from cyclicchamp-tools?
> Analyze P_near stability for large peptide dataset
> Generate backbone parameters for multiple peptide sizes
```

---

### Quick Operations (Sync API - Results in seconds)

These tools return results immediately (< 3 seconds):

| Tool | Description | Parameters |
|------|-------------|------------|
| `analyze_pnear_stability` | Analyze P_near stability metrics with correlation plots | `input_file`, `output_dir`, `min_pnear`, `show_plots`, `config_file` |
| `analyze_peptide_sequences` | Comprehensive sequence composition and properties | `input_file`, `output_dir`, `stable_only`, `min_pnear`, `show_plots`, `config_file` |
| `generate_backbone_parameters` | Generate CyclicChamp sampling parameters | `peptide_size`, `output_dir`, `optimize`, `num_combinations`, `show_plots`, `config_file` |

### Long-Running Tasks (Submit API - Background processing)

These tools return a job_id for tracking:

| Tool | Description | Parameters |
|------|-------------|------------|
| `submit_pnear_analysis` | Submit P_near analysis for background processing | Same as sync + `job_name` |
| `submit_sequence_analysis` | Submit sequence analysis for background processing | Same as sync + `job_name` |
| `submit_backbone_parameter_generation` | Submit parameter generation job | Same as sync + `job_name` |
| `submit_batch_pnear_analysis` | Process multiple P_near files | `input_files`, `output_base_dir`, `min_pnear`, `config_file`, `job_name` |
| `submit_peptide_size_parameter_sweep` | Generate parameters for multiple sizes | `peptide_sizes`, `output_dir`, `optimize_all`, `num_combinations`, `config_file`, `job_name` |

### Job Management Tools

| Tool | Description |
|------|-------------|
| `get_job_status` | Check job progress |
| `get_job_result` | Get results when completed |
| `get_job_log` | View execution logs |
| `cancel_job` | Cancel running job |
| `list_jobs` | List all jobs with optional status filter |

### Utility Tools

| Tool | Description |
|------|-------------|
| `list_available_configs` | Show available configuration files |
| `get_config_contents` | View configuration file contents |
| `get_tool_info` | Get comprehensive tool information |

---

## Examples

### Example 1: Quick P_near Analysis

**Goal:** Analyze stability metrics for cyclic peptide designs

**Using Script:**
```bash
python scripts/pnear_analysis.py \
  --input examples/data/20res_Pnear_list.txt \
  --output-dir results/quick_analysis
```

**Using MCP (in Claude Code):**
```
Analyze P_near stability for @examples/data/20res_Pnear_list.txt with min_pnear=0.9. Show me the correlation between Rosetta and GA methods and identify stable designs.
```

**Expected Output:**
- Correlation plot comparing Rosetta vs GA P_near values
- Energy vs P_near scatter plots for both methods
- Statistical report with stable design counts and top candidates

### Example 2: Sequence Composition Analysis

**Goal:** Understand amino acid patterns in stable cyclic peptides

**Using Script:**
```bash
python scripts/sequence_analysis.py \
  --input examples/data/results/Pnear_values_15res.txt \
  --stable-only \
  --output-dir results/stable_analysis
```

**Using MCP (in Claude Code):**
```
Analyze peptide sequences from @examples/data/results/Pnear_values_15res.txt using analyze_peptide_sequences. Focus only on stable designs (stable_only=true) and show me:
1. Amino acid composition patterns
2. L/D chirality distribution
3. Physicochemical property correlations
```

**Expected Output:**
- 6-panel composition plot (AA frequency, chirality, hydrophobicity, charge, aromatic content, secondary structure preferences)
- 9x9 property correlation heatmap
- Detailed statistical report with sequence insights

### Example 3: CyclicChamp Parameter Generation

**Goal:** Generate optimized backbone sampling parameters for different peptide sizes

**Using Script:**
```bash
python scripts/backbone_sampling_params.py \
  --size 24 \
  --optimize \
  --output-dir results/params_24res
```

**Using MCP (in Claude Code):**
```
Generate backbone sampling parameters for 24-residue cyclic peptides using generate_backbone_parameters with optimize=true and num_combinations=20. Show me the parameter ranges and MATLAB-ready code.
```

**Expected Output:**
- 6-panel parameter visualization (energy thresholds, temperatures, move parameters)
- Complete JSON parameter file
- MATLAB-ready code for CyclicChamp implementation
- 20 optimization parameter combinations

### Example 4: Virtual Screening Pipeline

**Goal:** Screen multiple peptide datasets for stability patterns

**Using MCP (in Claude Code):**
```
I want to analyze multiple cyclic peptide datasets for stability patterns:

1. Use submit_batch_pnear_analysis with these files:
   - @examples/data/20res_Pnear_list.txt
   - @examples/data/24res_Pnear_list.txt
   Set output_base_dir to "screening_results"

2. For each completed analysis, identify designs with:
   - P_near > 0.9 (both Rosetta and GA)
   - Energy < -40 kcal/mol

3. Generate backbone parameters for the most promising peptide sizes
```

### Example 5: End-to-End Stability Assessment

**Goal:** Complete analysis workflow for peptide design validation

**Using MCP (in Claude Code):**
```
For the dataset @examples/data/20res_Pnear_list.txt, perform a complete stability assessment:

1. Analyze P_near stability with min_pnear=0.95
2. For stable designs only, analyze sequence composition patterns
3. Generate backbone sampling parameters for 20-residue peptides with optimization
4. Show me summary statistics and identify the top 5 most stable designs
```

---

## Demo Data

The `examples/data/` directory contains sample data for testing:

| File | Description | Size | Use With |
|------|-------------|------|----------|
| `20res_Pnear_list.txt` | P_near results for 20-residue peptides | 17.5 KB | All P_near and sequence tools |
| `24res_Pnear_list.txt` | P_near results for 24-residue peptides | 133 KB | All P_near and sequence tools |
| `Pnear_list.txt` | Comprehensive P_near dataset | 176 KB | All P_near and sequence tools |
| `results/Pnear_values_15res.txt` | Small 15-residue sample | - | Quick testing |
| `results/Pnear_values_20res.txt` | 20-residue sample | - | Quick testing |
| `results/Pnear_values_24res.txt` | 24-residue sample | - | Quick testing |
| `sequences/l_res.txt` | L-amino acid definitions | - | Sequence analysis reference |
| `sequences/d_res.txt` | D-amino acid definitions | - | Sequence analysis reference |

### Data Format

**P_near files use tab-delimited format:**
```
Name                Energy    P_near_Rosetta    P_near_GA    Sequence
design_001          -45.23    0.95              0.93         ASP-GLU-SER-DLEU-TYR-PRO-...
design_002          -42.15    0.87              0.91         ASP-LEU-SER-DLEU-PHE-GLY-...
```

- **Required columns**: Name, Energy, P_near_Rosetta, P_near_GA, Sequence
- **D-amino acids**: Denoted with D prefix (e.g., DLEU, DPHE, DTYR)
- **Energy units**: kcal/mol
- **P_near range**: 0.0 to 1.0 (>0.9 = stable)

---

## Configuration Files

The `configs/` directory contains configuration templates:

| Config | Description | Key Parameters |
|--------|-------------|-----------------|
| `pnear_analysis_config.json` | P_near analysis settings | `min_pnear: 0.9`, plotting colors, figure sizes |
| `sequence_analysis_config.json` | Sequence analysis settings | AA properties, hydrophobic thresholds, polar residues |
| `backbone_sampling_config.json` | Parameter formulas | Mathematical formulas, cooling rates, optimization |
| `default_config.json` | Global defaults | Output format, DPI, stability thresholds |

### Config Example

```json
{
  "analysis": {
    "min_pnear": 0.9,
    "stable_only": false
  },
  "output": {
    "format": "png",
    "plot_dpi": 300
  },
  "plotting": {
    "figure_size": [10, 8],
    "alpha": 0.6
  },
  "colors": {
    "rosetta": "blue",
    "ga": "orange"
  }
}
```

---

## Troubleshooting

### Environment Issues

**Problem:** Environment not found
```bash
# Recreate environment
mamba create -p ./env python=3.12 pip -y
mamba activate ./env
mamba run -p ./env pip install matplotlib numpy scipy loguru click pandas tqdm
mamba run -p ./env pip install --force-reinstall --no-cache-dir fastmcp
```

**Problem:** Import errors
```bash
# Verify installation
mamba run -p ./env python -c "import numpy; import matplotlib; import scipy; import fastmcp; print('All imports successful')"

# Test script functions
mamba run -p ./env python -c "from scripts.pnear_analysis import run_pnear_analysis; print('Scripts ready')"
```

**Problem:** Package conflicts
```bash
# Clean installation
mamba clean --all
mamba create -p ./env python=3.12 pip -y --force
# Reinstall packages as above
```

### MCP Issues

**Problem:** Server not found in Claude Code
```bash
# Check MCP registration
claude mcp list

# Re-add if needed
claude mcp remove cyclicchamp-tools
claude mcp add cyclicchamp-tools -- $(pwd)/env/bin/python $(pwd)/src/server.py
```

**Problem:** Tools not working in Claude Code
```bash
# Test server directly
mamba run -p ./env python -c "
import sys
sys.path.insert(0, 'src')
from server import mcp
print('Server imports OK')
"

# Start dev server to check for errors
mamba run -p ./env fastmcp dev src/server.py
```

**Problem:** File path errors
```
Use absolute paths or @ references in Claude Code:
- @examples/data/20res_Pnear_list.txt ✓
- examples/data/20res_Pnear_list.txt ✗
```

### Data Issues

**Problem:** Invalid P_near file format
```
Ensure your P_near file has these exact columns (tab-separated):
Name    Energy    P_near_Rosetta    P_near_GA    Sequence

Check file with: head -1 your_file.txt
```

**Problem:** Missing demo data
```bash
# Check if demo files exist
ls -la examples/data/
ls -la examples/data/results/

# Files should include:
# - 20res_Pnear_list.txt
# - 24res_Pnear_list.txt
# - Pnear_list.txt
```

### Job Issues

**Problem:** Job stuck in pending status
```bash
# Check job directory
ls -la jobs/

# View job log
tail -20 jobs/<job_id>/job.log
```

**Problem:** Job failed
```
Use get_job_log with job_id to see error details:
get_job_log(job_id="<job_id>", tail=100)
```

**Problem:** Job not found
```
Use list_jobs() to see all available job IDs:
list_jobs()
```

---

## Development

### Running Tests

```bash
# Activate environment
mamba activate ./env

# Run server tests
python test_server.py

# Test individual scripts
python scripts/pnear_analysis.py --input examples/data/results/Pnear_values_15res.txt
python scripts/sequence_analysis.py --input examples/data/results/Pnear_values_15res.txt
python scripts/backbone_sampling_params.py --size 15
```

### Starting Dev Server

```bash
# Run MCP server in dev mode
mamba run -p ./env fastmcp dev src/server.py

# Check server logs
# Dev server will show inspector URL for testing tools
```

---

## Performance

### Expected Performance

| Tool | Dataset Size | Runtime | Memory | Output Files |
|------|--------------|---------|--------|--------------|
| `analyze_pnear_stability` | 100 designs | ~1 sec | 10 MB | 3 files |
| `analyze_pnear_stability` | 1000 designs | ~2 sec | 50 MB | 3 files |
| `analyze_peptide_sequences` | 100 sequences | ~1 sec | 15 MB | 3 files |
| `analyze_peptide_sequences` | 1000 sequences | ~3 sec | 75 MB | 3 files |
| `generate_backbone_parameters` | Any size | <1 sec | 5 MB | 3-5 files |

### Memory Requirements
- **Minimum**: 500 MB RAM for basic analysis
- **Recommended**: 2 GB RAM for large datasets (>1000 designs)
- **Disk Space**: ~10 MB per analysis output

---

## License

Based on the original CyclicChamp methodology. See the repo/ directory for original implementation details.

## Credits

Based on [CyclicChamp](https://github.com/ichen-lab-ucsb/CyclicChamp) - Heuristic energy-based cyclic peptide design
Original repository structure and algorithms by the Chen Lab, UC Santa Barbara
MCP implementation and tool extraction by Claude Sonnet 4

---

**Total MCP Tools Available: 16**
- 5 Job Management Tools
- 3 Sync Analysis Tools
- 5 Submit/Batch Tools
- 3 Utility Tools

**Ready for Claude Code and Gemini CLI integration**
