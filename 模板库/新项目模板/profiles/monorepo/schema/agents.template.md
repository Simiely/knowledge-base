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
- 同一命令、清单、报错表只允许一个权威位置；别处链接，不复制
- 未验证的内容不写进正文；确需提及就标「暂未验证」
- `docs/_generated/` 由生成器产出，不要手改

## 常用命令

```bash
python {{TOOL}}/check_repo.py --root .
python {{TOOL}}/generate.py --root . --check
pwsh tools/update-repo-kit.ps1 -Check
```

## 当前规模

- 页面：{{PAGES}}（critical={{CRITICAL}}）
- 按 type：{{TYPES}}
- 词表版本：{{VERSION}}

## 边界

机器只保结构、链接、真源与新鲜度；语义正确性靠人审。不要把本文件写成第二本规范。
