# MCP Integration Test Prompts for CyclicChamp Tools

This file contains comprehensive test prompts to validate the CyclicChamp MCP server functionality with Claude Code and Gemini CLI.

## Tool Discovery Tests

### Prompt 1: List All Tools
```
What MCP tools are available for cyclic peptides? Give me a brief description of each tool category.
```

### Prompt 2: Tool Details
```
Show me detailed information about the get_tool_info tool and explain what it returns.
```

### Prompt 3: Available Configurations
```
What configuration files are available for the cyclic peptide analysis tools?
```

## Sync Tool Tests (Fast Operations)

### Prompt 4: Basic Tool Discovery
```
Use the get_tool_info tool to show me all available CyclicChamp tools and their categories.
```

### Prompt 5: Pnear Analysis Test
```
Run a P_near stability analysis on the demo data file "examples/data/20res_Pnear_list.txt" using the analyze_pnear_stability tool. Set min_pnear to 0.8 and output_dir to "test_results/pnear_test".
```

### Prompt 6: Sequence Analysis Test
```
Analyze peptide sequences using the analyze_peptide_sequences tool with input file "examples/data/20res_Pnear_list.txt", output directory "test_results/sequence_test", and analyze only stable designs with min_pnear of 0.9.
```

### Prompt 7: Backbone Parameter Generation
```
Generate backbone sampling parameters for a 15-residue cyclic peptide using the generate_backbone_parameters tool. Set optimize=True, num_combinations=10, and output_dir="test_results/params_15res".
```

### Prompt 8: Error Handling - Invalid Peptide Size
```
Try to generate backbone parameters for a peptide size of 25 residues (which should be invalid).
```

### Prompt 9: Error Handling - Missing File
```
Try to run P_near analysis on a non-existent file "nonexistent_file.txt".
```

## Submit API Tests (Async Operations)

### Prompt 10: Submit Pnear Analysis Job
```
Submit a P_near analysis job using submit_pnear_analysis with input file "examples/data/24res_Pnear_list.txt", output directory "test_results/async_pnear", and job name "test_pnear_24res".
```

### Prompt 11: Check Job Status
```
Check the status of the most recently submitted job using get_job_status with the job ID from the previous submission.
```

### Prompt 12: List All Jobs
```
List all jobs using list_jobs to see current status of all submitted jobs.
```

### Prompt 13: Get Job Logs
```
Show the last 30 lines of logs for the most recent job using get_job_log.
```

### Prompt 14: Submit Sequence Analysis Job
```
Submit a sequence analysis job with submit_sequence_analysis for file "examples/data/Pnear_list.txt", output directory "test_results/async_sequence", stable_only=False, and job name "full_sequence_analysis".
```

### Prompt 15: Submit Parameter Generation Job
```
Submit a backbone parameter generation job for peptide size 20 with optimization enabled and 15 combinations using submit_backbone_parameter_generation.
```

### Prompt 16: Monitor Job Progress
```
List only jobs with status "completed" to see which analyses have finished.
```

### Prompt 17: Get Job Results
```
Get the results from the first completed job using get_job_result.
```

## Batch Processing Tests

### Prompt 18: Batch Pnear Analysis
```
Submit a batch P_near analysis for multiple files using submit_batch_pnear_analysis with input files ["examples/data/20res_Pnear_list.txt", "examples/data/24res_Pnear_list.txt"], output base directory "test_results/batch_pnear", and job name "batch_comparison".
```

### Prompt 19: Parameter Sweep for Multiple Sizes
```
Submit a parameter sweep for multiple peptide sizes [7, 15, 20] using submit_peptide_size_parameter_sweep with optimization enabled, 8 combinations per size, and output directory "test_results/param_sweep".
```

### Prompt 20: Monitor Batch Jobs
```
List all jobs to see the status of the batch and sweep operations.
```

## Configuration Tests

### Prompt 21: List Available Configs
```
Use list_available_configs to see what configuration files are available and their descriptions.
```

### Prompt 22: View Config Contents
```
Use get_config_contents to show me the contents of the default configuration file.
```

