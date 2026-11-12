---
id: docs.decisions.index
title: 决策索引
summary: ADR 的唯一索引；编号唯一，不要求连续。
type: reference
kind: index
status: active
owner: "@platform"
topics: [governance]
source_type: doc
source: docs/decisions/ADR-0001-v2-architecture.md
last_reviewed: 2026-11-11
related: ["docs.decisions.0001:see-also", "docs.decisions.0002:see-also", "docs.decisions.0003:see-also"]
---
# 决策索引

append-only。新 ADR 落地必须同步更新本表；检查器逐个编号核对，但**不要求编号连续**——
并行分支可以跳号，唯一性比连续性重要。

| 编号 | 标题 | 状态 |
|---|---|---|
| ADR-0001 | 采用四平面 × 三表面的 v2 架构 | Accepted |
| ADR-0002 | v2.2 是 v2.1 的 opt-in 超集 | Accepted |
| ADR-0003 | 把踩坑经验做成 kind=pitfall | Accepted |

## Related Items

- **see-also**: [ADR-0001](ADR-0001-v2-architecture.md) — 本索引的第一条决策。
- **see-also**: [ADR-0002](ADR-0002-v2-2-compatibility.md) — 兼容性与 monorepo 能力。
- **see-also**: [ADR-0003](ADR-0003-pitfall-as-content-kind.md) — 失败模式作为一等内容。
