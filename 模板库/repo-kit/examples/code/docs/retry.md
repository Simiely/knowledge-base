---
id: code.config.retry
title: 重试策略
summary: retry_max 与 timeout_ms 的组合语义，以及如何验证最坏耗时。
type: how-to
kind: standard
status: active
owner: "@platform"
topics: [config]
source_type: code
source: examples/code/config.py
last_reviewed: 2026-11-01
related: []
---
# 重试策略

`retry_max` 与 `timeout_ms` 组合决定最坏耗时。配置含义见 [运行时配置](./config.md#运行时配置)。

本页不重复声明关系类型：`related` 为空是对的，反向链接由生成器派生，不写回被引用文件。

## 步骤

1. 确认真源里的两个值。
2. 跑一次可观察结果的测试，断言实际耗时，而不是「没抛异常」。
3. 若真源改了键，本页必须在同一个 PR 一起改。

## 验证

用 `python scripts/check_repo.py --root .` 确认 `TRUTH_DRIFT=0`；再用实际超时断言验证行为。
