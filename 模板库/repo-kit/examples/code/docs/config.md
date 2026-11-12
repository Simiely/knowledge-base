---
id: code.config.settings
title: 运行时配置
summary: 运行时配置键的语义；数值以真源为准，本页不复制。
type: reference
kind: standard
status: active
owner: "@platform"
tier: critical
topics: [config]
defines: runtime-settings
source_type: code
source: examples/code/config.py
source_commit: 7eaf524c
last_reviewed: 2026-11-01
related: ["code.config.retry:depends-on", "docs.concepts.ssot:see-also"]
---
# 运行时配置

本页是 `runtime-settings` 的唯一定义处，真源锚定到 `examples/code/config.py`。

`retry_max` 控制最大重试次数，`timeout_ms` 是单次超时，`cache_ttl` 是缓存有效期，
`maxRetries` 是兼容旧客户端的上限别名。四者均在真源中以字面量定义；本页不复制数值，只描述语义。

参考表应由 schema 生成并校验「生成结果 ≠ 已提交内容」即失败，而不是手写维护。

## Related Items

- **depends-on**: [重试策略](./retry.md) — 重试次数与超时的组合语义在那里展开。
- **see-also**: [单一事实源](../../../docs/concepts/ssot.md) — 本页为何只定义一次。
