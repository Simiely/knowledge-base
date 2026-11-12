# DEVELOPMENT.md · knowledge-base

## 项目概览

本仓库解决两件事：

1. **沉淀经验**：把各项目踩过的坑写成可检索的条目（`用户库/`）。
2. **提供上游**：把规范、模板和机器校验打包成可复制的骨架（`模板库/`）。

不做什么：不做项目源码托管，不做 Rive/AE/C4D 教程翻译，不收录未验证的内容。

## 架构说明

```text
knowledge-base/
├── README.md              门面：两库关系 + 三个入口
├── AGENTS.md              AI / 维护者入口
├── DEVELOPMENT.md         本文件：架构与维护流程
├── CHANGELOG.md           版本历史
├── 模板库/                骨架（零个人数据）
│   ├── 单项目规范/         人读规范：4 文件模型 + 机器层
│   ├── 新项目模板/         可复制骨架：base + monorepo/skills/link-only
│   ├── repo-kit/           机器校验工具（版本单一来源）
│   ├── 模板/               经验条目模板
│   └── 解决方案/ 等        索引空壳
├── 用户库/                数据：经验条目与索引
├── schema/                本仓库 link-only 校验配置
├── tools/                 本仓库的 repo-kit 安装与版本锁
└── .github/workflows/     自检 + 模板自测 + kit 自测
```

**上游/下游**：`模板库/` 是上游，`用户库/` 是下游；数据永不回流。

**两层模型**：

| 层 | 负责 | 产物 |
|---|---|---|
| 人层 | 4 文件 + 生长式拆分 | README / AGENTS / DEVELOPMENT / CHANGELOG |
| 机器层 | 契约、链接、生成、版本锁 | repo-kit + schema + CI |

**模板不是成品仓库**：`新项目模板/base` 与 `profiles/*` 是片段，单看会有断链；
`新建仓库.ps1` 负责拼装、替换占位符、安装 repo-kit，并跑检查。

## 关键问题与方案

### 问题：模板文件在本仓库里链接是断的

**TL;DR**：模板是片段，按目标仓库根目录写相对链接；不要在本仓库里直接检查模板。

- 根因：`docs/index.md` 里的 `../README.md` 指向生成后的根目录，模板目录里没有这个文件。
- 解决：知识库自检忽略 `模板库/新项目模板/**`；CI 的 `template-smoke` 复制三个 profile 到临时目录后跑检查。
- 预防：改模板后必须让 `template-smoke` 全绿，不能只看模板目录。

### 问题：模板与 kit 版本漂移

**TL;DR**：模板通过 `新建仓库.ps1` 安装当前 `模板库/repo-kit/VERSION` 对应的工具，并写版本锁。

- 根因：手复制工具会留下旧副本。
- 解决：模板不预置工具副本；初始化时从 repo-kit 安装并生成 `schema/kit.lock.json`。
- 预防：CI 每个 profile 都跑 `update-repo-kit.ps1 -Check`。

## 维护流程

1. 改规范 / 模板 → 只动 `模板库/`
2. 改经验数据 → 只动 `用户库/`
3. 跑 `python tools/repo-kit/check_repo.py --root .`
4. 跑模板自测：按 `.github/workflows/repo-check.yml` 的三条命令本地复制验证
5. CHANGELOG 追加版本；AGENTS 基线行更新
6. 推送
