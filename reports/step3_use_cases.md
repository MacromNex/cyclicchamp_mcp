# Step 3: Use Cases Report

## Scan Information
- **Scan Date**: 2025-12-31
- **Filter Applied**: cyclic peptide backbone sampling using CyclicChamp simulated annealing, large rings up to 24 residues, mixed chirality
- **Python Version**: 3.12
- **Environment Strategy**: single
- **Repository Type**: CyclicChamp - heuristic energy-based cyclic peptide design

## Use Cases

### UC-001: P_near Stability Analysis
- **Description**: Analyzes P_near stability metrics for cyclic peptide designs from CyclicChamp results. P_near combines RMSD and energy to assess design quality (>0.9 = stable).
- **Script Path**: `examples/use_case_1_pnear_analysis.py`
- **Complexity**: medium
- **Priority**: high
- **Environment**: `./env`
- **Source**: `repo/CyclicPeptide/Clustercenters_15res/Pnear_15res.py`, README.md methodology

**Inputs:**
| Name | Type | Description | Parameter |
|------|------|-------------|----------|
| input_file | file | P_near results file (Pnear_values_*.txt) | --input, -i |
| min_pnear | float | Minimum P_near threshold for stable designs | --min-pnear, -p |
| output_dir | string | Output directory for plots and reports | --output-dir, -o |

**Outputs:**
| Name | Type | Description |
|------|------|-------------|
| correlation_plot | PNG | P_near correlation: Rosetta vs GA |
| energy_plots | PNG | Energy vs P_near scatter plots |
| analysis_report | TXT | Statistical analysis and top designs |

**Example Usage:**
```bash
python examples/use_case_1_pnear_analysis.py --input examples/data/results/Pnear_values_15res.txt
python examples/use_case_1_pnear_analysis.py --input examples/data/results/Pnear_values_20res.txt --min-pnear 0.8
```

**Example Data**: `examples/data/results/Pnear_values_15res.txt`, `Pnear_values_20res.txt`, `Pnear_values_24res.txt`

---

### UC-002: Sequence Composition Analysis
- **Description**: Comprehensive analysis of cyclic peptide sequences including amino acid composition, L/D chirality patterns, and physicochemical properties correlation with stability.
- **Script Path**: `examples/use_case_2_sequence_analysis.py`
- **Complexity**: medium
- **Priority**: high
- **Environment**: `./env`
- **Source**: Sequence parsing from P_near results, chirality analysis methodology

**Inputs:**
| Name | Type | Description | Parameter |
|------|------|-------------|----------|
| input_file | file | P_near results file with sequences | --input, -i |
| stable_only | flag | Analyze only stable designs (P_near > 0.9) | --stable-only |
| min_pnear | float | P_near threshold for stable designs | --min-pnear, -p |
| output_dir | string | Output directory | --output-dir, -o |

**Outputs:**
| Name | Type | Description |
|------|------|-------------|
| composition_plots | PNG | AA composition and chirality distribution |
| properties_correlation | PNG | Physicochemical properties correlation matrix |
| sequence_report | TXT | Statistics and property analysis |

**Example Usage:**
```bash
python examples/use_case_2_sequence_analysis.py --input examples/data/results/Pnear_values_15res.txt --stable-only
python examples/use_case_2_sequence_analysis.py --input examples/data/results/Pnear_values_24res.txt
```

**Example Data**: Uses same P_near result files, analyzes embedded sequence strings

---

### UC-003: Backbone Sampling Parameter Optimization
- **Description**: Generates and optimizes CyclicChamp backbone sampling parameters for different peptide sizes (7, 15, 20, 24 residues) using the paper's formulas for simulated annealing.
- **Script Path**: `examples/use_case_3_backbone_sampling_params.py`
- **Complexity**: simple
- **Priority**: medium
- **Environment**: `./env`
- **Source**: `repo/CyclicPeptide/Energy_15residue.m`, parameter formulas from README.md

