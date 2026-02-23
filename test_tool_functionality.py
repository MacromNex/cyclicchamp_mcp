#!/usr/bin/env python3
"""
Direct Tool Functionality Test

Test the actual tool functions to validate they work correctly.
This simulates what would happen when MCP calls these functions.
"""

import sys
from pathlib import Path
import json
from datetime import datetime

# Setup paths correctly
MCP_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(MCP_ROOT / "src"))
sys.path.insert(0, str(MCP_ROOT / "scripts"))

def test_tool_info():
    """Test 1: Tool Information Discovery"""
    print("🔍 Test 1: Tool Information Discovery")
    try:
        # Import the tool function directly
        import server

        # Get the actual function
        get_tool_info = getattr(server, 'get_tool_info')

        # Call it
        result = get_tool_info()

        if result["status"] == "success":
            print(f"✅ SUCCESS: Found {len(result['tool_categories'])} tool categories")

            for category, info in result["tool_categories"].items():
                print(f"   📁 {category}: {len(info['tools'])} tools")
                for tool in info['tools']:
                    print(f"      - {tool}")

            return True, result
        else:
            print(f"❌ FAILED: {result}")
            return False, result

    except Exception as e:
        print(f"💥 ERROR: {e}")
        return False, {"error": str(e)}

def test_backbone_parameters():
    """Test 2: Backbone Parameter Generation (Sync Tool)"""
    print("\n🔍 Test 2: Backbone Parameter Generation")
    try:
        import server
        generate_backbone_parameters = getattr(server, 'generate_backbone_parameters')

        # Test with valid parameters
        result = generate_backbone_parameters(
            peptide_size=15,
            optimize=False,
            show_plots=False
        )

        if result.get("status") == "success":
            print("✅ SUCCESS: Generated backbone parameters")
            print(f"   📊 Parameters generated for {result.get('metadata', {}).get('peptide_size', '?')} residues")

            if 'parameters' in result:
                params = result['parameters']
                print(f"   🔧 Energy threshold: {params.get('energy_threshold', 'N/A')}")
                print(f"   🌡️  Initial temperature: {params.get('initial_temp', 'N/A')}")

            return True, result
        else:
            print(f"❌ FAILED: {result.get('error', 'Unknown error')}")
            return False, result

    except Exception as e:
        print(f"💥 ERROR: {e}")
        return False, {"error": str(e)}

def test_error_handling():
    """Test 3: Error Handling"""
    print("\n🔍 Test 3: Error Handling")
    try:
        import server
        generate_backbone_parameters = getattr(server, 'generate_backbone_parameters')

        # Test with invalid peptide size
        result = generate_backbone_parameters(peptide_size=99)

        if result.get("status") == "error" and "Invalid peptide size" in result.get("error", ""):
            print("✅ SUCCESS: Error handling works correctly")
            print(f"   ⚠️  Error message: {result['error']}")
            return True, result
        else:
            print(f"❌ FAILED: Expected error not returned. Got: {result}")
            return False, result

    except Exception as e:
        print(f"💥 ERROR: {e}")
        return False, {"error": str(e)}

def test_job_manager():
    """Test 4: Job Manager Functionality"""
    print("\n🔍 Test 4: Job Manager")
    try:
        from jobs.manager import job_manager

        # Test list jobs
        jobs_result = job_manager.list_jobs()

        if isinstance(jobs_result, dict) and 'jobs' in jobs_result:
            job_count = len(jobs_result['jobs'])
            print(f"✅ SUCCESS: Job manager operational")
            print(f"   📋 Found {job_count} existing jobs")

            if job_count > 0:
                print("   📄 Recent jobs:")
                for job in jobs_result['jobs'][:3]:  # Show first 3
                    print(f"      - {job.get('job_id', 'Unknown')}: {job.get('status', 'Unknown')}")

            return True, jobs_result
        else:
            print(f"❌ FAILED: Unexpected result format: {type(jobs_result)}")
            return False, jobs_result

    except Exception as e:
        print(f"💥 ERROR: {e}")
        return False, {"error": str(e)}

