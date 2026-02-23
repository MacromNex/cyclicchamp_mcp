#!/usr/bin/env python3
"""
Use Case 3: Backbone Sampling Parameter Optimization for CyclicChamp

This script demonstrates parameter optimization for cyclic peptide backbone sampling
using simulated annealing. It implements the parameter calculation formulas from
the CyclicChamp paper for different peptide sizes (7, 15, 20, 24 residues).

Usage:
    python use_case_3_backbone_sampling_params.py --size 15
    python use_case_3_backbone_sampling_params.py --size 20 --optimize
"""

import argparse
import numpy as np
import matplotlib.pyplot as plt
import sys
from pathlib import Path
import json

def calculate_energy_thresholds(n):
    """
    Calculate energy thresholds for CyclicChamp backbone sampling.

    Args:
        n: Number of residues in the cyclic peptide

    Returns:
        Dictionary with energy thresholds
    """
    thresholds = {
        'rama_threshold': 8 * n,  # Ramachandran energy threshold
        'rep_threshold': 10 + ((n - 7) * 10) / 17,  # Repulsive energy threshold
        'cyc_threshold': 1,  # Cyclic backbone closure deviation threshold
        'hbond_count_threshold': int(np.ceil(n / 3))  # Number of hydrogen bonds threshold
    }

    # Good backbone candidate criteria
    thresholds['rep_criteria'] = 5 + ((n - 7) * 10) / 17
    thresholds['cyc_criteria'] = 1
    thresholds['hbond_count_criteria'] = int(np.ceil(n / 3))

    return thresholds

def calculate_initial_temperatures(n):
    """
    Calculate initial temperatures for simulated annealing.

    Args:
        n: Number of residues in the cyclic peptide

    Returns:
        Dictionary with initial temperatures
    """
    temperatures = {
        't0_rama': 10 + ((n - 7) * 20) / 17,    # Ramachandran energy
        't0_rep': 20 + ((n - 7) * 80) / 17,     # Repulsive energy
        't0_cyc': 2 + ((n - 7) * 4) / 17,       # Cyclic backbone closure
        't0_hbond': 2 + ((n - 7) * 4) / 17      # Hydrogen bond energy
    }

    return temperatures

def calculate_move_parameters(n):
    """
    Calculate random move parameters.

    Args:
        n: Number of residues in the cyclic peptide

    Returns:
        Dictionary with move parameters
    """
    # k0: smaller value for larger n (range 0.5-1.0)
    k0 = 1.0 - 0.5 * (n - 7) / 17 if n > 7 else 1.0
    k0 = max(0.5, min(1.0, k0))

    # b: larger value for larger n (range 15-18)
    b = 15 + 3 * (n - 7) / 17 if n > 7 else 15
    b = max(15, min(18, b))

    return {'k0': k0, 'b': b}

def calculate_cooling_rates():
    """
    Calculate temperature dropping rates (cooling rates) for simulated annealing.

    Returns:
        Dictionary with cooling rates
    """
    # These are suggested values from the paper
    cooling_rates = {
        'c_rama': 4,     # Ramachandran energy cooling rate
        'c_rep': 14,     # Repulsive energy cooling rate
        'c_cyc': 18,     # Cyclic backbone closure cooling rate
        'c_hbond': 20    # Hydrogen bond energy cooling rate
    }

    return cooling_rates

def optimize_parameters_combinatorial(n, num_combinations=20):
    """
    Generate well-spaced parameter combinations for optimization.

    Args:
        n: Number of residues
        num_combinations: Number of parameter combinations to generate

    Returns:
        List of parameter dictionaries
    """
    # Parameter ranges for optimization
    k0_range = np.linspace(0.5, 1.0, 4)
    b_range = np.linspace(15, 18, 4)
    c_rama_range = [2, 4, 6, 8]
    c_rep_range = [10, 14, 18, 22]
    c_cyc_range = [14, 18, 22, 26]
    c_hbond_range = [16, 20, 24, 28]

    # Generate combinations
    combinations = []
    np.random.seed(42)  # For reproducibility

    for _ in range(num_combinations):
        combo = {
            'k0': float(np.random.choice(k0_range)),
            'b': float(np.random.choice(b_range)),
            'c_rama': int(np.random.choice(c_rama_range)),
            'c_rep': int(np.random.choice(c_rep_range)),
            'c_cyc': int(np.random.choice(c_cyc_range)),
            'c_hbond': int(np.random.choice(c_hbond_range))
        }
        combinations.append(combo)

    return combinations

def simulate_annealing_schedule(initial_temp, cooling_rate, max_iterations=10000):
    """
    Simulate a temperature schedule for simulated annealing.

    Args:
        initial_temp: Initial temperature
        cooling_rate: Cooling rate parameter
        max_iterations: Maximum number of iterations

    Returns:
        Arrays of iterations and temperatures
    """
    iterations = np.arange(1, max_iterations + 1)
    temperatures = initial_temp / (1 + cooling_rate * np.log(iterations))

    return iterations, temperatures

