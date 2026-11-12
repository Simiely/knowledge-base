#Requires -Version 5.1
<#
.SYNOPSIS
    Create a clean project repository from the knowledge-base template.

.DESCRIPTION
    Copies base/ + profiles/<Profile>/ into -Target, replaces placeholders,
    installs the pinned repo-kit copy with tools/update-repo-kit.ps1, then runs
    generate (except link-only) and check.

    The script is ASCII-only on purpose: Windows PowerShell 5.1 reads
    non-BOM scripts as ANSI, which would corrupt Chinese literals.

.EXAMPLE
    pwsh 新建仓库.ps1 -Name my-tool -Profile monorepo -Target ..\my-tool
.EXAMPLE
    pwsh 新建仓库.ps1 -Name my-skills -Profile skills -Target ..\my-skills -Owner simiely
#>
param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^[A-Za-z0-9][A-Za-z0-9._-]*$')]
    [string]$Name,

    [Parameter(Mandatory = $true)]
    [ValidateSet('monorepo', 'skills', 'link-only')]
    [string]$Profile,

    [Parameter(Mandatory = $true)]
    [string]$Target,

    [string]$Owner = 'simiely',
    [string]$Summary = 'One line: what this repository is for.',
    [switch]$Force,
    [switch]$SkipGenerate,
    [switch]$SkipCheck
)

$ErrorActionPreference = 'Stop'
$here = $PSScriptRoot
$baseDir = [System.IO.Path]::Combine($here, 'base')
$profileDir = [System.IO.Path]::Combine($here, 'profiles', $Profile)
$kitDir = [System.IO.Path]::GetFullPath([System.IO.Path]::Combine($here, '..', 'repo-kit'))
$targetDir = [System.IO.Path]::GetFullPath($Target)

if (-not (Test-Path -LiteralPath $baseDir)) { throw "base not found: $baseDir" }
if (-not (Test-Path -LiteralPath $profileDir)) { throw "profile not found: $profileDir" }
if (-not (Test-Path -LiteralPath ([System.IO.Path]::Combine($kitDir, 'VERSION')))) { throw "kit not found: $kitDir" }

$ownerName = $Owner.TrimStart('@').ToLower()
$date = Get-Date -Format 'yyyy-MM-dd'
$kitVersion = (Get-Content -LiteralPath ([System.IO.Path]::Combine($kitDir, 'VERSION')) -Raw -Encoding ASCII).Trim()

if (Test-Path -LiteralPath $targetDir) {
    $existing = @(Get-ChildItem -LiteralPath $targetDir -Force)
    if ($existing.Count -gt 0 -and -not $Force) {
        throw "target is not empty: $targetDir (use -Force to overwrite)"
    }
}
else {
    New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
}

function Copy-Tree([string]$Source, [string]$Destination) {
    Get-ChildItem -LiteralPath $Source -Force | ForEach-Object {
        $to = [System.IO.Path]::Combine($Destination, $_.Name)
        if ($_.PSIsContainer) {
            New-Item -ItemType Directory -Path $to -Force | Out-Null
            Copy-Tree -Source $_.FullName -Destination $to
        }
        else {
            Copy-Item -LiteralPath $_.FullName -Destination $to -Force
        }
    }
}

Copy-Tree -Source $baseDir -Destination $targetDir
Copy-Tree -Source $profileDir -Destination $targetDir

$map = @{
    '{{PROJECT_NAME}}'    = $Name
    '{{PROJECT_SUMMARY}}' = $Summary
    '{{OWNER}}'           = $ownerName
    '{{DATE}}'            = $date
    '{{PROFILE}}'         = $Profile
    '{{KIT_VERSION}}'     = $kitVersion
}

$textExt = @('.md', '.json', '.yml', '.yaml', '.txt', '.ps1')
Get-ChildItem -LiteralPath $targetDir -Recurse -File -Force | ForEach-Object {
    if (($textExt -contains $_.Extension.ToLower()) -or ($_.Name -eq '.gitignore')) {
        $text = [System.IO.File]::ReadAllText($_.FullName, [System.Text.Encoding]::UTF8)
        foreach ($key in $map.Keys) {
            $text = $text.Replace($key, $map[$key])
        }
        $enc = New-Object System.Text.UTF8Encoding($false)
        [System.IO.File]::WriteAllText($_.FullName, $text, $enc)
    }
}

$toolsDir = [System.IO.Path]::Combine($targetDir, 'tools')
New-Item -ItemType Directory -Path $toolsDir -Force | Out-Null
$updater = [System.IO.Path]::Combine($toolsDir, 'update-repo-kit.ps1')
Copy-Item -LiteralPath ([System.IO.Path]::Combine($kitDir, 'tools', 'update-repo-kit.ps1')) -Destination $updater -Force

$shell = if ($PSVersionTable.PSEdition -eq 'Core') { 'pwsh' } else { 'powershell' }
& $shell -NoProfile -ExecutionPolicy Bypass -File $updater -Source $kitDir -Profile $Profile
if ($LASTEXITCODE -ne 0) { throw 'repo-kit install failed' }

if ($Profile -ne 'link-only' -and -not $SkipGenerate) {
    & python ([System.IO.Path]::Combine($targetDir, 'tools', 'repo-kit', 'generate.py')) --root $targetDir --write
    if ($LASTEXITCODE -ne 0) { throw 'generate failed' }
}

if (-not $SkipCheck) {
    & python ([System.IO.Path]::Combine($targetDir, 'tools', 'repo-kit', 'check_repo.py')) --root $targetDir
    if ($LASTEXITCODE -ne 0) { throw 'check_repo failed' }

    & $shell -NoProfile -ExecutionPolicy Bypass -File $updater -Check
    if ($LASTEXITCODE -ne 0) { throw 'kit lock check failed' }
}

Write-Output ''
Write-Output ("CREATED: {0}" -f $targetDir)
Write-Output ("PROFILE: {0}   KIT: {1}" -f $Profile, $kitVersion)
Write-Output 'NEXT:'
Write-Output ("  cd {0}" -f $targetDir)
Write-Output '  git init'
Write-Output '  git add .'
Write-Output '  git commit -m "init: from knowledge-base template"'
Write-Output '  update AGENTS.md baseline with the first commit hash'
