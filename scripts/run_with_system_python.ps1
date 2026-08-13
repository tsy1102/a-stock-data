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
# V16.4.1: 强制 UTF-8 输出（opencode 子进程不加载 Profile，系统代码页 936 时中文乱码）
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [Console]::OutputEncoding

# ────────────────────────────────────────────────────────────────────────────
# 自动探测系统 Python 3.12（不再硬编码路径——机器/发行版不同会失效）
# 探测顺序:
#   1) 环境变量 SYSTEM_PYTHON_EXE 显式指定（优先）
#   2) py 启动器:  py -3.12 -c "import sys; print(sys.executable)"
#   3) Windows Store Python 3.12 包目录（AppData 内 shim，随包版本号通配）
#   4) PATH 上的 python.exe 且 --version 输出 Python 3.12.x
# ────────────────────────────────────────────────────────────────────────────
function Find-SystemPython {
    $override = $env:SYSTEM_PYTHON_EXE
    if ($override -and (Test-Path -LiteralPath $override)) {
        return $override
    }

    $pyLauncher = Get-Command py.exe -ErrorAction SilentlyContinue
    if ($pyLauncher) {
        $probe = & $pyLauncher.Source -3.12 -c "import sys; print(sys.executable)" 2>$null
        if ($LASTEXITCODE -eq 0 -and $probe) {
            $p = ($probe | Select-Object -First 1).Trim()
            if (Test-Path -LiteralPath $p) { return $p }
        }
    }

    $storeGlob = Join-Path $env:LOCALAPPDATA 'Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.12_*\python.exe'
    $storePkg = Get-ChildItem -Path $storeGlob -ErrorAction SilentlyContinue |
        Sort-Object Name -Descending | Select-Object -First 1
    if ($storePkg) { return $storePkg.FullName }

    $anyPy = Get-Command python.exe -ErrorAction SilentlyContinue
    if ($anyPy) {
        $ver = (& $anyPy.Source --version 2>&1 | Out-String)
        if ($ver -match 'Python 3\.12') { return $anyPy.Source }
    }
    return $null
}

$PYTHON_EXE = Find-SystemPython
if (-not $PYTHON_EXE) {
    Write-Host "[ERROR] System Python 3.12 not found. Set env SYSTEM_PYTHON_EXE or install Python 3.12." -ForegroundColor Red
    exit 1
}

# Put system Python dir at front of PATH
$PYTHON_DIR = Split-Path -Parent $PYTHON_EXE
$env:PATH = "$PYTHON_DIR;$PYTHON_DIR\Scripts;" + $env:PATH

# Forward all args to system Python (splatting) and propagate exit code
& $PYTHON_EXE @args
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }