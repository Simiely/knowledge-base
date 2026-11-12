# AGENTS.md · {{PROJECT_NAME}} 技能仓库规则

> 📌 **文档基线**：{{DATE}}（`initial`）—— 从 knowledge-base 新项目模板创建
> **更新文档/代码后，请更新此行**（日期 + 新 commit hash），并在 CHANGELOG 追加版本

本仓库是 {{PROJECT_NAME}}，以 `skills/<name>/SKILL.md` 为交付物。回答相关问题前先读这份。

## 技术栈

- WorkBuddy Skills：`SKILL.md` frontmatter 含 `name` + `description`
- 本机技能目录：`%USERPROFILE%\.workbuddy\skills\<name>\SKILL.md`

## 关键坑（3~5 条，越具体越好）

- 待填：只写代码里看不出的信息

## 约定

- 每个技能一个子目录，`SKILL.md` 是唯一入口
- `description` 必须含触发词 + 适用对象 + 能力摘要
- `references/` 是长资料，只做链接检查，不强制 frontmatter
- 新增技能：目录 + README 列表 + CHANGELOG + 本文件
- 中文文档；未验证的内容不写进正文

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

## 目录

- [skills/README.md](skills/README.md) — 技能目录结构与新增步骤
- [DEVELOPMENT.md](DEVELOPMENT.md) — 架构与问题记录

## 边界

机器只保 `SKILL.md` 契约、链接与入口；技能质量与语义正确性靠人审。
