---
id: docs.concepts.provenance
title: 证据与新鲜度
summary: source 类型、页面级与断言级 provenance、快照与复核窗口。
type: explanation
kind: standard
status: active
owner: "@platform"
tier: critical
topics: [governance]
defines: provenance
source_type: schema
source: schema/frontmatter.schema.json
last_reviewed: 2026-11-11
related: ["docs.concepts.types:depends-on"]
---
# 证据与新鲜度

「可锚定」不是给页面加一个 `source` 字段就完了。要区分三件事：

1. **真源是什么类型**：代码符号、schema、URL、仓库内文档。
2. **锚定到哪一层**：页面级，还是断言级。
3. **什么时候该重新看**：复核窗口，而不是「最近改过」。

## 四种 source_type

| 类型 | 适用 | 校验 |
|---|---|---|
| `code` | 配置键、API 字段、CLI flag | 路径必须是文件 |
| `schema` | OpenAPI / JSON Schema / protobuf | 路径必须是文件 |
| `doc` | 仓库内另一份权威文档 | 路径必须是文件 |
| `url` | 原始材料、研究、访谈记录 | 必须 `http(s)` + `source_retrieved` |

一页往往不止一个真源。`source` 是主源；`sources` 是附加源，用 inline list 写：

```yaml
source: shared/build/install.ps1
sources: ["code:shared/build/install.ps1", "doc:docs/install.md", "url:https://example.org/log"]
```

校验器会逐个检查路径/URL。v2.1 的单一 `source` 在真实仓库里经常是「半真话」：安装页同时依赖
安装脚本、插件 notes 和实机日志；只写一个路径，等于把其余来源藏起来。

代码仓库的参考表应**从 schema 生成**，而不是手写；知识仓库的 URL 应记录
`source_retrieved`，critical 页建议再加 `source_hash`。外链会腐烂：Pew 2024 的研究显示，
2013 年的网页到 2023 年有 38% 已不可访问。快照不是洁癖，是引用完整性。

## 页面级 vs 断言级

v1 的口号是「每条断言可锚定」，但数据模型是页面级：一页里多条断言共享一个 `source`。
v2 明确选择**页面级默认**：

- 所有页：`source_type` + `source` + `last_reviewed`。
- `tier: critical` 的页：可以用块 ID / 小节级 source 做 claim-level，但不强制。
- 只有受监管、高价值知识库才值得为每条断言付成本。

这不是妥协，是承认成本。Zettelkasten 的「一个想法一张卡」也有凝聚力成本；把每句话拆成
一张卡，最后会失去上下文。

## 新鲜度

- `last_reviewed`：ISO 日期，人工复核时间。
- `review_days`：覆盖默认窗口；normal 365 天，critical 90 天。
- 不要手写 `updated`；checkout / 同步 / 备份会重置它。
- `STALE` 对 critical 是 ERROR，对 normal 是 WARN。

## 生成优先

最强的「不漂移」不是查出来的，是生成出来的：

- 参考表从 OpenAPI / JSON Schema 生成，CI 比对生成结果。
- 索引、反链、`AGENTS.md`、`llms.txt` 从 frontmatter 生成。
- 代码真源用 AST / schema，不用语言专属正则。

## Related Items

- **depends-on**: [类型系统](./types.md) — `type`/`kind` 决定 provenance 强度。
