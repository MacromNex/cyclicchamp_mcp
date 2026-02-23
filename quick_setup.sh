#!/bin/bash
# Quick Setup Script for CyclicChamp MCP
# CyclicPeptide/CyclicChamp: Heuristic energy-based cyclic peptide design pipeline
# Designs cyclic peptides of mixed L- and D-amino acids, and non-canonical amino acids
# Requires Rosetta installation for full functionality
# Source: https://github.com/qiyaozhu/CyclicPeptide

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Setting up CyclicChamp MCP ==="

# Step 1: Create Python environment
echo "[1/3] Creating Python 3.12 environment..."
(command -v mamba >/dev/null 2>&1 && mamba create -p ./env python=3.12 pip -y) || \
(command -v conda >/dev/null 2>&1 && conda create -p ./env python=3.12 pip -y) || \
(echo "Warning: Neither mamba nor conda found, creating venv instead" && python3 -m venv ./env)

# Step 2: Install core dependencies
echo "[2/3] Installing core dependencies..."
./env/bin/pip install matplotlib numpy scipy loguru click pandas tqdm

# Step 3: Install fastmcp
echo "[3/3] Installing fastmcp..."
./env/bin/pip install --force-reinstall --no-cache-dir fastmcp

echo ""
echo "=== CyclicChamp MCP Setup Complete ==="
echo "Note: Full CyclicChamp functionality requires Rosetta installation"
echo "See: https://docs.rosettacommons.org/docs/latest/getting_started/Getting-Started"
echo "To run the MCP server: ./env/bin/python src/server.py"
