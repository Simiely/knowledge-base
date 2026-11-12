---
id: docs.usage
title: 使用说明
summary: 命令、新页清单、关系语义、报错表、baseline 与 v1 迁移。
type: how-to
kind: standard
status: active
owner: "@platform"
tier: critical
topics: [governance]
defines: usage-guide
source_type: doc
source: scripts/check_repo.py
last_reviewed: 2026-11-11
related: []
---
# 使用说明

本页是 `usage-guide` 的**唯一**权威位置。`AGENTS.md`、`README.md`、`CONTRIBUTING.md` 只保留
指向这里的指针，不复制命令与清单。

## 1. 起手三条

```bash
python -m pip install -r requirements.txt
python scripts/check_repo.py --root .
python scripts/generate.py --root . --check
```

正对照（建议每次改校验器后跑）：

```bash
python scripts/drift_probe.py --root .
python -m unittest discover -s tests
```

`drift_probe` 是 **kit 自测**，依赖本仓库自带的 `examples/` 夹具；它验证的是「校验器会不会红」，
不是「你的仓库是否合规」。复制到消费仓库后运行会打印 `SKIP` 并退出 0；消费仓库的验收仍用
`check_repo.py` + `generate.py --check`。

严格构建（有文档站时）：

```bash
mkdocs build --strict --clean      # 或 Docusaurus onBrokenLinks/onBrokenAnchors: 'throw'
```

外链不进 PR 检查，走每日 schedule；第三方站点按自己的时钟挂，不该阻塞无关合并。

## 1.1 v2.2 / v2.3 兼容模式

v2.2 起的默认行为与 v2.1 一致；以下能力全部 opt-in：

| 能力 | 开启方式 |
|---|---|
| 嵌套 `AGENTS.md` / `README.md` / `CHANGELOG.md` 免 frontmatter | `context_files` / `exempt_basenames` |
| 一次性报告不参与过期判定 | `kind: report` + `status: archived` |
| 一页多源 | `sources: ["code:...", "doc:..."]` |
| 同 PR co-change | `sources.json` 的 `co_change` + `--changed-since` / `--changed-files` |
| SARIF / GitHub 输出 | `--format sarif|github` |
| baseline fingerprint | `--baseline-format v2` |
| summary WARN | `summary_policy: "warn"` 或 `--strict-summary` |
| GitHub 风格锚点 | `slugger: "github"` |
| 踩坑页（失败模式库） | `kind: pitfall` + 八个必填字段 |
| 已解决的坑不参与过期判定 | `status: resolved` |

不配置这些，v2.1 仓库的检查结果不变。

## 2. 新建一页

复制 [`_template.md`](_template.md)，按下面清单填完，挂到 [文档索引](index.md)：

> `_` 开头与 `*.template.md` 的文件是模板，不参与校验；不要让模板带着假链接进入扫描范围。

- [ ] `id` 全局唯一、小写点分，与文件名解耦（改名不改 id）
- [ ] `title` 是一句能独立理解的话，不是文件名
- [ ] `type` 取自 `tutorial / how-to / reference / explanation`
- [ ] `kind` 取自 `standard / decision / index / note / glossary / report / pitfall`
- [ ] `status` 取自 `draft / active / resolved / superseded / archived`
- [ ] `owner` 是 `@team` 形式，必须有人认领
- [ ] `source_type` + `source` 指向真实真源；URL 必须有 `source_retrieved`
- [ ] 有多个真源时，`sources` 用 `code:/schema:/doc:/url:` 前缀列全
- [ ] `standard / index / decision` 建议写 `summary`（`summary_policy: warn` 时检查）
- [ ] `tier: critical` 的页填 `last_reviewed`，默认 90 天窗口
- [ ] `defines` 全局唯一；概念只在 `docs/concepts/` 定义一次
- [ ] `related` 用 `id:rel`；方向性关系只写一侧
- [ ] 用了锚点？确认目标标题没被改名

