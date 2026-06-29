#!/bin/bash
# Runs the test suite with coverage and generates an HTML report.
# Usage: ./run_tests.sh

set -e

pytest \
  --cov=. \
  --cov-report=term-missing \
  --cov-report=html \
  --cov-config=.coveragerc

echo ""
echo "HTML coverage report generated at htmlcov/index.html"
