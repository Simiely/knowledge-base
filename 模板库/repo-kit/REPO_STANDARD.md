# REPO_STANDARD.md — 仓库统一标准 v2.1.0

日期：2026-11-16
配套工具：repo-kit v2.5.3

本标准的目的是让多个仓库**用同一套契约和工具链验收**，而不是把所有仓库改成同一种内容结构。
统一的是「怎么检查」，不是「写什么」。

## 1. L0 契约（所有仓库必须一致）

### 1.1 唯一入口

每个仓库根目录必须有 `AGENTS.md`。它可以是生成文件，也可以是手写正文，但必须是人与 AI 的第一入口。

### 1.2 固定工具位置

```
tools/
├── repo-kit/
│   ├── check_repo.py        # 必须
│   └── generate.py          # 使用生成表面的 profile 必须
└── update-repo-kit.ps1      # 必须，版本锁与升级
schema/
├── taxonomy.json            # 仓库自己的词表与扫描配置
├── frontmatter.schema.json  # kit 提供，不手改
├── skills.schema.json       # 有 skills profile 时由 kit 提供
├── sources.json             # 仓库自己的真源映射
└── kit.lock.json            # kit 版本、profile 与文件哈希
```

不再把 kit 脚本放在 `scripts/`；`scripts/` 只放仓库自己的业务脚本。

例外：**kit 源仓库自身**仍把源脚本放在 `scripts/`，它是分发源；消费仓库一律安装到
`tools/repo-kit/`。`drift_probe.py` 与 `release.py` 只存在于 kit 源仓库，不随消费仓库分发。

### 1.3 固定命令

```bash
python tools/repo-kit/check_repo.py --root .
python tools/repo-kit/generate.py --root . --check   # 仅生成型 profile
pwsh tools/update-repo-kit.ps1 -Check                # 版本锁
```

PR 里再跑一次带变更集的检查（同 PR co-change 的唯一触发方式）：

```bash
python tools/repo-kit/check_repo.py --root . --changed-since origin/main
```

不带 `--changed-since` 时变更集为空，`sources.json` 的 `co_change` 与
`TRUTH_DOCS_NOT_UPDATED` 整段跳过——「真源改了文档没改」不会被发现。
`--changed-since` 依赖 git 历史，CI 里必须 `fetch-depth: 0`。

退出码：`0` 通过，`1` 有不变量失败，`2` 用法/依赖错误。
输出：默认文本；`--json`、`--format sarif|github` 对所有仓库一致。

### 1.4 版本锁

`schema/kit.lock.json` 至少包含：

```json
{
  "kit": "repo-kit",
  "version": "2.5.3",
  "spec_version": "2.1.2",
  "profile": "monorepo",
  "installed": "2026-11-16",
  "files": {
    "tools/repo-kit/check_repo.py": "sha256:...",
    "schema/frontmatter.schema.json": "sha256:..."
  }
}
```

`spec_version` 是该仓库所遵循的**规范版本**（见 `../单项目规范/spec.json`），
与工具版本 `version` 独立；任何程序读这一个字段即可判断仓库按哪一版规范整理。

升级只能通过 `update-repo-kit.ps1`，禁止手工复制脚本；`-Check` 哈希不一致即失败。
锁里的哈希按 **LF 归一化** 计算，Windows 的 CRLF checkout 与 Linux CI 得到同一个值。

### 1.5 CI

**按「有没有真源」分两档**，不要一套抄到底。判据：`schema/sources.json` 存在且 `code` 非空。

**A 档 · 有真源（`monorepo` / `skills`）**

1. 安装文档依赖（**显式装，不要 `-r requirements.txt`**：代码仓的这份文件是运行/构建清单）。
2. `check_repo.py --root .`
3. PR 事件：`check_repo.py --root . --changed-since origin/<base>`（见 1.3）。
4. `generate.py --root . --check`
5. `pwsh tools/update-repo-kit.ps1 -Check`

**B 档 · 无真源（`knowledge` / `link-only`）**

1. `python -m pip install -r requirements.txt`（这类仓库的 `requirements.txt` 就是文档依赖）。
2. `check_repo.py --root .`
3. `generate.py --root . --check`（link-only 不适用）
4. `pwsh tools/update-repo-kit.ps1 -Check`

不需要 `fetch-depth: 0` 与 `--changed-since`——没有 `sources.json` 时它们是空转，
只会增加一个「看起来在检查」的假动作。

CI 细节约定：

