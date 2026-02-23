#!/usr/bin/env python3
"""
Script: sequence_analysis.py
Description: Analyze cyclic peptide sequences including amino acid composition, chirality, and properties

Original Use Case: examples/use_case_2_sequence_analysis.py
Dependencies Removed: None (already minimal)

Usage:
    python scripts/sequence_analysis.py --input <input_file> --output-dir <output_dir>

Example:
    python scripts/sequence_analysis.py --input examples/data/results/Pnear_values_15res.txt --output-dir results/
"""

# ==============================================================================
# Minimal Imports (only essential packages)
# ==============================================================================
import argparse
import json
import os
import sys
from collections import Counter
from pathlib import Path
from typing import Union, Optional, Dict, Any, List, Tuple

# Essential scientific packages
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ==============================================================================
# Configuration (extracted from use case)
# ==============================================================================
DEFAULT_CONFIG = {
    "min_pnear": 0.9,
    "stable_only": False,
    "output_format": "png",
    "plot_dpi": 300,
    "show_plots": False,
    "max_top_designs": 10
}

# ==============================================================================
# Inlined Utility Functions (simplified from standard amino acid processing)
# ==============================================================================
def parse_sequence(sequence_str: str) -> Tuple[List[str], List[str]]:
    """Parse a sequence string like 'ASP-GLU-SER-DLEU-TYR' into amino acids and chirality."""
    residues = sequence_str.split('-')
    amino_acids = []
    chiralities = []

    # Standard amino acid mapping
    aa_map = {
        'ALA': 'A', 'ARG': 'R', 'ASN': 'N', 'ASP': 'D', 'CYS': 'C',
        'GLN': 'Q', 'GLU': 'E', 'GLY': 'G', 'HIS': 'H', 'ILE': 'I',
        'LEU': 'L', 'LYS': 'K', 'MET': 'M', 'PHE': 'F', 'PRO': 'P',
        'SER': 'S', 'THR': 'T', 'TRP': 'W', 'TYR': 'Y', 'VAL': 'V'
    }

    for res in residues:
        if res.startswith('D'):  # D-amino acid
            aa_name = res[1:]  # Remove 'D' prefix
            chiralities.append('D')
        else:  # L-amino acid
            aa_name = res
            chiralities.append('L')

        # Convert to single letter code
        if aa_name in aa_map:
            amino_acids.append(aa_map[aa_name])
        else:
            amino_acids.append('X')  # Unknown amino acid

    return amino_acids, chiralities

def calculate_physicochemical_properties(amino_acids: List[str]) -> Dict[str, float]:
    """Calculate basic physicochemical properties of the peptide."""

    # Amino acid properties (Kyte-Doolittle hydrophobicity scale)
    hydrophobicity = {
        'A': 1.8, 'R': -4.5, 'N': -3.5, 'D': -3.5, 'C': 2.5,
        'Q': -3.5, 'E': -3.5, 'G': -0.4, 'H': -3.2, 'I': 4.5,
        'L': 3.8, 'K': -3.9, 'M': 1.9, 'F': 2.8, 'P': -1.6,
        'S': -0.8, 'T': -0.7, 'W': -0.9, 'Y': -1.3, 'V': 4.2,
        'X': 0.0
    }

    # Charge at physiological pH
    charge = {
        'A': 0, 'R': 1, 'N': 0, 'D': -1, 'C': 0,
        'Q': 0, 'E': -1, 'G': 0, 'H': 0.5, 'I': 0,
        'L': 0, 'K': 1, 'M': 0, 'F': 0, 'P': 0,
        'S': 0, 'T': 0, 'W': 0, 'Y': 0, 'V': 0,
        'X': 0
    }

    properties = {
        'length': len(amino_acids),
        'hydrophobicity': np.mean([hydrophobicity[aa] for aa in amino_acids]),
        'net_charge': sum(charge[aa] for aa in amino_acids),
        'charged_residues': sum(1 for aa in amino_acids if abs(charge[aa]) >= 1),
        'hydrophobic_residues': sum(1 for aa in amino_acids if hydrophobicity[aa] > 2.0),
        'polar_residues': sum(1 for aa in amino_acids if aa in 'STNQDE'),
        'aromatic_residues': sum(1 for aa in amino_acids if aa in 'FWY'),
        'proline_count': amino_acids.count('P')
    }

    return properties

