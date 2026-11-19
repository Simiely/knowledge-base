#Requires -Version 5.1
<#
.SYNOPSIS
    Fleet audit: spec version, kit lock consistency, CI wiring, dead baselines, legacy keys.

.DESCRIPTION
    Scans <ReposRoot>/<repo>/ and reports per repo:
      - spec   : declared spec_version in schema/kit.lock.json vs ../单项目规范/spec.json
               current / behind-patch (only the patch differs: shown, never counts as an
               issue) / behind (major or minor differs) / newer / v1 / legacy / invalid
      - kit    : schema/taxonomy.json version must equal kit.lock.json version
      - flags  : one or more of
                   skew:<a>vs<b>       taxonomy version != lock version (silent drift)
                   no-lock             no schema/kit.lock.json (machine layer missing)
                   ci-missing          no workflow references check_repo.py
                   ci-no-fetch-depth   uses --changed-since without fetch-depth: 0
                   baseline:<n>        schema/check-baseline.json still present (dead config?)
                   legacy-keys         taxonomy still uses deprecated exemption keys
                   legacy-nokey        taxonomy has neither frontmatter_exempt nor legacy keys

    Non-repo directories are skipped. Directories named verify-* are skipped (throwaway clones).

.EXAMPLE
    pwsh audit-spec.ps1 -ReposRoot C:\work
    pwsh audit-spec.ps1 -ReposRoot C:\work,C:\work\sub -Json
#>
param(
    [Parameter(Mandatory = $true)][string[]]$ReposRoot,
    [switch]$Json
)

$specVersion = (Get-Content (Join-Path $PSScriptRoot 'spec.json') -Raw | ConvertFrom-Json).version
$specParts = $specVersion.Split('.') | ForEach-Object { [int]$_ }
$legacyKeys = @('context_files', 'exempt_basenames', 'entry_files', 'link_only_files')

function Compare-Ver([string]$value) {
    if ($value -notmatch '^(\d+)\.(\d+)\.(\d+)$') { return 'invalid' }
    $parts = $Matches[1], $Matches[2], $Matches[3] | ForEach-Object { [int]$_ }
    # 主/次版本是契约边界：落后必须报。补丁版本只做措辞澄清，落后不算缺陷
    # （规范 2.1.4 起），单独给一个状态用于显示，不计入 issues。
    for ($i = 0; $i -lt 2; $i++) {
        if ($parts[$i] -gt $specParts[$i]) { return 'newer' }
        if ($parts[$i] -lt $specParts[$i]) { return 'behind' }
    }
    if ($parts[2] -lt $specParts[2]) { return 'behind-patch' }
    if ($parts[2] -gt $specParts[2]) { return 'newer' }
    return 'current'
}

# 计入 issues（= 退出码 1）的状态。behind-patch 故意不在其中：发一个只改措辞的
# PATCH 版，不该让全 fleet 变红。
$issueStates = @('behind', 'newer', 'legacy', 'v1', 'invalid')

