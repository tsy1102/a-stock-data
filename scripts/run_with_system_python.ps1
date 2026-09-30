# ============================================================================
# run_with_system_python.ps1 - Run commands using project/system Python 3.12
# ============================================================================
# Purpose: Select a verified Python 3.12 runtime and forward the command arguments.
#
# Usage (PowerShell):
#   .\scripts\run_with_system_python.ps1 get_sht_report.py 600519 --no-upload
#
# If execution policy blocks the script, allow this invocation only:
#   powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_with_system_python.ps1 ...
# ============================================================================

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
# V16.4.1: 强制 UTF-8 输出（opencode 子进程不加载 Profile，系统代码页 936 时中文乱码）
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [Console]::OutputEncoding

# ────────────────────────────────────────────────────────────────────────────
# 自动探测 Python 3.12（不再硬编码系统路径——机器/发行版不同会失效）
# 探测顺序:
#   1) 环境变量 SYSTEM_PYTHON_EXE 显式指定（优先）
#   2) 项目虚拟环境 .venv\Scripts\python.exe（仅接受 Python 3.12）
#   3) py 启动器:  py -3.12 -c "import sys; print(sys.executable)"
#   4) Windows Store Python 3.12 包目录（AppData 内 shim，随包版本号通配）
#   5) PATH 上的 python.exe 且 --version 输出 Python 3.12.x
# ────────────────────────────────────────────────────────────────────────────
function Invoke-CapturedProcess {
    param(
        [string]$FileName,
        [string]$Arguments
    )

    $startInfo = [System.Diagnostics.ProcessStartInfo]::new()
    $startInfo.FileName = $FileName
    $startInfo.Arguments = $Arguments
    $startInfo.UseShellExecute = $false
    $startInfo.CreateNoWindow = $true
    $startInfo.RedirectStandardOutput = $true
    $startInfo.RedirectStandardError = $true
    $startInfo.StandardOutputEncoding = [System.Text.UTF8Encoding]::new($false)
    $startInfo.StandardErrorEncoding = [System.Text.UTF8Encoding]::new($false)
    $startInfo.EnvironmentVariables['PYTHONUTF8'] = '1'

    $process = [System.Diagnostics.Process]::new()
    $process.StartInfo = $startInfo
    if (-not $process.Start()) {
        throw "Failed to start process: $FileName"
    }

    $stdout = $process.StandardOutput.ReadToEnd()
    $stderr = $process.StandardError.ReadToEnd()
    $process.WaitForExit()
    $result = [pscustomobject]@{
        ExitCode = $process.ExitCode
        Output = $stdout
        Error = $stderr
    }
    $process.Dispose()
    return $result
}

function Get-PythonVersionProbe {
    param([string]$Executable)

    if (-not (Test-Path -LiteralPath $Executable -PathType Leaf)) {
        return [pscustomobject]@{ IsPython312 = $false; Version = 'executable not found' }
    }

    $result = Invoke-CapturedProcess -FileName $Executable -Arguments '--version'
    $version = ($result.Output + $result.Error).Trim()
    $is312 = $result.ExitCode -eq 0 -and $version -match '^Python 3\.12(?:\.\d+)?$'
    return [pscustomobject]@{ IsPython312 = $is312; Version = $version }
}

function Find-SystemPython {
    $override = $env:SYSTEM_PYTHON_EXE
    if (-not [string]::IsNullOrWhiteSpace($override)) {
        $probe = Get-PythonVersionProbe -Executable $override
        if (-not $probe.IsPython312) {
            Write-Host "[ERROR] SYSTEM_PYTHON_EXE must point to Python 3.12: $override ($($probe.Version))" -ForegroundColor Red
            exit 1
        }
        return $override
    }

    $projectRoot = Split-Path -Parent $PSScriptRoot
    $projectVenvPython = Join-Path $projectRoot '.venv\Scripts\python.exe'
    if ((Get-PythonVersionProbe -Executable $projectVenvPython).IsPython312) {
        return $projectVenvPython
    }

    $pyLauncher = Get-Command py.exe -ErrorAction SilentlyContinue
    if ($pyLauncher) {
        $launcherArgs = '-3.12 -X utf8 -c "import sys; print(sys.executable)"'
        $launcherResult = Invoke-CapturedProcess -FileName $pyLauncher.Source -Arguments $launcherArgs
        $pythonPath = ''
        foreach ($line in ($launcherResult.Output -split "`r?`n")) {
            if (-not [string]::IsNullOrWhiteSpace($line)) {
                $pythonPath = $line.Trim()
                break
            }
        }
        if ($launcherResult.ExitCode -eq 0 -and (Get-PythonVersionProbe -Executable $pythonPath).IsPython312) {
            return $pythonPath
        }
    }

    if ($env:LOCALAPPDATA) {
        $storeRoot = Join-Path $env:LOCALAPPDATA 'Microsoft\WindowsApps'
        if (Test-Path -LiteralPath $storeRoot) {
            $storePackages = Get-ChildItem -LiteralPath $storeRoot -Directory -ErrorAction SilentlyContinue |
                Where-Object { $_.Name -like 'PythonSoftwareFoundation.Python.3.12_*' } |
                Sort-Object Name -Descending
            foreach ($package in $storePackages) {
                $storePython = Join-Path $package.FullName 'python.exe'
                if ((Get-PythonVersionProbe -Executable $storePython).IsPython312) {
                    return $storePython
                }
            }
        }
    }

    $anyPython = Get-Command python.exe -ErrorAction SilentlyContinue
    if ($anyPython -and (Get-PythonVersionProbe -Executable $anyPython.Source).IsPython312) {
        return $anyPython.Source
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
