"""MCP Server for CyclicChamp Tools

Provides both synchronous and asynchronous (submit) APIs for cyclic peptide analysis.
"""

from fastmcp import FastMCP
from pathlib import Path
from typing import Optional, List, Dict, Any
import sys

# Setup paths
SCRIPT_DIR = Path(__file__).parent.resolve()
MCP_ROOT = SCRIPT_DIR.parent
SCRIPTS_DIR = MCP_ROOT / "scripts"
CONFIG_DIR = MCP_ROOT / "configs"
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(SCRIPTS_DIR))

from jobs.manager import job_manager
from loguru import logger

# Create MCP server
mcp = FastMCP("cyclicchamp-tools")

# ==============================================================================
# Job Management Tools (for async operations)
# ==============================================================================

@mcp.tool()
def get_job_status(job_id: str) -> dict:
    """
    Get the status of a submitted cyclic peptide computation job.

    Args:
        job_id: The job ID returned from a submit_* function

    Returns:
        Dictionary with job status, timestamps, and any errors
    """
    return job_manager.get_job_status(job_id)

@mcp.tool()
def get_job_result(job_id: str) -> dict:
    """
    Get the results of a completed cyclic peptide computation job.

    Args:
        job_id: The job ID of a completed job

    Returns:
        Dictionary with the job results or error if not completed
    """
    return job_manager.get_job_result(job_id)

@mcp.tool()
def get_job_log(job_id: str, tail: int = 50) -> dict:
    """
    Get log output from a running or completed job.

    Args:
        job_id: The job ID to get logs for
        tail: Number of lines from end (default: 50, use 0 for all)

    Returns:
        Dictionary with log lines and total line count
    """
    return job_manager.get_job_log(job_id, tail)

@mcp.tool()
def cancel_job(job_id: str) -> dict:
    """
    Cancel a running cyclic peptide computation job.

    Args:
        job_id: The job ID to cancel

    Returns:
        Success or error message
    """
    return job_manager.cancel_job(job_id)

@mcp.tool()
def list_jobs(status: Optional[str] = None) -> dict:
    """
    List all submitted cyclic peptide computation jobs.

    Args:
        status: Filter by status (pending, running, completed, failed, cancelled)

    Returns:
        List of jobs with their status
    """
    return job_manager.list_jobs(status)

# ==============================================================================
# Synchronous Tools (for fast operations < 10 min)
# ==============================================================================

@mcp.tool()
def analyze_pnear_stability(
    input_file: str,
    output_dir: Optional[str] = None,
    min_pnear: Optional[float] = None,
    show_plots: bool = False,
    config_file: Optional[str] = None
) -> dict:
    """
    Analyze P_near stability values for cyclic peptide designs.

    Fast operation - returns results immediately (~1-2 seconds).
    Analyzes stability values from CyclicChamp results and generates
    correlation plots and statistical reports.

    Args:
        input_file: Path to Pnear_values_*.txt file with tab-delimited data
        output_dir: Output directory for plots and reports (optional)
        min_pnear: Minimum P_near threshold for stable designs (default: 0.9)
        show_plots: Whether to display plots interactively (default: False)
        config_file: Path to JSON config file for advanced settings

    Returns:
        Dictionary with analysis results including:
        - designs: List of design names
        - energies: Energy values
        - pnear_rosetta: Rosetta P_near values
        - pnear_ga: GA P_near values
        - sequences: Peptide sequences
        - stable_designs_rosetta: Indices of stable designs (Rosetta)
        - stable_designs_ga: Indices of stable designs (GA)
        - output_files: List of generated files
        - metadata: Summary statistics
    """
    from pnear_analysis import run_pnear_analysis

    try:
        # Load config if provided
        config = {}
        if config_file:
            import json
            config_path = Path(config_file)
            if not config_path.is_absolute():
                config_path = CONFIG_DIR / config_path
            with open(config_path) as f:
                config = json.load(f)

        # Override config with parameters
        if min_pnear is not None:
            config.setdefault('analysis', {})['min_pnear'] = min_pnear

        result = run_pnear_analysis(
            input_file=input_file,
            output_dir=output_dir,
            config=config,
            show_plots=show_plots
        )
        return {"status": "success", **result}

    except FileNotFoundError as e:
        return {"status": "error", "error": f"File not found: {e}"}
    except ValueError as e:
        return {"status": "error", "error": f"Invalid input: {e}"}
    except Exception as e:
        logger.error(f"P_near analysis failed: {e}")
        return {"status": "error", "error": str(e)}

