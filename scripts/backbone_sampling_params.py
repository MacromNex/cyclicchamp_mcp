#!/usr/bin/env python3
"""
Script: backbone_sampling_params.py
Description: Generate backbone sampling parameters for CyclicChamp simulated annealing

Original Use Case: examples/use_case_3_backbone_sampling_params.py
Dependencies Removed: None (already minimal)

Usage:
    python scripts/backbone_sampling_params.py --size <peptide_size> --output-dir <output_dir>

Example:
    python scripts/backbone_sampling_params.py --size 15 --output-dir results/
"""

# ==============================================================================
# Minimal Imports (only essential packages)
# ==============================================================================
import argparse
import json
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
    "optimize": False,
    "num_combinations": 20,
    "max_iterations": 10000,
    "output_format": "png",
    "plot_dpi": 300,
    "show_plots": False,
    "random_seed": 42
}

# Supported peptide sizes
SUPPORTED_SIZES = [7, 15, 20, 24]

# ==============================================================================
# Inlined Utility Functions (parameter calculation formulas)
# ==============================================================================
def calculate_energy_thresholds(n: int) -> Dict[str, float]:
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

def calculate_initial_temperatures(n: int) -> Dict[str, float]:
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

def calculate_move_parameters(n: int) -> Dict[str, float]:
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

def calculate_cooling_rates() -> Dict[str, int]:
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

