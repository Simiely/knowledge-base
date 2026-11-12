---
id: docs.generated.index
title: 生成索引
summary: 从 frontmatter 自动生成的导航；勿手改。
type: reference
kind: index
status: active
owner: "@platform"
source_type: doc
source: schema/taxonomy.json
last_reviewed: 2026-11-11
related: []
---

# 生成索引

> 生成文件，勿手改。运行 `python scripts/generate.py --root . --write` 重建。

## 按 type

### how-to

| 页面 | kind | status | owner | tier | source |
|---|---|---|---|---|---|
| [重试策略](../../examples/code/docs/retry.md) | standard | active | @platform | normal | `examples/code/config.py` |
| [使用说明](../usage.md) | standard | active | @platform | critical | `scripts/check_repo.py` |

### reference

| 页面 | kind | status | owner | tier | source |
|---|---|---|---|---|---|
| [运行时配置](../../examples/code/docs/config.md) | standard | active | @platform | critical | `examples/code/config.py` |
| [决策索引](../decisions/index.md) | index | active | @platform | normal | `docs/decisions/ADR-0001-v2-architecture.md` |
| [文档索引](../index.md) | index | active | @platform | normal | `docs/usage.md` |

### explanation

| 页面 | kind | status | owner | tier | source |
|---|---|---|---|---|---|
| [证据与新鲜度](../concepts/provenance.md) | standard | active | @platform | critical | `schema/frontmatter.schema.json` |
| [单一事实源](../concepts/ssot.md) | standard | active | @platform | critical | `AGENTS.md` |
| [类型系统](../concepts/types.md) | standard | active | @platform | normal | `schema/taxonomy.json` |
| [ADR-0001 采用四平面 × 三表面的 v2 架构](../decisions/ADR-0001-v2-architecture.md) | decision | active | @platform | normal | `scripts/check_repo.py` |
| [ADR-0002 v2.2 是 v2.1 的 opt-in 超集](../decisions/ADR-0002-v2-2-compatibility.md) | decision | active | @platform | normal | `scripts/check_repo.py` |
| [ADR-0003 把踩坑经验做成 kind=pitfall](../decisions/ADR-0003-pitfall-as-content-kind.md) | decision | active | @platform | normal | `schema/frontmatter.schema.json` |
| [引导摩擦](../../examples/knowledge/note-b.md) | note | active | @research | normal | `https://example.org/interview-log` |
| [先看到价值再看到价格](../../examples/knowledge/note-a.md) | note | active | @research | critical | `https://example.org/primary-study` |

## 全部页面

| id | 标题 | type | kind | status |
|---|---|---|---|---|
| `code.config.retry` | [重试策略](../../examples/code/docs/retry.md) | how-to | standard | active |
| `code.config.settings` | [运行时配置](../../examples/code/docs/config.md) | reference | standard | active |
| `docs.concepts.provenance` | [证据与新鲜度](../concepts/provenance.md) | explanation | standard | active |
| `docs.concepts.ssot` | [单一事实源](../concepts/ssot.md) | explanation | standard | active |
| `docs.concepts.types` | [类型系统](../concepts/types.md) | explanation | standard | active |
| `docs.decisions.0001` | [ADR-0001 采用四平面 × 三表面的 v2 架构](../decisions/ADR-0001-v2-architecture.md) | explanation | decision | active |
| `docs.decisions.0002` | [ADR-0002 v2.2 是 v2.1 的 opt-in 超集](../decisions/ADR-0002-v2-2-compatibility.md) | explanation | decision | active |
| `docs.decisions.0003` | [ADR-0003 把踩坑经验做成 kind=pitfall](../decisions/ADR-0003-pitfall-as-content-kind.md) | explanation | decision | active |
| `docs.decisions.index` | [决策索引](../decisions/index.md) | reference | index | active |
| `docs.index` | [文档索引](../index.md) | reference | index | active |
| `docs.usage` | [使用说明](../usage.md) | how-to | standard | active |
| `knowledge.onboarding.friction` | [引导摩擦](../../examples/knowledge/note-b.md) | explanation | note | active |
| `knowledge.pricing.value-first` | [先看到价值再看到价格](../../examples/knowledge/note-a.md) | explanation | note | active |
