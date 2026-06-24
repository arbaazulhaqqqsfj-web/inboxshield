$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot

$bundledPython = Join-Path $env:USERPROFILE ".cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
$pythonCommand = Get-Command python -ErrorAction SilentlyContinue
$pyCommand = Get-Command py -ErrorAction SilentlyContinue

if (Test-Path -LiteralPath $bundledPython) {
    $python = $bundledPython
} elseif ($pythonCommand -and $pythonCommand.Source -notlike "*WindowsApps*") {
    $python = $pythonCommand.Source
} elseif ($pyCommand -and $pyCommand.Source -notlike "*WindowsApps*") {
    $python = $pyCommand.Source
} else {
    throw "Python 3.11+ was not found. Install Python from https://python.org and retry."
}

Write-Host "Starting InboxShield at http://localhost:8080" -ForegroundColor Green
& $python -m inboxshield.web
