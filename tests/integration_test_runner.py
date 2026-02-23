#!/usr/bin/env python3
"""
Integration Test Runner for CyclicChamp MCP Server

This script tests the MCP server functionality by calling tools directly,
simulating how they would be called through Claude Code or Gemini CLI.
"""

import json
import sys
import time
from datetime import datetime
from pathlib import Path

# Setup paths
SCRIPT_DIR = Path(__file__).parent.resolve()
MCP_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(MCP_ROOT / "src"))

def create_test_result():
    """Create a test result structure."""
    return {
        "test_date": datetime.now().isoformat(),
        "server_path": str(MCP_ROOT / "src" / "server.py"),
        "environment": "Python " + sys.version.split()[0],
        "tests": {},
        "summary": {},
        "issues": []
    }

def test_server_startup():
    """Test 1: Server Startup and Import"""
    try:
        from src.server import mcp
        return {
            "status": "passed",
            "message": "Server imports successfully",
            "execution_time": "< 1s"
        }
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e),
            "execution_time": "< 1s"
        }

def test_tool_info():
    """Test 2: Tool Information"""
    try:
        from src.server import mcp
        # We can't directly call mcp tools in this context, but we can verify the functions exist
        # Let's check the actual function from the server module

        # Import the tool function directly
        sys.path.insert(0, str(MCP_ROOT / "src"))
        from server import get_tool_info

        result = get_tool_info()

        if result["status"] == "success":
            tool_count = sum(len(cat["tools"]) for cat in result["tool_categories"].values())
            return {
                "status": "passed",
                "message": f"Found {tool_count} tools across {len(result['tool_categories'])} categories",
                "tool_categories": list(result["tool_categories"].keys()),
                "execution_time": "< 1s"
            }
        else:
            return {
                "status": "failed",
                "error": "get_tool_info returned error status",
                "execution_time": "< 1s"
            }
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e),
            "execution_time": "< 1s"
        }

def test_job_manager():
    """Test 3: Job Manager Integration"""
    try:
        from src.jobs.manager import job_manager

        # Test list jobs
        jobs_result = job_manager.list_jobs()

        if isinstance(jobs_result, dict):
            job_count = len(jobs_result.get('jobs', []))
            return {
                "status": "passed",
                "message": f"Job manager operational, found {job_count} existing jobs",
                "existing_jobs": job_count,
                "execution_time": "< 1s"
            }
        else:
            return {
                "status": "failed",
                "error": "Job manager returned unexpected result type",
                "execution_time": "< 1s"
            }
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e),
            "execution_time": "< 1s"
        }

def test_demo_data_access():
    """Test 4: Demo Data Access"""
    try:
        demo_files = [
            MCP_ROOT / "examples" / "data" / "20res_Pnear_list.txt",
            MCP_ROOT / "examples" / "data" / "24res_Pnear_list.txt",
            MCP_ROOT / "examples" / "data" / "Pnear_list.txt"
        ]

        accessible_files = []
        for file_path in demo_files:
            if file_path.exists() and file_path.is_file():
                accessible_files.append(file_path.name)

        if len(accessible_files) >= 2:
            return {
                "status": "passed",
                "message": f"Can access {len(accessible_files)} demo files",
                "accessible_files": accessible_files,
                "execution_time": "< 1s"
            }
        else:
            return {
                "status": "failed",
                "error": f"Only {len(accessible_files)} demo files accessible",
                "accessible_files": accessible_files,
                "execution_time": "< 1s"
            }
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e),
            "execution_time": "< 1s"
        }

def test_sync_tool_execution():
    """Test 5: Sync Tool Execution"""
    try:
        # Test backbone parameter generation (fastest sync tool)
        from server import generate_backbone_parameters

        result = generate_backbone_parameters(
            peptide_size=15,
            output_dir=None,
            optimize=False
        )

        if result.get("status") == "success":
            return {
                "status": "passed",
                "message": "Sync tool executed successfully",
                "tool_tested": "generate_backbone_parameters",
                "result_keys": list(result.keys()),
                "execution_time": "1-3s"
            }
        else:
            return {
                "status": "failed",
                "error": f"Tool returned error: {result.get('error', 'Unknown error')}",
                "execution_time": "1-3s"
            }
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e),
            "execution_time": "1-3s"
        }

