$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -LiteralPath $repoRoot

if (-not $env:OSS20B_BACKEND) {
    $env:OSS20B_BACKEND = "llama_server"
}

$bundledPythonRoot = "C:\Users\Andy\.cache\codex-runtimes\codex-primary-runtime\dependencies\python"
$oss20bExe = Join-Path $bundledPythonRoot "Scripts\oss20b.exe"
$pythonExe = Join-Path $bundledPythonRoot "python.exe"

if (Test-Path -LiteralPath $oss20bExe) {
    & $oss20bExe chat
    exit $LASTEXITCODE
}

if (Test-Path -LiteralPath $pythonExe) {
    & $pythonExe -m oss20b_pro.app chat
    exit $LASTEXITCODE
}

Write-Error @"
Could not find a runnable oss20b command.

Checked:
  $oss20bExe
  $pythonExe

Install the project into the bundled Python runtime or run the module with an available Python 3.11+ interpreter.
"@