## 3. type 与 kind 的分工

`type` 回答「读者来干什么」，`kind` 回答「这是什么工件」。两者正交，不要混在一个闭集里。

| type | 读者意图 | 典型形式 | DITA 对应 |
|---|---|---|---|
| `tutorial` | 学会 | 一步步带做 | task / concept |
| `how-to` | 完成 | 目标导向的步骤 | task |
| `reference` | 查 | 表格、字段、命令 | reference |
| `explanation` | 理解 | 背景、取舍、原理 | concept |

| kind | 用途 |
|---|---|
| `standard` | 规范、指南、约定 |
| `decision` | ADR，append-only |
| `index` | 导航页 |
| `note` | 观察、访谈、临时结论 |
| `glossary` | 术语表 |
| `report` | 一次性分析、计划、复盘；通常 `status: archived`，不参与过期判定 |
| `pitfall` | 失败模式：症状、根因、检测、规避、恢复；见 3.1 |

### 3.1 什么时候写 `kind: pitfall`

`pitfall` 不是技能，也不是规范。它是**技能的失败模式**：技能回答「怎么做对」，坑回答
「哪里会做错、错了怎么发现、怎么退出来」。凡是满足下面任意一条，就值得单独建页：

- 同一个错误被不同的人或 agent 犯过两次以上；
- 症状会误导排查方向（例如「找不到文件」其实是配置被忽略）；
- 代价高（数据丢失、不可逆迁移、线上中断），必须在动手前看到。

八个字段都是必填，写不出 `detect` 或 `avoid` 说明还没想清楚，先留在 issue 里：

| 字段 | 写什么 | 反例 |
|---|---|---|
| `summary` | 一句话说清会踩什么 | 「注意备份」 |
| `symptom` | 用户能观察到的现象，含原文报错 | 「有点问题」 |
| `cause` | 机制层面的根因，不是「手滑」 | 「操作失误」 |
| `detect` | 一个能跑的检查或可观察信号 | 「仔细检查」 |
| `avoid` | 下次怎么做对，指向权威步骤 | 「小心一点」 |
| `recover` | 已经踩了怎么退出来，含数据风险 | 「重装试试」 |
| `applies_to` | 页面 id 或技能 name 列表，至少一个 | 留空 |
| `severity` | `low / medium / high / critical` | 「严重」 |

`status: resolved` 表示根因已消除（例如代码已修）。它不参与过期判定，但仍保留在
[踩坑索引](_generated/pitfalls.md) 的「已解决」区：读者需要知道这个坑曾经存在，以及为什么现在不会踩。
只是「很久没发生」不算 resolved，那应该是 `active` + 更新 `last_reviewed`。

v1 迁移：`concept` → `explanation`；`howto` → `how-to`；`faq` → `reference` + `note`；
`decision` → `explanation` + `decision`；`index` → `reference` + `index`；`note` → `explanation` + `note`。

## 4. 关系语义

关系词只有六个。**方向性关系只存一侧**，反向由生成器派生；**对称关系**可以两侧都写，
校验器会按无向边去重并给 `REL_DUP` 警告。

| 关系 | 方向 | 反向 | 说明 |
|---|---|---|---|
| `depends-on` | 有向 | `depended-on-by` | A 依赖 B |
| `extends` | 有向 | `extended-by` | A 扩展 B |
| `spawned-from` | 有向 | `spawned` | A 由 B 派生 |
| `supersedes` | 有向 | `superseded-by` | A 取代 B |
| `contradicts` | 对称 | — | A 与 B 冲突 |
| `see-also` | 对称 | — | 弱关联，必须说明为什么 |

写法：

```yaml
related: ["code.config.retry:depends-on"]
```

不要写反向；不要在两侧各写一遍方向性关系。目标 id 必须存在。

