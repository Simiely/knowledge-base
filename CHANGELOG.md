# CHANGELOG

## v1.2.1 — 2026-11-16

规范 `2.1.1`、repo-kit `2.5.1`。两处「规范允许、工具不允许」的修复，均由 `dufs-gui` 接入的 dry-run 暴露。

### 修复

- `generate.py` 只生成 `taxonomy.generated_files` 声明的文件。此前它无条件重写 `AGENTS.md`，
  手写 AGENTS 的仓库永远 `GENERATED_STALE`——与 REPO_STANDARD 1.1/4 直接冲突。
- 模板 CI 显式安装文档依赖（`PyYAML` / `markdown-it-py` / `jsonschema`），不再
  按仓库的 `requirements.txt` 装。代码仓的 `requirements.txt` 是运行/构建清单
  （`dufs-gui` 只有 `pyinstaller==6.22.3`），照装会在 `check_repo.py` 报 `DEPENDENCY_MISSING`。
- `monorepo` 的 `include` 补 `CHANGELOG.md`：它在 `exempt_basenames` 里却不在 `include` 里，
  等于四件套中的 CHANGELOG 从不参与链接检查。

### 迁移

- 首个完整用户：`dufs-gui`（`bd399e3`）。`REPO CHECK PASS`（pages=11）、`GENERATE CHECK PASS`、
  `KIT LOCK PASS`（v2.5.1, spec=2.1.1），同时纠正 8 处文档与代码相反的表述。
- 其余 11 个已接入仓库无需改动；要改手写 AGENTS 的，把 `AGENTS.md` 从 `generated_files` 去掉即可。

## v1.2.0 — 2026-11-16

规范升 `2.1.0`、repo-kit 升 `2.5.0`。主题是**让已写下的条款真的生效**，不新增概念。

起因：在 `dufs-gui` 上做接入审计时发现四项完成定义可被「空壳」满足——结构全绿、
内容与代码相反（README 承诺了仓库无法产出的产物、AGENTS 教的实现已被替换、版本号硬编码
13 处且已错一处）。随后抽样 3 个已接入仓库复核，定位到的问题不是条款不够，而是回路没通。

### 变更

- `check_repo.py`：`LINK_DIR` 不再产出告警。指向**存在**的目录是合法写法（GitHub 渲染目录列表），
  真断链由 `LINK_BROKEN` 覆盖。实测该项在 blender-tips 常驻 170 条、知识库自身 4 条（都在
  README 的仓库导航上），`PASS` 照旧——常驻 WARN 会训练出「WARN 可以无视」。
- `check_repo.py`：`SPEC_VERSION` 升至 `2.1.0`。
- `monorepo` profile：`include` / `entry_files` 补 `DEVELOPMENT.md`。此前四件套之一
  **从不进扫描范围**，「> 200 行拆 docs/」的阈值等于没写。
- 模板 CI（`monorepo` / `skills`）：加 `fetch-depth: 0` 与 PR-only 的 `--changed-since`。
  缺这两处时 `sources.json` 的 `co_change` 永不触发——kit 里唯一能发现「代码改了文档没改」
  的机制，在 11 个已接入仓库里全部没跑起来。`EverythingCmdPal` 是唯一手工绕过此缺失的。
- `REPO_STANDARD.md`：1.3 补 co-change 命令与前提，1.5 补 `fetch-depth` / `paths:` /
  「WARN 不是免死金牌」的判定口径，§6 接入清单补「taxonomy 必须覆盖四件套」。
- `单项目规范`：`spec.json` → `2.1.0`，新增 `migrations/v2.1.0.md`，README 的完成定义段
  补「四项全绿的含义要说准」。

### 自检

- 知识库自身（`link-only`）：`REPO CHECK: PASS`，**WARN 4 → 0**（4 条全是 README 目录导航的 `LINK_DIR`）。
- kit：49 项单测 OK；`drift_probe` 8/8；`GENERATE CHECK: PASS`。
- 脚手架 smoke：三个 profile 全部 `PASS` + `GENERATE CHECK: PASS`；反向对照注入
  `DEVELOPMENT.md` 断链后如期报 `LINK_BROKEN`。
- 已接入仓库跑新校验器：`SPEC_OUTDATED` 每仓库恰好 1 条（提示可迁移），LINK_DIR 归零。

### 迁移

- 11 个已接入仓库按 [`migrations/v2.1.0.md`](模板库/单项目规范/migrations/v2.1.0.md)
  分两步升级：重装 kit、taxonomy 补 `DEVELOPMENT.md`。未升级者行为不变。

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
