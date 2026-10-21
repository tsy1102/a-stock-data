# ============================================================================
# run_offline_checks.ps1 - 单一离线维护验收入口
# ============================================================================
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [Console]::OutputEncoding

$SCRIPT_ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path
$PROJECT_ROOT = Split-Path -Parent $SCRIPT_ROOT
$PYTHON_RUNNER = Join-Path $SCRIPT_ROOT 'run_with_system_python.ps1'
$TEST_RUNNER = Join-Path $SCRIPT_ROOT 'run_tests.ps1'

if (-not (Test-Path -LiteralPath (Join-Path $PROJECT_ROOT 'pyproject.toml'))) {
    throw "项目根目录无 pyproject.toml: $PROJECT_ROOT"
}
if (-not (Test-Path -LiteralPath $PYTHON_RUNNER)) {
    throw "Python 启动器不存在: $PYTHON_RUNNER"
}
if (-not (Test-Path -LiteralPath $TEST_RUNNER)) {
    throw "测试启动器不存在: $TEST_RUNNER"
}

function Invoke-PythonCheck {
    param(
        [string]$Label,
        [string[]]$PythonArguments
    )
    Write-Host "▶ $Label" -ForegroundColor Cyan
    & $PYTHON_RUNNER @PythonArguments
    $exitCode = $LASTEXITCODE
    if ($exitCode -ne 0) {
        throw "$Label 失败，退出码=$exitCode"
    }
}

Push-Location -LiteralPath $PROJECT_ROOT
try {
    Invoke-PythonCheck 'Python 语法' @('scripts/verify_python_syntax.py')
    Invoke-PythonCheck 'Mypy 类型' @('-m', 'mypy')
    Invoke-PythonCheck 'Black 格式' @('scripts/verify_black_api.py')
    Invoke-PythonCheck 'AxData 摘要新鲜度' @('scripts/build_axdata_crosswalk_summary.py', '--check')
    Invoke-PythonCheck '数据访问收口' @('scripts/verify_data_access.py')
    Invoke-PythonCheck '字典与附录同步' @('scripts/verify_sync_check.py')
    Invoke-PythonCheck 'Canonical contract' @('scripts/verify_canonical_contract.py')
    Invoke-PythonCheck 'Registry parity' @('scripts/registry_parity.py')

    Write-Host '▶ 离线测试套件' -ForegroundColor Cyan
    & $TEST_RUNNER -Mode skip_real
    $testExitCode = $LASTEXITCODE
    if ($testExitCode -ne 0) {
        throw "离线测试套件失败，退出码=$testExitCode"
    }
    Write-Host '✅ 离线维护验收全部通过' -ForegroundColor Green
}
finally {
    Pop-Location
}
