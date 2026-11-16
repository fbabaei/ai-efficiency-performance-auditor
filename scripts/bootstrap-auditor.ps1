param(
    [string]$TargetRepoPath,
    [string]$TargetRepoUrl,
    [string]$SourceRepoPath,
    [string]$SourceRepoUrl = "https://github.com/fbabaei/ai-efficiency-performance-auditor.git",
    [string[]]$Skills = @(),
    [switch]$IncludeServicePerformanceSkill,
    [switch]$Interactive,
    [string]$AuditFocus = "latency, token/tool-call efficiency, retries",
    [string]$AuditEmailRecipient = "",
    [switch]$IncludeTeamsNotification = $true
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$script:ProvidedIncludeServiceSkill = $PSBoundParameters.ContainsKey("IncludeServicePerformanceSkill")
$script:ProvidedSkills = $PSBoundParameters.ContainsKey("Skills")
$script:ProvidedAuditFocus = $PSBoundParameters.ContainsKey("AuditFocus")
$script:ProvidedAuditRecipient = $PSBoundParameters.ContainsKey("AuditEmailRecipient")
$script:ProvidedTeamsPreference = $PSBoundParameters.ContainsKey("IncludeTeamsNotification")

function Assert-GitAvailable {
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        throw "git is required but was not found in PATH."
    }
}

function Ensure-Directory([string]$PathValue) {
    if (-not (Test-Path -LiteralPath $PathValue)) {
        New-Item -ItemType Directory -Path $PathValue -Force | Out-Null
    }
}

function Resolve-RepoName([string]$RepoUrl) {
    $name = [IO.Path]::GetFileNameWithoutExtension($RepoUrl.TrimEnd("/"))
    if ([string]::IsNullOrWhiteSpace($name)) {
        throw "Could not infer repository name from URL: $RepoUrl"
    }
    return $name
}

function Ensure-Repo([string]$LocalPath, [string]$RepoUrl) {
    if (Test-Path -LiteralPath $LocalPath) {
        if (-not (Test-Path -LiteralPath (Join-Path $LocalPath ".git"))) {
            throw "Path exists but is not a git repository: $LocalPath"
        }
        Write-Host "Updating repository: $LocalPath"
        & git -C $LocalPath pull --ff-only
        return
    }
    Ensure-Directory -PathValue ([IO.Path]::GetDirectoryName($LocalPath))
    Write-Host "Cloning repository: $RepoUrl -> $LocalPath"
    & git clone $RepoUrl $LocalPath
}

function Copy-DirectoryTree([string]$Source, [string]$Destination) {
    Ensure-Directory -PathValue ([IO.Path]::GetDirectoryName($Destination))
    Copy-Item -LiteralPath $Source -Destination $Destination -Recurse -Force
}

function Compose-ScoutAuditCommand(
    [string]$AuditTarget,
    [string]$Focus,
    [string]$EmailRecipient,
    [bool]$IncludeTeams
) {
    $command = "Audit $AuditTarget; focus on $Focus; format words."
    if (-not [string]::IsNullOrWhiteSpace($EmailRecipient)) {
        if ($IncludeTeams) {
            $command = "Audit $AuditTarget; focus on $Focus; send report to $EmailRecipient and teams; format words."
        }
        else {
            $command = "Audit $AuditTarget; focus on $Focus; send report to $EmailRecipient; format words."
        }
    }
    return $command
}

function Run-InteractivePrompts {
    if ([string]::IsNullOrWhiteSpace($script:TargetRepoPath) -and [string]::IsNullOrWhiteSpace($script:TargetRepoUrl)) {
        Write-Host "Choose target mode:"
        Write-Host "  1) GitHub repository URL"
        Write-Host "  2) Local repository path"
        $mode = Read-Host "Enter 1 or 2"
        if ($mode -eq "1") {
            $script:TargetRepoUrl = Read-Host "Target repository URL"
        }
        elseif ($mode -eq "2") {
            $script:TargetRepoPath = Read-Host "Target local repository path"
        }
        else {
            throw "Invalid selection. Enter 1 or 2."
        }
    }

    if (-not $script:ProvidedIncludeServiceSkill) {
        $include = (Read-Host "Include service-performance-review skill? (Y/n)").Trim()
        if ([string]::IsNullOrWhiteSpace($include) -or $include.ToLowerInvariant() -eq "y" -or $include.ToLowerInvariant() -eq "yes") {
            $script:IncludeServicePerformanceSkill = $true
        }
    }

    if (-not $script:ProvidedSkills -and ($script:Skills | Measure-Object).Count -eq 0) {
        $extraSkills = Read-Host "Additional skills (comma-separated, optional)"
        if (-not [string]::IsNullOrWhiteSpace($extraSkills)) {
            $script:Skills = $extraSkills.Split(",") | ForEach-Object { $_.Trim() } | Where-Object { $_ }
        }
    }

    if (-not $script:ProvidedAuditFocus) {
        $focus = Read-Host "Audit focus (default: latency, token/tool-call efficiency, retries)"
        if (-not [string]::IsNullOrWhiteSpace($focus)) {
            $script:AuditFocus = $focus
        }
    }

    if (-not $script:ProvidedAuditRecipient) {
        $recipient = Read-Host "Email recipient for Scout delivery (optional)"
        if (-not [string]::IsNullOrWhiteSpace($recipient)) {
            $script:AuditEmailRecipient = $recipient
        }
    }

    if (-not $script:ProvidedTeamsPreference) {
        $teams = (Read-Host "Include Teams notification in Scout command? (Y/n)").Trim()
        if ($teams.ToLowerInvariant() -eq "n" -or $teams.ToLowerInvariant() -eq "no") {
            $script:IncludeTeamsNotification = $false
        }
        else {
            $script:IncludeTeamsNotification = $true
        }
    }
}

