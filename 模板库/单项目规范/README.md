# 单项目（单仓库）文档规范 · 使用说明

> 规范版本 v2.1.4 · 2026-11-18 · 变更见 [CHANGELOG.md](CHANGELOG.md)

> 让**单个仓库**的内容模块化、清晰合理、可快速提取，并与 knowledge-base 无缝衔接。
> 适用：所有个人项目仓库（AE 脚本 / C4D 插件 / Blender 插件 / Web 项目 / 小程序）。
> 本模块位置：`单项目规范/`，与多项目沉淀（解决方案/ 等）并列，见根目录 README「一套方案，两个层级」。

## 一、核心原则（4 条）

1. **按"给谁看"分层**：默认 4 个文件，各管一类读者，不混装
2. **超阈值才拆分**：不提前设计目录，内容多了自然长成树（与 knowledge-base 同一哲学）
3. **拆分后主文件 = 门面 + 索引**：主文件永远精简，细节用链接引用
4. **问题记录模板与 knowledge-base 完全一致**：提炼到经验库时零转换搬运

## 二、四个默认文件

| 文件 | 给谁看 | 放什么 | 更新时机 | 拆分阈值 |
|---|---|---|---|---|
| `README.md` | 用户 / 访客 | 项目是什么、安装、快速开始、截图 | 发版时 | > 150 行 → `docs/使用指南.md`、`docs/API.md` |
| `AGENTS.md` | **AI / 未来的你**（自动加载） | 技术栈精确版本、关键坑、约定、常用命令 | 踩坑 / 约定变化时 | > 150 行 → `rules/*.md`（@引用） |
| `DEVELOPMENT.md` | 开发者（自己） | 架构说明、关键问题与方案 | 每次改动 | > 200 行 → `docs/架构.md`、`docs/问题记录/` |
| `CHANGELOG.md` | 所有人 | 版本变更记录 | 发版时 | 不拆，按版本分节 |

`docs/` 目录是**长出来的**（触发拆分才建），不是项目一开始就建的。

## 三、机器层与模板（repo-kit）

4 文件是**人层**；每个新仓库再加一层机器校验，防止链接腐烂、契约漂移。

| 层 | 负责 | 产物 |
|---|---|---|
| 人层 | 4 文件与生长式拆分 | `README.md` / `AGENTS.md` / `DEVELOPMENT.md` / `CHANGELOG.md` |
| 机器层 | 内容契约、链接/锚点、真源、生成产物、版本锁 | `tools/repo-kit/`、`schema/`、`schema/kit.lock.json`、CI |

**文件归属决定可改性。** 同一个仓里四类文件的字节来源不同，动手前先查这一栏。
「下游的格式规则」（BOM、行尾、缩进、键序、格式重排……）**默认只作用于后两类**：

| 文件类别 | 怎么判定 | 谁定字节 | 谁校验 | 下游能否改 |
|---|---|---|---|---|
| kit 托管 | `schema/kit.lock.json` 的 `files` 键 | 上游 repo-kit | 上游测试 + 下游 `update-repo-kit.ps1 -Check` 比哈希 | ❌ 改了即 `KIT LOCK: FAIL` |
| 生成物 | `schema/taxonomy.json` 的 `generated_files` | 生成器 | `generate.py --check` | ❌ 手改会被覆盖或报过期 |
| 仓自有配置 | `schema/taxonomy.json`、`.gitattributes` 等 | 下游 | `check_repo.py` | ✅ |
| 仓自有内容 | `docs/**`、根 4 文件、脚本 | 下游 | `check_repo.py` + 仓自有 lint | ✅ |

为什么要写死这张表：2026-11-19 在 `video-upscale-deploy` 撞到过一次——仓里要求「所有 `.ps1` 带 BOM」，
而 `tools/update-repo-kit.ps1` 被 lock 按字节锁住，加 BOM 就 `KIT LOCK: FAIL`。
**两条规则同时成立，规则就永远不可能绿**——这不是欠债，是作用域没划清。

划清之后各管各的：kit 文件的编码由**上游**负责（上游测试自己的发行物），下游只校验自己写的文件。
真要改 kit 文件的字节，只能改上游并在同一次提交里刷新锁，**不要在仓里就地改**——
业界同类机制（pip 的 `tools/vendoring/patches/`、npm 的 `patchedDependencies`）都要求
「改动显式记录 + 哈希进锁」，就地改的下场是下次安装被覆盖或 CI 直接红。

规范版本单独标记：最新版本见 [`spec.json`](spec.json)，每个仓库通过 `schema/kit.lock.json` 的
`spec_version` 声明自己按哪一版整理。任何程序读这一个字段即可判断版本。