**Inputs:**
| Name | Type | Description | Parameter |
|------|------|-------------|----------|
| size | int | Peptide size (7, 15, 20, or 24) | --size, -s |
| optimize | flag | Generate parameter combinations | --optimize |
| output_dir | string | Output directory | --output-dir, -o |

**Outputs:**
| Name | Type | Description |
|------|------|-------------|
| parameters_summary | PNG | Energy thresholds and temperature schedules |
| parameters_json | JSON | Complete parameter set |
| matlab_code | TXT | Ready-to-use MATLAB parameters |
| optimization_combinations | JSON | Parameter sets for optimization (if --optimize) |

**Example Usage:**
```bash
python examples/use_case_3_backbone_sampling_params.py --size 15
python examples/use_case_3_backbone_sampling_params.py --size 20 --optimize
python examples/use_case_3_backbone_sampling_params.py --size 24 --output-dir custom_output
```

**Example Data**: Uses mathematical formulas, no external data required

---

## Summary

| Metric | Count |
|--------|-------|
| Total Found | 3 |
| Scripts Created | 3 |
| High Priority | 2 |
| Medium Priority | 1 |
| Low Priority | 0 |
| Demo Data Copied | Yes |

## Demo Data Index

| Source | Destination | Description |
|--------|-------------|-------------|
| `repo/CyclicPeptide/GoodDesigns/15res_CyclicChamp/Pnear_values_15res.txt` | `examples/data/results/Pnear_values_15res.txt` | P_near results for 15-residue peptides |
| `repo/CyclicPeptide/GoodDesigns/20res_CyclicChamp/Pnear_values_20res.txt` | `examples/data/results/Pnear_values_20res.txt` | P_near results for 20-residue peptides |
| `repo/CyclicPeptide/GoodDesigns/24res_CyclicChamp/Pnear_values_24res.txt` | `examples/data/results/Pnear_values_24res.txt` | P_near results for 24-residue peptides |
| `repo/CyclicPeptide/l_res.txt` | `examples/data/sequences/l_res.txt` | L-amino acid types |
| `repo/CyclicPeptide/d_res.txt` | `examples/data/sequences/d_res.txt` | D-amino acid types |
| `repo/CyclicPeptide/Clustercenters_15res/*.pdb` | `examples/data/structures/` | Sample cluster center PDB structures |
| `repo/CyclicPeptide/Clustercenters_15res/Pnear_list.txt` | `examples/data/Pnear_list.txt` | Design list for 15-residue peptides |
| `repo/CyclicPeptide/Clustercenters_20res/Pnear_list.txt` | `examples/data/20res_Pnear_list.txt` | Design list for 20-residue peptides |
| `repo/CyclicPeptide/Clustercenters_24res/Pnear_list.txt` | `examples/data/24res_Pnear_list.txt` | Design list for 24-residue peptides |

## Use Case Focus Areas

**CyclicChamp-Specific Capabilities Covered:**
1. **Simulated Annealing Parameters**: UC-003 implements the exact parameter calculation formulas
2. **Mixed Chirality Analysis**: UC-002 analyzes L/D amino acid patterns in designs
3. **Energy Landscape Stability**: UC-001 focuses on P_near stability metric analysis
4. **Large Ring Support**: All use cases support 7, 15, 20, and 24-residue peptides

**MCP Tool Potential:**
- **Real-time Analysis**: Convert scripts to MCP tools for interactive analysis
- **Parameter Optimization**: Web interface for parameter tuning
- **Design Exploration**: Interactive P_near and sequence filtering
- **Comparison Tools**: Compare different peptide sizes and methods

## Technical Notes

- **Python Environment**: All scripts use standard scientific Python (numpy, matplotlib, pandas, scipy)
- **Data Format**: P_near files use tab-separated format with sequence strings
- **Sequence Parsing**: Custom parser handles D-amino acid prefix notation (e.g., "DTYR-PRO-SER")
- **Parameter Formulas**: Mathematical implementation of CyclicChamp paper formulas
- **Visualization**: Comprehensive plotting for analysis and reporting