@mcp.tool()
def analyze_peptide_sequences(
    input_file: str,
    output_dir: Optional[str] = None,
    stable_only: bool = False,
    min_pnear: Optional[float] = None,
    show_plots: bool = False,
    config_file: Optional[str] = None
) -> dict:
    """
    Analyze cyclic peptide sequence composition, chirality, and physicochemical properties.

    Fast operation - returns results immediately (~1-3 seconds).
    Analyzes amino acid composition, D/L chirality patterns, hydrophobicity,
    charge distribution, and correlations with stability.

    Args:
        input_file: Path to Pnear_values_*.txt file with sequence data
        output_dir: Output directory for plots and reports (optional)
        stable_only: Analyze only stable designs above threshold (default: False)
        min_pnear: Minimum P_near threshold for stable designs (default: 0.9)
        show_plots: Whether to display plots interactively (default: False)
        config_file: Path to JSON config file for advanced settings

    Returns:
        Dictionary with analysis results including:
        - sequence_data: DataFrame with full analysis (design, energy, properties)
        - amino_acid_composition: Counter with AA frequency counts
        - chirality_distribution: Counter with L/D amino acid counts
        - output_files: List of generated files (plots, reports)
        - metadata: Analysis parameters and summary statistics
    """
    from sequence_analysis import run_sequence_analysis

    try:
        # Load config if provided
        config = {}
        if config_file:
            import json
            config_path = Path(config_file)
            if not config_path.is_absolute():
                config_path = CONFIG_DIR / config_path
            with open(config_path) as f:
                config = json.load(f)

        # Override config with parameters
        if stable_only is not None:
            config.setdefault('analysis', {})['stable_only'] = stable_only
        if min_pnear is not None:
            config.setdefault('analysis', {})['min_pnear'] = min_pnear

        result = run_sequence_analysis(
            input_file=input_file,
            output_dir=output_dir,
            config=config,
            show_plots=show_plots
        )
        return {"status": "success", **result}

    except FileNotFoundError as e:
        return {"status": "error", "error": f"File not found: {e}"}
    except ValueError as e:
        return {"status": "error", "error": f"Invalid input: {e}"}
    except Exception as e:
        logger.error(f"Sequence analysis failed: {e}")
        return {"status": "error", "error": str(e)}

@mcp.tool()
def generate_backbone_parameters(
    peptide_size: int,
    output_dir: Optional[str] = None,
    optimize: bool = False,
    num_combinations: Optional[int] = None,
    show_plots: bool = False,
    config_file: Optional[str] = None
) -> dict:
    """
    Generate backbone sampling parameters for CyclicChamp simulated annealing.

    Fast operation - returns results immediately (<1 second).
    Calculates energy thresholds, initial temperatures, move parameters,
    and cooling rates optimized for the specified peptide size.

    Args:
        peptide_size: Number of residues in the cyclic peptide [7, 15, 20, 24]
        output_dir: Output directory for parameter files and plots (optional)
        optimize: Generate parameter combinations for optimization (default: False)
        num_combinations: Number of parameter combinations to generate (default: 20)
        show_plots: Whether to display parameter plots interactively (default: False)
        config_file: Path to JSON config file for parameter formulas

    Returns:
        Dictionary with generated parameters including:
        - parameters: Complete parameter set (energy thresholds, temperatures, etc.)
        - optimization_combinations: List of parameter combinations (if optimize=True)
        - output_files: List of generated files (JSON, plots, reports)
        - metadata: Peptide size and configuration used
    """
    from backbone_sampling_params import run_backbone_sampling_params

    try:
        # Validate peptide size
        valid_sizes = [7, 15, 20, 24]
        if peptide_size not in valid_sizes:
            return {
                "status": "error",
                "error": f"Invalid peptide size {peptide_size}. Must be one of: {valid_sizes}"
            }

        # Load config if provided
        config = {}
        if config_file:
            import json
            config_path = Path(config_file)
            if not config_path.is_absolute():
                config_path = CONFIG_DIR / config_path
            with open(config_path) as f:
                config = json.load(f)

        # Override config with parameters
        if optimize is not None:
            config.setdefault('optimization', {})['optimize'] = optimize
        if num_combinations is not None:
            config.setdefault('optimization', {})['num_combinations'] = num_combinations

        result = run_backbone_sampling_params(
            peptide_size=peptide_size,
            output_dir=output_dir,
            config=config,
            show_plots=show_plots
        )
        return {"status": "success", **result}

    except ValueError as e:
        return {"status": "error", "error": f"Invalid input: {e}"}
    except Exception as e:
        logger.error(f"Parameter generation failed: {e}")
        return {"status": "error", "error": str(e)}