def generate_parameter_summary(n, output_dir="examples/data/results"):
    """
    Generate a comprehensive parameter summary for a given peptide size.

    Args:
        n: Number of residues
        output_dir: Output directory for results
    """
    print(f"Generating parameter summary for {n}-residue cyclic peptide...")

    # Calculate all parameters
    thresholds = calculate_energy_thresholds(n)
    temperatures = calculate_initial_temperatures(n)
    move_params = calculate_move_parameters(n)
    cooling_rates = calculate_cooling_rates()

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Generate plots
    plt.figure(figsize=(15, 10))

    # Plot 1: Energy thresholds vs peptide size
    sizes = range(7, 25)
    rama_thresholds = [calculate_energy_thresholds(s)['rama_threshold'] for s in sizes]
    rep_thresholds = [calculate_energy_thresholds(s)['rep_threshold'] for s in sizes]

    plt.subplot(2, 3, 1)
    plt.plot(sizes, rama_thresholds, 'o-', label='Ramachandran')
    plt.plot(sizes, rep_thresholds, 's-', label='Repulsive')
    plt.axvline(x=n, color='red', linestyle='--', alpha=0.7)
    plt.xlabel('Peptide Size (residues)')
    plt.ylabel('Energy Threshold')
    plt.title('Energy Thresholds vs Peptide Size')
    plt.legend()
    plt.grid(True, alpha=0.3)

    # Plot 2: Initial temperatures vs peptide size
    t0_rama = [calculate_initial_temperatures(s)['t0_rama'] for s in sizes]
    t0_rep = [calculate_initial_temperatures(s)['t0_rep'] for s in sizes]

    plt.subplot(2, 3, 2)
    plt.plot(sizes, t0_rama, 'o-', label='Ramachandran')
    plt.plot(sizes, t0_rep, 's-', label='Repulsive')
    plt.axvline(x=n, color='red', linestyle='--', alpha=0.7)
    plt.xlabel('Peptide Size (residues)')
    plt.ylabel('Initial Temperature')
    plt.title('Initial Temperatures vs Peptide Size')
    plt.legend()
    plt.grid(True, alpha=0.3)

    # Plot 3: Move parameters vs peptide size
    k0_values = [calculate_move_parameters(s)['k0'] for s in sizes]
    b_values = [calculate_move_parameters(s)['b'] for s in sizes]

    plt.subplot(2, 3, 3)
    plt.plot(sizes, k0_values, 'o-', label='k0')
    plt.plot(sizes, b_values, 's-', label='b')
    plt.axvline(x=n, color='red', linestyle='--', alpha=0.7)
    plt.xlabel('Peptide Size (residues)')
    plt.ylabel('Parameter Value')
    plt.title('Move Parameters vs Peptide Size')
    plt.legend()
    plt.grid(True, alpha=0.3)

    # Plot 4-6: Temperature schedules for current peptide size (limit to 3 subplots)
    max_iter = 10000

    temp_items = list(temperatures.items())
    for i, (temp_type, temp_value) in enumerate(temp_items[:3]):  # Only first 3 to avoid subplot overflow
        cooling_key = f"c_{temp_type.split('_')[1]}"
        cooling_rate = cooling_rates[cooling_key]

        iterations, temps = simulate_annealing_schedule(temp_value, cooling_rate, max_iter)

        plt.subplot(2, 3, 4 + i)
        plt.semilogy(iterations, temps)
        plt.xlabel('Iteration')
        plt.ylabel('Temperature')
        plt.title(f'{temp_type.replace("_", " ").title()} Schedule\n(T0={temp_value:.1f}, c={cooling_rate})')
        plt.grid(True, alpha=0.3)

    plt.tight_layout()
    output_file = output_path / f"parameters_summary_{n}res.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Saved parameter summary plot to {output_file}")
    plt.close()

    # Save parameters to JSON file
    all_params = {
        'peptide_size': n,
        'energy_thresholds': thresholds,
        'initial_temperatures': temperatures,
        'move_parameters': move_params,
        'cooling_rates': cooling_rates
    }

    json_file = output_path / f"parameters_{n}res.json"
    with open(json_file, 'w') as f:
        json.dump(all_params, f, indent=2)
    print(f"Saved parameters to {json_file}")

    # Generate text report
    report_file = output_path / f"parameters_report_{n}res.txt"
    with open(report_file, 'w') as f:
        f.write(f"CyclicChamp Backbone Sampling Parameters\n")
        f.write(f"=" * 50 + "\n\n")
        f.write(f"Peptide size: {n} residues\n\n")

        f.write(f"Energy Thresholds:\n")
        f.write(f"-" * 20 + "\n")
        for key, value in thresholds.items():
            f.write(f"{key:25s}: {value:8.2f}\n")

        f.write(f"\nInitial Temperatures:\n")
        f.write(f"-" * 20 + "\n")
        for key, value in temperatures.items():
            f.write(f"{key:25s}: {value:8.2f}\n")

        f.write(f"\nMove Parameters:\n")
        f.write(f"-" * 15 + "\n")
        for key, value in move_params.items():
            f.write(f"{key:25s}: {value:8.2f}\n")

        f.write(f"\nCooling Rates:\n")
        f.write(f"-" * 13 + "\n")
        for key, value in cooling_rates.items():
            f.write(f"{key:25s}: {value:8.2f}\n")

        f.write(f"\nRecommended MATLAB Code:\n")
        f.write(f"-" * 25 + "\n")
        f.write(f"% Parameters for {n}-residue cyclic peptide\n")
        f.write(f"n = {n};\n")
        f.write(f"rama_threshold = {thresholds['rama_threshold']};\n")
        f.write(f"rep_threshold = {thresholds['rep_threshold']:.2f};\n")
        f.write(f"cyc_threshold = {thresholds['cyc_threshold']};\n")
        f.write(f"count_threshold = {thresholds['hbond_count_threshold']};\n\n")
        f.write(f"t0_rama = {temperatures['t0_rama']:.2f};\n")
        f.write(f"t0_rep = {temperatures['t0_rep']:.2f};\n")
        f.write(f"t0_cyc = {temperatures['t0_cyc']:.2f};\n")
        f.write(f"t0_hbond = {temperatures['t0_hbond']:.2f};\n\n")
        f.write(f"k0 = {move_params['k0']:.2f};\n")
        f.write(f"b = {move_params['b']:.2f};\n\n")
        f.write(f"c_rama = {cooling_rates['c_rama']};\n")
        f.write(f"c_rep = {cooling_rates['c_rep']};\n")
        f.write(f"c_cyc = {cooling_rates['c_cyc']};\n")
        f.write(f"c_hbond = {cooling_rates['c_hbond']};\n")

    print(f"Saved parameter report to {report_file}")

    return all_params

