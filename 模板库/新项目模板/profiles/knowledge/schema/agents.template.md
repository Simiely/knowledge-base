# AGENTS.md · {{PROJECT_NAME}} 项目规则

> 📌 **文档基线**：{{DATE}}（`initial`）—— 从 knowledge-base 新项目模板创建（knowledge profile）
> **更新文档后请更新此行**（日期 + 新 commit hash），并在 CHANGELOG 追加版本

本仓库是 {{PROJECT_NAME}} 的知识库。回答相关问题前先读这份，再读 [docs/index.md](docs/index.md)。

## 内容范围

- **收**：可复用的判断、可复现的步骤、踩过的坑（一坑一篇）
- **不收**：一次性流水账、只有结论没有依据的断言、能从代码里直接读出来的说明

## 组织约定

- 一个主题一页，页面之间用 `related` / `depends-on` 建立关系，**不做目录式大文件**
- 概念只在一处定义（`defines`），其他地方链接，不复制
- 新页从 [docs/_template.md](docs/_template.md) 复制，`status: draft` 起步
- 一次性分析/复盘用 `kind: report` + `status: archived`，不参与过期判定

## 写作约定

- 标题写「判断」，不写「关于 X」——读者扫标题就知道这页主张什么
- 每条结论后面跟**怎么验证**；不能验证的写清限制
- 报错原文、命令、参数一律放进行内代码，方便检索
- 引用外部资料必须给链接，并注明是哪个版本

## 常用命令

```bash
python tools/repo-kit/check_repo.py --root .
python tools/repo-kit/generate.py --root . --check
pwsh tools/update-repo-kit.ps1 -Check
python -m pip install -r requirements.txt   # 文档检查依赖
```

## 当前规模

- 页面：{{PAGES}}（critical={{CRITICAL}}）
- 按 type：{{TYPES}}
- 词表版本：{{VERSION}}

## 边界

- 机器层只保结构、链接、生成物与新鲜度；**内容对不对靠人审**。
- 不追求「写得多」，追求「下次能直接照着做」。