# ==============================================================================
# Submit Tools (for long-running operations > 10 min) - Future Expansion
# ==============================================================================

@mcp.tool()
def submit_pnear_analysis(
    input_file: str,
    output_dir: Optional[str] = None,
    min_pnear: Optional[float] = None,
    config_file: Optional[str] = None,
    job_name: Optional[str] = None
) -> dict:
    """
    Submit a P_near stability analysis job for background processing.

    Use this for very large datasets or when you want to track job progress.
    For typical datasets, use analyze_pnear_stability() for immediate results.

    Args:
        input_file: Path to Pnear_values_*.txt file
        output_dir: Output directory for results
        min_pnear: Minimum P_near threshold for stable designs
        config_file: Path to JSON config file
        job_name: Optional name for easier job tracking

    Returns:
        Dictionary with job_id for tracking. Use:
        - get_job_status(job_id) to check progress
        - get_job_result(job_id) to get results when completed
        - get_job_log(job_id) to see execution logs
    """
    script_path = str(SCRIPTS_DIR / "pnear_analysis.py")

    args = {"input": input_file}
    if output_dir:
        args["output-dir"] = output_dir
    if min_pnear is not None:
        args["min-pnear"] = min_pnear
    if config_file:
        args["config"] = config_file

    return job_manager.submit_job(
        script_path=script_path,
        args=args,
        job_name=job_name or f"pnear_analysis_{Path(input_file).stem}"
    )

@mcp.tool()
def submit_sequence_analysis(
    input_file: str,
    output_dir: Optional[str] = None,
    stable_only: bool = False,
    min_pnear: Optional[float] = None,
    config_file: Optional[str] = None,
    job_name: Optional[str] = None
) -> dict:
    """
    Submit a sequence analysis job for background processing.

    Use this for very large datasets or when you want to track job progress.
    For typical datasets, use analyze_peptide_sequences() for immediate results.

    Args:
        input_file: Path to Pnear_values_*.txt file
        output_dir: Output directory for results
        stable_only: Analyze only stable designs
        min_pnear: Minimum P_near threshold
        config_file: Path to JSON config file
        job_name: Optional name for tracking

    Returns:
        Dictionary with job_id for tracking
    """
    script_path = str(SCRIPTS_DIR / "sequence_analysis.py")

    args = {"input": input_file}
    if output_dir:
        args["output-dir"] = output_dir
    if stable_only:
        args["stable-only"] = ""  # Flag argument
    if min_pnear is not None:
        args["min-pnear"] = min_pnear
    if config_file:
        args["config"] = config_file

    return job_manager.submit_job(
        script_path=script_path,
        args=args,
        job_name=job_name or f"sequence_analysis_{Path(input_file).stem}"
    )

@mcp.tool()
def submit_backbone_parameter_generation(
    peptide_size: int,
    output_dir: Optional[str] = None,
    optimize: bool = False,
    num_combinations: Optional[int] = None,
    config_file: Optional[str] = None,
    job_name: Optional[str] = None
) -> dict:
    """
    Submit backbone parameter generation job for background processing.

    Use this when generating many parameter combinations or for integration
    with automated workflows. For typical use, generate_backbone_parameters()
    provides immediate results.

    Args:
        peptide_size: Number of residues [7, 15, 20, 24]
        output_dir: Output directory for results
        optimize: Generate parameter combinations
        num_combinations: Number of combinations to generate
        config_file: Path to JSON config file
        job_name: Optional name for tracking

    Returns:
        Dictionary with job_id for tracking
    """
    # Validate peptide size first
    valid_sizes = [7, 15, 20, 24]
    if peptide_size not in valid_sizes:
        return {
            "status": "error",
            "error": f"Invalid peptide size {peptide_size}. Must be one of: {valid_sizes}"
        }

    script_path = str(SCRIPTS_DIR / "backbone_sampling_params.py")

    args = {"size": peptide_size}
    if output_dir:
        args["output-dir"] = output_dir
    if optimize:
        args["optimize"] = ""  # Flag argument
    if num_combinations is not None:
        args["num-combinations"] = num_combinations
    if config_file:
        args["config"] = config_file

    return job_manager.submit_job(
        script_path=script_path,
        args=args,
        job_name=job_name or f"backbone_params_{peptide_size}res"
    )

