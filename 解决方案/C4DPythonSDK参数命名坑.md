---
tags: [c4d, sdk, api]
date: 2026-08-03
status: stable
related: []
source: https://github.com/Simiely/c4d-mesh-face-sorter/blob/main/DEVELOPMENT.md
---
# C4D Python SDK 参数命名坑

**TL;DR**：C4D Python SDK 部分 API 与 C++ SDK 不一致，参数名也和常规理解不同——`GroupBegin` 用 `title=` 不用 `name=`（`name=` 是 `AddStaticText` 的）；`ScrollGroupEnd` **不存在**，用 `GroupEnd()` 结束滚动组。写 UI 前查 Python SDK 签名，别想当然。

## 问题

- 给 `GroupBegin` 传 `name="xxx"` → 抛 `TypeError`，`CreateLayout` 提前退出，**后面控件全部被跳过**（无声故障，只有第一个 StaticText 可见，无错误弹窗）
- C4D 2024 报 `AttributeError: 'GeDialog' has no attribute 'ScrollGroupEnd'`

## 根因

- C4D 各方法参数名不一致：`AddStaticText` 用 `name=`，`GroupBegin` 却用 `title=`
- Python SDK 与 C++ SDK 不完全一致（`ScrollGroupBegin` 存在但 `ScrollGroupEnd` 不存在）

## 解决

```python
# GroupBegin 用位置参数，不传 name=
GroupBegin(id, flags, cols, rows, "xxx")
# 滚动组用 GroupEnd() 结束
```

## 预防

- UI 构建函数参数一律查 Python SDK 签名，不沿用 C++ 习惯或记忆
- `CreateLayout` 抛错会导致后面控件全消失且无提示——遇到"控件莫名消失"先查有没有 TypeError 被吞
