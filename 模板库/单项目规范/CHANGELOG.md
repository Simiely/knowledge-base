# 单项目规范 · 版本记录

规范版本（`spec_version`）与 repo-kit 工具版本独立：规范描述“仓库应该长什么样”，
kit 描述“用哪个校验器检查”。仓库通过 `schema/kit.lock.json` 的 `spec_version`
字段声明自己按哪一版规范整理。

## [2.1.3] - 2026-11-17

### Added

- `schema/taxonomy.json` 新增 **`frontmatter_exempt`**，作为「不要求 frontmatter」的唯一配置：

  ```json
  "frontmatter_exempt": {"names": ["AGENTS.md", "README.md"], "paths": ["rules/**"]}
  ```

### Deprecated

- `context_files` / `exempt_basenames` / `entry_files` / `link_only_files`：四种写法表达同一件事，
  保留生效但报 `TAXONOMY_LEGACY_KEY`。迁移见 `repo-kit/scripts/migrate-taxonomy.py`。
- `slugger`（固定 `github`）与 `summary_policy`（固定 `warn`）：实测 12 个仓库取值相同，
  不再是配置项。`summary_policy` 的默认值从 `off` 改为 `warn`，是本次唯一的**行为变化**。

### Why

不是审美：四种写法导致「新仓库该往哪个键里加」每次都要读代码才知道，
而 `check_repo` 与 `generate` 各实现一遍，改一处必漏另一处。

### 工具（不改变任何要求，不触发仓库升级）

- `audit-spec.ps1` 从「只比 spec_version」扩成 fleet 体检，新增四项：
  `taxonomy.version` 与 `kit.lock.version` 漂移、CI 是否真的接 `check_repo`
  （含 `--changed-since` 缺 `fetch-depth: 0` 的静默失效）、死 baseline、旧豁免键残留。
  任一不满足退出码为 1，可进任意流水线。
- 五类缺陷各造一个副本验证过：全部命中，13 个真实仓库零误报。

## [2.1.2] - 2026-11-16

补两处「规范写了、执行面没跟上」的地方。由 `blender-tips` 真实升级暴露。

### Changed

- **CI 按「有没有真源」分两档**（`REPO_STANDARD` 1.5）：
  A 档（`monorepo` / `skills`，有 `sources.json`）保留 `fetch-depth: 0` + PR 的 `--changed-since`
  + 显式装文档依赖；B 档（`knowledge` / `link-only`，无真源）只跑 check + generate + lock。
  原文是一套通用条款，结果 knowledge 仓库抄了三个空转步骤——`--changed-since` 在没有
  `sources.json` 时什么都不会发生，只是让人误以为在检查。
- **补 `knowledge` profile 的骨架**：规范第 2 节一直列着它，但 `新项目模板/profiles/` 只有
  三个，这类仓库只能手写 CI。模板 1.1.0 补齐，同时开始记录模板版本号。

### Added

- **baseline 的生命周期**（`REPO_STANDARD` 1.6）：进入（`--write-baseline`）→ 退出
  （`--prune-baseline`）→ 清算（删文件、去掉 CI 参数）。规则收紧或静音后必须跑一次，
  否则 baseline 会变成压制「已消失问题」的死配置——`blender-tips` 的 170 条就是这种情况。

### Migration

- 无需迁移。`knowledge` 仓库下次升级时可直接改用模板的 CI 形态；
  有 baseline 的仓库跑一次 `--prune-baseline` 清掉失效条目。

## [2.1.1] - 2026-11-16

只有澄清，没有新增要求。两处原文与工具实现不一致，2.5.1 把工具改成与原文一致。

### Clarified

- `AGENTS.md`「可以是生成文件，也可以是手写正文」现在真的成立：`generate.py` 只生成
  `taxonomy.generated_files` 里声明的文件。此前它无条件重写 `AGENTS.md`，手写仓库必红。
- 接入清单不再要求往仓库的 `requirements.txt` 里塞文档依赖：CI 显式安装，
  仓库的 `requirements.txt` 保持运行/构建语义。后者让代码仓库（如 `dufs-gui`，
  只有 `pyinstaller==2.x`）按模板必失败。

### Migration

- 无需迁移。想改手写的仓库把 `AGENTS.md` 从 `generated_files` 去掉即可；
  其余仓库行为不变。`spec.json` 的 `min_kit` 抬到 `2.5.1`。

## [2.1.0] - 2026-11-16

修订依据：在 `dufs-gui` 上做接入审计时发现，规范的四项完成定义可以被「空壳」满足——
结构全绿、内容与代码相反。随后抽样 3 个已接入仓库（EverythingCmdPal / taskbar-drawer /
blender-tips）复核，定位到的不是「条款不够」，而是**已写下的条款在回路里没生效**。
本版因此是收敛版：不新增概念，只让既有条款真的运行。

### Changed

- `LINK_DIR` 不再算问题：指向**存在**的目录是合法写法。实测该规则在 blender-tips
  常驻 170 条、knowledge-base 自身 4 条，`PASS` 却照旧——常驻 WARN 会训练出
  「WARN 可以无视」，进而淹掉 `ORPHAN`、`PITFALL_*` 这类真信号。
- 四件套的扫描覆盖面：`monorepo` profile 的 `include` / `entry_files` 补 `DEVELOPMENT.md`。
  此前四件套之一从不进扫描范围，「> 200 行拆 docs/」的阈值等于没写。
- CI 约定补充三条：`fetch-depth: 0`、PR 事件跑 `--changed-since`、`paths:` 覆盖门面文件。
  缺第一条时变更集恒为空，`co_change` **静默失效**——kit 里唯一能发现「代码改了文档没改」
  的机制，在 11 个已接入仓库里全部没跑起来。

### Added

- `REPO_STANDARD.md` 1.5 增加「WARN 不是免死金牌」的判定口径：单仓库常驻数十上百条的
  规则视为失效，要么修规则，要么显式降 INFO。
- 接入清单增加一条：`taxonomy.json` 必须覆盖四件套。

### Migration

- 见 `migrations/v2.1.0.md`。已接入仓库只需两步：重装 kit（`kit.lock.json` 的哈希随新文件重写）、
  把 `DEVELOPMENT.md` 加进 `include` 与 `entry_files`。
- 未做第二步的仓库行为不变，仍算 2.0.0 语义；`spec_version` 由 `kit.lock.json` 决定，
  不在本文件推断。

## [2.0.0] - 2026-11-13

### Added

- repo-kit 机器层：`tools/repo-kit`、`schema/`、`llms.txt`、`docs/_generated/`
- 文档 frontmatter 契约与四件套门面要求
- `repo-check` CI（不变量 + 生成物一致性 + kit 锁）
- `schema/kit.lock.json` 声明 `spec_version`，供任意程序读取

### Migration

- 旧仓库：按 `migrations/v2.0.0.md` 接入 kit 并补齐 frontmatter
- 验收：`REPO CHECK` / `GENERATE CHECK` / `KIT LOCK` 三项 PASS

## [1.0.0] - 2026-08-01

### Added

- 根目录四件套：`README` / `AGENTS` / `DEVELOPMENT` / `CHANGELOG`
- AGENTS 文档基线约定（日期 + commit）
- 超阈值拆分与“主文件 = 门面 + 索引”

### Notes

- 该版本无机器层，仅靠人工维护；`kit.lock` 不存在的仓库按此版本识别
