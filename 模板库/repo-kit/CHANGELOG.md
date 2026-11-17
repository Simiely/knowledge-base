# Changelog

## [2.7.3] - 2026-11-17

修 `skills` 契约：这套 profile 从 2.0 起就在，但**从未被任何仓库使用过**，
所以它的规则一直没被真实校验。2.7.3 首次接第一个 skills 仓（davinci-skills），
顺手拿 Agent Skills 官方规范（agentskills.io/specification）对了一遍，发现两处过宽。

### Fixed

| 项 | 2.7.2 | 2.7.3 | 官方规范 |
|---|---|---|---|
| `description.maxLength` | 1200 | **1024** | 1024 |
| `name.pattern` | `^[a-z0-9][a-z0-9-]*$` | **`^[a-z0-9]+(-[a-z0-9]+)*$`** | 禁止尾连字符、禁止连续连字符 |

旧的 `name` 正则允许 `my-skill-` 和 `a--b`，旧的长度上限允许 1100 字符的描述——
两者都能通过检查器，却会被 Claude 的加载器拒绝。**这是"检查通过 ≠ 能用"的一类缺陷。**

### Added

- `tests/test_skills_contract.py`（8 项）：合法名、尾连字符、连续连字符、大写、name≠目录、
  description 超 1024 / 未超 / 低于本仓下限（`SKILL_DESC_SHORT`）。

### Note

- `min_description: 40` 是**本仓约定**，不是官方要求（官方只要求非空）。
  文档已按这个口径写，避免以后拿官方规范对照时误以为两者冲突。

### Compatibility

- 目前只有 davinci-skills 会用 `skills` profile，收紧不影响任何存量仓库。
- 其他 profile 的仓库无需重装。

## [2.7.2] - 2026-11-17

收尾：文档里还在教已废弃的写法，以及一个让发布流程连踩四次的缺陷。

### Fixed

- **README / usage 的示例仍指向旧键**：`context_files` / `exempt_basenames` /
  `link_only_files` 在 2.7.0 已废弃，但 README 的「能力表」和 usage 的 skills 示例
  还在用它们。读者按示例配置会一路踩到 `TAXONOMY_LEGACY_KEY`。
  现改为 `frontmatter_exempt.names` / `.paths`。
- **`release.py` 不再依赖人补生成物**：版本号写进 `AGENTS.md` / `llms.txt` 的 `{{VERSION}}`，
  发布后必须 `generate --write`，否则仓库立刻自检失败。这一步此前靠人记，
  2.6.0 / 2.7.0 / 2.7.1 / 2.7.2 **连踩四次**；现在 release 自己跑。

### Deprecated

- `--strict-summary`：2.7.0 把 `summary_policy` 固定为 `warn` 后，这个开关已不产生任何效果
  （条件恒真）。按 SemVer，**删除公开 flag 是 MAJOR**，所以本版只把它标成 `[已废弃]`，
  留到 3.0 再删。`usage.md` 的对应表格行同步改写。

### Compatibility

- 无行为变化，无需重装。

## [2.7.1] - 2026-11-17

纯结构重构（L4）：`main()` 604 行 → **296 行**，拆出六个各自只做一件事的函数。
**没有任何行为变化**——验收方式是逐字节比对输出，不是"看起来一样"。

### Changed（仅结构）

| 函数 | 行数 | 职责 |
|---|---|---|
| `build_parser()` | 20 | 参数定义 |
| `collect_docs()` | 27 | 扫出参与校验的 Markdown，记录豁免集合 |
| `check_skill_contracts()` | 37 | skills profile 的 SKILL.md 契约，返回技能名表 |
| `build_page_index()` | 183 | frontmatter / id / 词表 / 关系 / 坑位，产出五个累加器 |
| `check_links_and_orphans()` | 77 | 链接、锚点、孤儿页（入链由调用方传入并累加） |
| `render_report()` | 28 | 四种输出格式与退出码 |

`main()` 现在是一条线：解析 → 加载 → 收文档 → 技能契约 → 页面索引 → 关系校验 →
链接/孤儿 → ADR → 真源 → 变更集/baseline → 输出。

