# AGENTS.md · knowledge-base

> 📌 **文档基线**：2026-11-12（`b9469bc`）—— 建立模板库 / 新项目模板 / repo-kit 三层上游
> 更新文档或模板后，请更新此行，并在 CHANGELOG 追加版本

本仓库是个人经验库，也是所有仓库的**上游**：`模板库/` 提供规范与可复制骨架，
`用户库/` 存放实际经验数据。

## 结构

- [`模板库/`](模板库/README.md) — 骨架，零个人数据：单项目规范 / 新项目模板 / repo-kit
- [`用户库/`](用户库/README.md) — 数据：经验条目、索引、盘点表

## 铁律

- **数据永不回流模板库**：用户库的条目、索引行、盘点表不复制进模板库
- 模板库只放规范、模板、索引空壳、机器工具
- 模板文件是**片段**，不参与本仓库链接检查；由 CI 的 `template-smoke` 复制成临时仓库后验证
- 隐私红线：不写 token / 密码 / 邮箱 / 本机绝对路径 / 未公开项目细节

## 常用命令

```bash
python tools/repo-kit/check_repo.py --root .
pwsh tools/update-repo-kit.ps1 -Check
pwsh 模板库/新项目模板/新建仓库.ps1 -Name demo -Profile monorepo -Target ..\demo
```

## 边界

本仓库采用 `link-only` profile：只查链接、锚点与入口，不要求 90+ 篇经验条目改 frontmatter。
内容真源仍是 `用户库/` 与各项目仓库；语义正确性靠人审。