def main():
    parser = argparse.ArgumentParser(
        description="Generate CyclicChamp backbone sampling parameters",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python use_case_3_backbone_sampling_params.py --size 15
    python use_case_3_backbone_sampling_params.py --size 20 --optimize
    python use_case_3_backbone_sampling_params.py --size 24 --output-dir custom_output
        """
    )

    parser.add_argument('--size', '-s', type=int, required=True, choices=[7, 15, 20, 24],
                       help='Peptide size in residues (7, 15, 20, or 24)')
    parser.add_argument('--optimize', action='store_true',
                       help='Generate parameter combinations for optimization')
    parser.add_argument('--output-dir', '-o', default='examples/data/results',
                       help='Output directory for results (default: examples/data/results)')

    args = parser.parse_args()

    try:
        # Generate parameter summary
        params = generate_parameter_summary(args.size, args.output_dir)

        if args.optimize:
            print(f"\nGenerating optimization parameters...")
            combinations = optimize_parameters_combinatorial(args.size)

            # Save optimization parameters
            output_path = Path(args.output_dir)
            opt_file = output_path / f"optimization_parameters_{args.size}res.json"
            with open(opt_file, 'w') as f:
                json.dump(combinations, f, indent=2)
            print(f"Saved {len(combinations)} parameter combinations to {opt_file}")

            # Create optimization plot
            plt.figure(figsize=(12, 8))

            k0_values = [c['k0'] for c in combinations]
            b_values = [c['b'] for c in combinations]
            c_rama_values = [c['c_rama'] for c in combinations]
            c_rep_values = [c['c_rep'] for c in combinations]

            plt.subplot(2, 2, 1)
            plt.scatter(k0_values, b_values, alpha=0.7, s=50)
            plt.xlabel('k0')
            plt.ylabel('b')
            plt.title('Move Parameter Combinations')
            plt.grid(True, alpha=0.3)

            plt.subplot(2, 2, 2)
            plt.scatter(c_rama_values, c_rep_values, alpha=0.7, s=50)
            plt.xlabel('c_rama')
            plt.ylabel('c_rep')
            plt.title('Cooling Rate Combinations')
            plt.grid(True, alpha=0.3)

            plt.subplot(2, 2, 3)
            plt.hist(k0_values, bins=10, alpha=0.7, edgecolor='black')
            plt.xlabel('k0')
            plt.ylabel('Frequency')
            plt.title('k0 Distribution')

            plt.subplot(2, 2, 4)
            plt.hist(c_rep_values, bins=10, alpha=0.7, edgecolor='black')
            plt.xlabel('c_rep')
            plt.ylabel('Frequency')
            plt.title('c_rep Distribution')

            plt.tight_layout()
            opt_plot_file = output_path / f"optimization_combinations_{args.size}res.png"
            plt.savefig(opt_plot_file, dpi=300, bbox_inches='tight')
            print(f"Saved optimization plot to {opt_plot_file}")
            plt.close()

        print(f"\nParameter generation complete! Check {args.output_dir} for results.")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()