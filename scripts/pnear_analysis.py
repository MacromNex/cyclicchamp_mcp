#!/usr/bin/env python3
"""
Script: pnear_analysis.py
Description: Analyze P_near stability values for cyclic peptide designs

Original Use Case: examples/use_case_1_pnear_analysis.py
Dependencies Removed: None (already minimal)

Usage:
    python scripts/pnear_analysis.py --input <input_file> --output-dir <output_dir>

Example:
    python scripts/pnear_analysis.py --input examples/data/results/Pnear_values_15res.txt --output-dir results/
"""

# ==============================================================================
# Minimal Imports (only essential packages)
# ==============================================================================
import argparse
import json
import os
import sys
from pathlib import Path
from typing import Union, Optional, Dict, Any, List

# Essential scientific packages
import numpy as np
import matplotlib.pyplot as plt

# ==============================================================================
# Configuration (extracted from use case)
# ==============================================================================
DEFAULT_CONFIG = {
    "min_pnear": 0.9,
    "output_format": "png",
    "plot_dpi": 300,
    "show_plots": False
}

# ==============================================================================
# Core Function (main logic extracted from use case)
# ==============================================================================
def run_pnear_analysis(
    input_file: Union[str, Path],
    output_dir: Optional[Union[str, Path]] = None,
    config: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Analyze P_near values from CyclicChamp results.

    Args:
        input_file: Path to Pnear_values_*.txt file
        output_dir: Directory to save output plots and reports (optional)
        config: Configuration dict (uses DEFAULT_CONFIG if not provided)
        **kwargs: Override specific config parameters

    Returns:
        Dict containing:
            - designs: List of design names
            - energies: Array of energy values
            - pnear_rosetta: Array of P_near values (Rosetta method)
            - pnear_ga: Array of P_near values (GA method)
            - sequences: List of peptide sequences
            - stable_designs_rosetta: Indices of stable designs (Rosetta)
            - stable_designs_ga: Indices of stable designs (GA)
            - output_files: List of generated output files

    Example:
        >>> result = run_pnear_analysis("input.txt", "results/")
        >>> print(f"Found {len(result['stable_designs_ga'])} stable designs")
    """
    # Setup
    input_file = Path(input_file)
    config = {**DEFAULT_CONFIG, **(config or {}), **kwargs}
    min_pnear = config['min_pnear']

    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    # Set output directory
    if output_dir is None:
        output_dir = input_file.parent / "analysis_results"
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Read the P_near data
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

    # Convert to numpy arrays
    energies = np.array(energies)
    pnear_rosetta = np.array(pnear_rosetta)
    pnear_ga = np.array(pnear_ga)

    if len(energies) == 0:
        raise ValueError("No valid designs found in the input file!")

    # Find stable designs
    stable_designs_rosetta = np.where(pnear_rosetta > min_pnear)[0]
    stable_designs_ga = np.where(pnear_ga > min_pnear)[0]

    output_files = []

    # Create visualizations
    # P_near comparison plot
    plt.figure(figsize=(10, 8))
    plt.scatter(pnear_rosetta, pnear_ga, alpha=0.6, s=50)
    plt.axhline(y=min_pnear, color='red', linestyle='--', linewidth=2, label=f'P_near = {min_pnear}')
    plt.axvline(x=min_pnear, color='red', linestyle='--', linewidth=2)
    plt.xlabel('P_near (Rosetta)')
    plt.ylabel('P_near (GA)')
    plt.title('P_near Correlation: Rosetta vs Genetic Algorithm')
    plt.legend()
    plt.grid(True, alpha=0.3)

    # Highlight stable designs
    stable_both = np.intersect1d(stable_designs_rosetta, stable_designs_ga)
    if len(stable_both) > 0:
        plt.scatter(pnear_rosetta[stable_both], pnear_ga[stable_both],
                   color='green', s=100, alpha=0.8, label=f'Stable in both ({len(stable_both)})')
        plt.legend()

    output_file = output_path / f"pnear_correlation_{input_file.stem}.png"
    plt.savefig(output_file, dpi=config['plot_dpi'], bbox_inches='tight')
    output_files.append(str(output_file))

    if config['show_plots']:
        plt.show()
    plt.close()

    # Energy vs P_near plot
    plt.figure(figsize=(12, 6))

    plt.subplot(1, 2, 1)
    plt.scatter(energies, pnear_rosetta, alpha=0.6, s=50, color='blue')
    plt.axhline(y=min_pnear, color='red', linestyle='--', linewidth=2)
    plt.xlabel('Energy (kcal/mol)')
    plt.ylabel('P_near (Rosetta)')
    plt.title('Energy vs P_near (Rosetta)')
    plt.grid(True, alpha=0.3)

    plt.subplot(1, 2, 2)
    plt.scatter(energies, pnear_ga, alpha=0.6, s=50, color='orange')
    plt.axhline(y=min_pnear, color='red', linestyle='--', linewidth=2)
    plt.xlabel('Energy (kcal/mol)')
    plt.ylabel('P_near (GA)')
    plt.title('Energy vs P_near (GA)')
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    output_file = output_path / f"energy_vs_pnear_{input_file.stem}.png"
    plt.savefig(output_file, dpi=config['plot_dpi'], bbox_inches='tight')
    output_files.append(str(output_file))

    if config['show_plots']:
        plt.show()
    plt.close()

    # Generate summary report
    report_file = output_path / f"analysis_report_{input_file.stem}.txt"
    with open(report_file, 'w') as f:
        f.write(f"P_near Analysis Report\n")
        f.write(f"=" * 50 + "\n\n")
        f.write(f"Input file: {input_file}\n")
        f.write(f"Total designs analyzed: {len(designs)}\n")
        f.write(f"P_near threshold: {min_pnear}\n\n")

        f.write(f"Energy Statistics:\n")
        f.write(f"  Min: {energies.min():.2f} kcal/mol\n")
        f.write(f"  Max: {energies.max():.2f} kcal/mol\n")
        f.write(f"  Mean: {energies.mean():.2f} kcal/mol\n\n")

        f.write(f"P_near Statistics (Rosetta):\n")
        f.write(f"  Min: {pnear_rosetta.min():.3f}\n")
        f.write(f"  Max: {pnear_rosetta.max():.3f}\n")
        f.write(f"  Mean: {pnear_rosetta.mean():.3f}\n")
        f.write(f"  Stable designs (>{min_pnear}): {len(stable_designs_rosetta)}\n\n")

        f.write(f"P_near Statistics (GA):\n")
        f.write(f"  Min: {pnear_ga.min():.3f}\n")
        f.write(f"  Max: {pnear_ga.max():.3f}\n")
        f.write(f"  Mean: {pnear_ga.mean():.3f}\n")
        f.write(f"  Stable designs (>{min_pnear}): {len(stable_designs_ga)}\n\n")

        f.write(f"Top Stable Designs (GA P_near > {min_pnear}):\n")
        f.write("-" * 50 + "\n")
        if len(stable_designs_ga) > 0:
            # Sort by GA P_near value
            sorted_indices = stable_designs_ga[np.argsort(pnear_ga[stable_designs_ga])[::-1]]
            for i, idx in enumerate(sorted_indices[:10]):  # Top 10
                f.write(f"{i+1:2d}. {designs[idx]:<20} "
                       f"Energy: {energies[idx]:6.2f} "
                       f"P_near(GA): {pnear_ga[idx]:.3f}\n")
                f.write(f"    Sequence: {sequences[idx]}\n\n")

    output_files.append(str(report_file))

    return {
        'designs': designs,
        'energies': energies,
        'pnear_rosetta': pnear_rosetta,
        'pnear_ga': pnear_ga,
        'sequences': sequences,
        'stable_designs_rosetta': stable_designs_rosetta,
        'stable_designs_ga': stable_designs_ga,
        'output_files': output_files,
        'metadata': {
            'input_file': str(input_file),
            'output_dir': str(output_path),
            'config': config,
            'total_designs': len(designs),
            'stable_count_rosetta': len(stable_designs_rosetta),
            'stable_count_ga': len(stable_designs_ga)
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
        'min_pnear': args.min_pnear,
        'show_plots': args.show_plots
    })

    try:
        # Run analysis
        result = run_pnear_analysis(
            input_file=args.input,
            output_dir=args.output_dir,
            config=config
        )

        print(f"P_near Analysis completed successfully!")
        print(f"Total designs: {result['metadata']['total_designs']}")
        print(f"Stable designs (Rosetta): {result['metadata']['stable_count_rosetta']}")
        print(f"Stable designs (GA): {result['metadata']['stable_count_ga']}")
        print(f"Output files generated: {len(result['output_files'])}")
        print(f"Results saved to: {result['metadata']['output_dir']}")

        return result

    except Exception as e:
        print(f"Error during analysis: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()