- A 档的 `actions/checkout` 必须 `fetch-depth: 0`，否则 `--changed-since` 拿不到基分支历史，
  变更集退化为空集，且**不会报错**——这是「检查写了但从不生效」的典型形态。
- PR 的 `paths:` 过滤器要包含 `DEVELOPMENT.md`、`CHANGELOG.md`，否则只改门面文件的
  PR 不会触发文档检查。
- 内部链接检查（lychee 等）必须排除 `_template.md` 这类占位文件，否则模板里的示例链接会被当断链。
- SARIF 上传在未启用 GitHub Advanced Security 的私有仓库会报 `Resource not accessible`；
  上传步骤用 `continue-on-error: true`，不阻塞文档检查本身。
- `PASS` 只代表 `ERROR=0`，**WARN 不计入判定**。若某条规则在单仓库常驻几十上百条
  （v2.4.0 的 `LINK_DIR` 即如此），它已经失效：要么修正规则，要么明确降为 INFO，
  不要靠「反正只是 WARN」长期挂着——那会训练出无视 WARN 的习惯，连带淹掉真信号。

### 1.6 baseline 的生命周期

baseline 是**临时脚手架**，不是长期配置：它压制的是「已知但还没修」的问题。

- 进入：存量仓库首接入时 `--write-baseline schema/check-baseline.json`（建议 `--baseline-format v2`）。
- 退出：规则收紧或静音后，旧条目会变成压制「已消失问题」的死配置。此时跑

  ```bash
  python tools/repo-kit/check_repo.py --root . --prune-baseline schema/check-baseline.json
  ```

  它按**全量结果**重算，删掉不再命中的条目并打印清单。
- 清算：条目降到 0 就**删文件**并去掉 CI 的 `--baseline` 参数。

为什么写进规范：`blender-tips` 的 baseline 有 170 条，全是 v2.5.0 已静音的 `LINK_DIR`。
一份压制「已消失问题」的 baseline 比没有更危险——它让人以为还有待办，也掩盖真正的新增项。

## 2. Profiles

| Profile | 适用 | 检查内容 | 生成 |
|---|---|---|---|
| `monorepo` | 代码仓库 / 多插件仓库 | frontmatter、链接/锚点、真源、新鲜度、生成产物 | 是 |
| `skills` | 技能仓库 | SKILL.md 契约、references 链接、页面契约 | 是 |
| `knowledge` | 知识库 / 文档仓 | 页面契约、pitfall、关系、新鲜度 | 是 |
| `link-only` | 有自建内容管线的知识库 | 只查链接/锚点、入口与技能契约 | 否 |

`link-only` 用于 rive-tips 这类仓库：文档不带 frontmatter，内容真源由它自己的
`tools/sync-skill.ps1 -Check` 保证；repo-kit 只补链接与入口检查。它的摘要显示 `pages=0`，
表示没有内容页，不代表没检查——链接与入口仍会报错。

`skills` 仓如果共享仓库根的 `scripts/`、`docs/`（安装时把 `skills/*` 与它们平铺到同一层），
要在 taxonomy 里设 `skills.install_prefix`（仓库里多出的那一层，通常是 `"skills"`）；
不设则按技能目录自包含处理。

四个 profile 的骨架都在 `新项目模板/profiles/`；`knowledge` 自模板 **1.1.0** 起才提供
（此前规范列了它、模板却没有，导致这类仓库的 CI 只能手写）。

## 3. 当前仓库清单

| 仓库 | Profile | 工具版本 | 说明 |
|---|---|---|---|
| EverythingCmdPal | `monorepo` | 2.4.0 | 插件文档按 include 白名单扫描 |
| taskbar-drawer | `monorepo` | 2.4.0 | 单应用；AGENTS 由模板生成，DEVELOPMENT 保持根文档 |
| blender-render-console | `monorepo` | 2.4.0 | Python GUI；450 项单测进 CI；走查文档 3 篇 |
| procedural-drawing-lab | `monorepo` | 2.4.0 | 零依赖静态实验场；docs 仅导航，实验清单以 README 为准 |
| MultiSwitch | `monorepo` | 2.4.0 | 双产品：Python 切换器 + Node 积分工具；版本口径各自独立；AGENTS 已瘦身，运维/报告/安全文档归入 docs/ |
| home-inventory | `knowledge` | 2.4.0 | 含 pitfall 页 |
| design-tips | `knowledge` | 2.4.0 | 通用设计技巧条目 |
| blender-tips | `knowledge` | 2.4.0 | 43 篇 Blender 技巧页；AGENTS 由模板生成 |
| weread-budget-extension | `knowledge` | 2.4.0 | MV3 + 平台版双端 |
| workbuddy-skills | `skills` | 2.4.0 | SKILL.md 独立契约；15 个技能（13 在用 + 2 归档） |
| rive-tips | `link-only` | 2.4.0 | 保留 docs → references 快照同步 |

