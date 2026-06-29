# Runs the test suite with coverage and generates an HTML report.
# Usage: .\run_tests.ps1

$ErrorActionPreference = "Stop"

pytest `
  --cov=. `
  --cov-report=term-missing `
  --cov-report=html `
  --cov-config=.coveragerc

Write-Host ""
Write-Host "HTML coverage report generated at htmlcov/index.html"