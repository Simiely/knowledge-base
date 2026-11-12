---
id: docs.index
title: 文档索引
summary: 人工导航枢纽；生成索引见 _generated/index.md。
type: reference
kind: index
status: active
owner: "@platform"
topics: [governance]
source_type: doc
source: docs/usage.md
last_reviewed: 2026-11-11
related: []
---
# 文档索引

这是人工维护的导航。**完整页面索引**由生成器产出，见 [生成索引](_generated/index.md)；
**反向链接**见 [反向链接](_generated/backlinks.md)；**踩坑导航**见 [踩坑索引](_generated/pitfalls.md)。

## 开始

- [使用说明](usage.md) — 唯一权威：命令、新页清单、报错表、baseline、迁移
- [类型系统](concepts/types.md) — `type` 与 `kind` 的分工
- [证据与新鲜度](concepts/provenance.md) — source、复核窗口、快照
- [单一事实源](concepts/ssot.md) — Rule of One 及其边界
- [决策索引](decisions/index.md) — ADR

## 示例

- [代码仓库：运行时配置](../examples/code/docs/config.md)
- [知识仓库：价值先于价格](../examples/knowledge/note-a.md)

## 边界

本页只负责人工导航；不要在这里复制完整清单。生成索引与反链由 `scripts/generate.py` 产出，
手改会在 `GENERATE CHECK` 里失败。
