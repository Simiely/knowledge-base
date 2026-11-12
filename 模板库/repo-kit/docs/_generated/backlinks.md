---
id: docs.generated.backlinks
title: 反向链接
summary: 从 related 与 pitfall 的 applies_to 自动派生的反向链接；勿手改。
type: reference
kind: index
status: active
owner: "@platform"
source_type: doc
source: schema/taxonomy.json
last_reviewed: 2026-11-11
related: []
---

# 反向链接

> 生成文件，勿手改。方向性关系只存一侧，本页是派生结果；对称关系按规范边去重。
> `applies_to` 是 pitfall 的专用字段，可指向页面 id 或技能 name；技能没有页面可链，故只出现在目标列。

| 目标 id / 技能 | 来源 id | 关系 | 来源页面 |
|---|---|---|---|
| `code.config.retry` | [运行时配置](../../examples/code/docs/config.md) | depends-on（反向：depended-on-by） | `examples/code/docs/config.md` |
| `docs.concepts.provenance` | [ADR-0001 采用四平面 × 三表面的 v2 架构](../decisions/ADR-0001-v2-architecture.md) | depends-on（反向：depended-on-by） | `docs/decisions/ADR-0001-v2-architecture.md` |
| `docs.concepts.ssot` | [运行时配置](../../examples/code/docs/config.md) | see-also | `examples/code/docs/config.md` |
| `docs.concepts.ssot` | [类型系统](../concepts/types.md) | see-also | `docs/concepts/types.md` |
| `docs.concepts.types` | [证据与新鲜度](../concepts/provenance.md) | depends-on（反向：depended-on-by） | `docs/concepts/provenance.md` |
| `docs.decisions.0001` | [决策索引](../decisions/index.md) | see-also | `docs/decisions/index.md` |
| `docs.decisions.0002` | [ADR-0003 把踩坑经验做成 kind=pitfall](../decisions/ADR-0003-pitfall-as-content-kind.md) | see-also | `docs/decisions/ADR-0003-pitfall-as-content-kind.md` |
| `docs.decisions.0002` | [决策索引](../decisions/index.md) | see-also | `docs/decisions/index.md` |
| `docs.decisions.0003` | [决策索引](../decisions/index.md) | see-also | `docs/decisions/index.md` |
| `knowledge.onboarding.friction` | [先看到价值再看到价格](../../examples/knowledge/note-a.md) | extends（反向：extended-by） | `examples/knowledge/note-a.md` |
