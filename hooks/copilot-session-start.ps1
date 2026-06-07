#!/usr/bin/env pwsh

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$sessionStart = Join-Path $scriptDir "session-start"

$env:AEGIS_HOOK_JSON_STYLE = "compact"
$env:COPILOT_CLI = "1"

if (Test-Path Env:CLAUDE_PLUGIN_ROOT) {
    Remove-Item Env:CLAUDE_PLUGIN_ROOT
}

$gitBash = @(
    "C:\Program Files\Git\bin\bash.exe",
    "C:\Program Files (x86)\Git\bin\bash.exe"
) | Where-Object { Test-Path $_ } | Select-Object -First 1

if ($gitBash) {
    & $gitBash $sessionStart
    exit $LASTEXITCODE
}

if (Get-Command bash -ErrorAction SilentlyContinue) {
    & bash $sessionStart
    exit $LASTEXITCODE
}

Write-Output "{}"
exit 0
