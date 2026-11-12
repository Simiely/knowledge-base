# AGENTS.md · {{PROJECT_NAME}} 项目规则

> 📌 **文档基线**：{{DATE}}（`initial`）—— 从 knowledge-base 新项目模板创建
> **更新文档/代码后，请更新此行**（日期 + 新 commit hash），并在 CHANGELOG 追加版本

本仓库是 {{PROJECT_NAME}}。回答相关问题前先读这份，再读 [docs/index.md](docs/index.md)。

## 技术栈

- 待填：语言 / 框架 / 精确版本

## 关键坑（3~5 条，越具体越好）

- 待填：只写代码里看不出的信息

## 约定

- 中文文档；标题与文件名一致，不带空格
- 改真源时，**同一个 PR** 带上所有引用它的文档
- 未验证的内容不写进正文；确需提及就标「暂未验证」

## 常用命令

```bash
python tools/repo-kit/check_repo.py --root .
pwsh tools/update-repo-kit.ps1 -Check
```

## 边界

本仓库采用 `link-only` profile：repo-kit 只查本地链接、锚点与入口，不要求 frontmatter；
内容真源由本仓库自己的管线保证。语义正确性靠人审。