上表是**各仓库当前安装的工具版本**，不是应有版本。v2.5.0 发布后，未升级的仓库会收到一条
`SPEC_OUTDATED`（WARN，每仓库一条，提示有迁移可用）；升级步骤见
`../单项目规范/migrations/v2.1.0.md`。

## 4. 不统一的内容模型

以下差异是设计选择，不是欠债：

- 词表 `topics`、文档语言与文件名（中文文件名合法）。
- `AGENTS.md` 是生成还是手写。
- 坑位是独立 `kind: pitfall` 页，还是像 rive-tips 那样用一张总表。
- 内容真源管线：rive-tips 的 docs → skill references 快照同步优先于通用规则。

## 5. 升级流程

1. 在 kit 源仓库改完并跑通 `check_repo`、`generate --check`、`drift_probe`、单元测试。
2. 发版用脚本，不要手改版本号：

   ```bash
   python scripts/release.py --version 2.7.0          # 同步 taxonomy + 脚本 + 跑测试
   python scripts/release.py --version 2.7.0 --min-kit 2.7.0   # 需要抬 spec 的 min_kit 时
   python scripts/release.py --check                  # 只校验（可进 CI）
   ```

   **版本的唯一定义处**是 `schema/taxonomy.json` 的 `version`——安装器与脚手架都读它，
   `check_repo.py` 的 `KIT_VERSION` 由 `release.py` 写入，`generate.py` 只引用不拥有。
   早先的 `VERSION` 文件已删除：它和 `taxonomy.version` 分别喂给脚手架与安装器，
   两者不一致时同版本 kit 会产出两个版本号，且无任何检查能发现。

3. 跨版本号的一处仍需手工确认：`spec.json` 的 `version` ↔ `check_repo.py` 的 `SPEC_VERSION`
   （规范版本，不是 kit 版本）。漏改会立刻 `SPEC_NEWER`，自己的仓库先红。
4. 在每个仓库运行：
   ```powershell
   pwsh tools/update-repo-kit.ps1 -Source <kit 路径> -Profile <profile>
   pwsh tools/update-repo-kit.ps1 -Check
   python tools/repo-kit/check_repo.py --root .
   python tools/repo-kit/generate.py --root . --check
   ```
5. 更新该仓库 `schema/taxonomy.json` 的 `version` 与新增词表（如 `pitfall`）。
6. 提交时把 `schema/kit.lock.json` 一起带上。

## 6. 新仓库接入清单

- [ ] 建 `tools/repo-kit/`，放 `check_repo.py`、按需 `generate.py`
- [ ] 建 `schema/`，写 `taxonomy.json`、`sources.json`
- [ ] 从 kit 复制 `frontmatter.schema.json`（有 skills 时再复制 `skills.schema.json`）
- [ ] 复制 `tools/update-repo-kit.ps1`，选择 profile，生成 `kit.lock.json`
- [ ] 文档依赖**不要**写进仓库的 `requirements.txt`：模板 CI 已显式安装
      `PyYAML` / `markdown-it-py` / `jsonschema`；仓库自己的 `requirements.txt`
      只放运行/构建依赖（代码仓库常见只有打包工具）
- [ ] `taxonomy.json` 的 `include` 与 `entry_files` 覆盖**四件套**（`README` / `AGENTS` /
      `DEVELOPMENT` / `CHANGELOG`），否则四件套的体量阈值永远不会被检查
- [ ] `taxonomy.json` 的 `generated_files` 决定**生成范围**：`AGENTS.md` 打算手写就把它
      从这个清单里去掉（`generate.py` 自 2.5.1 起尊重该清单）；打算生成就必须同时有
      `schema/agents.template.md`。两者都不做会报 `GENERATED_BLOCKED` 并拒绝写入（2.7.4 起）
- [ ] 加 CI：check + `--changed-since`（PR 事件）+ generate --check（如适用）+ lock check
- [ ] 在 `AGENTS.md` 写清入口、命令与边界
