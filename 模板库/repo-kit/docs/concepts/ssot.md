---
id: docs.concepts.ssot
title: 单一事实源
summary: Rule of One 的含义、机器可判的部分，以及它管不了的语义真假。
type: explanation
kind: standard
status: active
owner: "@platform"
tier: critical
topics: [governance]
defines: single-source-of-truth
source_type: doc
source: AGENTS.md
last_reviewed: 2026-11-01
related: []
---
# 单一事实源

**Rule of One**：每类信息只有一个权威位置，需要出现在别处时链接，不复制。

这是全仓库对 `single-source-of-truth` 的唯一定义处。其他文档只链接到这里；若第二份文件也写
`defines: single-source-of-truth`，检查器报 `DEFINES_DUP`。

## 为什么会漂移

同一事实写两遍，改一次只能改到其中一份，另一份从「正确」悄悄变成「误导」。链接检查、schema
lint、prose lint 全都能过——因为那份失效文档本身格式完好。所以 SSOT 必须是机器可判的不变量，
不是写作建议。

## 归属表

| 信息 | 唯一权威位置 |
|---|---|
| 规则与禁令 | `AGENTS.md` |
| 用法、命令、报错表 | [使用说明](../usage.md) |
| 概念定义 | `docs/concepts/` |
| 字段行为 | `source` 指向的真源 |
| 设计理由 | `docs/decisions/` |
| 全量索引/反链 | `docs/_generated/`（生成） |

## 边界

SSOT 管的是「只有一份」，管不了「这一份是不是真的」。后者靠从真源生成 + 人审。不要用
SSOT 的口号给语义正确性打包票。

需要类型系统时，见[类型系统](./types.md)；那是另一份契约，不在本页复制。
