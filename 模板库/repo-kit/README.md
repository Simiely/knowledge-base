# repo-kit v2.3.2

一个面向代码仓库与知识仓库的**轻量治理骨架**。它不试图「自动保证文档正确」，而是把
「内容契约、类型化关系、证据与新鲜度、可执行校验」串成一条可维护的闭环。

多仓库统一方式见 [REPO_STANDARD.md](REPO_STANDARD.md)：统一工具位置、命令、输出与版本锁，
不统一内容模型。

## 设计：四平面 × 三表面

| 平面 | 职责 | 关键产物 |
|---|---|---|
| A 内容契约 | `type`/`kind`、稳定 `id`、状态、owner、受控词表 | `schema/frontmatter.schema.json`、`schema/taxonomy.json` |
| B 知识图谱 | 方向性/对称性关系、反链、索引 | `docs/_generated/backlinks.md`、`docs/_generated/index.md` |
| C 证据与新鲜度 | source 类型、来源快照、复核窗口 | `schema/sources.json`、`last_reviewed`、`review_days` |
| D 验证与治理 | schema/lint/link、diff CI、baseline、人审 | `scripts/check_repo.py`、CI、ADR |

| 表面 | 给谁 | 入口 |
|---|---|---|
| S1 阅读 | 人 | 文档站、搜索、`docs/_generated/index.md` |
| S2 机器 | AI / RAG / 工具 | `AGENTS.md`、`llms.txt` |
| S3 贡献 | 工程师与非技术贡献者 | PR、issue 建议、Web 编辑器 |

核心原则：**最小可行词表 + 生成优先 + 组合工具 + 渐进执行 + 人审语义。**

## 快速开始

```bash
python -m pip install -r requirements.txt

python scripts/check_repo.py --root .          # 不变量检查
python scripts/generate.py --root . --check    # 生成产物是否最新
python scripts/check_repo.py --root . --format sarif > repo-kit.sarif  # 可选：SARIF
python scripts/drift_probe.py --root .         # 正对照：注入 8 类漂移，确认会红
python -m unittest discover -s tests           # 单元测试
```

全绿信号：

```
REPO CHECK: PASS  (ERROR=0)
GENERATE CHECK: PASS
DRIFT PROBE: PASS  (8/8 被拦截)
```

## 目录

```
repo-kit-v2/
├── AGENTS.md                  # 生成：AI/人的唯一入口（薄）
├── llms.txt                   # 生成：机器消费入口
├── schema/
│   ├── taxonomy.json          # type/kind/status/topics/relations
│   ├── frontmatter.schema.json# 内容契约（JSON Schema）
│   └── sources.json           # 真源映射
├── scripts/
│   ├── check_repo.py          # 不变量校验器
│   ├── generate.py            # 生成 AGENTS/llms/index/backlinks
│   └── drift_probe.py         # 正对照 + 负对照
├── docs/
│   ├── index.md               # 人工导航
│   ├── usage.md               # 唯一权威用法
│   ├── concepts/              # 概念定义（SSOT）
│   ├── decisions/             # ADR（append-only）
│   └── _generated/            # 生成产物（index/backlinks/pitfalls），勿手改
├── examples/
│   ├── code/                  # 代码仓库 profile 的最小示例
│   └── knowledge/             # 知识仓库 profile 的最小示例
└── tests/                     # 反例与回归测试
```

## 能力矩阵

