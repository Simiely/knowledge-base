---
tags: [android, permission]
date: 2026-08-03
status: stable
related: []
source: https://github.com/Simiely/meituan-bike-reminder/blob/main/DEVELOPMENT.md
---
# Android 13+ 通知权限必须运行时申请

**TL;DR**：Android 13（API 33）起通知是**运行时危险权限**，光在 Manifest 声明 `POST_NOTIFICATIONS` 不够，必须在用到前 `requestPermissions` 弹窗申请，否则提醒/通知静默失效。

## 问题
App 在 Android 13 上声明了 `POST_NOTIFICATIONS`，但只声明没申请，「该锁车了」通知根本不弹，用户毫无感知。低版本（≤12）测试一切正常。

## 根因
Android 13（TIRAMISU）把通知权限从「安装时授予」改为「运行时危险权限」——声明只是白名单，不弹窗申请就等于没授权。

## 解决
在发车流程最前面调用：
```kotlin
ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.POST_NOTIFICATIONS), REQ_CODE)
```
`onRequestPermissionsResult` 里**只记日志、不阻塞主流程**（权限异步，用户可能稍后才同意）。

## 预防
- 所有依赖系统通知做提醒/保活的功能，Android 13+ 都必须补运行时申请
- 低版本测得好好的 ≠ 新系统没问题，发版前在 API 33+ 真机验证

## 来源
提炼自 [meituan-bike-reminder](https://github.com/Simiely/meituan-bike-reminder)：
[DEVELOPMENT.md ②](https://github.com/Simiely/meituan-bike-reminder/blob/main/DEVELOPMENT.md)（Android 13+ 通知权限）