Assert-GitAvailable

if ([string]::IsNullOrWhiteSpace($TargetRepoPath) -and [string]::IsNullOrWhiteSpace($TargetRepoUrl)) {
    if (-not $Interactive) {
        throw "Provide -TargetRepoPath or -TargetRepoUrl, or run with -Interactive."
    }
}

if ($Interactive) {
    Run-InteractivePrompts
}

$workingRoot = Join-Path $HOME "workspace"
Ensure-Directory -PathValue $workingRoot

$resolvedTargetForAudit = ""
if ([string]::IsNullOrWhiteSpace($TargetRepoPath)) {
    $targetName = Resolve-RepoName -RepoUrl $TargetRepoUrl
    $TargetRepoPath = Join-Path $workingRoot $targetName
    Ensure-Repo -LocalPath $TargetRepoPath -RepoUrl $TargetRepoUrl
    $resolvedTargetForAudit = $TargetRepoUrl
}
elseif (-not (Test-Path -LiteralPath (Join-Path $TargetRepoPath ".git"))) {
    throw "Target path is not a git repository: $TargetRepoPath"
}
else {
    $resolvedTargetForAudit = $TargetRepoPath
}

if ([string]::IsNullOrWhiteSpace($SourceRepoPath)) {
    $sourceName = Resolve-RepoName -RepoUrl $SourceRepoUrl
    $SourceRepoPath = Join-Path $workingRoot $sourceName
    Ensure-Repo -LocalPath $SourceRepoPath -RepoUrl $SourceRepoUrl
}
elseif (-not (Test-Path -LiteralPath (Join-Path $SourceRepoPath ".git"))) {
    throw "Source path is not a git repository: $SourceRepoPath"
}

$sourceAgent = Join-Path $SourceRepoPath ".github\agents\ai-efficiency-performance-auditor.agent.md"
if (-not (Test-Path -LiteralPath $sourceAgent)) {
    throw "Agent definition not found in source repo: $sourceAgent"
}

$targetAgentsDir = Join-Path $TargetRepoPath ".github\agents"
Ensure-Directory -PathValue $targetAgentsDir
Copy-Item -LiteralPath $sourceAgent -Destination (Join-Path $targetAgentsDir "ai-efficiency-performance-auditor.agent.md") -Force
Write-Host "Copied agent definition to $targetAgentsDir"

$skillsToCopy = New-Object System.Collections.Generic.List[string]
if ($IncludeServicePerformanceSkill) {
    $skillsToCopy.Add("service-performance-review")
}
foreach ($skill in $Skills) {
    if (-not [string]::IsNullOrWhiteSpace($skill)) {
        $skillsToCopy.Add($skill.Trim())
    }
}

$skillsToCopy = $skillsToCopy | Select-Object -Unique
if ($skillsToCopy.Count -gt 0) {
    $targetSkillsRoot = Join-Path $TargetRepoPath ".github\skills"
    Ensure-Directory -PathValue $targetSkillsRoot
    foreach ($skillName in $skillsToCopy) {
        $sourceSkill = Join-Path $SourceRepoPath ".github\skills\$skillName"
        if (-not (Test-Path -LiteralPath $sourceSkill)) {
            throw "Requested skill not found in source repo: $sourceSkill"
        }
        $targetSkill = Join-Path $targetSkillsRoot $skillName
        Copy-DirectoryTree -Source $sourceSkill -Destination $targetSkill
        Write-Host "Copied skill: $skillName"
    }
}

Write-Host ""
Write-Host "Bootstrap complete."
Write-Host "Target repo: $TargetRepoPath"
$scoutCommand = Compose-ScoutAuditCommand -AuditTarget $resolvedTargetForAudit -Focus $AuditFocus -EmailRecipient $AuditEmailRecipient -IncludeTeams $IncludeTeamsNotification
$commandFile = Join-Path $TargetRepoPath "SCOUT-AUDIT-COMMAND.txt"
Set-Content -LiteralPath $commandFile -Value $scoutCommand -Encoding UTF8
Write-Host "Scout command saved: $commandFile"
Write-Host ""
Write-Host "Run this in Scout:"
Write-Host $scoutCommand