# ==============================================================================
# Batch Processing Tools
# ==============================================================================

@mcp.tool()
def submit_batch_pnear_analysis(
    input_files: List[str],
    output_base_dir: Optional[str] = None,
    min_pnear: Optional[float] = None,
    config_file: Optional[str] = None,
    job_name: Optional[str] = None
) -> dict:
    """
    Submit batch P_near analysis for multiple input files.

    Processes multiple Pnear_values_*.txt files in a single job.
    Useful for analyzing results from multiple CyclicChamp runs.

    Args:
        input_files: List of paths to Pnear_values_*.txt files
        output_base_dir: Base directory for all outputs
        min_pnear: Minimum P_near threshold for all analyses
        config_file: Path to JSON config file
        job_name: Optional name for the batch job

    Returns:
        Dictionary with job_id for tracking the batch job
    """
    # For now, submit individual jobs - could be optimized with a batch script
    import json

    # Create a batch job by submitting multiple individual jobs
    batch_id = f"batch_{len(input_files)}_files"
    submitted_jobs = []

    for i, input_file in enumerate(input_files):
        file_stem = Path(input_file).stem
        job_result = submit_pnear_analysis(
            input_file=input_file,
            output_dir=f"{output_base_dir}/{file_stem}" if output_base_dir else None,
            min_pnear=min_pnear,
            config_file=config_file,
            job_name=f"{job_name}_{file_stem}" if job_name else f"batch_pnear_{i+1}"
        )

        if job_result["status"] == "submitted":
            submitted_jobs.append(job_result["job_id"])

    return {
        "status": "batch_submitted",
        "batch_id": batch_id,
        "job_ids": submitted_jobs,
        "total_jobs": len(submitted_jobs),
        "message": f"Submitted {len(submitted_jobs)} P_near analysis jobs. Use list_jobs() to monitor all."
    }

@mcp.tool()
def submit_peptide_size_parameter_sweep(
    peptide_sizes: Optional[List[int]] = None,
    output_dir: Optional[str] = None,
    optimize_all: bool = True,
    num_combinations: Optional[int] = None,
    config_file: Optional[str] = None,
    job_name: Optional[str] = None
) -> dict:
    """
    Submit parameter generation jobs for multiple peptide sizes.

    Generates backbone sampling parameters for all specified sizes.
    Useful for comprehensive parameter studies across different peptide lengths.

    Args:
        peptide_sizes: List of peptide sizes (default: [7, 15, 20, 24])
        output_dir: Base output directory
        optimize_all: Generate optimization combinations for all sizes
        num_combinations: Number of combinations per size
        config_file: Path to JSON config file
        job_name: Base name for the parameter sweep jobs

    Returns:
        Dictionary with job_ids for tracking all parameter generation jobs
    """
    if peptide_sizes is None:
        peptide_sizes = [7, 15, 20, 24]

    # Validate all sizes first
    valid_sizes = [7, 15, 20, 24]
    invalid_sizes = [size for size in peptide_sizes if size not in valid_sizes]
    if invalid_sizes:
        return {
            "status": "error",
            "error": f"Invalid peptide sizes {invalid_sizes}. Must be from: {valid_sizes}"
        }

    submitted_jobs = []

    for size in peptide_sizes:
        job_result = submit_backbone_parameter_generation(
            peptide_size=size,
            output_dir=f"{output_dir}/{size}res" if output_dir else None,
            optimize=optimize_all,
            num_combinations=num_combinations,
            config_file=config_file,
            job_name=f"{job_name}_{size}res" if job_name else f"params_{size}res"
        )

        if job_result["status"] == "submitted":
            submitted_jobs.append(job_result["job_id"])

    return {
        "status": "sweep_submitted",
        "sweep_id": f"param_sweep_{len(peptide_sizes)}_sizes",
        "job_ids": submitted_jobs,
        "peptide_sizes": peptide_sizes,
        "total_jobs": len(submitted_jobs),
        "message": f"Submitted {len(submitted_jobs)} parameter generation jobs for sizes {peptide_sizes}"
    }