**全局盘点**用 `audit-spec.ps1`，它同时查五件事（任一不满足即退出码 1；仅补丁版本落后只显示、不计入）：

```powershell
pwsh 模板库/单项目规范/audit-spec.ps1 -ReposRoot <仓库父目录>,<单个仓库路径>
# 加 -Json 输出机器可读结果
```

| 检查 | 抓什么 |
|---|---|
| `spec` / `state` | `spec_version` 主/次版本落后、缺失、格式非法或高于校验器；**仅补丁落后标 `behind-patch`，只显示不计 issues** |
| `skew:a-vs-b` | `taxonomy.version` 与 `kit.lock.version` 不一致（只改了一边） |
| `ci-missing` / `ci-no-fetch-depth` | CI 没接 `check_repo`；或用了 `--changed-since` 却没收全历史 |
| `baseline:N` | 还留着 `schema/check-baseline.json`（规则静音后它是死配置） |
| `legacy-keys` / `legacy-nokey` | taxonomy 仍是旧豁免键，或新旧都没有 |

这个脚本**不随仓库分发**，改它不产生任何锁哈希变更。

**新建仓库不要手搭目录**：

```powershell
pwsh 模板库/新项目模板/新建仓库.ps1 -Name my-tool -Profile monorepo -Target ..\my-tool
```

四个 profile：

- `monorepo`：代码仓库，带 `docs/` + 生成索引
- `knowledge`：以文档为主的知识仓/应用仓，页面带 frontmatter 契约 + pitfall/freshness 检查（脚手架见 repo-kit 上游 `knowledge` profile；`新建仓库.ps1` 暂只支持另外三个）
- `skills`：技能仓库，带 `SKILL.md` 契约
- `link-only`：已有内容管线的文档仓，只查链接/锚点，不要求 frontmatter

**完成定义**（四项全绿才算整理完）：

```text
REPO CHECK: PASS
GENERATE CHECK: PASS   # link-only 不适用
KIT LOCK: PASS
CI: PASS
```

若仓里有**自有的机器检查**（如 `tools/check_text.py`、`pytest`、`guardrails lint-manual`），
它同样是完成定义的一部分，而且**必须接进 CI**。
只在 `AGENTS.md` 的「常用命令」里列着、实际没人跑的检查等于没有——2026-11-19 实测：
`video-upscale-deploy` 的 BOM 检查红了半年，因为既不在 CI 里，也不在上面的四项里。

机器层只保结构、链接、真源与新鲜度；语义真假仍靠人审。

**四项全绿的含义要说准**：它证明「结构整齐、链接可达、生成物不过期」，
**不证明「文档说的是真的」**。v2.1.0 因此修了两处会让它名不副实的地方——
`DEVELOPMENT.md` 是否真的在扫描范围内、`--changed-since` 是否真的传给了校验器。
两者缺任一，四项依然会全绿，但覆盖率是空的。

`PASS` 只统计 `ERROR`；`WARN` 不计入判定。因此单仓库常驻几十上百条的告警项等于失效，
应当修规则或显式降级，不要长期挂着（v2.1.0 的 `LINK_DIR` 即此类）。

**直接复制提示词**：[新建仓库 / 整理已有仓库](../提示词模板.md)。

## 四、怎么开始用

**新项目**：不要手建 4 个文件，直接用 [`模板库/新项目模板/新建仓库.ps1`](../新项目模板/新建仓库.ps1)
选一个 profile；脚本会生成 4 文件 + 机器层，并跑通检查。

**已有仓库**（多数情况）：
1. 补一个 `AGENTS.md`（核心规则，第 5 节模板）
2. 把 DEVELOPMENT.md 里的历史问题，挑重要的改写成统一格式（第 6 节）
3. 需要机器校验时，按 [`新项目模板/README.md`](../新项目模板/README.md) 安装对应 profile 的 `tools/repo-kit/` 与 CI
4. 其余文件保持原样，不用推翻重来

## 五、AGENTS.md 怎么写

只写**代码里看不出的**信息，核心约束 150 行内；细节放 `rules/` 目录，用 @引用按需读取（避免 AI 每次加载过多上下文）。行数按文件总行数（`wc -l`）计。

```markdown
# AGENTS.md · 项目规则

## 技术栈
- 精确版本：如 AE 2026 中文版 + ExtendScript（ES3）
  （语法限制速查可放知识库 `速查表/`，此处留链接占位）

## 关键坑（3~5 条，越具体越好）
- 示例：某个 API 在中文版取不到值 → 用候选 fallback 列表
- 示例：代码改动不生效 → 先清对应工具缓存

## 约定
- UI 标签用中文；注释用中文；.jsx 单文件交付

## 常用命令
- 构建 / 测试 / 发布：按项目实际写

## 详细规则（按需 @引用）
- @rules/技术栈.md  @rules/常见坑.md
```

