# 单项目规范 · 版本记录

规范版本（`spec_version`）与 repo-kit 工具版本独立：规范描述“仓库应该长什么样”，
kit 描述“用哪个校验器检查”。仓库通过 `schema/kit.lock.json` 的 `spec_version`
字段声明自己按哪一版规范整理。

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
