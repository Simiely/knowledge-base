# Changelog

## [2.3.2] - 2026-11-11

### Added

- `REPO_STANDARD.md` v1.0.0：统一入口、工具位置、命令、输出、版本锁与 CI；
  四个 profile：`monorepo` / `skills` / `knowledge` / `link-only`。
- `tools/update-repo-kit.ps1`：按 profile 安装 kit 文件并写 `schema/kit.lock.json`；
  `-Check` 只验哈希，可在 CI 运行。
- 新仓库接入清单与「不统一的内容模型」边界。

### Changed

- 标准路径统一为 `tools/repo-kit/`；`scripts/` 只放仓库自己的业务脚本。
- `generate.py` 的生成页提示改为按实际工具路径输出（`tools/repo-kit/generate.py`），
  不再硬编码 `scripts/generate.py`。
- `drift_probe.py` 明确为 kit 自测，不随消费仓库分发。

## [2.3.1] - 2026-11-11

### Fixed

- `drift_probe.py` 在消费仓库里不再抛 `FileNotFoundError`：它依赖 kit 自带的 `examples/` 夹具，
  缺少夹具时打印 `SKIP` 并退出 0。正负对照是校验器自测，不是仓库验收。

## [2.3.0] - 2026-11-11

### Added

- `kind: pitfall`：把「容易犯错的部分」做成一等内容页。必填 `summary`、`symptom`、`cause`、
  `detect`、`avoid`、`recover`、`applies_to`、`severity`；`applies_to` 可指向页面 id 或技能 name。
- `status: resolved`：根因已消除的坑保留可检索性，不参与过期判定。
- 检查码 `PITFALL_FIELD` / `PITFALL_SEVERITY` / `PITFALL_TARGET` / `PITFALL_SELF`；
  `applies_to` 计入入链，坑不会因为只被目标页引用而误报 `ORPHAN`。
- 生成 `docs/_generated/pitfalls.md`（未解决/已解决/按适用范围）；`applies_to` 同步进 `backlinks.md`。
- ADR-0003、`docs/usage.md` 3.1、`docs/concepts/types.md` 的 pitfall 说明。

### Changed

- `taxonomy.json` 升到 `2.3.0`：`kinds` 加 `pitfall`，`statuses` 加 `resolved`，
  `generated_files` 加 `docs/_generated/pitfalls.md`。
- `generate.py` 的索引与 `llms.txt` 把 pitfall 从 By type 移到独立 Pitfalls 分区。

### Compatibility

- 不写 `kind: pitfall` 的仓库，检查结果与 v2.2 一致。
- 复制 v2.3 `taxonomy.json` 的仓库需要跑一次 `generate.py --write`，补出 `pitfalls.md`。

## [2.2.1] - 2026-11-11

### Added

- `skills` profile：`skills/**/SKILL.md` 用独立 `schema/skills.schema.json` 校验
  `name` / `description` / name 与目录一致 / description 最小长度，不套通用页面 schema。
- `link_only_files`：`skills/**/references/*.md` 这类长资料只做链接检查，不强制 frontmatter。
- workbuddy-skills 实测：15 个 SKILL.md 全部通过契约检查；修复 2 条归档目录软断链。
- 42 个测试全绿。

## [2.2.0] - 2026-11-11

### Added

- `context_files` / `exempt_basenames`：任意层级 `AGENTS.md`、`README.md`、`CHANGELOG.md` 等
  不再强制 frontmatter；默认关闭，monorepo 显式开启。
- `kind: report`：一次性分析/计划/复盘可归档，`report` / `archived` 不参与过期判定。
- `sources: ["code:...", "doc:...", "url:..."]`：一页多源 provenance；`source` 仍是主源。
- 同 PR co-change：`sources.json` 的 `co_change` + `--changed-since` / `--changed-files`；
  真源变了但映射文档没变 → `TRUTH_DOCS_NOT_UPDATED`；`--allow-truth-only` 逃生口。
- `--format sarif` / `--format github`：稳定 `partialFingerprints`，可接 GitHub code scanning /
  PR annotation。
- `--baseline-format v2`：baseline 支持 fingerprint；读取时自动兼容 v1/v2。
- `summary_policy`（默认 `off`）与 `--strict-summary`；`slugger`（默认 `legacy`，可选 `github`）。

### Changed

- 默认行为保持 v2.1：不配置新字段时，检查结果与 v2.1 一致。
- `generate.py` 的索引与 `llms.txt` 增加 Reports 分区，不再把 report 混进 evergreen。

## [2.1.0] - 2026-11-11

### Added

- `taxonomy.json` 支持 `include` 白名单：真实仓库可以只扫描 `docs/**` + `README.md`，
  插件目录/历史报告按需逐步纳入。
- `schema/agents.template.md` 可覆盖 `AGENTS.md` 正文；模板占位符 `{{PAGES}}`、
  `{{CRITICAL}}`、`{{TYPES}}`、`{{VERSION}}`。
- `*.template.md` 与 `_` 开头的文件不参与校验，避免模板里的示例链接被当成真实断链。
- `llms.txt` 标题改从 `taxonomy.name` 读取，不再依赖目录名；复制/改名仓库不会导致
  `GENERATE CHECK` 误报。

### Changed

- `LINK_DIR` 从 ERROR 降为 WARN：GitHub 可以渲染目录链接，真实仓库常用它做“源码目录”导航。
- `llms.txt` 的 Core 链接按文件是否存在动态生成；没有 `examples/` 时不再输出空章节。

## [2.0.0] - 2026-11-11

### Changed

- 架构从「七层 + 八条不变量」重构为「四平面 × 三表面」：内容契约、知识图谱、证据与新鲜度、
  验证与治理；阅读、机器、贡献三个表面。
- `type` 与 `kind` 拆开：`type` 使用 tutorial / how-to / reference / explanation；
  `kind` 使用 standard / decision / index / note / glossary。
- frontmatter 从手写解析改为 PyYAML + JSON Schema；Markdown 从正则改为 markdown-it。
- 关系模型加入 `direction` / `inverse` / `transitive`：方向性关系单侧，对称关系显式声明。
- ADR 只校验编号唯一与索引同步，不再要求编号连续。

### Added

- 生成器：`AGENTS.md`、`llms.txt`、`docs/_generated/index.md`、`docs/_generated/backlinks.md`。
- `--baseline`、`--write-baseline`、`--changed-since`：存量仓库渐进接入。
- 正对照 + 负对照：`drift_probe.py` 注入 8 类漂移；合法样例必须全绿。
- 单元测试：代码块假链接、行内代码、`#L3` 锚点、重名标题、README 入链、嵌套 frontmatter、
  camelCase 键、source_commit、superseded_by、唯一入口。
- `source_type` / `source_retrieved` / `source_hash` / `review_days` / `confidence` 字段。

### Removed

- 移除「八条不变量都能被脚本检查」的过度承诺；改为能力矩阵。
- 移除 `last_verified`，统一为 `last_reviewed`。
- 移除 ADR 编号连续性检查。