def test_pnear_analysis():
    """Test 5: P_near Analysis with Demo Data"""
    print("\n🔍 Test 5: P_near Analysis")
    try:
        import server
        analyze_pnear_stability = getattr(server, 'analyze_pnear_stability')

        # Use smallest demo file for fastest test
        demo_file = "examples/data/20res_Pnear_list.txt"

        if not Path(demo_file).exists():
            print(f"⚠️  SKIPPED: Demo file not found: {demo_file}")
            return True, {"status": "skipped", "reason": "Demo file not available"}

        result = analyze_pnear_stability(
            input_file=demo_file,
            min_pnear=0.8,
            show_plots=False
        )

        if result.get("status") == "success":
            print("✅ SUCCESS: P_near analysis completed")

            if 'designs' in result:
                design_count = len(result['designs'])
                print(f"   🧬 Analyzed {design_count} designs")

            if 'stable_designs_rosetta' in result:
                stable_count = len(result['stable_designs_rosetta'])
                print(f"   ✨ Found {stable_count} stable designs (Rosetta)")

            return True, result
        else:
            print(f"❌ FAILED: {result.get('error', 'Unknown error')}")
            return False, result

    except Exception as e:
        print(f"💥 ERROR: {e}")
        return False, {"error": str(e)}

def test_submit_api():
    """Test 6: Submit API"""
    print("\n🔍 Test 6: Submit API")
    try:
        import server
        submit_backbone_parameter_generation = getattr(server, 'submit_backbone_parameter_generation')

        result = submit_backbone_parameter_generation(
            peptide_size=7,
            optimize=True,
            num_combinations=5,
            job_name="test_submit_api"
        )

        if result.get("status") == "submitted":
            print("✅ SUCCESS: Job submitted successfully")
            print(f"   🆔 Job ID: {result.get('job_id', 'Unknown')}")
            print(f"   📝 Job Name: {result.get('job_name', 'Unknown')}")
            return True, result
        else:
            print(f"❌ FAILED: {result.get('error', 'Unknown error')}")
            return False, result

    except Exception as e:
        print(f"💥 ERROR: {e}")
        return False, {"error": str(e)}

def run_comprehensive_test():
    """Run all functionality tests."""
    print("🧪 CyclicChamp MCP Tools - Comprehensive Functionality Test")
    print("=" * 70)

    tests = [
        ("Tool Information Discovery", test_tool_info),
        ("Backbone Parameter Generation", test_backbone_parameters),
        ("Error Handling", test_error_handling),
        ("Job Manager", test_job_manager),
        ("P_near Analysis", test_pnear_analysis),
        ("Submit API", test_submit_api),
    ]

    results = {}
    passed_count = 0

    for test_name, test_func in tests:
        success, result = test_func()
        results[test_name] = {
            "success": success,
            "result": result
        }
        if success:
            passed_count += 1

    # Summary
    total_tests = len(tests)
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print(f"   Total Tests: {total_tests}")
    print(f"   Passed: {passed_count}")
    print(f"   Failed: {total_tests - passed_count}")
    print(f"   Success Rate: {(passed_count/total_tests)*100:.1f}%")

    if passed_count == total_tests:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ MCP server tools are fully functional")
        status = "success"
    else:
        print(f"\n⚠️  {total_tests - passed_count} tests failed")
        status = "partial_success"

    # Save results
    test_report = {
        "test_date": datetime.now().isoformat(),
        "total_tests": total_tests,
        "passed": passed_count,
        "failed": total_tests - passed_count,
        "success_rate": f"{(passed_count/total_tests)*100:.1f}%",
        "status": status,
        "detailed_results": results
    }

    report_file = Path("reports/tool_functionality_test.json")
    report_file.parent.mkdir(exist_ok=True)

    with open(report_file, 'w') as f:
        json.dump(test_report, f, indent=2)

    print(f"\n📝 Detailed results saved to: {report_file}")

    return status == "success"

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)