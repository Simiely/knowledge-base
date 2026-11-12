---
id: docs.usage
title: 使用说明
summary: 校验命令、新页清单与常见报错处理。
type: how-to
kind: standard
status: active
owner: "@{{OWNER}}"
topics: [governance]
defines: usage-guide
source_type: doc
source: tools/repo-kit/check_repo.py
last_reviewed: {{DATE}}
related: []
---
# 使用说明

本页是 `usage-guide` 的唯一权威位置。

## 起手三条

```bash
python -m pip install -r requirements.txt
python tools/repo-kit/check_repo.py --root .
python tools/repo-kit/generate.py --root . --check
```

版本锁：

```bash
pwsh tools/update-repo-kit.ps1 -Check
```

## 新建一页

复制 [_template.md](_template.md)，按清单填完，挂到 [文档索引](index.md)：

- [ ] `id` 全局唯一、小写点分，与文件名解耦
- [ ] `title` 是一句能独立理解的话
- [ ] `type` 取自 tutorial / how-to / reference / explanation
- [ ] `kind` 取自 standard / decision / index / note / glossary / report / pitfall
- [ ] `status` 取自 draft / active / resolved / superseded / archived
- [ ] `owner` 是 `@team` 形式
- [ ] `source_type` + `source` 指向真实真源
- [ ] `last_reviewed` 是 ISO 日期
- [ ] 用了锚点？确认目标标题没被改名

## 报错了怎么读

| 码 | 含义 | 修法 |
|---|---|---|
| `FM_MISSING` | 缺 frontmatter / 未闭合 / YAML 解析失败 | 补 `---` 块 |
| `SCHEMA` | 字段缺失、类型错、未知字段 | 按 `schema/frontmatter.schema.json` 修 |
| `VOCAB` | type/kind/status/topic 越界 | 先改词表，再写文档 |
| `LINK_BROKEN` / `ANCHOR_BROKEN` | 断链 / 锚点不存在 | 修链接或标题 |
| `SOURCE_MISSING` | 真源不存在 | 修路径或补真源 |
| `STALE` | 超过复核窗口 | 复核并更新 `last_reviewed` |
| `GENERATED_MISSING` / `GENERATED_STALE` | 生成产物缺失或过期 | 跑 `generate.py --write` |
| `KIT LOCK: FAIL` | 工具文件被改或版本锁过期 | 用 `update-repo-kit.ps1` 重新安装 |

## 边界

校验器验证不了「这句话是不是真的」。改公开接口、schema、onboarding 的 PR，需要人把文档与代码并排读一遍。
