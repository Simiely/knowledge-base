---
tags: [c4d, sdk, python]
date: 2026-08-03
status: stable
related: [模板/插件Release打包模板.md]
---
# C4D 2026 移除的 Python SDK API

**TL;DR**：C4D 2026 移除了 `ListView` / `GePopupMenu` / `ScrollGroupEnd` 等 UI API，且 `AddStaticText(border=)`、`AddComboBox(cols=)` 等 kwargs 改为仅位置参数（positional-only）。老插件直接跑会报错，需按 2026 SDK 重写相关代码。

## 问题

C4D 2023-2025 开发的插件在 C4D 2026 加载时报 `AttributeError` / `TypeError`，控件创建失败。

## 根因

- 2026 新版 Python SDK 移除了部分 UI 类/方法：`ListView`、`GePopupMenu`、`ScrollGroupEnd` 等
- 部分方法签名变化：`AddStaticText(border=...)`、`AddComboBox(cols=...)` 等 kwargs 变为 position-only，传关键字参数会报错

## 解决

1. 用 2026 SDK 支持的替代 API 重写被移除的部分（对照 SDK 变更文档逐个替换）
2. kwargs 改回位置参数传参，或按新签名调整
3. 兼容性策略：目标版本定为 C4D 2023-2026，用版本判断分流新旧 API

## 预防

- 新插件代码统一按 2026 SDK 规范编写，不再使用已移除 API
- **遇代码改动后不生效，先清理 `.pypc` 缓存再重试**（缓存会导致旧代码残留）
- 提交问题给他人时附上控制台完整 traceback