### 为什么没有继续拆

`build_page_index` 仍有 183 行，因为 frontmatter、id、词表、关系、坑位**共享同一批累加器**
（关系与坑位还要做二次校验）。再拆就得把这五个容器包成状态对象，那是一次重新设计，
不是重构——收益是"数字更小"，代价是行为等价性需要用同样的力气重新证明。

`main()` 剩下的 296 行里，`changed / baseline / prune` 那段约 90 行是最值得下一步抽的，
但它同时改 report 与退出码，风险高于收益，留到下次真需要改这块时再做。

### 验证

- 65 项单测通过。
- **逐字节比对**：一个注入 9 ERROR + 3 WARN 的夹具（覆盖坏链、坏锚点、缺 frontmatter、
  重复 id、非法关系、孤儿页、过期页），text / json / sarif 三种输出与重构前完全一致；
  另外 5 个真实仓库（kit 自身、dufs-gui、blender-tips、home-inventory、EverythingCmdPal）
  的 text / json 输出也逐字节一致。
- `release --check` PASS、`drift_probe` 8/8。

### Compatibility

- 无需重装：行为等价，已装 2.7.0 的仓库继续可用。重装只是让文件内容对齐到 2.7.1。

## [2.7.0] - 2026-11-17

结构收敛第二批（L2）：**「哪些文件不要求 frontmatter」从四种写法收敛成一种**。
由 12 个仓库的实测数据驱动，不是审美问题。

### 数据依据

| 事实 | 实测 |
|---|---|
| `context_files` | **12/12 都是 `["AGENTS.md"]`** —— 不是配置，是常量 |
| `slugger` | **12/12 都是 `github`** —— `legacy` 从未被使用 |
| `summary_policy` | 11 `warn` + 1 `off`（后者 `pages=0`，开关从未生效） |
| 四种豁免键 | 经 `matches_basename()` 证实同一语义：`context_files` 与 `exempt_basenames` 是同一行代码 |

同一段豁免逻辑还在 `check_repo.py` 与 `generate.py` 里**各实现了一遍**，加一个仓库需求要动两处。

### Added

- `frontmatter_exempt: {"names": [...], "paths": [...]}`：`names` 按文件名匹配（任意层级），
  `paths` 按相对路径 glob 匹配；也接受扁平列表。
- `check_repo.resolve_exempt()`：唯一的归一化入口，`generate.py` 改为复用它。
- `scripts/migrate-taxonomy.py`：**文本手术**式迁移（只删旧键、插新键，不重排其余字节），
  带 `--check` 预览 diff。
- `tests/test_exempt.py`（4 项）：names 任意层级、paths 不误伤同名、生成器与校验器同判定、旧键仍生效并告警。

### Changed

- `slugger` 固定 `github`、`summary_policy` 固定 `warn`。后者是**行为变化**：
  `--strict-summary` 不再是唯一触发条件。影响面为零——唯一设 `off` 的仓库 `pages=0`。
- 旧键（`context_files` / `exempt_basenames` / `entry_files` / `link_only_files`）仍生效，
  但报 `TAXONOMY_LEGACY_KEY`（每仓一条）。

### Compatibility

- **不破坏**：旧 taxonomy 不改也能跑，只是多一条 WARN。
- 迁移一个仓库只需两条命令（`migrate-taxonomy --check` 看 diff，`--write` 落盘），
  验收标准是迁移前后 `check_repo` 的 (errors, warnings, pages) 三元组不变。

## [2.6.0] - 2026-11-16

结构收敛第一批：**版本号从「五处拷贝」变成「一处定义」**，并把 CI 模板的不一致修掉。
起因：`generate.py --help` 停在 2.5.2 而 kit 已是 2.5.3，追下去发现根本问题是
`VERSION`（脚手架读）与 `taxonomy.version`（安装器读）是两个独立来源，一旦不一致，
同一版 kit 会产出两种版本号且无任何检查能发现。

### Added

