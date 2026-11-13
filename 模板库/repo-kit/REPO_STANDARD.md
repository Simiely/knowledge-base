# REPO_STANDARD.md — 仓库统一标准 v2.0.0

日期：2026-11-13
配套工具：repo-kit v2.4.0

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
`tools/repo-kit/`。`drift_probe.py` 只存在于 kit 源仓库，不随消费仓库分发。

### 1.3 固定命令

```bash
python tools/repo-kit/check_repo.py --root .
python tools/repo-kit/generate.py --root . --check   # 仅生成型 profile
pwsh tools/update-repo-kit.ps1 -Check                # 版本锁
```

退出码：`0` 通过，`1` 有不变量失败，`2` 用法/依赖错误。
输出：默认文本；`--json`、`--format sarif|github` 对所有仓库一致。

### 1.4 版本锁

`schema/kit.lock.json` 至少包含：

```json
{
  "kit": "repo-kit",
  "version": "2.4.0",
  "spec_version": "2.0.0",
  "profile": "monorepo",
  "installed": "2026-11-13",
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

同一套模板，至少三步：

1. 安装 `requirements.txt`。
2. 跑 `check_repo.py`（以及生成型 profile 的 `generate.py --check`）。
3. 跑 `update-repo-kit.ps1 -Check`。

CI 细节约定：

- 内部链接检查（lychee 等）必须排除 `_template.md` 这类占位文件，否则模板里的示例链接会被当断链。
- SARIF 上传在未启用 GitHub Advanced Security 的私有仓库会报 `Resource not accessible`；
  上传步骤用 `continue-on-error: true`，不阻塞文档检查本身。

## 2. Profiles

| Profile | 适用 | 检查内容 | 生成 |
|---|---|---|---|
| `monorepo` | 代码仓库 / 多插件仓库 | frontmatter、链接/锚点、真源、新鲜度、生成产物 | 是 |
| `skills` | 技能仓库 | SKILL.md 契约、references 链接、页面契约 | 是 |
| `knowledge` | 知识库 / 文档仓 | 页面契约、pitfall、关系、新鲜度 | 是 |
| `link-only` | 有自建内容管线的知识库 | 只查链接/锚点、入口与技能契约 | 否 |

`link-only` 用于 rive-tips 这类仓库：文档不带 frontmatter，内容真源由它自己的
`tools/sync-skill.ps1 -Check` 保证；repo-kit 只补链接与入口检查。

## 3. 当前仓库清单

| 仓库 | Profile | 工具版本 | 说明 |
|---|---|---|---|
| EverythingCmdPal | `monorepo` | 2.4.0 | 插件文档按 include 白名单扫描 |
| home-inventory | `knowledge` | 2.4.0 | 含 pitfall 页 |
| design-tips | `knowledge` | 2.4.0 | 通用设计技巧条目 |
| weread-budget-extension | `knowledge` | 2.4.0 | MV3 + 平台版双端 |
| workbuddy-skills | `skills` | 2.3.2 | SKILL.md 独立契约 |
| rive-tips | `link-only` | 2.3.2 | 保留 docs → references 快照同步 |

## 4. 不统一的内容模型

以下差异是设计选择，不是欠债：

- 词表 `topics`、文档语言与文件名（中文文件名合法）。
- `AGENTS.md` 是生成还是手写。
- 坑位是独立 `kind: pitfall` 页，还是像 rive-tips 那样用一张总表。
- 内容真源管线：rive-tips 的 docs → skill references 快照同步优先于通用规则。

## 5. 升级流程

1. 在 kit 源仓库改完并跑通 `check_repo`、`generate --check`、`drift_probe`、单元测试。
2. 升 `schema/taxonomy.json` 的 `version`，写 CHANGELOG。
3. 在每个仓库运行：
   ```powershell
   pwsh tools/update-repo-kit.ps1 -Source <kit 路径> -Profile <profile>
   pwsh tools/update-repo-kit.ps1 -Check
   python tools/repo-kit/check_repo.py --root .
   python tools/repo-kit/generate.py --root . --check
   ```
4. 更新该仓库 `schema/taxonomy.json` 的 `version` 与新增词表（如 `pitfall`）。
5. 提交时把 `schema/kit.lock.json` 一起带上。

## 6. 新仓库接入清单

- [ ] 建 `tools/repo-kit/`，放 `check_repo.py`、按需 `generate.py`
- [ ] 建 `schema/`，写 `taxonomy.json`、`sources.json`
- [ ] 从 kit 复制 `frontmatter.schema.json`（有 skills 时再复制 `skills.schema.json`）
- [ ] 复制 `tools/update-repo-kit.ps1`，选择 profile，生成 `kit.lock.json`
- [ ] 加 `requirements.txt`：PyYAML、markdown-it-py、jsonschema
- [ ] 加 CI：check + generate --check（如适用）+ lock check
- [ ] 在 `AGENTS.md` 写清入口、命令与边界
