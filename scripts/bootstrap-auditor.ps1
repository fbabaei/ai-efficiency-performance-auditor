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
$script:ProvidedSourceUrl = $PSBoundParameters.ContainsKey("SourceRepoUrl")
$script:ProvidedAuditFocus = $PSBoundParameters.ContainsKey("AuditFocus")
$script:ProvidedAuditRecipient = $PSBoundParameters.ContainsKey("AuditEmailRecipient")
$script:ProvidedTeamsPreference = $PSBoundParameters.ContainsKey("IncludeTeamsNotification")
$script:WorkflowPrompt = ""
$script:ExtraFocus = ""

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

function Test-WorkflowCatalog([string]$Root) {
    return (Test-Path -LiteralPath (Join-Path $Root "scripts\audit-workflows.txt") -PathType Leaf) -and
        (Test-Path -LiteralPath (Join-Path $Root "docs\usage-prompts.md") -PathType Leaf)
}

function Initialize-InteractiveSource([string]$LocalPath, [string]$RepoUrl) {
    Assert-DirectoryPath $LocalPath
    if (-not (Test-Path -LiteralPath $LocalPath)) {
        Ensure-Repo -LocalPath $LocalPath -RepoUrl $RepoUrl
        return
    }
    if (-not (Test-RepoRoot $LocalPath)) { throw "Source path is not a git repository: $LocalPath" }
    $origin = & git -C $LocalPath config --local --get remote.origin.url
    if ($LASTEXITCODE -ne 0 -or $origin -cne $RepoUrl) {
        throw "Existing auditor checkout does not match the requested source URL: $LocalPath. Pass -SourceRepoPath to select a trusted checkout explicitly."
    }
    Write-Host "Reusing auditor checkout: $LocalPath"
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

function Select-AuditWorkflow([string]$CatalogRoot) {
    $workflows = @(Get-Content -LiteralPath (Join-Path $CatalogRoot "scripts\audit-workflows.txt") |
        ForEach-Object {
            $fields = $_.Split("|")
            [pscustomobject]@{ Id = $fields[0]; Title = $fields[1]; Skills = $fields[2] }
        })
    $headings = @{
        'audit-start'       = 'Get started'
        'audit-context'     = 'Review application performance'
        'audit-plan'        = 'Plan and review changes'
        'audit-measurement' = 'Measurement and observability'
        'audit-compare'     = 'Compare and verify results'
        'audit-focused'     = 'Combined and trace-only audits'
    }
    $useColor = -not [Console]::IsOutputRedirected -and $Host.UI.SupportsVirtualTerminal -and
        $env:TERM -ne 'dumb' -and -not $env:NO_COLOR
    $categories = @()
    $category = 0
    for ($i = 0; $i -lt $workflows.Count; $i++) {
        $entry = $workflows[$i]
        if ($headings.ContainsKey($entry.Id)) {
            $categories += $headings[$entry.Id]
            $category++
        }
        $entry | Add-Member -NotePropertyName Category -NotePropertyValue $category
    }
    if ($categories.Count -eq 0) { throw "No workflow categories found." }

    while ($true) {
        Write-Host "`nChoose a workflow category:"
        for ($i = 0; $i -lt $categories.Count; $i++) {
            $line = "  $($i + 1)) $($categories[$i])"
            if ($useColor) { Write-Host $line -ForegroundColor Cyan }
            else { Write-Host $line }
        }
        Write-Host "  0) Cancel"
        $choice = (Read-Host "Choose a category [1]").Trim()
        if ($choice -eq "0") { Write-Host "Setup cancelled."; exit 0 }
        if (-not $choice) { $choice = "1" }
        $category = 0
        if (-not [int]::TryParse($choice, [ref]$category) -or $category -lt 1 -or $category -gt $categories.Count) {
            Write-Host "Unknown category. Enter a listed number."
            continue
        }

        $heading = "`n  $($categories[$category - 1])"
        if ($useColor) { Write-Host $heading -ForegroundColor Cyan }
        else { Write-Host $heading }
        $visible = @(for ($i = 0; $i -lt $workflows.Count; $i++) {
            $entry = $workflows[$i]
            if ($entry.Category -ne $category) { continue }
            $number = '    {0,2})' -f ($i + 1)
            $label = " $($entry.Title) [$($entry.Id)]"
            if ($useColor) {
                Write-Host $number -ForegroundColor Green -NoNewline
                Write-Host $label
            }
            else { Write-Host "$number$label" }
            $i
        })
        Write-Host "     B) Back to categories"
        Write-Host "     0) Cancel"
        $defaultNumber = $visible[0] + 1
        while ($true) {
            $answer = (Read-Host "Choose a number or workflow ID [$defaultNumber]").Trim()
            if ($answer -eq "0") { Write-Host "Setup cancelled."; exit 0 }
            if ($answer -eq "b") { break }
            if (-not $answer) { return $workflows[$visible[0]] }
            foreach ($index in $visible) {
                if ($answer -ceq $workflows[$index].Id -or $answer -eq [string]($index + 1)) {
                    return $workflows[$index]
                }
            }
            Write-Host "Unknown workflow in this category. Enter a listed number or ID."
        }
    }
}

function Run-InteractivePrompts([string]$CatalogRoot) {
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

    if ([string]::IsNullOrWhiteSpace($script:TargetRepoPath) -and [string]::IsNullOrWhiteSpace($script:TargetRepoUrl)) {
        throw "A target repository URL or local path is required."
    }
    $workflow = Select-AuditWorkflow -CatalogRoot $CatalogRoot
    $catalog = Get-Content -Raw -LiteralPath (Join-Path $CatalogRoot "docs\usage-prompts.md")
    $sections = @($catalog -csplit '(?m)^## ' | Where-Object {
        ($_ -split '\r?\n', 2)[0] -ceq $workflow.Title
    })
    $blocks = if ($sections.Count -eq 1) {
        [regex]::Matches($sections[0], '(?ms)^```text\r?\n(.*?)^```[ \t]*\r?$')
    }
    $blocks = @($blocks)
    if ($blocks.Count -ne 1 -or -not $blocks[0].Groups[1].Value.Trim()) {
        throw "Expected one nonempty prompt for $($workflow.Title)."
    }
    $script:WorkflowPrompt = $blocks[0].Groups[1].Value.TrimEnd()
    if ($workflow.Skills) { $script:Skills += $workflow.Skills.Split(",") }
    Write-Host "Selected: $($workflow.Title). Required skills: $(if ($workflow.Skills) { $workflow.Skills } else { 'none' })."

    $script:ExtraFocus = if ($script:ProvidedAuditFocus) { $script:AuditFocus } else { Read-Host "Additional focus within this workflow (optional)" }

    if (-not $script:ProvidedAuditRecipient) {
        $recipient = Read-Host "Email recipient for Scout delivery (optional)"
        if (-not [string]::IsNullOrWhiteSpace($recipient)) {
            $script:AuditEmailRecipient = $recipient
        }
    }

    if (-not $script:ProvidedTeamsPreference -and -not [string]::IsNullOrWhiteSpace($script:AuditEmailRecipient)) {
        $script:IncludeTeamsNotification = (Read-Host "Include a Teams completion notification? (y/N)").Trim() -match '\A(y|yes)\z'
    }
}

Assert-GitAvailable
$workingRoot = Join-Path $HOME "workspace"
$launcherRoot = Split-Path -Parent $PSScriptRoot
$bundled = (Split-Path -Leaf $PSScriptRoot) -eq "scripts" -and
    $launcherRoot -and (Test-RepoRoot $launcherRoot) -and (Test-WorkflowCatalog $launcherRoot)

if ([string]::IsNullOrWhiteSpace($TargetRepoPath) -and [string]::IsNullOrWhiteSpace($TargetRepoUrl)) {
    if (-not $bundled) { $Interactive = $true }
    if (-not $Interactive) {
        throw "Provide -TargetRepoPath or -TargetRepoUrl, or run with -Interactive."
    }
}

if ($Interactive) {
    if (-not $SourceRepoPath) {
        if ($bundled -and -not $ProvidedSourceUrl) {
            $SourceRepoPath = $launcherRoot
        }
        else {
            $SourceRepoPath = Join-Path $workingRoot (Resolve-RepoName $SourceRepoUrl)
            Initialize-InteractiveSource -LocalPath $SourceRepoPath -RepoUrl $SourceRepoUrl
        }
    }
    elseif (-not (Test-RepoRoot $SourceRepoPath)) {
        throw "Source path is not a git repository: $SourceRepoPath"
    }
    $catalogRoot = if ($bundled) { $launcherRoot } else { $SourceRepoPath }
    if (-not (Test-WorkflowCatalog $catalogRoot)) {
        throw "Auditor workflow catalog missing in $catalogRoot. Update the auditor checkout or select a current checkout with -SourceRepoPath."
    }
    Run-InteractivePrompts -CatalogRoot $catalogRoot
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

if ($Interactive) {
    $scoutCommand = "Use this local application repository (do not clone or update it): $TargetRepoPath`nUse .github/agents/$agentName and any explicitly requested skill files as audit guidance. Do not broaden the selected evidence scope.`n`n$WorkflowPrompt"
    if (-not [string]::IsNullOrWhiteSpace($ExtraFocus)) {
        $scoutCommand += "`n`nAdditional focus within the selected scope: $ExtraFocus"
    }
    if (-not [string]::IsNullOrWhiteSpace($AuditEmailRecipient)) {
        $scoutCommand += "`n`nScout delivery only: After the audit, confirm the recipient and approved summary content with me before emailing $AuditEmailRecipient. Do not send source code or raw evidence."
        if ($IncludeTeamsNotification) {
            $scoutCommand += " After successful email delivery, send the same recipient a brief Teams completion notification without audit details."
        }
    }
}
else {
    $scoutCommand = Compose-ScoutAuditCommand -AuditTarget $resolvedTargetForAudit -Focus $AuditFocus -EmailRecipient $AuditEmailRecipient -IncludeTeams $IncludeTeamsNotification
}
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
if ($Interactive) { Write-Host "Review and replace placeholders before pasting into Scout:" }
else { Write-Host "Run this in Scout:" }
Write-Host $scoutCommand
