---
id: docs.decisions.0001
title: ADR-0001 采用四平面 × 三表面的 v2 架构
summary: 从「七层 + 八条不变量」重构为内容契约、知识图谱、证据、验证四个平面，以及阅读、机器、贡献三个表面。
type: explanation
kind: decision
status: active
owner: "@platform"
topics: [governance]
source_type: doc
source: scripts/check_repo.py
last_reviewed: 2026-11-11
related: ["docs.concepts.provenance:depends-on"]
---
# ADR-0001 采用四平面 × 三表面的 v2 架构

- Status: Accepted
- Date: 2026-11-11
- Owners: @platform

## Context

v1 把「文档不漂移」写成七层 + 八条不变量，并声称八条都能被脚本检查。实测发现：

- 不变量 1（唯一入口）没有检查；不变量 7（每条断言可锚定）只做到页面级路径存在；
  不变量 8（同 PR 带文档）脚本判不了。
- 自研正则解析 Markdown/YAML，在代码块假链接、`#L3` 源码行号、重名标题、README 入链、
  嵌套 frontmatter、camelCase 键等场景上误报/漏报。
- 没有 baseline / ignore / changed-only，真实仓库第一天就会全红。
- 规范自身有 35 处无出处的 citation，违反自己的 provenance 规则。

继续修 bug 只能得到「更严格的 v1」。真正的问题是重心：把成熟工具该做的事，自己重做了一遍。

## Decision

采用「四平面 × 三表面」：

**四平面（生产侧）**

1. **内容契约**：`type` 与 `kind` 拆开；JSON Schema 表达字段；最小可行词表。
2. **知识图谱**：关系声明 `direction` / `inverse` / `transitive`；方向性关系单侧，
   对称关系显式声明；反链与索引由生成器派生。
3. **证据与新鲜度**：`source_type` / `source` / `source_retrieved` / `source_hash`；
   页面级默认，critical 页才考虑 claim-level；`last_reviewed` + `review_days`。
4. **验证与治理**：组合 PyYAML、markdown-it、lychee/Vale（可选）、JSON Schema；
   `--baseline` / `--changed-since` 渐进执行；人审语义。

**三表面（消费侧）**

- **阅读**：文档站、搜索、生成索引。
- **机器**：`AGENTS.md`（薄）、`llms.txt`、MCP/RAG；全部从同一份 frontmatter 生成。
- **贡献**：工程师走 PR；非技术贡献者走 issue / Web 编辑器，不让 Git 成为门槛。

**原则**：最小可行词表 + 生成优先 + 组合工具 + 渐进执行 + 人审语义。

## Consequences

正面：

- 误报/漏报显著减少；代码块、行内代码、源码行号不再被误判。
- 存量仓库可以第一天 `ERROR=0`（legacy WARN），团队不会关 CI。
- 索引、反链、`AGENTS.md`、`llms.txt` 不再手写，减少一类漂移。
- 关系语义比 v1 准确：对称关系不再被强行单侧。

代价：

- 引入 PyYAML、markdown-it-py 两个依赖；不再「零依赖」。
- `type`/`kind` 拆分需要迁移存量页面。
- 生成器增加一个 CI 步骤；生成产物必须提交，否则 `GENERATE CHECK` 失败。
- 仍然无法验证语义真假；人审不可省。

## Verification

```bash
python scripts/check_repo.py --root .
python scripts/generate.py --root . --check
python scripts/drift_probe.py --root .
python -m unittest discover -s tests
```

- `drift_probe.py` 注入 8 类漂移，要求 8/8 拦截。
- 负对照：合法的 golden 仓库必须全绿。
- 单元测试覆盖 v1 的已知误报/漏报。

## NOT RUN

- 未在真实组织做过 90 天采纳实验；ROI 证据本身是冲突的。
- 未验证中文/CJK 锚点在 GitHub/Docusaurus/MkDocs 的差异；当前实现是近似 GitHub slug。
- 未接真实 git 历史做 `source_commit` 全量校验；`--check-git` 是可选步骤。
- 未接文档站；`mkdocs build --strict` 只是建议命令。

## Supersession

None。要改本决策，写新 ADR 并标 `Supersedes: ADR-0001`，本文只翻 status，正文不动。

## Related Items

- **depends-on**: [证据与新鲜度](../concepts/provenance.md) — 本决策的 provenance 设计依据。