| 能力 | 级别 | 说明 |
|---|---|---|
| frontmatter schema 校验 | 强 | JSON Schema（内置子集校验器；装 `jsonschema` 则用标准引擎） |
| ID / defines 唯一 | 强 | 全局唯一，改名不改 id |
| 词表闭集 | 强 | `type/kind/status/tier/confidence/topics/relations` |
| 方向性关系单侧 | 强 | 反向由生成器派生；对称关系允许两侧并去重 |
| 链接 / 锚点 | 强 | 用 markdown-it 解析，跳过代码块与行内代码；只对 `.md` 查锚点 |
| 真源存在性 | 强 | `code/schema/doc` 必须是文件；URL 必须有 `source_retrieved` |
| 真源标识符漂移 | 中 | 由 `sources.json` 的 pattern 驱动；不是所有语言都适配 |
| 新鲜度 | 强 | `last_reviewed` + `review_days`；critical 默认 90 天 |
| 生成产物最新 | 强 | `generate.py --check` 比对 |
| baseline / changed-only | 强 | 存量仓库渐进接入；v2 baseline 带 fingerprint |
| 扫描范围 | 强 | `taxonomy.json` 的 `include` / `ignore`；`*.template.md` 自动跳过 |
| 生成入口可覆盖 | 强 | `schema/agents.template.md` + `taxonomy.name` |
| monorepo 上下文 | 强 | `context_files` / `exempt_basenames`，默认关闭，显式开启 |
| 多源 provenance | 强 | `source` 主源 + `sources` 附加源（code/schema/url/doc） |
| 报告生命周期 | 强 | `kind: report` / `status: archived` 不参与过期判定 |
| 同 PR co-change | 强 | `co_change` + `--changed-since` / `--changed-files` |
| SARIF / GitHub 输出 | 强 | `--format sarif` / `--format github`，带稳定 fingerprint |
| skills profile | 强 | `skills/**/SKILL.md` 用独立 schema；`link_only_files` 只查链接 |
| 语义真假 | 无 | 只能人审；这是边界，不是缺陷 |
| 踩坑页 | 强 | `kind: pitfall` 八个必填字段；`applies_to` 可指向页面或技能；生成踩坑索引 |
| 已解决的坑 | 强 | `status: resolved` 不参与过期判定，仍保留在索引 |

## v2.3 相对 v2.2 的变化

- **坑有了位置**：`kind: pitfall` 承载失败模式（症状/根因/检测/规避/恢复），不再混进规范或技能。
- **可检查**：缺字段、severity 越界、`applies_to` 目标不存在或指向自己 → `PITFALL_*` ERROR。
- **可导航**：`docs/_generated/pitfalls.md` 按未解决/已解决/适用范围聚合；反链包含 `applies_to`。
- **可退休**：`status: resolved` 表示根因已消除，免过期但保留可检索性。
- **默认不变**：没有 pitfall 页的仓库，检查结果与 v2.2 一致；复制新 taxonomy 后跑一次 `generate.py --write`。

## v2.2 相对 v2.1 的变化

- **默认行为不变**：v2.1 仓库不改配置，升级后结果一致；新能力全部 opt-in。
- `context_files` / `exempt_basenames`：嵌套 `AGENTS.md`、任意层级 `README/CHANGELOG` 不再强制
  frontmatter，但仍检查链接。
- `kind: report`：一次性分析/计划/复盘可以归档，不参与过期判定。
- `sources`：一页可以声明多个真源；`source` 仍是主源。
- `co_change`：真源变了但映射文档没变 → `TRUTH_DOCS_NOT_UPDATED`；`--allow-truth-only` 逃生口。
- `--format sarif|github`：结果可以进 GitHub code scanning 或 PR annotation。
- `--baseline-format v2`：baseline 可用 fingerprint；v1 仍可读。
- `summary_policy` / `slugger`：默认 `off` / `legacy`，显式开启才生效。
- `skills` profile：`SKILL.md` 用 `schema/skills.schema.json` 校验 `name/description`；`references` 可只查链接。

## v2.0 相对 v1 的变化

- `type` 与 `kind` 拆开：`type` 用 Diátaxis/DITA 的信息类型，`kind` 表示标准/决策/索引/笔记。
- 关系加入 `direction` 与 `inverse`：方向性关系只存一侧，对称关系显式声明。
- frontmatter 改用 JSON Schema + PyYAML；Markdown 用 markdown-it 解析。
- 增加生成器：`AGENTS.md`、`llms.txt`、索引、反链全部生成，不写回源文件。
- 增加 baseline、changed-only、负对照（合法样例必须全绿）。
- ADR 只校验唯一性与索引同步，不再要求编号连续。
- 修正 v1 的已知误报/漏报：代码块假链接、`#L3` 锚点、重名标题、README 入链、嵌套 frontmatter、camelCase 键、`source_commit`、`superseded_by`、唯一入口。

## 边界

`check_repo.py` 验证不了「这句话是不是真的」。一份描述已删除服务的文档，schema、链接、锚点、
新鲜度都可能全过。改公开标识符 / schema / onboarding 流程的 PR，仍然需要人把文档与代码路径
并排读一遍。

不适用：一次性小任务、草稿箱、探索期材料、目标本身不清楚的项目。别给这些上规范。
