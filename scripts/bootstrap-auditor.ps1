param(
    [string]$TargetRepoPath,
    [string]$TargetRepoUrl,
    [string]$SourceRepoPath,
    [string]$SourceRepoUrl = "https://github.com/fbabaei/ai-efficiency-performance-auditor.git",
    [string[]]$Skills = @(),
    [switch]$IncludeServicePerformanceSkill
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

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

Assert-GitAvailable

if ([string]::IsNullOrWhiteSpace($TargetRepoPath) -and [string]::IsNullOrWhiteSpace($TargetRepoUrl)) {
    throw "Provide -TargetRepoPath or -TargetRepoUrl."
}

$workingRoot = Join-Path $HOME "workspace"
Ensure-Directory -PathValue $workingRoot

if ([string]::IsNullOrWhiteSpace($TargetRepoPath)) {
    $targetName = Resolve-RepoName -RepoUrl $TargetRepoUrl
    $TargetRepoPath = Join-Path $workingRoot $targetName
    Ensure-Repo -LocalPath $TargetRepoPath -RepoUrl $TargetRepoUrl
}
elseif (-not (Test-Path -LiteralPath (Join-Path $TargetRepoPath ".git"))) {
    throw "Target path is not a git repository: $TargetRepoPath"
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
Write-Host "Next step: open the target repo and run an audit prompt with AI Efficiency & Performance Auditor."
