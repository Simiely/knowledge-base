---
tags: [android, alarm, background]
date: 2026-08-03
status: stable
related: []
source: https://github.com/Simiely/meituan-bike-reminder/blob/main/DEVELOPMENT.md
---
# Android 后台启动限制（BAL）与 PendingIntent 授权

**TL;DR**：Android 10+ 从后台启动其他 App 的 Activity 会被静默拦截（BAL）。从后台拉起外部 App（扫码/支付/分享）必须用带「后台启动授权」的 `PendingIntent`，普通 `startActivity` 会被吞掉。

## 问题
App 内「启动」按钮拉起美团扫一扫，只打开美团首页、不弹扫码页；而图标冷启动路径正常。

## 根因
Android 10+ 后台启动限制（Background Activity Launch）：**图标冷启动有系统「刚回前台」宽限期**能拉起；按钮路径 App 已转后台（被预热顶到后台）、无宽限期 → 普通 `startActivity` 被 BAL 静默拦截。

## 解决
第二步拉起扫码必须用带后台启动授权的 PendingIntent，三个版本位都要覆盖：
- API 31+：`FLAG_ALLOW_BACKGROUND_ACTIVITY_STARTS`（compileSdk 34 的 stub 已移除该常量 → 反射读取 + 硬编码 `0x01000000` 回退）
- API 34（发送方）：`ActivityOptions.setPendingIntentBackgroundActivityStartMode(MODE_BACKGROUND_ACTIVITY_START_ALLOWED)`
- API 35（创建方）：`PendingIntent.setPendingIntentCreatorBackgroundActivityStartMode(MODE_BACKGROUND_ACTIVITY_START_ALLOWED)`

## 预防
- 从后台拉起外部 App 一律用授权 PendingIntent，别用普通 startActivity
- 调试这种问题先在目标机确认：图标路径通、按钮路径不通 → 基本就是 BAL

## 来源
提炼自 [meituan-bike-reminder](https://github.com/Simiely/meituan-bike-reminder)：
[DEVELOPMENT.md v2.7.1 节](https://github.com/Simiely/meituan-bike-reminder/blob/main/DEVELOPMENT.md)（BAL 拦截与 PendingIntent 授权）
