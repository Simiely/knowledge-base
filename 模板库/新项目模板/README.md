# 新项目模板 · 复制即用的仓库骨架

> 开新仓库时不用从零搭目录：选一个 profile，跑一条命令，得到一个能直接通过检查的干净骨架。
> 规范本身见 [单项目规范](../单项目规范/README.md)；机器工具来源见 [repo-kit](../repo-kit/README.md)。

## 三个 profile

| Profile | 适用 | 生成后包含 |
|---|---|---|
| `monorepo` | 代码仓库 / 多插件仓库 | 4 文件 + `docs/` + 生成索引 + CI |
| `skills` | 技能仓库 | 4 文件 + `skills/` 契约 + references 只查链接 + CI |
| `link-only` | 已有内容管线的文档仓 | 4 文件 + 链接/锚点检查 + CI，不要求 frontmatter |

三个 profile 都带：`README.md`、`AGENTS.md`、`DEVELOPMENT.md`、`CHANGELOG.md`、
`schema/`、`tools/repo-kit/`、`tools/update-repo-kit.ps1`、`requirements.txt`、`.gitignore`。

## 怎么用

新建时可以直接复制 [提示词模板 A](../提示词模板.md) 交给 AI，或手动执行下面的命令。

```powershell
pwsh 新建仓库.ps1 -Name my-tool -Profile monorepo -Target ..\my-tool
pwsh 新建仓库.ps1 -Name my-skills -Profile skills -Target ..\my-skills
pwsh 新建仓库.ps1 -Name my-notes -Profile link-only -Target ..\my-notes
```

参数：

| 参数 | 必填 | 说明 |
|---|---|---|
| `-Name` | 是 | 仓库名，只允许字母/数字/`.`/`_`/`-` |
| `-Profile` | 是 | `monorepo` / `skills` / `link-only` |
| `-Target` | 是 | 目标目录；非空时需加 `-Force` |
| `-Owner` | 否 | 默认 `simiely`，写入 frontmatter 的 `owner` |
| `-Summary` | 否 | 写入 README 的一句话简介 |
| `-SkipGenerate` | 否 | 只复制，不跑生成器 |
| `-SkipCheck` | 否 | 只复制，不跑检查（不推荐） |

脚本会：

1. 复制 `base/` + `profiles/<profile>/`
2. 替换 `{{PROJECT_NAME}}`、`{{OWNER}}`、`{{DATE}}`、`{{PROFILE}}`、`{{KIT_VERSION}}`
3. 从 [repo-kit](../repo-kit/) 安装固定版本的工具，写 `schema/kit.lock.json`
4. `monorepo` / `skills` 跑一次生成器
5. 跑 `check_repo.py` 和版本锁校验；失败即退出非零

生成后的仓库应当直接是：

```text
REPO CHECK: PASS
GENERATE CHECK: PASS
KIT LOCK: PASS
```

## 为什么不是直接复制本目录

模板文件是**片段**：`docs/index.md` 里的 `../README.md` 指向的是生成后的根目录，单独看会断链。
所以模板不参与知识库自身的链接检查，而是由 CI 的 `template-smoke` 复制成三个临时仓库后验证。

## 边界

- 模板只给骨架，不含业务示例、个人数据、本机路径或 token。
- 已有仓库不自动升级；升级走 `tools/update-repo-kit.ps1`。
- 模板变更是骨架变更，改完必须让 `template-smoke` 全绿。
