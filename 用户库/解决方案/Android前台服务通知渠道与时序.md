---
tags: [android, notification, service]
date: 2026-08-03
status: stable
related: [Android13通知权限运行时申请.md]
source: https://github.com/Simiely/DarkMask/blob/main/DEVELOPMENT.md
---
# Android 前台服务通知不显示：渠道 id + 权限时序

**TL;DR**：Android 13+ 前台服务通知不显示是两个坑叠加：① 通知渠道一旦创建**重要性无法升高**，必须换新渠道 id + `IMPORTANCE_HIGH`；② 权限弹窗是**异步**的，`requestPermissions` 后立刻 `startForegroundService` 的通知会被静默丢弃——用 `registerForActivityResult` 在授权回调中启动。

## 问题
Android 13+，蒙版运行正常但通知栏看不到常驻通知；`IMPORTANCE_LOW` 渠道在 HyperOS 上被自动折叠/隐藏。

## 根因（两个问题叠加）
1. **渠道重要性不可变**：旧渠道 `IMPORTANCE_LOW` 创建后，代码内无法升高——必须用新渠道 id 才能让 `IMPORTANCE_HIGH` 生效
2. **权限异步时序**：`requestPermissions()` 弹窗后不等待用户点击就立刻 `startForegroundService()`，此时 `POST_NOTIFICATIONS` 未授予，系统静默丢弃通知

## 解决
```kotlin
// ❌ 旧写法：不等授权就启动
ActivityCompat.requestPermissions(this, arrayOf(POST_NOTIFICATIONS), 1)
startForegroundService(i)  // 通知被静默丢弃

// ✅ 正确做法：新渠道 id + 授权回调中启动
val chId = "darkmask_fg_v2"  // 不是旧 id，渠道一旦创建重要性就固定
NotificationChannel(chId, "...", NotificationManager.IMPORTANCE_HIGH)

val launcher = registerForActivityResult(RequestPermission()) { granted ->
    if (granted) startOverlayServiceNow()
}
```
完整配置：setOngoing + setOnlyAlertOnce + PRIORITY_HIGH + VISIBILITY_PUBLIC + 渠道静音（无声音/振动/角标）。

## 预防
- 改渠道重要性 = 换新渠道 id，别想着原地升级
- 依赖通知权限的服务启动，一律在权限回调里做，别在 requestPermissions 后直接 startForegroundService
- Android 13+ 通知相关功能发版前在真机验证（低版本测不出来）

## 来源
提炼自 [DarkMask](https://github.com/Simiely/DarkMask)：
[DEVELOPMENT.md ①](https://github.com/Simiely/DarkMask/blob/main/DEVELOPMENT.md)（前台服务通知不显示）
