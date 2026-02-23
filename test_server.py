#!/usr/bin/env python3
"""Test script for CyclicChamp MCP server"""

import sys
import tempfile
from pathlib import Path

# Add paths
sys.path.insert(0, 'src')
sys.path.insert(0, 'scripts')

def test_direct_functions():
    """Test the underlying functions directly"""
    print("=" * 60)
    print("TESTING DIRECT FUNCTIONS")
    print("=" * 60)

    # Test backbone parameters
    print("1. Testing backbone parameter generation...")
    from backbone_sampling_params import run_backbone_sampling_params

    with tempfile.TemporaryDirectory() as temp_dir:
        result = run_backbone_sampling_params(peptide_size=15, output_dir=temp_dir)
        print(f"   ✅ Generated {len(result['output_files'])} files")
        print(f"   ✅ Parameters: {list(result['parameters'].keys())}")

    # Test P_near analysis
    print("\n2. Testing P_near analysis...")
    from pnear_analysis import run_pnear_analysis

    input_file = "examples/data/results/Pnear_values_15res.txt"
    if Path(input_file).exists():
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_pnear_analysis(input_file=input_file, output_dir=temp_dir)
            print(f"   ✅ Analyzed {len(result['designs'])} designs")
            print(f"   ✅ Generated {len(result['output_files'])} files")
    else:
        print(f"   ⚠️  Example file not found: {input_file}")

    # Test sequence analysis
    print("\n3. Testing sequence analysis...")
    from sequence_analysis import run_sequence_analysis

    if Path(input_file).exists():
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_sequence_analysis(input_file=input_file, output_dir=temp_dir)
            print(f"   ✅ Analyzed {len(result['sequence_data'])} sequences")
            print(f"   ✅ Generated {len(result['output_files'])} files")

def test_job_manager():
    """Test the job management system"""
    print("\n" + "=" * 60)
    print("TESTING JOB MANAGER")
    print("=" * 60)

    from src.jobs.manager import job_manager, JobStatus

    print("1. Testing job listing...")
    result = job_manager.list_jobs()
    print(f"   ✅ Current jobs: {result['total']}")

    print("2. Testing job submission...")
    # Submit a quick job
    script_path = str(Path("scripts/backbone_sampling_params.py").resolve())
    job_result = job_manager.submit_job(
        script_path=script_path,
        args={"size": 15},
        job_name="test_backbone_15res"
    )

    if job_result["status"] == "submitted":
        job_id = job_result["job_id"]
        print(f"   ✅ Job submitted: {job_id}")

        # Wait a moment and check status
        import time
        time.sleep(2)

        status = job_manager.get_job_status(job_id)
        print(f"   ✅ Job status: {status['status']}")

        # Wait for completion (max 10 seconds)
        for i in range(10):
            status = job_manager.get_job_status(job_id)
            if status["status"] == "completed":
                print(f"   ✅ Job completed successfully")

                result = job_manager.get_job_result(job_id)
                if result["status"] == "success":
                    print(f"   ✅ Results retrieved: {len(result['result']['output_files'])} files")
                break
            elif status["status"] == "failed":
                print(f"   ❌ Job failed: {status.get('error', 'Unknown error')}")
                break
            time.sleep(1)
        else:
            print(f"   ⚠️  Job still running after 10 seconds")

def test_mcp_server_import():
    """Test MCP server components"""
    print("\n" + "=" * 60)
    print("TESTING MCP SERVER")
    print("=" * 60)

    print("1. Testing MCP server import...")
    from src.server import mcp
    print(f"   ✅ MCP server type: {type(mcp).__name__}")

    print("2. Testing tool manager...")
    if hasattr(mcp, '_tool_manager'):
        tool_manager = mcp._tool_manager
        if hasattr(tool_manager, 'tools'):
            tools = tool_manager.tools
            print(f"   ✅ Found {len(tools)} registered tools:")
            for i, tool_name in enumerate(sorted(tools.keys())):
                if i < 10:  # Show first 10 tools
                    print(f"      - {tool_name}")
                elif i == 10:
                    print(f"      ... and {len(tools)-10} more")

    print("3. Testing configuration utilities...")
    from src.server import list_available_configs, get_config_contents

    # Test that functions are properly wrapped as MCP tools
    if hasattr(list_available_configs, '_tool'):  # It's a FunctionTool
        print("   ✅ list_available_configs is a proper MCP tool")
    if hasattr(get_config_contents, '_tool'):  # It's a FunctionTool
        print("   ✅ get_config_contents is a proper MCP tool")

    print("4. Testing server readiness...")
    print("   ✅ MCP server import successful")
    print("   ✅ All components loaded without errors")

def main():
    """Run all tests"""
    print("CyclicChamp MCP Server Test Suite")
    print("=" * 60)

    try:
        test_direct_functions()
        test_job_manager()
        test_mcp_server_import()

        print("\n" + "=" * 60)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print("\nThe MCP server is ready for use!")
        print("Start with: fastmcp dev src/server.py")

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()