## Error Recovery Tests

### Prompt 23: Cancel Running Job
```
If any jobs are currently running, cancel one of them using cancel_job.
```

### Prompt 24: Handle Invalid Job ID
```
Try to get the status of a non-existent job ID "invalid_job_123".
```

### Prompt 25: Multiple Error Conditions
```
Try to submit a sequence analysis job with an invalid input file path and see how errors are handled.
```

## End-to-End Real-World Scenarios

### Scenario 1: Complete Analysis Workflow
```
I have a dataset of 20-residue cyclic peptide designs from CyclicChamp. Help me:
1. First, analyze the P_near stability values to identify stable designs
2. Then analyze the sequence composition of only the stable designs
3. Finally, generate optimized backbone parameters for 20-residue peptides
Use the file "examples/data/20res_Pnear_list.txt" and put all outputs in "test_results/workflow1/".
```

### Scenario 2: Parameter Study Workflow
```
I want to do a comprehensive parameter study:
1. Generate backbone parameters for peptides of sizes 7, 15, and 20 residues
2. For each size, create 12 parameter combinations for optimization
3. Track all jobs and show me the results when they complete
Put outputs in "test_results/param_study/".
```

### Scenario 3: Comparative Analysis
```
I have results from two different CyclicChamp runs and want to compare them:
1. Run P_near analysis on both "examples/data/20res_Pnear_list.txt" and "examples/data/24res_Pnear_list.txt"
2. Use a minimum P_near threshold of 0.85 for both
3. Show me which dataset has more stable designs and their characteristics
Put outputs in "test_results/comparison/".
```

### Scenario 4: Large Scale Processing
```
For a large-scale study, I need to:
1. Submit batch analysis of multiple datasets using all available demo files
2. Monitor progress and show me when each completes
3. Compile results once all jobs are done
Use "test_results/large_scale/" as the output directory.
```

## Integration Validation Tests

### Prompt 26: Tool Availability Check
```
Verify that all expected tools are available by listing them and confirm we have:
- 5 job management tools
- 3 sync analysis tools
- 3 async analysis tools
- 2 batch processing tools
- 3 utility tools
```

### Prompt 27: File Access Test
```
Test that the MCP server can access demo data by listing the files it can see in the examples/data/ directory.
```

### Prompt 28: Output Directory Creation
```
Test that the server can create output directories by running a quick analysis with a new output path "test_results/directory_test/".
```

### Prompt 29: Job Persistence Test
```
Submit a job, then immediately check if it appears in the job list to verify job tracking works.
```

### Prompt 30: Cross-Tool Integration
```
Test tool integration by:
1. Using get_tool_info to find analysis tools
2. Using list_available_configs to find config files
3. Running analyze_pnear_stability with a config file
4. Checking that outputs are created properly
```

## Performance and Stress Tests

### Prompt 31: Concurrent Job Submission
```
Submit multiple jobs simultaneously to test job queue handling:
1. Submit pnear analysis job
2. Submit sequence analysis job
3. Submit parameter generation job
4. Check that all jobs are queued properly
```

### Prompt 32: Large Dataset Test
```
Run analysis on the largest demo file "examples/data/Pnear_list.txt" to test performance with more data.
```

## Expected Behaviors

- **Sync tools** should execute within 1-10 seconds and return results immediately
- **Submit tools** should return a job_id and status="submitted" instantly
- **Job management tools** should provide accurate status tracking
- **Error handling** should return structured error messages with helpful details
- **File paths** should work with both relative and absolute paths
- **Batch operations** should create multiple jobs and track them properly
- **Configuration** should allow customization of analysis parameters

## Success Criteria

✓ All tool discovery prompts work and show expected tools
✓ Sync tools execute successfully with demo data
✓ Submit API workflow (submit -> status -> result) functions correctly
✓ Job management tools provide accurate information
✓ Batch processing creates and tracks multiple jobs
✓ Error handling returns helpful messages for invalid inputs
✓ File access works for demo data and output creation
✓ End-to-end scenarios complete successfully
✓ Integration with Claude Code shows all tools available