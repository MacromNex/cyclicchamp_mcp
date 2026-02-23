# CyclicChamp MCP Examples

This directory contains example use case scripts and demo data for the CyclicChamp MCP tool.

## Available Use Cases

### Use Case 1: P_near Analysis (`use_case_1_pnear_analysis.py`)

Analyzes P_near stability metrics for cyclic peptide designs from CyclicChamp.

**Description**: P_near is a stability metric that combines RMSD and energy to assess design quality. Values > 0.9 indicate stable designs.

**Usage**:
```bash
python examples/use_case_1_pnear_analysis.py --input examples/data/results/Pnear_values_15res.txt
python examples/use_case_1_pnear_analysis.py --input examples/data/results/Pnear_values_20res.txt --min-pnear 0.8
```

**Outputs**:
- P_near correlation plots (Rosetta vs GA)
- Energy vs P_near scatter plots
- Analysis report with statistics

### Use Case 2: Sequence Analysis (`use_case_2_sequence_analysis.py`)

Analyzes cyclic peptide sequences including amino acid composition, chirality patterns, and physicochemical properties.

**Description**: Comprehensive sequence analysis including L/D chirality distribution, hydrophobicity, charge, and property correlations.

**Usage**:
```bash
python examples/use_case_2_sequence_analysis.py --input examples/data/results/Pnear_values_15res.txt
python examples/use_case_2_sequence_analysis.py --input examples/data/results/Pnear_values_20res.txt --stable-only
```

**Outputs**:
- Amino acid composition plots
- Physicochemical property correlations
- Sequence analysis report

### Use Case 3: Backbone Sampling Parameters (`use_case_3_backbone_sampling_params.py`)

Calculates and optimizes CyclicChamp backbone sampling parameters for different peptide sizes.

**Description**: Generates parameter sets for simulated annealing backbone sampling based on CyclicChamp methodology.

**Usage**:
```bash
python examples/use_case_3_backbone_sampling_params.py --size 15
python examples/use_case_3_backbone_sampling_params.py --size 20 --optimize
```

**Outputs**:
- Parameter summary plots
- MATLAB-ready parameter files
- Optimization parameter combinations

## Demo Data

### Input Data (`examples/data/`)

- **Results** (`examples/data/results/`):
  - `Pnear_values_15res.txt`: P_near results for 15-residue peptides
  - `Pnear_values_20res.txt`: P_near results for 20-residue peptides
  - `Pnear_values_24res.txt`: P_near results for 24-residue peptides

- **Sequences** (`examples/data/sequences/`):
  - `l_res.txt`: L-amino acid types
  - `d_res.txt`: D-amino acid types

- **Structures** (`examples/data/structures/`):
  - Sample PDB files of cluster centers

- **Lists** (`examples/data/`):
  - `Pnear_list.txt`: List of designs for analysis
  - Various size-specific lists

### Example Data Format

**P_near results file format**:
```
Name				Energy		Rosetta		GA		Sequence
clustercenter169032		-37.788		0.958		0.889		DTYR-DILE-DGLU-PRO-DVAL-ILE-PRO-SER-DSER-DGLU-PRO-TYR-DLYS-GLU-SER
```

- **Name**: Design identifier
- **Energy**: Rosetta energy (kcal/mol)
- **Rosetta**: P_near value from Rosetta sampling
- **GA**: P_near value from genetic algorithm sampling
- **Sequence**: Amino acid sequence (D-prefix indicates D-amino acid)

## Quick Start

1. **Activate the environment**:
   ```bash
   mamba activate ./env
   ```

2. **Run a basic P_near analysis**:
   ```bash
   python examples/use_case_1_pnear_analysis.py --input examples/data/results/Pnear_values_15res.txt
   ```

3. **Analyze sequences for stable designs only**:
   ```bash
   python examples/use_case_2_sequence_analysis.py --input examples/data/results/Pnear_values_15res.txt --stable-only
   ```

4. **Generate parameters for 20-residue peptides**:
   ```bash
   python examples/use_case_3_backbone_sampling_params.py --size 20
   ```

## Understanding the CyclicChamp Pipeline

The CyclicChamp methodology involves:

1. **Backbone Sampling**: Generate diverse backbone conformations using simulated annealing
2. **Clustering**: Group similar backbones into clusters
3. **Relaxation**: Energy minimize cluster centers with Rosetta FastRelax
4. **Design**: Add side chains using Rosetta FastDesign
5. **Validation**: Test design stability using P_near energy landscape analysis

## Output Files

Each use case generates multiple output files:

- **Plots**: PNG files with visualizations
- **Reports**: TXT files with detailed analysis
- **Data**: JSON/CSV files with processed results

All outputs are saved to `examples/data/results/` by default.

## Dependencies

Required packages (installed in the conda environment):
- numpy
- matplotlib
- pandas
- scipy

## Citation

If you use CyclicChamp in your research, please cite:

Zhu, Q., Mulligan, V. K., & Shasha, D. "Heuristic energy-based cyclic peptide design". [Paper details]