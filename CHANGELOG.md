# CHANGELOG

## v1.1.0 — 2026-11-13

规范版本可被机器读取；知识库自身与四个消费仓库同步升级到 repo-kit 2.4.0。

### 新增

- `模板库/单项目规范/spec.json`：规范版本真源（当前 `2.0.0`），配套 `CHANGELOG.md` 与 `migrations/v2.0.0.md`。
- `模板库/单项目规范/audit-spec.ps1`：扫描各仓库 `schema/kit.lock.json` 的 `spec_version`，输出 `current / behind / v1 / legacy / invalid / newer`，支持 `-Json`。
- 各仓库 `schema/kit.lock.json` 新增 `spec_version` 字段，任意程序读该字段即可判断按哪一版规范整理。
- `用户库/仓库盘点表.md` 新增「规范版本」列，并回填四个仓库的文档基线。

### 变更

- vendored `模板库/repo-kit/` 升级到 `2.4.0`：安装器写入 `spec_version`，`check_repo.py` 新增 SPEC 校验（缺字段 WARN；格式非法、主版本落后、高于校验器支持 ERROR；次版本落后 WARN）。
- 知识库自身 `link-only` kit 从 2.3.2 升级到 2.4.0，锁内写入 `spec_version: 2.0.0`。
- design-tips / home-inventory / EverythingCmdPal / weread-budget-extension 升级到 kit 2.4.0，`spec_version` 均为 `2.0.0`。

### 验证

- 知识库自检：`REPO CHECK: PASS`（4 条既有 LINK_DIR WARN）、`KIT LOCK: PASS (v2.4.0, spec=2.0.0, profile=link-only)`。
- 四个消费仓库三项检查全部 PASS。

## v1.0.0 — 2026-11-12

建立「规范 + 新项目模板 + repo-kit」三层上游。

### 新增

- `模板库/单项目规范/`：保留 4 文件模型，新增机器层（repo-kit、版本锁、CI）与完成定义。
- `模板库/新项目模板/`：`base/` + `monorepo` / `skills` / `link-only` 三个 profile，
  以及 `新建仓库.ps1`（复制、替换占位符、安装 kit、生成、检查）。
- `模板库/提示词模板.md`：新建仓库与整理已有仓库两段简短提示词；只指向规范仓库，不写死路径/名称，缺信息先提问。
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