- `scripts/release.py`：
  - `--version X.Y.Z` 同步 `taxonomy.version` / `taxonomy.name` / `check_repo.py` 的
    `KIT_VERSION`，可选抬 `spec.json` 的 `min_kit`；随后跑单测、`drift_probe`、
    `check_repo`、`generate --check`；并在 CHANGELOG 插入空节。
  - `--check` 只校验副本一致性，可进 CI。
- 测试从 49 项增至 **61 项**，补的都是「改过但没测」的地方：
  - `entry_files`：免 frontmatter、但链接仍被检查（2.5.0 的取舍）
  - `generated_files` 三态：缺键=全生成 / 显式空=零生成 / 子集=只生成那些（2.5.2 的修复）
  - `--prune-baseline`：失效条目删除、仍命中的保留（2.5.3 的新能力）
  - **CI 模板四条语义不变量**（不是逐行比对）：校验器与锁步骤必在；`--changed-since`
    必须配 `fetch-depth: 0`；`generate` 步骤只能出现在有生成器的 profile；
    同档 profile 的依赖装法必须一致
  - `release --check` 自身：版本漂移与 `VERSION` 文件复活都要被拦

### Changed

- **删除 `repo-kit/VERSION`**。脚手架改为读 `schema/taxonomy.json` 的 `version`，
  与安装器同源。`KIT_VERSION` 只由 `check_repo.py` 拥有，`generate.py` 引用它。
- 两个脚本的 `argparse` 描述改为运行时拼版本号，docstring 不再写版本——这类文字
  不参与校验，写死一次就会漂。
- **CI 模板统一**：`knowledge` 与 `link-only` 同属无真源档，此前一个用
  `-r requirements.txt`、一个显式装三个包（两次独立修改的痕迹）。现统一为 `-r`，
  步骤名也统一为 `Doc dependencies`。

### Compatibility

- 消费仓库无需改动，也不必重装：本版只改 kit 源仓库的版本管理与模板，
  已装副本与其 `kit.lock` 仍然匹配。
- 模板变化只影响**以后新建**的仓库；已存在仓库的 CI 保持原样（不受影响）。

## [2.5.3] - 2026-11-16

补「baseline 生命周期」这个长期空档。由 `blender-tips` 真实升级暴露。

### Added

- `check_repo.py --prune-baseline <文件>`：跑一遍全量检查，**删除 baseline 中已不再命中的条目**，
  只保留仍存在的问题，并把结果重写为 v2（带指纹）。

  为什么需要：`blender-tips` 的 baseline 有 **170 条，全部是 `LINK_DIR`**。
  该规则在 2.5.0 静音后，这些问题已不存在，但配置文件还在压制它们——
  **一份压制「已消失问题」的 baseline 比没有更危险**：它让人误以为还有待办，
  也会掩盖真正新增的条目。规范只写了「用 baseline 渐进接入」，没写「规则变更后怎么收尾」。

- 与 `--changed-since` 同用时忽略变更集并打印提示：清理必须按全量结果判断，
  否则「本次未改动的文件」会被误判成「已不再命中」而误删。

## [2.5.2] - 2026-11-16

一处会**静默覆盖手写文档**的语义错误。由 12 仓升级 dry-run 暴露。

### Fixed

- `generate.py` 区分「没声明 `generated_files`」与「显式声明为空」：

  | taxonomy | 旧行为（2.5.1） | 新行为（2.5.2） |
  |---|---|---|
  | 缺 `generated_files` 键 | 全量生成 5 个文件 | 不变（兼容旧仓库） |
  | `"generated_files": []` | **全量生成 5 个文件** | 一个都不生成 |

  旧写法是 `set(tax.get("generated_files") or [])`，空列表与缺键等价，于是
  `link-only` 这类「有手写 `AGENTS.md`、清单为空」的仓库一旦跑 `generate --write`
  就会被 kit 的兜底模板覆盖。升级 dry-run 里 `rive-tips` 正是这样被冲掉，
  并因此伪造出 4 条指向 `docs/usage.md` 的断链——**误报的根源是覆盖，不是链接本身**。

### Compatibility