`kind: pitfall` 的 `applies_to` 不走 `related`：它可能指向技能 name（没有页面 id），
因此单独成字段，并由生成器写进 [反向链接](_generated/backlinks.md) 与
[踩坑索引](_generated/pitfalls.md)。普通页面不要写 `applies_to`。

## 5. 证据与新鲜度

| `source_type` | `source` 是什么 | 额外要求 |
|---|---|---|
| `code` | 源码/配置文件路径 | 必须是文件，不能是目录 |
| `schema` | JSON Schema / OpenAPI 等 | 必须是文件 |
| `doc` | 仓库内另一份文档 | 必须是文件 |
| `url` | 原始材料/出处 URL | 必须写 `source_retrieved` |

- `source_commit`：7–40 位小写 hex。CI 加 `--check-git` 时会验证提交存在。
- `source_hash`：`sha256:<64 hex>`，用于 URL 快照；可选，但 critical 知识页建议填。
- `sources`：附加真源，inline list，元素以 `code:/schema:/doc:/url:` 开头；`source` 仍是主源。
  一页依赖安装脚本 + 插件 notes + 实机日志时，不要只写一个路径。
- `last_reviewed`：ISO 日期；`review_days` 覆盖默认窗口（normal 365 天，critical 90 天）。
- `kind: report`、`status: archived` 与 `status: resolved` 不参与过期判定；报告的日期写在
  `last_reviewed` 即可，已解决的坑保留原复核日期。
- 不要手写 `updated`；它会被 checkout 重置，本身就是漂移源。

## 6. 报错了怎么读