# ==============================================================================
# Core Function (main logic extracted from use case)
# ==============================================================================
def run_sequence_analysis(
    input_file: Union[str, Path],
    output_dir: Optional[Union[str, Path]] = None,
    config: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Analyze cyclic peptide sequences from CyclicChamp designs.

    Args:
        input_file: Path to Pnear_values_*.txt file
        output_dir: Directory to save output plots and reports (optional)
        config: Configuration dict (uses DEFAULT_CONFIG if not provided)
        **kwargs: Override specific config parameters

    Returns:
        Dict containing:
            - sequence_data: DataFrame with sequence analysis results
            - amino_acid_composition: Counter of amino acid frequencies
            - chirality_distribution: Counter of L/D amino acid frequencies
            - output_files: List of generated output files

    Example:
        >>> result = run_sequence_analysis("input.txt", "results/")
        >>> print(f"Analyzed {len(result['sequence_data'])} sequences")
    """
    # Setup
    input_file = Path(input_file)
    config = {**DEFAULT_CONFIG, **(config or {}), **kwargs}
    stable_only = config['stable_only']
    min_pnear = config['min_pnear']

    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    # Set output directory
    if output_dir is None:
        output_dir = input_file.parent / "sequence_analysis_results"
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Read the data
    designs = []
    energies = []
    pnear_ga = []
    sequences = []

    with open(input_file, 'r') as f:
        lines = f.readlines()

    # Parse the file (handle double tabs by filtering empty strings)
    for line in lines:
        if line.strip() and not line.startswith('Name'):
            parts = [p for p in line.strip().split('\t') if p]  # Filter out empty strings
            if len(parts) >= 5:
                try:
                    designs.append(parts[0])
                    energies.append(float(parts[1]))
                    pnear_ga.append(float(parts[3]))  # Use GA P_near
                    sequences.append(parts[4])
                except ValueError:
                    continue

    # Filter for stable designs if requested
    if stable_only:
        stable_indices = [i for i, p in enumerate(pnear_ga) if p > min_pnear]
        designs = [designs[i] for i in stable_indices]
        energies = [energies[i] for i in stable_indices]
        pnear_ga = [pnear_ga[i] for i in stable_indices]
        sequences = [sequences[i] for i in stable_indices]

    if len(sequences) == 0:
        raise ValueError("No sequences found to analyze!")

    # Analyze each sequence
    sequence_data = []
    all_amino_acids = []
    all_chiralities = []

    for i, seq in enumerate(sequences):
        amino_acids, chiralities = parse_sequence(seq)
        properties = calculate_physicochemical_properties(amino_acids)

        sequence_data.append({
            'design': designs[i],
            'energy': energies[i],
            'pnear_ga': pnear_ga[i],
            'sequence': seq,
            'length': properties['length'],
            'hydrophobicity': properties['hydrophobicity'],
            'net_charge': properties['net_charge'],
            'charged_residues': properties['charged_residues'],
            'hydrophobic_residues': properties['hydrophobic_residues'],
            'polar_residues': properties['polar_residues'],
            'aromatic_residues': properties['aromatic_residues'],
            'proline_count': properties['proline_count'],
            'd_residues': chiralities.count('D'),
            'l_residues': chiralities.count('L'),
            'd_fraction': chiralities.count('D') / len(chiralities)
        })

        all_amino_acids.extend(amino_acids)
        all_chiralities.extend(chiralities)

    # Convert to DataFrame for easier analysis
    df = pd.DataFrame(sequence_data)

    # Generate composition counters
    aa_counts = Counter(all_amino_acids)
    chiral_counts = Counter(all_chiralities)

    output_files = []

    # Generate plots
    # Amino acid composition and properties
    plt.figure(figsize=(15, 10))

    plt.subplot(2, 3, 1)
    aa_names = list(aa_counts.keys())
    aa_freqs = list(aa_counts.values())
    plt.bar(aa_names, aa_freqs, alpha=0.7)
    plt.title('Amino Acid Composition')
    plt.xlabel('Amino Acid')
    plt.ylabel('Frequency')
    plt.xticks(rotation=45)

    plt.subplot(2, 3, 2)
    plt.bar(chiral_counts.keys(), chiral_counts.values(), alpha=0.7, color=['orange', 'green'])
    plt.title('Chirality Distribution')
    plt.xlabel('Chirality')
    plt.ylabel('Frequency')

    plt.subplot(2, 3, 3)
    plt.hist(df['d_fraction'], bins=15, alpha=0.7, edgecolor='black')
    plt.title('D-amino Acid Fraction Distribution')
    plt.xlabel('Fraction of D-amino acids')
    plt.ylabel('Number of Sequences')

    plt.subplot(2, 3, 4)
    plt.scatter(df['hydrophobicity'], df['pnear_ga'], alpha=0.6)
    plt.xlabel('Average Hydrophobicity')
    plt.ylabel('P_near (GA)')
    plt.title('Hydrophobicity vs P_near')

    plt.subplot(2, 3, 5)
    plt.scatter(df['net_charge'], df['pnear_ga'], alpha=0.6)
    plt.xlabel('Net Charge')
    plt.ylabel('P_near (GA)')
    plt.title('Net Charge vs P_near')

    plt.subplot(2, 3, 6)
    plt.scatter(df['proline_count'], df['pnear_ga'], alpha=0.6)
    plt.xlabel('Proline Count')
    plt.ylabel('P_near (GA)')
    plt.title('Proline Content vs P_near')

    plt.tight_layout()
    suffix = "_stable" if stable_only else "_all"
    output_file = output_path / f"sequence_analysis_{input_file.stem}{suffix}.png"
    plt.savefig(output_file, dpi=config['plot_dpi'], bbox_inches='tight')
    output_files.append(str(output_file))

    if config['show_plots']:
        plt.show()
    plt.close()

    # Physicochemical properties correlation matrix
    plt.figure(figsize=(10, 8))
    property_cols = ['hydrophobicity', 'net_charge', 'charged_residues',
                     'hydrophobic_residues', 'polar_residues', 'aromatic_residues',
                     'proline_count', 'd_fraction', 'pnear_ga']
    corr_matrix = df[property_cols].corr()

    plt.imshow(corr_matrix, cmap='coolwarm', aspect='auto', vmin=-1, vmax=1)
    plt.colorbar(label='Correlation')
    plt.xticks(range(len(property_cols)), property_cols, rotation=45)
    plt.yticks(range(len(property_cols)), property_cols)
    plt.title('Physicochemical Properties Correlation Matrix')

    # Add correlation values to the plot
    for i in range(len(property_cols)):
        for j in range(len(property_cols)):
            plt.text(j, i, f'{corr_matrix.iloc[i, j]:.2f}',
                    ha='center', va='center', color='black' if abs(corr_matrix.iloc[i, j]) < 0.5 else 'white')

    plt.tight_layout()
    output_file = output_path / f"properties_correlation_{input_file.stem}{suffix}.png"
    plt.savefig(output_file, dpi=config['plot_dpi'], bbox_inches='tight')
    output_files.append(str(output_file))

    if config['show_plots']:
        plt.show()
    plt.close()

    # Generate summary report
    report_file = output_path / f"sequence_analysis_report_{input_file.stem}{suffix}.txt"
    with open(report_file, 'w') as f:
        f.write(f"Sequence Analysis Report\n")
        f.write(f"=" * 50 + "\n\n")
        f.write(f"Input file: {input_file}\n")
        f.write(f"Analysis mode: {'Stable designs only' if stable_only else 'All designs'}\n")
        f.write(f"Number of sequences: {len(sequences)}\n\n")

        f.write(f"Amino Acid Composition:\n")
        for aa, count in sorted(aa_counts.items()):
            f.write(f"  {aa}: {count:3d} ({count/len(all_amino_acids)*100:.1f}%)\n")

        f.write(f"\nChirality Distribution:\n")
        for chiral, count in chiral_counts.items():
            f.write(f"  {chiral}-amino acids: {count:3d} ({count/len(all_chiralities)*100:.1f}%)\n")

        f.write(f"\nPhysicochemical Properties (Mean ± Std):\n")
        for prop in ['hydrophobicity', 'net_charge', 'charged_residues',
                     'hydrophobic_residues', 'polar_residues', 'aromatic_residues',
                     'proline_count', 'd_fraction']:
            mean_val = df[prop].mean()
            std_val = df[prop].std()
            f.write(f"  {prop:20s}: {mean_val:6.2f} ± {std_val:.2f}\n")

        f.write(f"\nCorrelation with P_near (GA):\n")
        for prop in ['hydrophobicity', 'net_charge', 'd_fraction', 'proline_count']:
            corr = df[prop].corr(df['pnear_ga'])
            f.write(f"  {prop:20s}: {corr:6.3f}\n")

    output_files.append(str(report_file))

    return {
        'sequence_data': df,
        'amino_acid_composition': aa_counts,
        'chirality_distribution': chiral_counts,
        'output_files': output_files,
        'metadata': {
            'input_file': str(input_file),
            'output_dir': str(output_path),
            'config': config,
            'total_sequences': len(sequences),
            'analysis_mode': 'stable_only' if stable_only else 'all_designs'
        }
    }

# ==============================================================================
# CLI Interface
# ==============================================================================
def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('--input', '-i', required=True, help='Input Pnear_values_*.txt file path')
    parser.add_argument('--output-dir', '-o', help='Output directory path')
    parser.add_argument('--config', '-c', help='Config file (JSON)')
    parser.add_argument('--stable-only', action='store_true',
                       help='Analyze only stable designs (P_near > threshold)')
    parser.add_argument('--min-pnear', '-p', type=float, default=0.9,
                       help='Minimum P_near threshold for stable designs (default: 0.9)')
    parser.add_argument('--show-plots', action='store_true', help='Show plots interactively')

    args = parser.parse_args()

    # Load config if provided
    config = None
    if args.config:
        with open(args.config) as f:
            config = json.load(f)

    # Override config with command line arguments
    if config is None:
        config = {}
    config.update({
        'stable_only': args.stable_only,
        'min_pnear': args.min_pnear,
        'show_plots': args.show_plots
    })

    try:
        # Run analysis
        result = run_sequence_analysis(
            input_file=args.input,
            output_dir=args.output_dir,
            config=config
        )

        print(f"Sequence Analysis completed successfully!")
        print(f"Total sequences: {result['metadata']['total_sequences']}")
        print(f"Analysis mode: {result['metadata']['analysis_mode']}")
        print(f"Amino acids found: {list(result['amino_acid_composition'].keys())}")
        print(f"Output files generated: {len(result['output_files'])}")
        print(f"Results saved to: {result['metadata']['output_dir']}")

        return result

    except Exception as e:
        print(f"Error during analysis: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()