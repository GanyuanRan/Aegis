#!/usr/bin/env pwsh

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptDir
$sessionStart = Join-Path $scriptDir "session-start"
$homeDirectory = if ($env:HOME) { $env:HOME } elseif ($env:USERPROFILE) { $env:USERPROFILE } else { [Environment]::GetFolderPath("UserProfile") }
$legacySkillsDir = Join-Path $homeDirectory ".config/aegis/skills"
$usingAegisPath = Join-Path $repoRoot "skills/using-aegis/SKILL.md"

$env:AEGIS_HOOK_JSON_STYLE = "compact"
$env:COPILOT_CLI = "1"
Remove-Item Env:CLAUDE_PLUGIN_ROOT -ErrorAction SilentlyContinue

function Get-AegisConfigValue {
    param(
        [string]$Key,
        [string[]]$AllowedValues,
        [string]$DefaultValue
    )

    $environmentName = "AEGIS_{0}" -f $Key.ToUpper()
    $configured = [Environment]::GetEnvironmentVariable($environmentName)
    $configFile = Join-Path $homeDirectory ".config/aegis/config.toml"

    if ([string]::IsNullOrWhiteSpace($configured) -and (Test-Path $configFile)) {
        $matches = Select-String -Path $configFile -Pattern "^\s*$Key\s*=\s*(.+)$"
        if ($matches) {
            $configured = $matches[-1].Matches[0].Groups[1].Value
        }
    }

    if (-not [string]::IsNullOrWhiteSpace($configured)) {
        $configured = ($configured -replace "#.*$", "").Trim()
        $configured = $configured.Trim('"')
        $configured = $configured.Trim("'")
        $configured = $configured.Trim()
    }

    if ($AllowedValues -contains $configured) {
        return $configured
    }

    return $DefaultValue
}

function Write-CopilotFallbackBootstrap {
    if ((Get-AegisConfigValue -Key "activation_mode" -AllowedValues @("auto", "explicit") -DefaultValue "auto") -eq "explicit") {
        Write-Output "{}"
        return
    }

    $tddMode = Get-AegisConfigValue -Key "tdd_mode" -AllowedValues @("auto", "off") -DefaultValue "off"
    try {
        $usingAegisContent = Get-Content -LiteralPath $usingAegisPath -Raw
    } catch {
        $usingAegisContent = "Error reading using-aegis skill"
    }

    $warningMessage = if (Test-Path $legacySkillsDir) {
        "`n`n<important-reminder>IN YOUR FIRST REPLY AFTER SEEING THIS MESSAGE YOU MUST TELL THE USER:⚠️ **WARNING:** Aegis no longer reads custom skills from ~/.config/aegis/skills. Move them to the current host's supported skills surface (for example ~/.claude/skills, ~/.copilot/skills, ~/.agents/skills, or repository .github/skills as appropriate). To make this message go away, remove ~/.config/aegis/skills</important-reminder>"
    } else {
        ""
    }

    $sessionContext = @"
<EXTREMELY_IMPORTANT>
You have Aegis.

Aegis TDD mode: $tddMode. off is the default and disables automatic TDD while verification-before-completion still applies; auto routes strict TDD only when risk warrants.

**Below is the compact 'aegis:using-aegis' hot path. For task-specific workflows, use the Skill tool to load only the relevant skill or reference:**

$usingAegisContent$warningMessage
</EXTREMELY_IMPORTANT>
"@

    @{ additionalContext = $sessionContext } | ConvertTo-Json -Compress | Write-Output
}

$gitBash = $null
if ($env:AEGIS_COPILOT_SKIP_BASH -ne "1") {
    $gitBash = @(
        "C:\Program Files\Git\bin\bash.exe",
        "C:\Program Files (x86)\Git\bin\bash.exe"
    ) | Where-Object { Test-Path $_ } | Select-Object -First 1
}

if ($gitBash) {
    & $gitBash $sessionStart
    exit $LASTEXITCODE
}

if ($env:AEGIS_COPILOT_SKIP_BASH -ne "1" -and (Get-Command bash -ErrorAction SilentlyContinue)) {
    & bash $sessionStart
    exit $LASTEXITCODE
}

Write-CopilotFallbackBootstrap
exit 0