| 码 | 含义 | 修法 |
|---|---|---|
| `FM_MISSING` | 缺 frontmatter / 没闭合 / YAML 解析失败 | 补 `---` 块 |
| `FM_STRUCTURE` | 用了嵌套对象或列表套列表 | 只留标量与 inline list |
| `SCHEMA` | 字段缺失、类型错、未知字段、格式不符 | 按 `schema/frontmatter.schema.json` 修 |
| `ID_FORMAT` / `ID_DUP` | id 不是小写点分 / 重复 | 改名不改 id |
| `VOCAB` | type/kind/status/tier/confidence/topic 越界 | 先改词表，再写文档 |
| `DEFINES_DUP` | 同一概念定义了两次 | 留一处，另一处改链接 |
| `SOURCE_MISSING` / `SOURCE_NOT_FILE` | 真源不存在 / 指向目录 | 修路径或补真源 |
| `SOURCE_FORMAT` | `sources` 元素不是 `type:value` 或类型不合法 | 用 `code:/schema:/doc:/url:` 前缀 |
| `SOURCE_OUTSIDE` | source 指向仓库外 | 改成仓库内路径 |
| `SOURCE_INVALID_URL` / `SOURCE_RETRIEVED` | URL 不合法 / 缺抓取日期 | 补 `http(s)://` 与 `source_retrieved` |
| `SOURCE_COMMIT_FORMAT` / `SOURCE_COMMIT_MISSING` | commit 格式错 / git 中不存在 | 修 hash 或去掉字段 |
| `GIT_UNAVAILABLE` | 非 git 仓库，跳过 commit 检查（WARN） | 在 git 仓库中运行 `--check-git` |
| `STALE` | 超过复核窗口 | 复核并更新 `last_reviewed` |
| `SUMMARY_MISSING` | standard/index/decision 缺 summary（WARN） | 补一句 summary，或把 `summary_policy` 设回 off |
| `PITFALL_FIELD` | `kind: pitfall` 缺必填字段 | 补 `symptom/cause/detect/avoid/recover/applies_to/severity` |
| `PITFALL_SEVERITY` | severity 不在四档内 | 用 `low/medium/high/critical` |
| `PITFALL_TARGET` | `applies_to` 指向不存在的页面 id 或技能 name | 修 id，或先把目标页/技能建出来 |
| `PITFALL_SELF` | `applies_to` 指向自己 | 坑要挂在被它影响的对象上 |
| `SKILL_FM` | SKILL.md 缺 frontmatter 或解析失败 | 补 `---` 块与 `name/description` |
| `SKILL_SCHEMA` | SKILL.md 的 name/description 不符合 schema | 按 `schema/skills.schema.json` 修 |
| `SKILL_NAME_DIR` | 技能 name 与目录名不一致 | 改名或改目录，保持二者一致 |
| `SKILL_NAME_DUP` | 两个技能用了同一个 name | 改成唯一 name |
| `SKILL_DESC_SHORT` | description 太短 | 写清触发词 + 适用对象 + 能力摘要 |
| `LINK_BROKEN` / `LINK_DIR` / `ANCHOR_BROKEN` | 断链 / 指向目录（WARN）/ 锚点不存在 | 修链接；目录链接确认不是误链 |
| `REL_FORMAT` / `REL_VOCAB` / `REL_TARGET` | 关系格式/词表/目标错 | 用 `id:rel`，目标必须存在 |
| `REL_SELF` | 页面引用自己（WARN） | 删掉自引用 |
| `REL_BOTH_SIDES` | 方向性关系写在两侧 | 删一侧，反向派生 |
| `REL_DUP` | 对称关系重复声明 | 可保留，建议删一侧 |
| `SUPERSEDED_MISSING` / `SUPERSEDED_STATUS` | superseded 缺 `superseded_by` / 目标状态不对 | 补字段并翻状态 |
| `SUPERSEDED_BACKLINK` | 目标页没有写回 `supersedes`（WARN） | 补上或接受警告 |
| `TRUTH_MISSING` / `TRUTH_DRIFT` | 真源不存在 / 文档引用了不存在的标识符 | 修路径，或同一个 PR 同步改代码与文档 |
| `TRUTH_DOCS_NOT_UPDATED` | 真源变了，但映射文档一个都没变 | 同一个 PR 改文档；纯重构用 `--allow-truth-only` |
| `ADR_DUP` / `ADR_INDEX` / `ADR_NAME` | ADR 编号重复 / 索引漏登记 / 文件名不合规 | 修编号、索引或文件名 |
| `ENTRY_DUP` | 出现第二份完整规则文件 | 改成一行指向 `AGENTS.md` |
| `GENERATED_MISSING` | 生成产物缺失 | 跑 `generate.py --write` |
| `GENERATED_STALE` | 生成产物过期 | 跑 `generate.py --write` |
| `CHANGED_EMPTY` | `--changed-since` 没检测到变更（WARN） | 确认 git ref / 在 git 仓库运行 |
| `ORPHAN` | 没有任何入链（WARN） | 挂到 `docs/index.md` 或补 `related` |

`--json` 输出给 CI 读：

```bash
python scripts/check_repo.py --root . --json
```

## 7. 存量仓库怎么接

### 7.1 先定扫描范围

`taxonomy.json` 支持这些配置：

- `include`：非空时只扫描匹配文件。真实仓库建议先 `["README.md", "AGENTS.md", "docs/**"]`。
- `ignore`：排除 `plugins/**`、`vendor/**`、`node_modules/**` 等。
- `context_files`：按 basename 匹配的 agent 上下文文件，例如 `["AGENTS.md"]`；不要求 frontmatter。
- `exempt_basenames`：按 basename 匹配的健康/产物文件，例如
  `["README.md", "CHANGELOG.md", "CONTRIBUTING.md", "SECURITY.md"]`；不要求 frontmatter。
- `slugger`：`legacy`（默认）或 `github`。
- `summary_policy`：`off`（默认）或 `warn`。
- `skills`：技能 profile，`{glob, schema, name_matches_dir, min_description}`；`SKILL.md` 不套通用页面 schema。
- `link_only_files`：只做链接检查、不要求 frontmatter 的 glob，例如 `skills/**/references/*.md`。

