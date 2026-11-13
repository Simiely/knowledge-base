# AGENTS.md — 仓库唯一入口

> 生成文件，勿手改。改规则请改 `schema/` 或 `scripts/generate.py`，再运行 `python scripts/generate.py --root . --write`。

这是给 AI 与人的**唯一入口**。完整用法见 [docs/usage.md](docs/usage.md)，概念定义见 [docs/concepts/ssot.md](docs/concepts/ssot.md)，决策见 [docs/decisions/index.md](docs/decisions/index.md)。`CLAUDE.md`、`CURSOR.md` 等只允许一行指向本文件。

## 非协商（只放最关键的 6 条）
1. 改真源（源码 / schema / 原始材料）时，**同一个 PR** 带上所有引用它的文档。
2. 同一概念、命令、清单只允许有一个权威位置；别处链接，不复制。
3. 禁止写回 backlinks；反向链接由 `scripts/generate.py` 生成。
4. 禁止手写 `updated`；新鲜度只用 `last_reviewed` + `review_days`。
5. 禁止自造 `type/kind/status/rel/topic` 词表外的值；禁止新增嵌套 frontmatter。
6. 未经用户确认不装软件、不付费、不对外发送、不改生产库。

## 怎么操作
只有一处权威：[使用说明](docs/usage.md)。本文件不复制命令清单、报错表和新页清单。

## 验收
```bash
python scripts/check_repo.py --root .
python scripts/generate.py --root . --check
```
验收信号：`REPO CHECK: PASS`（ERROR=0）。检查器验证不了「这句话是不是真的」；改公开标识符 / schema / onboarding 的 PR，需要人把文档与代码路径并排读一遍。

## 当前规模
- 页面：13（critical=5）
- 按 type：explanation=8, how-to=2, reference=3
- 词表版本：2.4.0

## 边界
机器只保结构、引用、新鲜度与真源标识符；语义正确性靠生成 + 人审。不要把本文件写成第二本规范。
