#!/usr/bin/env python3
"""
Basic Validation Test for CyclicChamp MCP Server

This script validates that the server can be imported and key components work,
without trying to call MCP tools directly.
"""

import sys
from pathlib import Path
import json
from datetime import datetime

# Setup paths
SCRIPT_DIR = Path(__file__).parent.resolve()
MCP_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(MCP_ROOT / "src"))
sys.path.insert(0, str(MCP_ROOT / "scripts"))

def test_basic_functionality():
    """Run basic validation tests."""
    results = {
        "test_date": datetime.now().isoformat(),
        "tests": {},
        "summary": {}
    }

    # Test 1: Server Import
    try:
        from src.server import mcp
        results["tests"]["server_import"] = {
            "status": "passed",
            "message": "Server imports successfully"
        }
    except Exception as e:
        results["tests"]["server_import"] = {
            "status": "failed",
            "error": str(e)
        }

    # Test 2: Job Manager
    try:
        from src.jobs.manager import job_manager
        job_list = job_manager.list_jobs()
        job_count = len(job_list.get('jobs', []))
        results["tests"]["job_manager"] = {
            "status": "passed",
            "message": f"Job manager works, {job_count} existing jobs",
            "job_count": job_count
        }
    except Exception as e:
        results["tests"]["job_manager"] = {
            "status": "failed",
            "error": str(e)
        }

    # Test 3: Script Functions Import
    try:
        from pnear_analysis import run_pnear_analysis
        from sequence_analysis import run_sequence_analysis
        from backbone_sampling_params import run_backbone_sampling_params
        results["tests"]["script_functions"] = {
            "status": "passed",
            "message": "All script functions import successfully"
        }
    except Exception as e:
        results["tests"]["script_functions"] = {
            "status": "failed",
            "error": str(e)
        }

    # Test 4: Demo Data Access
    demo_files = [
        MCP_ROOT / "examples" / "data" / "20res_Pnear_list.txt",
        MCP_ROOT / "examples" / "data" / "24res_Pnear_list.txt",
        MCP_ROOT / "examples" / "data" / "Pnear_list.txt"
    ]
    accessible = [f.name for f in demo_files if f.exists()]
    results["tests"]["demo_data_access"] = {
        "status": "passed" if len(accessible) >= 2 else "failed",
        "message": f"Can access {len(accessible)} demo files",
        "accessible_files": accessible
    }

    # Test 5: Dependencies
    try:
        import matplotlib
        import pandas
        import numpy
        import seaborn
        results["tests"]["dependencies"] = {
            "status": "passed",
            "message": "All required dependencies available"
        }
    except Exception as e:
        results["tests"]["dependencies"] = {
            "status": "failed",
            "error": str(e)
        }

    # Test 6: Output Directory Creation
    try:
        test_output = MCP_ROOT / "test_results" / "validation"
        test_output.mkdir(parents=True, exist_ok=True)
        results["tests"]["output_directory"] = {
            "status": "passed",
            "message": "Can create output directories"
        }
    except Exception as e:
        results["tests"]["output_directory"] = {
            "status": "failed",
            "error": str(e)
        }

    # Calculate summary
    total = len(results["tests"])
    passed = sum(1 for test in results["tests"].values() if test.get("status") == "passed")
    results["summary"] = {
        "total_tests": total,
        "passed": passed,
        "failed": total - passed,
        "success_rate": f"{(passed/total)*100:.1f}%" if total > 0 else "0%"
    }

    return results

def main():
    print("🔧 Basic MCP Server Validation")
    print("=" * 50)

    results = test_basic_functionality()

    for test_name, result in results["tests"].items():
        status_icon = "✓" if result["status"] == "passed" else "✗"
        print(f"{status_icon} {test_name.replace('_', ' ').title()}: {result.get('message', result.get('error'))}")

    print("\n" + "=" * 50)
    print("Summary:")
    print(f"  Total: {results['summary']['total_tests']}")
    print(f"  Passed: {results['summary']['passed']}")
    print(f"  Failed: {results['summary']['failed']}")
    print(f"  Success Rate: {results['summary']['success_rate']}")

    # Save results
    results_file = MCP_ROOT / "reports" / "basic_validation.json"
    results_file.parent.mkdir(exist_ok=True)
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {results_file}")

    success = results['summary']['passed'] == results['summary']['total_tests']
    if success:
        print("\n🎉 All basic validations PASSED!")
        print("✓ Ready for MCP integration testing")
    else:
        print(f"\n⚠️  {results['summary']['failed']} validations failed")

    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)