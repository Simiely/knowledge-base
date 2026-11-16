# 单项目规范 · 版本记录

规范版本（`spec_version`）与 repo-kit 工具版本独立：规范描述“仓库应该长什么样”，
kit 描述“用哪个校验器检查”。仓库通过 `schema/kit.lock.json` 的 `spec_version`
字段声明自己按哪一版规范整理。

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