- 现有消费仓不受影响：11 个已接入仓库要么缺键（旧行为不变），要么清单列了 5 个文件。
- `check_repo.py` 未改动，只换 `generate.py`；重装后 `kit.lock.json` 里
  `tools/repo-kit/generate.py` 的哈希会变，属预期。

## [2.5.1] - 2026-11-16

两处「规范允许、工具不允许」的修复。均由 `dufs-gui` 接入时的 dry-run 暴露。

### Fixed

- `generate.py` 只生成 `taxonomy.generated_files` 里声明过的文件，不再无条件重写 `AGENTS.md`。
  此前 `AGENTS.md` 被硬编码进输出字典，导致**手写 AGENTS 的仓库永远 `GENERATED_STALE`**，
  与 REPO_STANDARD 1.1（「可以是生成文件，也可以是手写正文」）和 4（「AGENTS 生成还是手写」
  属于不锁定的内容模型）直接冲突。
  兼容：未声明 `generated_files` 的仓库行为不变；声明了 5 件的仓库行为也不变。
- 模板 CI 改为显式安装文档依赖（`PyYAML` / `markdown-it-py` / `jsonschema`），
  不再 `python -m pip install -r requirements.txt`。代码仓库的 `requirements.txt` 是
  运行/构建清单（例如 `dufs-gui` 里只有 `pyinstaller==6.22.3`），按模板装会在
  `check_repo.py` 处报 `DEPENDENCY_MISSING` 退出 2。

### Changed

- `REPO_STANDARD` 6：文档依赖与仓库自有 `requirements.txt` 解耦，并说明
  `generated_files` 决定生成范围。
- `monorepo` profile 的 `include` 补 `CHANGELOG.md`：此前它在 `exempt_basenames` 里、
  却不在 `include` 里，等于**四件套中的 CHANGELOG 从不参与链接检查**（`exempt_basenames`
  只对已纳入扫描的文件生效）。`README.md` 一直是 include + exempt 双写，CHANGELOG 漏了。

## [2.5.0] - 2026-11-16

### Changed

- `LINK_DIR` 不再产出告警：**指向一个存在的目录是合法写法**（GitHub 渲染目录列表，
  README/DEVELOPMENT 索引源码目录常用），真断链仍由 `LINK_BROKEN` 覆盖。
  实测该项在 blender-tips 单仓 170 条、knowledge-base 自身 4 条（都在 README 的仓库导航上），
  常驻 WARN 会训练出「WARN 可以无视」的习惯，进而淹掉 `ORPHAN`、`PITFALL_*` 这类真信号。
- monorepo profile 的 `include` 与 `entry_files` 补 `DEVELOPMENT.md`：此前四件套之一
  **从不进入扫描范围**，「DEVELOPMENT > 200 行拆 docs/」的阈值实际未生效。
  归入 `entry_files`（与 skills profile 一致）：门面文件不要求 frontmatter，但链接参与检查。

### Added

- 模板 CI（`monorepo` / `skills`）新增 `fetch-depth: 0` 与 PR-only 的 `--changed-since` 步骤：
  `sources.json` 的 `co_change` 此前因变更集恒为空而**永不触发**，是 kit 里唯一能发现
  「代码改了文档没改」的机制。`EverythingCmdPal` 已手工绕过此缺失，现收进模板。

### Compatibility

- 判定逻辑的改变只**减少** WARN，不新增 ERROR；未装新 kit 的仓库行为不变。
- `DEVELOPMENT.md` 开始被检查后，存量仓库可能暴露此前隐藏的断链。
  不想改变现状的仓库可不更新 `schema/taxonomy.json`（仓库自有文件，安装器不覆盖）。

## [2.4.0] - 2026-11-13

### Added

- `schema/kit.lock.json` 新增 `spec_version`：安装器从 `../单项目规范/spec.json`
  读取并写入，任何程序可直接读取该字段判断仓库按哪一版规范整理。
- `check_repo.py` 新增 SPEC 检查：缺字段 WARN、格式非法/主版本落后 ERROR、
  次版本落后 WARN、高于校验器支持 ERROR。

### Changed

- `update-repo-kit.ps1` 的 `-Check` 输出与锁写入均包含 `spec_version`。

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
