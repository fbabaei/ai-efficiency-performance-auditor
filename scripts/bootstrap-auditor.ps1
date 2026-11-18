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
    [IO.Directory]::CreateDirectory($PathValue) | Out-Null
}

function Test-SafePathName([string]$Name) {
    return ($Name -cmatch '\A[a-zA-Z0-9][a-zA-Z0-9._-]*\z' -and
        -not $Name.EndsWith(".") -and $Name -notmatch '\A(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(\.|\z)')
}

function Test-RepoRoot([string]$PathValue) {
    if (-not (Test-Path -LiteralPath $PathValue -PathType Container)) {
        return $false
    }
    $info = & git -C $PathValue rev-parse --is-inside-work-tree --show-prefix 2>$null
    return ($LASTEXITCODE -eq 0 -and ($info -join "`n").TrimEnd("`n") -ceq "true")
}

function Assert-DirectoryPath([string]$PathValue) {
    $item = Get-Item -LiteralPath $PathValue -Force -ErrorAction SilentlyContinue
    if ($null -ne $item -and (-not $item.PSIsContainer -or ($item.Attributes -band [IO.FileAttributes]::ReparsePoint))) {
        throw "Expected a real directory, not a link or other entry: $PathValue"
    }
}

function Assert-NewInstallPath([string]$PathValue) {
    if ($null -ne (Get-Item -LiteralPath $PathValue -Force -ErrorAction SilentlyContinue)) {
        throw "Install path already exists; move it aside before rerunning: $PathValue"
    }
}

function Resolve-RepoName([string]$RepoUrl) {
    $name = ($RepoUrl.TrimEnd("/") -csplit '/')[-1] -creplace '\.git\z'
    if (-not (Test-SafePathName $name)) {
        throw "Could not infer repository name from URL: $RepoUrl"
    }
    return $name
}