def test_error_handling():
    """Test 6: Error Handling"""
    try:
        from server import generate_backbone_parameters

        # Test with invalid peptide size
        result = generate_backbone_parameters(peptide_size=99)  # Invalid size

        if result.get("status") == "error" and "Invalid peptide size" in result.get("error", ""):
            return {
                "status": "passed",
                "message": "Error handling works correctly",
                "error_message": result["error"],
                "execution_time": "< 1s"
            }
        else:
            return {
                "status": "failed",
                "error": "Expected error not returned properly",
                "actual_result": result,
                "execution_time": "< 1s"
            }
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e),
            "execution_time": "< 1s"
        }

def run_integration_tests():
    """Run all integration tests."""
    print("🧪 CyclicChamp MCP Integration Tests")
    print("=" * 60)

    test_result = create_test_result()

    tests = [
        ("Server Startup", test_server_startup),
        ("Tool Information", test_tool_info),
        ("Job Manager", test_job_manager),
        ("Demo Data Access", test_demo_data_access),
        ("Sync Tool Execution", test_sync_tool_execution),
        ("Error Handling", test_error_handling),
    ]

    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name} test...")
        start_time = time.time()

        try:
            result = test_func()
            elapsed = time.time() - start_time
            result["actual_execution_time"] = f"{elapsed:.2f}s"

            if result["status"] == "passed":
                print(f"   ✓ PASSED: {result['message']}")
            else:
                print(f"   ✗ FAILED: {result.get('error', 'Unknown error')}")
                test_result["issues"].append({
                    "test": test_name,
                    "error": result.get("error"),
                    "severity": "high" if test_name in ["Server Startup", "Tool Information"] else "medium"
                })

            test_result["tests"][test_name.lower().replace(" ", "_")] = result

        except Exception as e:
            print(f"   💥 ERROR: {e}")
            test_result["tests"][test_name.lower().replace(" ", "_")] = {
                "status": "error",
                "error": str(e),
                "execution_time": f"{time.time() - start_time:.2f}s"
            }
            test_result["issues"].append({
                "test": test_name,
                "error": str(e),
                "severity": "critical"
            })

    # Calculate summary
    total_tests = len(test_result["tests"])
    passed_tests = sum(1 for test in test_result["tests"].values() if test.get("status") == "passed")
    failed_tests = total_tests - passed_tests

    test_result["summary"] = {
        "total_tests": total_tests,
        "passed": passed_tests,
        "failed": failed_tests,
        "success_rate": f"{(passed_tests/total_tests)*100:.1f}%" if total_tests > 0 else "0%",
        "high_severity_issues": len([i for i in test_result["issues"] if i.get("severity") in ["high", "critical"]])
    }

    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print(f"   Total Tests: {total_tests}")
    print(f"   Passed: {passed_tests}")
    print(f"   Failed: {failed_tests}")
    print(f"   Success Rate: {test_result['summary']['success_rate']}")

    if test_result["issues"]:
        print(f"\n⚠️  Issues Found: {len(test_result['issues'])}")
        for issue in test_result["issues"]:
            print(f"   - {issue['test']}: {issue['error']} (severity: {issue['severity']})")

    if passed_tests == total_tests:
        print("\n🎉 All integration tests PASSED!")
        print("✓ MCP server is ready for production use")
        success = True
    else:
        print(f"\n⚠️  {failed_tests} tests failed - needs attention")
        success = False

    # Save results
    results_file = MCP_ROOT / "reports" / "integration_test_results.json"
    results_file.parent.mkdir(exist_ok=True)

    with open(results_file, 'w') as f:
        json.dump(test_result, f, indent=2)

    print(f"\n📝 Results saved to: {results_file}")

    return success, test_result

if __name__ == "__main__":
    success, results = run_integration_tests()
    sys.exit(0 if success else 1)