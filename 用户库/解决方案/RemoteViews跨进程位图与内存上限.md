---
tags: [android, widget, remoteviews, bitmap]
date: 2026-11-23
status: stable
related: [Android前台服务通知渠道与时序.md]
source: https://github.com/Simiely/dashwidget/blob/main/DEVELOPMENT.md
---
# RemoteViews 跨进程位图：私有文件 + 内存上限

**TL;DR**：桌面小组件渲染在 Launcher / `system_server` 进程，本 App 无法直接碰 View；截图写进 App 私有目录再 `setImageViewBitmap`，不要用 MediaStore 的 `content://` Uri。Android 17（API 37）起 RemoteViews 更新有 `6 × width × height` 字节的位图内存上限，超限直接抛 `IllegalArgumentException`。

## 问题
截图文件生成成功，桌面组件仍显示占位；或高版本系统上更新组件时报 `RemoteViews for widget update exceeds maximum bitmap memory usage`。

## 根因
1. **跨进程读不到 Uri**：Launcher 进程读取 MediaStore / FileProvider 的 `content://` 受权限与 work-profile 限制，`setImageViewUri` 常静默失败
2. **位图经 Binder 递送**：`setImageViewBitmap` 的 Bitmap 会放进 `RemoteViews.mBitmapCache`，由 `system_server` 跨进程传给宿主并计入内存预算
3. **部分更新的旧分配不释放**：`partiallyUpdateAppWidget` 会把 Action 追加到缓存的 RemoteViews 层次结构，旧图内存不回收

## 解决
1. 截图写 `files/shots/`（App 私有目录），先写 `.tmp` 再改名；读成 Bitmap 后 `setImageViewBitmap`，不走 Uri
2. 按组件可视尺寸降采样：`BitmapFactory.Options.inSampleSize` 取 2 的幂，不透明缩略图用 `RGB_565`；按 `WindowManager.currentWindowMetrics.bounds` 算预算，别用 `displayMetrics`
3. 换图用完整 `updateAppWidget`，不用 `partiallyUpdateAppWidget`
4. 后台刷新走 WorkManager，不要在 `AppWidgetProvider.onReceive/onUpdate` 里 `startForegroundService`（后台触发会抛 `ForegroundServiceStartNotAllowedException`）

## 预防
- 组件数据源优先 App 私有文件，不依赖跨进程 Uri 授权
- 位图预算按 `6 × w × h` 估，多尺寸 / 折叠屏每个 size bucket 都算一次
- 组件布局只使用 RemoteViews 白名单控件，自定义 View 一律不可用

## 来源
提炼自 [dashwidget](https://github.com/Simiely/dashwidget) 的「桌面组件读不到截图」与截图链路；高版本内存上限核对 Android Developers「创建基本 widget」与 Android 17 行为变更说明。
