<#
.SYNOPSIS
    One-click backup of opencode data + config, optionally project code.
.DESCRIPTION
    Backs up:
      1. opencode data dir   : ~/.local/share/opencode (sessions, auth.json, opencode.db)
      2. opencode config dir : ~/.config/opencode (opencode.jsonc, agents, skills, plugins)
      3. (optional) project  : a code directory (e.g. repo root, pass -ProjectPath . when run from it)
.EXAMPLE
    .\scripts\backup-opencode.ps1 -Destination D:\backup
    .\scripts\backup-opencode.ps1 -Destination D:\backup -IncludeProject -ProjectPath .
#>
param(
    [Parameter(Mandatory = $true)]
    [string]$Destination,
    [switch]$IncludeProject,
    [string]$ProjectPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
# V16.4.1: 强制 UTF-8 输出（opencode 子进程不加载 Profile，系统代码页 936 时中文乱码）
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [Console]::OutputEncoding

function Write-Step {
    param([string]$Message)
    Write-Output ("[STEP] " + $Message)
}

function Copy-Dir {
    param(
        [string]$Source,
        [string]$Target
    )
    if (-not (Test-Path -LiteralPath $Source)) {
        throw "source not found: $Source"
    }
    New-Item -ItemType Directory -Path $Target -Force | Out-Null
    $rbArgs = @($Source, $Target, '/E', '/XJ', '/R:3', '/W:2', '/NFL', '/NDL', '/NJH')
    & robocopy.exe @rbArgs | Out-Null
    $code = $LASTEXITCODE
    if ($code -ge 8) {
        throw "robocopy failed (exit $code): $Source -> $Target"
    }
    if (-not (Test-Path -LiteralPath $Target)) {
        throw "copy failed: $Source -> $Target"
    }
}

$dataDir = Join-Path $env:USERPROFILE '.local\share\opencode'
$configDir = Join-Path $env:USERPROFILE '.config\opencode'

if (-not (Test-Path -LiteralPath $Destination)) {
    New-Item -ItemType Directory -Path $Destination -Force | Out-Null
}
if (-not (Test-Path -LiteralPath $Destination)) {
    throw "cannot create destination: $Destination"
}

$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$target = Join-Path $Destination "opencode-backup-$stamp"
New-Item -ItemType Directory -Path $target | Out-Null
Write-Output ("Backup target: " + $target)

Write-Step 'Backing up opencode data (sessions / auth / db)...'
if (Test-Path -LiteralPath $dataDir) {
    Copy-Dir -Source $dataDir -Target (Join-Path $target 'opencode-data')
} else {
    Write-Warning "data dir not found, skipped: $dataDir"
}

Write-Step 'Backing up opencode config...'
if (Test-Path -LiteralPath $configDir) {
    Copy-Dir -Source $configDir -Target (Join-Path $target 'opencode-config')
} else {
    Write-Warning "config dir not found, skipped: $configDir"
}

if ($IncludeProject) {
    if ([string]::IsNullOrWhiteSpace($ProjectPath)) {
        throw '-IncludeProject requires -ProjectPath'
    }
    Write-Step "Backing up project: $ProjectPath"
    Copy-Dir -Source $ProjectPath -Target (Join-Path $target 'project')
}

$backupPath = Join-Path $target 'opencode-data\auth.json'
if (Test-Path -LiteralPath $backupPath) {
    Write-Warning 'auth.json (API keys) is included in this backup - keep it out of git/shared drives!'
}

$size = (Get-ChildItem -LiteralPath $target -Recurse -File | Measure-Object -Property Length -Sum).Sum
Write-Output ("Backup finished: " + $target + " (" + [math]::Round($size / 1MB, 2) + " MB)")
Write-Output 'On the new machine, restore the two folders to the same locations, then run:  opencode db path'
