#!/usr/bin/env python3
"""
Use Case 1: P_near Analysis for Cyclic Peptide Designs

This script analyzes P_near values for cyclic peptide designs from CyclicChamp results.
P_near is a stability metric that combines RMSD and energy to assess design quality.
P_near > 0.9 indicates a stable design.

Usage:
    python use_case_1_pnear_analysis.py --input examples/data/results/Pnear_values_15res.txt
    python use_case_1_pnear_analysis.py --input examples/data/results/Pnear_values_20res.txt --min-pnear 0.8
"""

import argparse
import matplotlib.pyplot as plt
import numpy as np
import os
import sys
from pathlib import Path

def analyze_pnear_data(input_file, min_pnear=0.9, output_dir="examples/data/results"):
    """
    Analyze P_near values from CyclicChamp results.

    Args:
        input_file: Path to Pnear_values_*.txt file
        min_pnear: Minimum P_near threshold for stable designs
        output_dir: Directory to save output plots and analysis
    """

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

    print(f"Analyzed {len(designs)} designs from {input_file}")

    if len(energies) > 0:
        print(f"Energy range: {energies.min():.2f} to {energies.max():.2f} kcal/mol")
        print(f"P_near (Rosetta) range: {pnear_rosetta.min():.3f} to {pnear_rosetta.max():.3f}")
        print(f"P_near (GA) range: {pnear_ga.min():.3f} to {pnear_ga.max():.3f}")
    else:
        print("No valid designs found in the input file!")
        return None

    # Find stable designs
    stable_designs_rosetta = np.where(pnear_rosetta > min_pnear)[0]
    stable_designs_ga = np.where(pnear_ga > min_pnear)[0]

    print(f"\nStable designs (P_near > {min_pnear}):")
    print(f"Rosetta method: {len(stable_designs_rosetta)} designs")
    print(f"GA method: {len(stable_designs_ga)} designs")

    # Create visualizations
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

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

    output_file = output_path / f"pnear_correlation_{Path(input_file).stem}.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Saved P_near correlation plot to {output_file}")
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
    output_file = output_path / f"energy_vs_pnear_{Path(input_file).stem}.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Saved energy vs P_near plot to {output_file}")
    plt.close()

    # Generate summary report
    report_file = output_path / f"analysis_report_{Path(input_file).stem}.txt"
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

    print(f"Saved analysis report to {report_file}")

    return {
        'designs': designs,
        'energies': energies,
        'pnear_rosetta': pnear_rosetta,
        'pnear_ga': pnear_ga,
        'sequences': sequences,
        'stable_designs_rosetta': stable_designs_rosetta,
        'stable_designs_ga': stable_designs_ga
    }

def main():
    parser = argparse.ArgumentParser(
        description="Analyze P_near values for cyclic peptide designs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python use_case_1_pnear_analysis.py --input examples/data/results/Pnear_values_15res.txt
    python use_case_1_pnear_analysis.py --input examples/data/results/Pnear_values_20res.txt --min-pnear 0.8
        """
    )

    parser.add_argument('--input', '-i', required=True,
                       help='Path to Pnear_values_*.txt file')
    parser.add_argument('--min-pnear', '-p', type=float, default=0.9,
                       help='Minimum P_near threshold for stable designs (default: 0.9)')
    parser.add_argument('--output-dir', '-o', default='examples/data/results',
                       help='Output directory for plots and reports (default: examples/data/results)')

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: Input file {args.input} not found!")
        sys.exit(1)

    try:
        results = analyze_pnear_data(args.input, args.min_pnear, args.output_dir)
        print(f"\nAnalysis complete! Check {args.output_dir} for results.")

    except Exception as e:
        print(f"Error during analysis: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()