## 六、DEVELOPMENT.md 怎么写

结构固定三块：**项目概览 → 架构说明 → 关键问题与方案**。

关键问题**一坑一篇**，格式与 knowledge-base 完全一致（提炼零转换）：

```markdown
## 问题：ScriptUI 布局宽度失控（380px）

**TL;DR**：alignChildren="fill" + edittext alignment="fill" 三重拉伸叠加导致宽度失控。

- 问题：三处 fill 叠加，宽度被撑到 380px
- 根因：alignChildren 与 alignment 同向拉伸叠加
- 解决：去掉其中一重 fill，改用显式尺寸
- 预防：布局写完先检查 fill 叠加次数
```

## 七、生长式拆分规则（什么时候拆）

| 触发条件 | 怎么拆 | 主文件保留什么 |
|---|---|---|
| `README.md` > 150 行 | 拆出 `docs/使用指南.md`、`docs/API.md` | 简介 + 安装 + 快速开始 + 文档索引 |
| `AGENTS.md` > 150 行 | 拆出 `rules/技术栈.md`、`rules/常见坑.md` | 核心约束 + @引用列表 |
| `DEVELOPMENT.md` > 200 行 | 拆出 `docs/架构.md`、`docs/问题记录/`（一坑一篇） | 架构总览 + 问题索引 |
| `CHANGELOG.md` | 天然按版本分节，**不拆** | — |

拆分后主文件变成"门面 + 索引"，所有细节用链接引用，读者从索引直达，不在长文里翻找。

> 量纲说明（2.1.4）：`AGENTS.md` 的阈值旧写作「150 词」，但按词数实测 97 个仓里
> **96 个超标**（中位数约 409 词），等于没人能执行；按行数只有 3 个超标。词数在编辑器里
> 也看不出，行数用 `wc -l` 即可机械核对，故统一为行。

## 八、与用户知识库的衔接（提炼管道）

```
单仓库踩坑 → DEVELOPMENT.md / docs/问题记录/ 记录（同一模板）
                    ↓ 项目收尾 / 季度回顾，挑跨项目通用的
           你的用户库/解决方案/ 或 速查表/
```

- **提炼时机**：项目收尾或季度回顾，挑"别的项目也会遇到"的问题复制过去
- **模板一致**：复制即用，不用重写格式
- **AGENTS.md 联动**：单仓库验证有效的"关键坑"，定期同步进用户库的速查表

## 九、每次改动的动作清单

| 场景 | 动作 |
|---|---|
| 改了功能 | DEVELOPMENT.md 追加/更新对应说明 |
| 踩坑并解决 | 写进问题记录（一坑一篇）→ 收尾时提炼 |
| 发版 | README（如有变更）+ CHANGELOG 加版本节 |
| 约定/坑变化 | AGENTS.md 更新，或新增 rules/ 文件 |

## 十、文档基线（断点续传）

**为什么**：仓库重写完成后，必须留下"基线标记"（日期 + commit hash），否则以后更新了没人记得重写到哪，可能从头重写。

**标注位置**：每个仓库的 `AGENTS.md` 顶部（AI 进仓库第一眼看的地方）：

```markdown
# AGENTS.md · 项目规则

> 📌 **文档基线**：YYYY-MM-DD（commit `abcdef1`）完成四件套重写
> **更新文档/代码后，请更新此行**（日期 + 新 commit hash），并在 CHANGELOG 追加版本
```

**为什么不只标日期**：日期是"天"级，同一天多个 commit 分不清；**commit hash 是"提交"级**，可用 `git diff <基线hash>` 精确对比"上次重写后改了什么"——断点续传的关键能力。

**维护流程**（改仓库后四步）：

```
① 该仓库 CHANGELOG.md 追加版本节
② AGENTS.md 基线行更新（新日期 + 新 commit hash）
③ knowledge-base/仓库盘点表.md 回填新 hash
④ 推送
```

**总表**：你的用户库根目录的 `仓库盘点表.md`（可选,模板见 [`初始化说明.md`](../初始化说明.md) 第四节）是全部仓库的断点索引（领域/四件套状态/重写日期/基线 commit）。更新仓库后必须回填。

**核对方法**：想确认某仓库"重写后改了什么"，用 `git log --oneline <基线hash>..HEAD` 或 `git diff <基线hash> HEAD`。
