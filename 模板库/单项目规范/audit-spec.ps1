#Requires -Version 5.1
<#
.SYNOPSIS
    Scan repos for their declared spec version and report drift.

.DESCRIPTION
    Reads version from spec.json in this directory, then scans
    <ReposRoot>/<repo>/schema/kit.lock.json:
      - no kit.lock               -> state=v1 (machine layer not installed)
      - lock without spec_version -> state=legacy (rerun installer to fix)
      - spec_version older        -> state=behind
      - same or patch-only newer  -> state=current
      - higher major/minor        -> state=newer (validator too old)

.EXAMPLE
    pwsh audit-spec.ps1 -ReposRoot C:\Users\2504\Projects
    pwsh audit-spec.ps1 -ReposRoot C:\Users\2504\Projects -Json
#>
param(
    [Parameter(Mandatory = $true)][string]$ReposRoot,
    [switch]$Json
)

$specVersion = (Get-Content (Join-Path $PSScriptRoot 'spec.json') -Raw | ConvertFrom-Json).version
$specParts = $specVersion.Split('.') | ForEach-Object { [int]$_ }

function Compare-Ver([string]$value) {
    if ($value -notmatch '^(\d+)\.(\d+)\.(\d+)$') { return 'invalid' }
    $parts = $Matches[1], $Matches[2], $Matches[3] | ForEach-Object { [int]$_ }
    for ($i = 0; $i -lt 3; $i++) {
        if ($parts[$i] -gt $specParts[$i]) { return 'newer' }
        if ($parts[$i] -lt $specParts[$i]) { return 'behind' }
    }
    return 'current'
}

$rows = foreach ($dir in Get-ChildItem -LiteralPath $ReposRoot -Directory) {
    $lock = Join-Path $dir.FullName 'schema/kit.lock.json'
    if (-not (Test-Path -LiteralPath $lock)) {
        [pscustomobject]@{ repo = $dir.Name; spec = '1.x'; state = 'v1'; detail = 'no schema/kit.lock.json' }
        continue
    }
    $lockData = Get-Content -LiteralPath $lock -Raw | ConvertFrom-Json
    $declared = [string]$lockData.spec_version
    if (-not $declared) {
        [pscustomobject]@{ repo = $dir.Name; spec = 'unknown'; state = 'legacy'; detail = 'kit.lock has no spec_version' }
        continue
    }
    $state = Compare-Ver $declared
    [pscustomobject]@{ repo = $dir.Name; spec = $declared; state = $state; detail = ('latest=' + $specVersion) }
}

if ($Json) {
    $rows | ConvertTo-Json -Depth 3
} else {
    $rows | Sort-Object state, repo | Format-Table -AutoSize
    $needs = @($rows | Where-Object { $_.state -in @('behind', 'v1', 'legacy', 'invalid', 'newer') }).Count
    Write-Output ('SPEC AUDIT: latest=' + $specVersion + ', checked=' + @($rows).Count + ', needs-upgrade=' + $needs)
}