`context_files` / `exempt_basenames` 默认都是空，所以 v2.1 单仓行为不变；monorepo 显式配置后，
Phase 2 的 baseline 会从 22 条降到 16 条。它们仍然参与链接检查，只是不再当内容页。

`_` 开头与 `*.template.md` 的文件不参与校验；`schema/agents.template.md` 可以覆盖
`AGENTS.md` 的正文（占位符 `{{PAGES}}`、`{{CRITICAL}}`、`{{TYPES}}`、`{{VERSION}}`）。

### 7.2 再建 baseline

不要第一天全量 ERROR。按这个顺序：

1. 复制 `schema/`、`scripts/`、`.github/` 三件套。
2. 改 `schema/taxonomy.json`：把 `topics` 换成你的领域词；先把词表定死。
3. 改 `schema/sources.json`：声明 `truth → docs` 映射。
4. 跑 `check_repo.py --write-baseline .repo-baseline.json`，把存量问题冻结成 baseline。
5. CI 用 `--baseline .repo-baseline.json --changed-since origin/main`：只对新增/修改文件报 ERROR。
6. 逐步清 baseline；清完再考虑全量 ERROR。
7. 最后才接严格构建、生成器、新鲜度评分。

```bash
# 首次
python scripts/check_repo.py --root . --write-baseline .repo-baseline.json

# PR
python scripts/check_repo.py --root . --baseline .repo-baseline.json --changed-since origin/main
```

## 8. 输出格式与同 PR 检查

```bash
# GitHub Actions 行内 annotation
python scripts/check_repo.py --root . --format github

# SARIF：交给 github/codeql-action/upload-sarif
python scripts/check_repo.py --root . --format sarif > repo-kit.sarif

# 同 PR co-change
python scripts/check_repo.py --root . --changed-files changed.txt --changed-since origin/main
```

`--changed-files` 可以接 `tj-actions/changed-files`；`--changed-since` 在浅克隆下可能为空，
需要 `fetch-depth: 0` 或 PR base SHA。

`sources.json` 的同 PR 配置：

```json
{
  "truth": "plugins/A/Package.appxmanifest",
  "patterns": [],
  "docs": [],
  "co_change": true,
  "co_change_docs": ["README.md", "plugins/A/CHANGELOG.md"]
}
```

真源变了但 `co_change_docs` 一个都没变 → `TRUTH_DOCS_NOT_UPDATED`。纯重构/格式化用
`--allow-truth-only`，或者在 PR 上明确写 NOT RUN。

baseline v2：

```bash
python scripts/check_repo.py --root . --write-baseline .repo-baseline.json --baseline-format v2
```

v1 baseline 仍可读；v2 用 fingerprint，message 小改不会让整条 baseline 失效。

### 7.3 skills 仓库

技能仓库的 `SKILL.md` 有自己的 `name/description` 契约，不能套通用页面 schema：

```json
"skills": {
  "glob": "skills/**/SKILL.md",
  "schema": "schema/skills.schema.json",
  "name_matches_dir": true,
  "min_description": 40
},
"link_only_files": ["skills/**/references/*.md"]
```

- `SKILL.md` 校验 name 格式、name 与目录一致、description 最小长度。
- `references/*.md` 只做链接检查，不要求 frontmatter。
- `SKILL.md` 仍会被链接检查；坏链接照样报 `LINK_BROKEN`。

## 9. 贡献表面

- 工程师：正常 PR。
- 非技术贡献者：开 issue，写「页面链接 + 应改成什么 + 出处」；维护者转 PR。
- 不要让「必须学 Git」成为文档修正的门槛；否则修正在 Slack 里消失。

## 10. 这套管不了什么

校验器验证不了「这句话是不是真的」。一份描述已删除服务的文档，schema、链接、锚点、新鲜度
都可能全过。改公开标识符 / schema / onboarding 的 PR，需要独立评审者把文档与代码路径**并排
读一遍**。

不适用：一次性小任务、草稿箱、探索期创作、目标本身不清楚时。别给这些上规范。