def optimize_parameters_combinatorial(n: int, num_combinations: int = 20, random_seed: int = 42) -> List[Dict[str, Any]]:
    """
    Generate well-spaced parameter combinations for optimization.

    Args:
        n: Number of residues
        num_combinations: Number of parameter combinations to generate
        random_seed: Random seed for reproducibility

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
    np.random.seed(random_seed)  # For reproducibility

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

def simulate_annealing_schedule(initial_temp: float, cooling_rate: int, max_iterations: int = 10000) -> tuple:
    """
    Simulate a temperature schedule for simulated annealing.

    Args:
        initial_temp: Initial temperature
        cooling_rate: Cooling rate parameter
        max_iterations: Maximum number of iterations

    Returns:
        Tuple of (iterations, temperatures) arrays
    """
    iterations = np.arange(1, max_iterations + 1)
    temperatures = initial_temp / (1 + cooling_rate * np.log(iterations))

    return iterations, temperatures

# ==============================================================================
# Core Function (main logic extracted from use case)
# ==============================================================================
def run_backbone_sampling_params(
    peptide_size: int,
    output_dir: Optional[Union[str, Path]] = None,
    config: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Generate comprehensive backbone sampling parameters for CyclicChamp.

    Args:
        peptide_size: Number of residues (7, 15, 20, or 24)
        output_dir: Directory to save output files (optional)
        config: Configuration dict (uses DEFAULT_CONFIG if not provided)
        **kwargs: Override specific config parameters

    Returns:
        Dict containing:
            - parameters: Complete parameter set
            - optimization_combinations: Parameter combinations (if optimize=True)
            - output_files: List of generated output files

    Example:
        >>> result = run_backbone_sampling_params(15, "results/")
        >>> print(result['parameters']['energy_thresholds'])
    """
    # Setup
    config = {**DEFAULT_CONFIG, **(config or {}), **kwargs}

    if peptide_size not in SUPPORTED_SIZES:
        raise ValueError(f"Peptide size {peptide_size} not supported. Supported sizes: {SUPPORTED_SIZES}")

    # Set output directory
    if output_dir is None:
        output_dir = Path("backbone_params_results")
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Calculate all parameters
    thresholds = calculate_energy_thresholds(peptide_size)
    temperatures = calculate_initial_temperatures(peptide_size)
    move_params = calculate_move_parameters(peptide_size)
    cooling_rates = calculate_cooling_rates()

    output_files = []

    # Generate plots
    plt.figure(figsize=(15, 10))

    # Plot 1: Energy thresholds vs peptide size
    sizes = range(7, 25)
    rama_thresholds = [calculate_energy_thresholds(s)['rama_threshold'] for s in sizes]
    rep_thresholds = [calculate_energy_thresholds(s)['rep_threshold'] for s in sizes]

    plt.subplot(2, 3, 1)
    plt.plot(sizes, rama_thresholds, 'o-', label='Ramachandran')
    plt.plot(sizes, rep_thresholds, 's-', label='Repulsive')
    plt.axvline(x=peptide_size, color='red', linestyle='--', alpha=0.7)
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
    plt.axvline(x=peptide_size, color='red', linestyle='--', alpha=0.7)
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
    plt.axvline(x=peptide_size, color='red', linestyle='--', alpha=0.7)
    plt.xlabel('Peptide Size (residues)')
    plt.ylabel('Parameter Value')
    plt.title('Move Parameters vs Peptide Size')
    plt.legend()
    plt.grid(True, alpha=0.3)

    # Plot 4-6: Temperature schedules for current peptide size (limit to 3 subplots)
    max_iter = config['max_iterations']

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
    output_file = output_path / f"parameters_summary_{peptide_size}res.png"
    plt.savefig(output_file, dpi=config['plot_dpi'], bbox_inches='tight')
    output_files.append(str(output_file))

    if config['show_plots']:
        plt.show()
    plt.close()

    # Save parameters to JSON file
    all_params = {
        'peptide_size': peptide_size,
        'energy_thresholds': thresholds,
        'initial_temperatures': temperatures,
        'move_parameters': move_params,
        'cooling_rates': cooling_rates
    }

    json_file = output_path / f"parameters_{peptide_size}res.json"
    with open(json_file, 'w') as f:
        json.dump(all_params, f, indent=2)
    output_files.append(str(json_file))

    # Generate text report with MATLAB code
    report_file = output_path / f"parameters_report_{peptide_size}res.txt"
    with open(report_file, 'w') as f:
        f.write(f"CyclicChamp Backbone Sampling Parameters\n")
        f.write(f"=" * 50 + "\n\n")
        f.write(f"Peptide size: {peptide_size} residues\n\n")

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
        f.write(f"% Parameters for {peptide_size}-residue cyclic peptide\n")
        f.write(f"n = {peptide_size};\n")
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

    output_files.append(str(report_file))

    # Handle optimization if requested
    optimization_combinations = None
    if config['optimize']:
        optimization_combinations = optimize_parameters_combinatorial(
            peptide_size,
            config['num_combinations'],
            config['random_seed']
        )

        # Save optimization parameters
        opt_file = output_path / f"optimization_parameters_{peptide_size}res.json"
        with open(opt_file, 'w') as f:
            json.dump(optimization_combinations, f, indent=2)
        output_files.append(str(opt_file))

        # Create optimization plot
        plt.figure(figsize=(12, 8))

        k0_values = [c['k0'] for c in optimization_combinations]
        b_values = [c['b'] for c in optimization_combinations]
        c_rama_values = [c['c_rama'] for c in optimization_combinations]
        c_rep_values = [c['c_rep'] for c in optimization_combinations]

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
        opt_plot_file = output_path / f"optimization_combinations_{peptide_size}res.png"
        plt.savefig(opt_plot_file, dpi=config['plot_dpi'], bbox_inches='tight')
        output_files.append(str(opt_plot_file))

        if config['show_plots']:
            plt.show()
        plt.close()

    return {
        'parameters': all_params,
        'optimization_combinations': optimization_combinations,
        'output_files': output_files,
        'metadata': {
            'peptide_size': peptide_size,
            'output_dir': str(output_path),
            'config': config,
            'optimization_enabled': config['optimize'],
            'num_combinations': len(optimization_combinations) if optimization_combinations else 0
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
    parser.add_argument('--size', '-s', type=int, required=True, choices=SUPPORTED_SIZES,
                       help=f'Peptide size in residues {SUPPORTED_SIZES}')
    parser.add_argument('--output-dir', '-o', help='Output directory path')
    parser.add_argument('--config', '-c', help='Config file (JSON)')
    parser.add_argument('--optimize', action='store_true',
                       help='Generate parameter combinations for optimization')
    parser.add_argument('--num-combinations', '-n', type=int, default=20,
                       help='Number of optimization combinations (default: 20)')
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
        'optimize': args.optimize,
        'num_combinations': args.num_combinations,
        'show_plots': args.show_plots
    })

    try:
        # Run parameter generation
        result = run_backbone_sampling_params(
            peptide_size=args.size,
            output_dir=args.output_dir,
            config=config
        )

        print(f"Backbone Sampling Parameters generated successfully!")
        print(f"Peptide size: {result['metadata']['peptide_size']} residues")
        print(f"Optimization enabled: {result['metadata']['optimization_enabled']}")
        if result['metadata']['optimization_enabled']:
            print(f"Optimization combinations: {result['metadata']['num_combinations']}")
        print(f"Output files generated: {len(result['output_files'])}")
        print(f"Results saved to: {result['metadata']['output_dir']}")

        return result

    except Exception as e:
        print(f"Error during parameter generation: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()