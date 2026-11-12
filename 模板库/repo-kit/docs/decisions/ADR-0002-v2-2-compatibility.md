---
id: docs.decisions.0002
title: ADR-0002 v2.2 是 v2.1 的 opt-in 超集
summary: 默认行为保持 v2.1；monorepo、report、多源、co-change、SARIF 全部显式开启。
type: explanation
kind: decision
status: active
owner: "@platform"
topics: [governance]
source_type: doc
source: scripts/check_repo.py
last_reviewed: 2026-11-11
related: []
---
# ADR-0002 v2.2 是 v2.1 的 opt-in 超集

- Status: Accepted
- Date: 2026-11-11
- Owners: @platform

## Context

v2.1 在 EverythingCmdPal 的真实仓库上验证通过：Phase 1 `ERROR=0`，9 类漂移 9/9 拦截。
但它也暴露了单仓版本不适配 monorepo 的地方：

- 嵌套 `AGENTS.md` 被当内容页；任意层级的 `README.md`/`CHANGELOG.md` 也要求 frontmatter。
- 只有单 `source`，无法表达一页依赖多个真源。
- `sources.json` 与 `--changed-since` 没有接起来，缺少真正的「同 PR 带文档」检查。
- 结果只有日志/JSON，进不了 GitHub PR annotation。
- baseline 按 `code+file+message` 匹配，message 一改就失效。

用户要求 v2.2 不能破坏 v2.1 的单仓用法。

## Decision

v2.2 是 v2.1 的 **opt-in 超集**，默认行为保持不变：

1. **context/health 文件**：`context_files` 与 `exempt_basenames` 默认空；配置后才把嵌套
   `AGENTS.md`、`README.md`、`CHANGELOG.md` 等排除出内容页，但仍检查链接。
2. **report 生命周期**：新增 `kind: report`；`report` 与 `archived` 不参与过期判定。
3. **多源 provenance**：新增可选 `sources: ["code:...", "doc:...", "url:..."]`；`source` 继续作为主源。
4. **同 PR co-change**：`sources.json` 的 `co_change` + `--changed-since`/`--changed-files`；
   真源变了但映射文档没变 → `TRUTH_DOCS_NOT_UPDATED`；`--allow-truth-only` 是纯重构逃生口。
5. **输出格式**：`--format sarif|github`；默认仍是 text/json。SARIF 带稳定 `partialFingerprints`。
6. **baseline v2**：`--baseline-format v2` 写入 fingerprint；读取时自动兼容 v1/v2。
7. **summary / slugger**：`summary_policy` 默认 `off`，`--strict-summary` 才 WARN；
   `slugger` 默认 `legacy`，`github` 是显式选择。

## Consequences

正面：

- v2.1 的仓库不改配置，升级后结果不变。
- EverythingCmdPal 的 Phase 2 baseline 从 22 条降到 16 条。
- 14 个一次性报告可以归为 `report`/`archived`，不再被迫 evergreen。
- 同 PR co-change 终于把 v1 的第 8 条不变量落成可执行检查。
- SARIF 可以把结果送进 GitHub code scanning，而不是只躺在日志里。

代价：

- monorepo 需要显式配置 `context_files`/`exempt_basenames`；不配就仍是 v2.1 行为。
- 多源 `sources` 是 inline list，不能表达每源独立的 commit/日期；复杂 provenance 仍需外部工具。
- co-change 对纯重构可能误报；需要 `--allow-truth-only` 或 PR 标签。
- `slugger: github` 仍是近似实现；Docusaurus/MkDocs 的最终锚点以站点 build 为准。

## Verification

- 36 个单元测试全绿（22 个 v2.1 回归 + 14 个 v2.2 新能力）。
- v2.1 兼容测试：默认配置下 v2.1 风格页仍然有效。
- EverythingCmdPal Phase 2：baseline 22 → 16；`TRUTH_DOCS_NOT_UPDATED` 在 manifest 单独变更时触发。
- SARIF 输出包含 `ruleId`、`level`、`location`、`partialFingerprints`。

## NOT RUN

- 未迁移 EverythingCmdPal 的 14 个插件文档；它们仍在 baseline。
- 未接 zhlint、MkDocs/Docusaurus build、GitHub code scanning 实际运行。
- 未验证中文/CJK 锚点在 GitHub/Docusaurus/MkDocs 的差异。
- 未实现每源独立 commit/日期与结构化表格检查（README 版本表仍是 Phase 3）。

## Supersession

None。要改本决策，写新 ADR 并标 `Supersedes: ADR-0002`，本文只翻 status，正文不动。