function Get-RepoFlags([string]$root) {
    $flags = New-Object System.Collections.Generic.List[string]

    $taxPath = Join-Path $root 'schema/taxonomy.json'
    $lockPath = Join-Path $root 'schema/kit.lock.json'

    # kit 版本漂移：taxonomy 与 lock 对不上，说明有人只改了一边
    $taxVer = $null; $lockVer = $null
    if (Test-Path -LiteralPath $taxPath) {
        $taxVer = [string](Get-Content -LiteralPath $taxPath -Raw | ConvertFrom-Json).version
    }
    if (Test-Path -LiteralPath $lockPath) {
        $lockVer = [string](Get-Content -LiteralPath $lockPath -Raw | ConvertFrom-Json).version
        if ($taxVer -and $lockVer -and $taxVer -ne $lockVer) {
            $flags.Add(("skew:{0}-vs-{1}" -f $taxVer, $lockVer))
        }
    }

    # 豁免键：既没有新键也没有旧键，说明配置被改坏了
    if (Test-Path -LiteralPath $taxPath) {
        $tax = Get-Content -LiteralPath $taxPath -Raw | ConvertFrom-Json
        $hasNew = $null -ne $tax.frontmatter_exempt
        $hasLegacy = $false
        foreach ($k in $legacyKeys) { if ($null -ne $tax.$k) { $hasLegacy = $true } }
        if ($hasLegacy) { $flags.Add('legacy-keys') }
        elseif (-not $hasNew) { $flags.Add('legacy-nokey') }
    }

    # 死 baseline：规则静音后它会变成压着已消失问题的配置
    $baseline = Join-Path $root 'schema/check-baseline.json'
    if (Test-Path -LiteralPath $baseline) {
        $n = 0
        try { $n = @((Get-Content -LiteralPath $baseline -Raw | ConvertFrom-Json).items).Count } catch { $n = -1 }
        $flags.Add("baseline:$n")
    }

    # CI 是否真的接线；用了 --changed-since 却没收全历史 = 检查永不生效
    $wfDir = Join-Path $root '.github/workflows'
    if (Test-Path -LiteralPath $wfDir) {
        $wired = $false; $changed = $false; $fetchDepth = $false
        foreach ($wf in Get-ChildItem -LiteralPath $wfDir -Filter *.yml -File -ErrorAction SilentlyContinue) {
            # 剔除整行注释再匹配：注释里提到 --changed-since 不代表真的用了它。
            # 例：ai-dev-guardrails 的 repo-check.yml 用注释解释"为什么不用"，
            # 曾被裸字符串匹配命中，在舰队审计里长期误报 ci-no-fetch-depth。
            # -Encoding UTF8 不能省：PS 5.1 对无 BOM 的 UTF-8 默认按 ANSI 解码，
            # 中文注释会被拆坏并吞掉换行，把下一行 run: 粘进注释里（实测 56 行→52 行）。
            $text = (Get-Content -LiteralPath $wf.FullName -Encoding UTF8 |
                Where-Object { $_ -notmatch '^\s*#' }) -join "`n"
            if ($text -match 'check_repo\.py') { $wired = $true }
            if ($text -match '--changed-since') { $changed = $true }
            if ($text -match 'fetch-depth:\s*0') { $fetchDepth = $true }
        }
        if (-not $wired) { $flags.Add('ci-missing') }
        elseif ($changed -and -not $fetchDepth) { $flags.Add('ci-no-fetch-depth') }
    } else {
        $flags.Add('ci-missing')
    }

    return $flags
}

$rows = @()
foreach ($root in $ReposRoot) {
    if (-not (Test-Path -LiteralPath $root)) { continue }
    # root 自身就是仓库就只查它；否则查它下面的一层目录
    $rootIsRepo = (Test-Path -LiteralPath (Join-Path $root 'schema/taxonomy.json'))
    $candidates = if ($rootIsRepo) { @(Get-Item -LiteralPath $root) } else { @(Get-ChildItem -LiteralPath $root -Directory) }
    foreach ($dir in $candidates) {
        if ($dir.Name -like 'verify-*' -or $dir.Name -like 'tmp-*') { continue }
        $taxPath = Join-Path $dir.FullName 'schema/taxonomy.json'
        $lockPath = Join-Path $dir.FullName 'schema/kit.lock.json'
        if (-not (Test-Path -LiteralPath $taxPath) -and -not (Test-Path -LiteralPath $lockPath)) { continue }

        $declared = $null; $state = 'v1'
        if (Test-Path -LiteralPath $lockPath) {
            $lockData = Get-Content -LiteralPath $lockPath -Raw | ConvertFrom-Json
            $declared = [string]$lockData.spec_version
            if (-not $declared) { $state = 'legacy' } else { $state = Compare-Ver $declared }
        } else {
            $declared = '1.x'
        }

        $kitVer = '-'
        if (Test-Path -LiteralPath $lockPath) {
            $kitVer = [string](Get-Content -LiteralPath $lockPath -Raw | ConvertFrom-Json).version
        }

        $flags = Get-RepoFlags $dir.FullName
        $rows += [pscustomobject]@{
            repo  = $dir.Name
            spec  = $declared
            state = $state
            kit   = $kitVer
            flags = ($flags -join ',')
        }
    }
}

$issues = @($rows | Where-Object { $_.flags -ne '' -or $issueStates -contains $_.state })
$patchBehind = @($rows | Where-Object { $_.state -eq 'behind-patch' }).Count

if ($Json) {
    $rows | ConvertTo-Json -Depth 3
} else {
    # 明确宽度，避免终端把表格截断后拼接到摘要行上
    $table = $rows | Sort-Object @{ Expression = { $_.flags -ne '' }; Descending = $true }, repo |
        Format-Table -AutoSize | Out-String -Width 200
    Write-Output $table.TrimEnd()
    Write-Output ('FLEET AUDIT: latest=' + $specVersion + ', repos=' + @($rows).Count + ', issues=' + $issues.Count + ', patch-behind=' + $patchBehind)
}

if ($issues.Count -gt 0) { exit 1 }
exit 0
