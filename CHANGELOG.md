# CHANGELOG

## v1.0.0 — 2026-11-12

建立「规范 + 新项目模板 + repo-kit」三层上游。

### 新增

- `模板库/单项目规范/`：保留 4 文件模型，新增机器层（repo-kit、版本锁、CI）与完成定义。
- `模板库/新项目模板/`：`base/` + `monorepo` / `skills` / `link-only` 三个 profile，
  以及 `新建仓库.ps1`（复制、替换占位符、安装 kit、生成、检查）。
- `模板库/提示词模板.md`：新建仓库与整理已有仓库两段提示词；只指向规范仓库、不贴规范正文，不写死路径/名称，缺信息先提问。
- `模板库/repo-kit/`：vendored repo-kit v2.3.2，含 `REPO_STANDARD.md`、脚本、schema、测试。
- 根 `schema/`、`tools/`、`requirements.txt`：知识库自身采用 `link-only` 校验。
- `.github/workflows/repo-check.yml`：自检 + 三个模板 smoke + kit 自测（drift_probe + 49 测试）。
- 根 `AGENTS.md`、`DEVELOPMENT.md`、本 CHANGELOG：让上游仓库自己遵守 4 文件模型。

### 变更

- 根 README 与 `模板库/README.md`：从「两个层级」升级为「三个入口」。
- `初始化说明.md`：先选「新项目仓库」或「新经验库」，再走对应路径。
- 用户库数据未迁移、未改写；仍使用原有 `tags/date/status/source` frontmatter。

### 验证

- 知识库自检：`REPO CHECK: PASS`（4 条目录链接 WARN）、`KIT LOCK: PASS`。
- vendored kit：`REPO CHECK: PASS`、`GENERATE CHECK: PASS`、`DRIFT PROBE: 8/8`、49 测试 OK。
- 三个 profile 本地生成后均通过 `check` / `generate --check` / `kit lock`（monorepo pages=2，skills 0，link-only 0）。
