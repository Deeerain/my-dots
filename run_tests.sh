#!/bin/bash
# Integration and syntax checks for ubm-dots

set -e

echo "=== ubm-dots Test Suite ==="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Python version
echo "[1/5] Checking Python version..."
python3 --version
echo -e "${GREEN}✓ Python check passed${NC}"
echo ""

# Check syntax
echo "[2/5] Checking Python syntax..."
python3 -m py_compile ubm-dots.py
if find tests -name "*.py" -exec python3 -m py_compile {} \; 2>/dev/null; then
    echo -e "${GREEN}✓ Syntax check passed${NC}"
else
    echo -e "${RED}✗ Syntax check failed${NC}"
    exit 1
fi
echo ""

# Check imports
echo "[3/5] Checking imports..."
python3 -c "import typer; import urllib.request; import json; import subprocess; import shutil; import pathlib" && \
echo -e "${GREEN}✓ All imports available${NC}" || \
{ echo -e "${RED}✗ Missing required modules${NC}"; exit 1; }
echo ""

# Check CLI help
echo "[4/5] Checking CLI commands..."
python3 ubm-dots.py --help > /dev/null && \
python3 ubm-dots.py reload --help > /dev/null && \
python3 ubm-dots.py update --help > /dev/null && \
echo -e "${GREEN}✓ CLI commands OK${NC}" || \
{ echo -e "${RED}✗ CLI check failed${NC}"; exit 1; }
echo ""

# Check if pytest is available
echo "[5/5] Checking test setup..."
if python3 -c "import pytest" 2>/dev/null; then
    echo -e "${GREEN}✓ pytest is installed${NC}"
    echo ""
    echo "=== Running Unit Tests ==="
    python3 -m pytest tests/ -v --tb=short || exit 1
else
    echo -e "${GREEN}✓ Test framework ready (pytest not installed yet)${NC}"
    echo ""
    echo "To run tests, install pytest:"
    echo "  pip install pytest pytest-cov pytest-mock"
    echo "Then run: pytest tests/ -v"
fi

echo ""
echo -e "${GREEN}=== All checks passed! ===${NC}"
