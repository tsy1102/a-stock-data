# ============================================================================
# run_tests.ps1 - 测试统一入口（shell 层强制走 .ps1 中转，禁止直接 pytest）
# ============================================================================
# 目的: 解决 shell 转义 + 路径（-LiteralPath）+ 退出码透传，避免 pytest 直连
#
# 用法 (PowerShell):
#   .\scripts\run_tests.ps1                                                  # 全部（跳过 real_network）
#   .\scripts\run_tests.ps1 -Mode module -Path tests/test_cache.py           # 单文件
#   .\scripts\run_tests.ps1 -Mode real                                       # 仅 real_network
#   .\scripts\run_tests.ps1 -Mode skip_real                                  # 全部但跳过 real_network
#   .\scripts\run_tests.ps1 -Mode expression -Expression "test_cache"        # -k 表达式
#   .\scripts\run_tests.ps1 -Mode skip_real -ExtraArgs '--maxfail=1','-x'    # 离线 + 失败即停
# ============================================================================
# 注意: param() 必须是脚本第一个语句（PS 5.1 解析顺序约束），Set-StrictMode 放在其后。

param(
    [ValidateSet('all', 'module', 'real', 'skip_real', 'expression')]
    [string]$Mode = 'all',
    [string]$Path = '',
    [string]$Expression = '',
    [string[]]$ExtraArgs = @()
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# ────────────────────────────────────────────────────────────────────────────
# 定位仓库根目录（本脚本位于 <root>/scripts/）
# ────────────────────────────────────────────────────────────────────────────
$SCRIPT_ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path
$PROJECT_ROOT = Split-Path -Parent $SCRIPT_ROOT
$RUNNER = Join-Path $SCRIPT_ROOT 'run_with_system_python.ps1'

if (-not (Test-Path -LiteralPath $RUNNER)) {
    Write-Host "[ERROR] run_with_system_python.ps1 not found: $RUNNER" -ForegroundColor Red
    exit 1
}
if (-not (Test-Path -LiteralPath (Join-Path $PROJECT_ROOT 'pyproject.toml'))) {
    Write-Host "[ERROR] 工作目录不是仓库根（pyproject.toml 缺失）: $PROJECT_ROOT" -ForegroundColor Red
    Write-Host "        请在仓库根目录下运行 .\scripts\run_tests.ps1" -ForegroundColor Yellow
    exit 1
}

# ────────────────────────────────────────────────────────────────────────────
# 装配 pytest 参数（对应 pyproject.toml [tool.pytest.ini_options]）
# ────────────────────────────────────────────────────────────────────────────
$pytestArgs = @('-m', 'pytest')

switch ($Mode) {
    'all' {
        $pytestArgs += @('tests/')
    }
    'module' {
        if ([string]::IsNullOrWhiteSpace($Path)) {
            Write-Host "[ERROR] -Mode module 需要 -Path <测试文件>" -ForegroundColor Red
            exit 1
        }
        if (-not (Test-Path -LiteralPath $Path)) {
            Write-Host "[ERROR] 测试文件不存在: $Path" -ForegroundColor Red
            exit 1
        }
        $pytestArgs += $Path
    }
    'real' {
        $pytestArgs += @('tests/', '-m', 'real_network')
    }
    'skip_real' {
        $pytestArgs += @('tests/', '-m', 'not real_network')
    }
    'expression' {
        if ([string]::IsNullOrWhiteSpace($Expression)) {
            Write-Host "[ERROR] -Mode expression 需要 -Expression '<expr>'" -ForegroundColor Red
            exit 1
        }
        $pytestArgs += @('tests/', '-k', $Expression)
    }
}

# 透传额外 pytest 参数
if ($ExtraArgs -and $ExtraArgs.Count -gt 0) {
    $pytestArgs += $ExtraArgs
}

# ────────────────────────────────────────────────────────────────────────────
# 执行（强制走系统 Python 3.12，透传退出码）
# ────────────────────────────────────────────────────────────────────────────
Write-Host "▶ pytest args: $($pytestArgs -join ' ')" -ForegroundColor Cyan
Push-Location -LiteralPath $PROJECT_ROOT
try {
    & $RUNNER @pytestArgs
    $code = $LASTEXITCODE
}
finally {
    Pop-Location
}

if ($code -ne 0) {
    Write-Host "[FAIL] 测试失败，退出码=$code" -ForegroundColor Red
} else {
    Write-Host "[OK] 测试全部通过" -ForegroundColor Green
}
exit $code
