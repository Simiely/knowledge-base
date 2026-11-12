---
id: docs.concepts.types
title: 类型系统
summary: 为什么把 type 和 kind 拆开，以及它们与 Diátaxis/DITA 的对应。
type: explanation
kind: standard
status: active
owner: "@platform"
topics: [governance]
defines: information-types
source_type: schema
source: schema/taxonomy.json
last_reviewed: 2026-11-11
related: ["docs.concepts.ssot:see-also"]
---
# 类型系统

v1 把 `concept/howto/reference/faq/decision/index/note` 放在一个闭集里。问题是它混了两个
正交维度：**读者意图**（学习、完成任务、查、理解）和**工件种类**（标准、决策、索引、笔记）。

v2 拆成两个字段：

- `type`：Diátaxis 的四类信息类型，回答「读者来干什么」。
- `kind`：工件种类，回答「这是什么」。

## type 与 kind 的分工

| type | 读者意图 | 写法重心 | DITA 对应 |
|---|---|---|---|
| `tutorial` | 学会 | 可复现的引导，少讲原理 | task / concept |
| `how-to` | 完成 | 目标、步骤、可观察结果 | task |
| `reference` | 查 | 完整、准确、可检索 | reference |
| `explanation` | 理解 | 背景、取舍、为什么 | concept |

`kind` 只保留七个：`standard`、`decision`、`index`、`note`、`glossary`、`report`、`pitfall`。
一个页面可以是 `type: explanation, kind: decision`（ADR），也可以是
`type: reference, kind: index`（导航页）。

`report` 是一次性分析、计划、复盘或实验记录。它通常写 `status: archived`，**不参与过期判定**；
不要把它硬塞进 `standard`，否则每年都要为一份已经完成使命的报告重新复核。v2.2 的真实案例里，
一个插件目录下有 14 份这类文档，全部逼成 evergreen 是反效果。

`pitfall` 是失败模式，不是技能，也不是规范。技能=触发条件 + 正确步骤 + 验证；坑=症状 +
根因 + 检测 + 规避 + 恢复。两者的读者意图也不同：查技能是在动手前，查坑是在出错后或动手前
排雷。把它做成 `kind` 而不是新平面，是因为它仍然是一份有 `source`、`owner`、复核窗口的内容页；
只是多了一组结构化字段，能被生成器聚合成[踩坑索引](../_generated/pitfalls.md)，并在
`symptom/cause/detect/avoid/recover` 缺失时直接报错。`status: resolved` 用于根因已消除的坑，
它不参与过期判定，但不会被删除：后来者仍需要知道这个坑曾经存在。

## 为什么不用一个闭集

- 一个 `decision` 既需要「解释为什么」，又需要「append-only 的工件语义」；塞进一个字段会
  逼你在两个维度之间二选一。
- DITA 用 topic type + map/bookmap 分离内容和组织；Diátaxis 用四类信息类型分离读者意图。
  两个成熟标准都不把「工件种类」混进信息类型。
- 拆开之后，schema 可以按 `type` 决定结构、按 `kind` 决定治理规则（例如 decision 必须
  append-only、index 可以生成）。

## 迁移

v1 的 `concept` → `explanation`；`howto` → `how-to`；`faq` → `reference` + `note`；
`decision` → `explanation` + `decision`；`index` → `reference` + `index`；`note` →
`explanation` + `note`。完整清单见[使用说明](../usage.md)。

## Related Items

- **see-also**: [单一事实源](./ssot.md) — 类型定义也只能有一处。