# ==============================================================================
# Utility Tools
# ==============================================================================

@mcp.tool()
def list_available_configs() -> dict:
    """
    List all available configuration files for CyclicChamp tools.

    Returns:
        Dictionary with available config files and their descriptions
    """
    config_files = {
        "pnear_analysis_config.json": "P_near analysis settings (thresholds, plotting options)",
        "sequence_analysis_config.json": "Sequence analysis settings (amino acid properties, plotting)",
        "backbone_sampling_config.json": "Backbone parameter formulas and optimization settings",
        "default_config.json": "Global default settings for all tools"
    }

    available_configs = {}
    for config_file, description in config_files.items():
        config_path = CONFIG_DIR / config_file
        if config_path.exists():
            available_configs[config_file] = {
                "description": description,
                "path": str(config_path),
                "exists": True
            }
        else:
            available_configs[config_file] = {
                "description": description,
                "path": str(config_path),
                "exists": False
            }

    return {
        "status": "success",
        "configs": available_configs,
        "config_directory": str(CONFIG_DIR)
    }

@mcp.tool()
def get_config_contents(config_file: str) -> dict:
    """
    Get the contents of a configuration file.

    Args:
        config_file: Name of the config file (e.g., "pnear_analysis_config.json")

    Returns:
        Dictionary with the config file contents
    """
    try:
        config_path = Path(config_file)
        if not config_path.is_absolute():
            config_path = CONFIG_DIR / config_path

        if not config_path.exists():
            return {"status": "error", "error": f"Config file not found: {config_path}"}

        import json
        with open(config_path) as f:
            config_data = json.load(f)

        return {
            "status": "success",
            "config_file": str(config_path),
            "contents": config_data
        }

    except json.JSONDecodeError as e:
        return {"status": "error", "error": f"Invalid JSON in config file: {e}"}
    except Exception as e:
        return {"status": "error", "error": f"Failed to read config file: {e}"}

@mcp.tool()
def get_tool_info() -> dict:
    """
    Get information about all available CyclicChamp MCP tools.

    Returns:
        Dictionary with tool categories, descriptions, and usage patterns
    """
    return {
        "status": "success",
        "server_info": {
            "name": "cyclicchamp-tools",
            "version": "1.0.0",
            "description": "MCP server for CyclicChamp cyclic peptide analysis tools"
        },
        "tool_categories": {
            "job_management": {
                "tools": ["get_job_status", "get_job_result", "get_job_log", "cancel_job", "list_jobs"],
                "description": "Manage asynchronous job execution"
            },
            "sync_analysis": {
                "tools": ["analyze_pnear_stability", "analyze_peptide_sequences", "generate_backbone_parameters"],
                "description": "Fast analysis tools with immediate results (<3 seconds)"
            },
            "async_analysis": {
                "tools": ["submit_pnear_analysis", "submit_sequence_analysis", "submit_backbone_parameter_generation"],
                "description": "Submit analysis jobs for background processing"
            },
            "batch_processing": {
                "tools": ["submit_batch_pnear_analysis", "submit_peptide_size_parameter_sweep"],
                "description": "Process multiple inputs or parameter combinations"
            },
            "utilities": {
                "tools": ["list_available_configs", "get_config_contents", "get_tool_info"],
                "description": "Configuration management and tool information"
            }
        },
        "usage_patterns": {
            "quick_analysis": "Use sync tools (analyze_*) for immediate results",
            "large_datasets": "Use submit tools (submit_*) for tracking and background processing",
            "batch_processing": "Use batch tools for multiple inputs",
            "job_tracking": "Use job management tools to monitor submitted jobs"
        },
        "supported_input_formats": {
            "pnear_files": "Tab-delimited Pnear_values_*.txt files with columns: Name, Energy, P_near_Rosetta, P_near_GA, Sequence",
            "peptide_sizes": "Integer values: 7, 15, 20, or 24 residues",
            "config_files": "JSON configuration files for customizing analysis parameters"
        }
    }

# ==============================================================================
# Entry Point
# ==============================================================================

if __name__ == "__main__":
    mcp.run()