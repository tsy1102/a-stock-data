# ============================================================================
# run_with_system_python.ps1 - Run commands using system Python 3.12
# ============================================================================
# Purpose: Avoid TRAE IDE's built-in Python 3.10 and force system Python 3.12
#
# Usage (PowerShell):
#   .\scripts\run_with_system_python.ps1 -m pytest tests/test_cache.py
#   .\scripts\run_with_system_python.ps1 -m unittest tests.test_cache
#   .\scripts\run_with_system_python.ps1 get_sht_report.py 600519 --no-upload
#
# If you hit execution policy error, run once:
#   Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
# ============================================================================

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$PYTHON_EXE = "C:\Users\tsy11\AppData\Local\Python\pythoncore-3.12-64\python.exe"

# Self-check (use -LiteralPath; user AppData path can contain spaces/[ ])
if (-not (Test-Path -LiteralPath $PYTHON_EXE)) {
    Write-Host "[ERROR] System Python 3.12 not found: $PYTHON_EXE" -ForegroundColor Red
    Write-Host "        Please update PYTHON_EXE in this script." -ForegroundColor Red
    exit 1
}

# Put system Python dir at front of PATH
$env:PATH = "C:\Users\tsy11\AppData\Local\Python\pythoncore-3.12-64;C:\Users\tsy11\AppData\Local\Python\pythoncore-3.12-64\Scripts;" + $env:PATH

# Forward all args to system Python (splatting) and propagate exit code
& $PYTHON_EXE @args
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }