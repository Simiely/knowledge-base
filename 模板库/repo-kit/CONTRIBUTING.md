# Contributing

## 同 PR 规则（最重要）

改了真源（源码 / schema / 原始材料），就必须在**同一个 PR** 里带上所有引用它的文档，由
`schema/sources.json` 的映射驱动。代码改键不更文档会被 `TRUTH_DRIFT` 拦下。

## 提交前

命令、新页清单、改决策流程、报错对照表全部见 [使用说明](docs/usage.md)。本页不复制，避免
第二份清单自己漂移。

```bash
python scripts/check_repo.py --root .
python scripts/generate.py --root . --check
```

本地先绿了再提交，别 push-and-pray。

## 评审

- `CODEOWNERS` 路由评审责任。
- PR 模板必须写：架构漂移影响、changelog 影响、本次**没跑**的检查（NOT RUN 边界）。
- 改公开标识符 / schema / onboarding 的 PR，需要独立评审者把文档与代码路径并排读一遍。

## 非技术贡献者

不必学 Git。可以开 issue，用「页面链接 + 应改成什么」的格式提交；维护者转成 PR。贡献表面
是架构的一部分，不是例外。