function Ensure-Repo([string]$LocalPath, [string]$RepoUrl) {
    Assert-DirectoryPath $LocalPath
    if (Test-Path -LiteralPath $LocalPath) {
        if (-not (Test-RepoRoot $LocalPath)) {
            throw "Path exists but is not a git repository: $LocalPath"
        }
        Write-Host "Updating repository: $LocalPath"
        & git -C $LocalPath pull --ff-only
        if ($LASTEXITCODE -ne 0) { throw "Git pull failed: $LocalPath" }
        return
    }
    Ensure-Directory -PathValue ([IO.Path]::GetDirectoryName($LocalPath))
    Write-Host "Cloning repository: $RepoUrl -> $LocalPath"
    & git clone -- $RepoUrl $LocalPath
    if ($LASTEXITCODE -ne 0) { throw "Git clone failed: $LocalPath" }
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

$skillsToCopy = @(
    if ($IncludeServicePerformanceSkill) { "service-performance-review" }
    foreach ($skill in $Skills) {
        if ($skill -cnotmatch '\A[a-z0-9][a-z0-9-]*\z' -or -not (Test-SafePathName $skill)) {
            throw "Invalid skill name '$skill': use lowercase ASCII letters, digits and hyphens, starting with a letter or digit."
        }
        $skill
    }
)
$skillsToCopy = @($skillsToCopy | Select-Object -Unique)

$workingRoot = Join-Path $HOME "workspace"

$resolvedTargetForAudit = ""
if ([string]::IsNullOrWhiteSpace($TargetRepoPath)) {
    $targetName = Resolve-RepoName -RepoUrl $TargetRepoUrl
    $TargetRepoPath = Join-Path $workingRoot $targetName
    Ensure-Repo -LocalPath $TargetRepoPath -RepoUrl $TargetRepoUrl
    $resolvedTargetForAudit = $TargetRepoUrl
}
elseif (-not (Test-RepoRoot $TargetRepoPath)) {
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
elseif (-not (Test-RepoRoot $SourceRepoPath)) {
    throw "Source path is not a git repository: $SourceRepoPath"
}

$SourceRepoPath = (Resolve-Path -LiteralPath $SourceRepoPath).ProviderPath
$TargetRepoPath = (Resolve-Path -LiteralPath $TargetRepoPath).ProviderPath
$agentName = "ai-efficiency-performance-auditor.agent.md"
$sourceAgentsDir = Join-Path $SourceRepoPath ".github/agents"
$sourceAgent = Join-Path $sourceAgentsDir $agentName
$targetAgentsDir = Join-Path $TargetRepoPath ".github/agents"
$targetAgent = Join-Path $targetAgentsDir $agentName
$sourceSkillsRoot = Join-Path $SourceRepoPath ".github/skills"
$targetSkillsRoot = Join-Path $TargetRepoPath ".github/skills"
$commandFile = Join-Path $TargetRepoPath "SCOUT-AUDIT-COMMAND.txt"

# Preflight every requested input and output before creating install paths.
Assert-DirectoryPath (Join-Path $SourceRepoPath ".github")
Assert-DirectoryPath $sourceAgentsDir
$agentItem = Get-Item -LiteralPath $sourceAgent -Force -ErrorAction SilentlyContinue
if ($null -eq $agentItem -or $agentItem.PSIsContainer -or ($agentItem.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
    throw "Agent definition must be a regular file in the source repo: $sourceAgent"
}
Assert-DirectoryPath (Join-Path $TargetRepoPath ".github")
Assert-DirectoryPath $targetAgentsDir
Assert-NewInstallPath $targetAgent
Assert-NewInstallPath $commandFile
if ($skillsToCopy.Count -gt 0) {
    Assert-DirectoryPath $sourceSkillsRoot
    Assert-DirectoryPath $targetSkillsRoot
    foreach ($skillName in $skillsToCopy) {
        $sourceSkill = Join-Path $sourceSkillsRoot $skillName
        Assert-DirectoryPath $sourceSkill
        if (-not (Test-Path -LiteralPath $sourceSkill -PathType Container)) {
            throw "Requested skill not found in source repo: $sourceSkill"
        }
        foreach ($entry in Get-ChildItem -LiteralPath $sourceSkill -Force -Recurse) {
            if ($entry.Attributes -band [IO.FileAttributes]::ReparsePoint) {
                throw "Skill contains a link: $($entry.FullName)"
            }
        }
        Assert-NewInstallPath (Join-Path $targetSkillsRoot $skillName)
    }
}

$scoutCommand = Compose-ScoutAuditCommand -AuditTarget $resolvedTargetForAudit -Focus $AuditFocus -EmailRecipient $AuditEmailRecipient -IncludeTeams $IncludeTeamsNotification
Ensure-Directory $targetAgentsDir
[IO.File]::Copy($sourceAgent, $targetAgent)
Write-Host "Copied agent definition to $targetAgentsDir"
if ($skillsToCopy.Count -gt 0) {
    Ensure-Directory $targetSkillsRoot
    foreach ($skillName in $skillsToCopy) {
        $sourceSkill = Join-Path $sourceSkillsRoot $skillName
        $targetSkill = Join-Path $targetSkillsRoot $skillName
        New-Item -ItemType Directory -Path $targetSkill | Out-Null
        Get-ChildItem -LiteralPath $sourceSkill -Force | Copy-Item -Destination $targetSkill -Recurse -Force
        Write-Host "Copied skill: $skillName"
    }
}
$stream = [IO.File]::Open($commandFile, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write)
try {
    $bytes = [Text.Encoding]::UTF8.GetBytes($scoutCommand + [Environment]::NewLine)
    $stream.Write($bytes, 0, $bytes.Length)
}
finally {
    $stream.Dispose()
}
Write-Host ""
Write-Host "Bootstrap complete."
Write-Host "Target repo: $TargetRepoPath"
Write-Host "Scout command saved: $commandFile"
Write-Host ""
Write-Host "Run this in Scout:"
Write-Host $scoutCommand
