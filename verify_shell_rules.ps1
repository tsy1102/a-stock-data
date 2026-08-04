Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$root = 'D:\GitHub\test'
$script:pass = 0
$script:fail = 0

function Report-Pass {
    param([string]$Name)
    Write-Host ('[PASS] ' + $Name)
    $script:pass = $script:pass + 1
}

function Report-Fail {
    param([string]$Name, [string]$Msg)
    Write-Host ('[FAIL] ' + $Name + ' : ' + $Msg)
    $script:fail = $script:fail + 1
}

# --- Test 1: literal-path ---
$hit = ''
$probeList = @(
    (Join-Path $root 'scripts\_diag_name.py')
    (Join-Path $env:ProgramFiles 'common files')
)
foreach ($p in $probeList) {
    if ($hit -ne '') { break }
    if (Test-Path -LiteralPath $p) { $hit = $p }
}
if ($hit -eq '') {
    Report-Fail -Name 'Test1' -Msg 'no candidate path found'
} else {
    Report-Pass -Name ('Test1 literal-path hit (' + $hit + ')')
}

# --- Test 2: env var ---
$env:TEST_AGENT_VAR = 'hello-agent'
$val = $env:TEST_AGENT_VAR
Remove-Item Env:\TEST_AGENT_VAR -ErrorAction SilentlyContinue
if ($val -ne 'hello-agent') {
    Report-Fail -Name 'Test2' -Msg ('env readback=' + $val)
} elseif (Test-Path Env:\TEST_AGENT_VAR) {
    Report-Fail -Name 'Test2' -Msg 'env not cleaned'
} else {
    Report-Pass -Name 'Test2 env-var read+write'
}

# --- Test 3: external cmd non-zero exit + stderr capture ---
# Use [System.Diagnostics.ProcessStartInfo] + ::new() (no New-Object, no $varname
# followed by property assignment immediately after) to dodge host wrapping.
$psi = [System.Diagnostics.ProcessStartInfo]::new()
$psi.FileName = 'git.exe'
$psi.Arguments = '--bogus-flag-for-test-12345'
$psi.RedirectStandardError = $true
$psi.RedirectStandardOutput = $true
$psi.UseShellExecute = $false
$proc = [System.Diagnostics.Process]::Start($psi)
$so = $proc.StandardOutput.ReadToEnd()
$se = $proc.StandardError.ReadToEnd()
$proc.WaitForExit()
$combined = $so + $se
$code = $proc.ExitCode

if ($code -eq 0) {
    Report-Fail -Name 'Test3' -Msg 'expected non-zero, got 0'
} elseif ([string]::IsNullOrWhiteSpace($combined)) {
    Report-Fail -Name 'Test3' -Msg 'no stderr/stdout captured from external command'
} else {
    $flat = ($combined.Trim() -replace [char]10, ' | ') -replace [char]13, ''
    Write-Host ('       git exited with code ' + $code + '; message: ' + $flat)
    Report-Pass -Name ('Test3 external-cmd non-zero exit (code=' + $code + ')')
}

Write-Host ''
Write-Host ('summary: pass=' + $script:pass + ' fail=' + $script:fail)
if ($script:fail -gt 0) { exit 1 } else { exit 0 }
