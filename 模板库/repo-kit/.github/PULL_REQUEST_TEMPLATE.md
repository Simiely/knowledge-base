## 这个 PR 改了什么

## 架构漂移影响
- [ ] 只改内容，不动结构
- [ ] 改了公开标识符 / config schema / onboarding 流程 → 需要独立评审者把文档与代码路径并排读一遍
- [ ] 抬高了任务层级 / 引入新的真源 → 需要新 ADR

## 文档与生成产物
- [ ] 真源变更已在**同一个 PR** 带上所有引用它的文档
- [ ] `docs/index.md` 已更新（新增页无孤儿）
- [ ] `docs/decisions/index.md` 已同步（涉及 ADR 时）
- [ ] `python scripts/generate.py --root . --write` 已跑过，生成产物已提交
- [ ] CHANGELOG 的 [Unreleased] 已更新

## 验证
命令与报错对照见 [使用说明](../docs/usage.md)。
- [ ] `python scripts/check_repo.py --root .` → PASS
- [ ] `python scripts/generate.py --root . --check` → PASS
- [ ] `python scripts/drift_probe.py --root .` → 8/8
- [ ] `python -m unittest discover -s tests` → OK

## NOT RUN（明确写出本次没跑的检查与原因）
