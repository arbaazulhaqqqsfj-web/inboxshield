$ErrorActionPreference = "Stop"

$candidates = @(
    (Get-Command python -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source -ErrorAction SilentlyContinue),
    (Get-Command py -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source -ErrorAction SilentlyContinue),
    "$env:USERPROFILE\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
) | Where-Object { $_ -and (Test-Path $_) }

if (-not $candidates) {
    throw "Python 3.11+ was not found. Install Python from https://python.org and retry."
}

$python = $candidates[0]
Write-Host "Starting InboxShield at http://localhost:8080" -ForegroundColor Green
& $python -m inboxshield.web

