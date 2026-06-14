$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$serverExe = Join-Path $repoRoot "llama-b9632-bin-win-vulkan-x64\llama-server.exe"

if (-not (Test-Path -LiteralPath $serverExe)) {
    Write-Error @"
Could not find local llama-server.exe.

Expected:
  $serverExe

Download or extract a llama.cpp Windows runtime folder that matches llama-*-bin-*/ and contains llama-server.exe.
"@
}

& $serverExe -hf "ggml-org/gpt-oss-20b-GGUF" --ctx-size 32768 --jinja -ub 2048 -b 2048
exit $LASTEXITCODE
