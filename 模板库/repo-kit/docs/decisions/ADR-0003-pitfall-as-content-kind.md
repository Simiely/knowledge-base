---
id: docs.decisions.0003
title: ADR-0003 把踩坑经验做成 kind=pitfall
summary: 坑是技能的失败模式；用内容页承载，加八个必填字段与生成索引，不新增平面。
type: explanation
kind: decision
status: active
owner: "@platform"
topics: [governance]
source_type: doc
source: schema/frontmatter.schema.json
last_reviewed: 2026-11-11
related: ["docs.decisions.0002:see-also"]
---
# ADR-0003 把踩坑经验做成 kind=pitfall

- Status: Accepted
- Date: 2026-11-11
- Owners: @platform

## Context

v2.2 的仓库里已经有两类东西被混在一起：

- **约束**：必须怎么做（`kind: standard`，例如「SQLite 是唯一真源」）。
- **坑**：这么做会坏（症状、根因、怎么发现、怎么退出来）。

约束写得再好，也挡不住「配置被忽略 → 找不到文件」这种症状误导排查。技能（`SKILL.md`）
回答「怎么做对」，但它不记录失败模式：一个技能可以有十几个失败分支，全部塞进 SKILL.md 会让
主流程不可读；拆成独立技能又会污染触发条件。用户明确要求「注意事项（容易犯错的部分）」
单独成层。

## Decision

不新增平面，也不新增技能类型。把坑做成**内容页的一个 kind**：

1. `kind: pitfall`，新增 `status: resolved`。
2. 必填字段：`summary`、`symptom`、`cause`、`detect`、`avoid`、`recover`、`applies_to`、`severity`。
   `applies_to` 可指向页面 id 或技能 name；普通页不写这个字段。
3. 检查码：`PITFALL_FIELD`（缺字段）、`PITFALL_SEVERITY`（越界）、`PITFALL_TARGET`（目标不存在）、
   `PITFALL_SELF`（指向自己）。
4. `applies_to` 计入入链：坑被目标页「引用」，孤儿检查不再误报。
5. `status: resolved` 不参与过期判定；`active` 的坑仍按 `review_days` 复核。
6. 生成 `docs/_generated/pitfalls.md`：未解决/已解决分区 + 按适用范围分组；
   `applies_to` 同时写入 `backlinks.md`。

字段设计参照 DITA troubleshooting（condition/cause/remedy）、FMEA（severity/detection）与
blameless postmortem（症状与根因分离）：`symptom` 是观察，`cause` 是机制，二者不能合并，
否则读者会拿症状当根因去修。

## Consequences

正面：

- 坑有稳定的 `id`、owner、真源与复核窗口，能被索引、反链和 CI 检查，而不是散落在 runbook 里。
- 技能保持「触发 + 步骤 + 验证」；失败模式链回 `applies_to`，两边都不膨胀。
- 已解决的坑保留可检索性；后来者能看到「为什么现在不会踩」。
- 默认行为仍与 v2.2 一致：没有 pitfall 页的仓库，检查结果不变。

代价：

- `detect` / `avoid` 写不出可执行内容时，字段会退化成空话；schema 只能限长度，不能限质量。
- `applies_to` 指向技能 name 时，技能侧没有反向字段可点，只能靠生成的索引。
- 复制 v2.3 `taxonomy.json` 的仓库需要跑一次 `generate.py --write`，否则报 `GENERATED_MISSING`。

## Verification

- 7 个 v2.3 测试：合法坑、缺字段、未知目标、自引用、resolved 免过期、指向技能、生成索引。
- 全套 49 个测试全绿；`drift_probe.py` 仍全绿。
- home-inventory 实测迁移 5 条坑，`check_repo` 与 `generate --check` 均通过。

## NOT RUN

- 未实现「同一 applies_to 下坑数量上限」「长期 active 自动升级 severity」等治理策略。
- 未验证 GitHub/Docusaurus 对中文锚点的最终渲染。

## Supersession

None。要改本决策，写新 ADR 并标 `Supersedes: ADR-0003`，本文只翻 status，正文不动。
