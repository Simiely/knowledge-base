---
tags: [android, overlay, ui]
date: 2026-08-03
status: stable
related: []
source: https://github.com/Simiely/DarkMask/blob/main/DEVELOPMENT.md
---
# Android 全屏蒙版盖住状态栏/刘海的正确姿势

**TL;DR**：`TYPE_APPLICATION_OVERLAY` + `MATCH_PARENT` 的蒙版被约束到"内容区"（状态栏与导航栏之间），盖不住状态栏/刘海。要覆盖全屏必须：物理全屏尺寸（R+ `maximumWindowMetrics`）+ `FLAG_LAYOUT_NO_LIMITS` + `LAYOUT_IN_DISPLAY_CUTOUT_MODE_ALWAYS`。

## 问题
`TYPE_APPLICATION_OVERLAY` + `MATCH_PARENT` 的蒙版被压在状态栏、导航栏、输入法之下，无法盖住状态栏。

## 根因
`TYPE_APPLICATION_OVERLAY` 的窗口层级本身低于状态栏，且 `MATCH_PARENT` 被系统约束到"内容区"（状态栏与导航栏之间）。

## 解决
```kotlin
// 获取物理全屏尺寸（含状态栏、导航栏、刘海）
fun realScreenSize(): Point {
    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
        val b = wm.maximumWindowMetrics.bounds   // ⚠️ 不是 getCurrentWindowMetrics()（那是窗口尺寸）
        return Point(b.width(), b.height())
    } else {
        wm.defaultDisplay.getRealSize(p)          // 不是 getSize()
    }
}
// 取最大边做正方形保证横竖屏都盖住
val side = max(real.x, real.y)
LayoutParams(side, side, TYPE_APPLICATION_OVERLAY,
    FLAG_NOT_FOCUSABLE or FLAG_NOT_TOUCHABLE
    or FLAG_LAYOUT_IN_SCREEN or FLAG_LAYOUT_NO_LIMITS,
    PixelFormat.TRANSLUCENT
).apply {
    gravity = TOP or START; x = 0; y = 0
    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P)
        layoutInDisplayCutoutMode = LAYOUT_IN_DISPLAY_CUTOUT_MODE_ALWAYS
}
```

## 预防
- 全屏覆盖类窗口：用 `maximumWindowMetrics`（物理尺寸）而非 `getCurrentWindowMetrics`（窗口尺寸）
- 老版本用 `defaultDisplay.getRealSize()` 而非 `getSize()`
- 盖刘海必须 `layoutInDisplayCutoutMode = ALWAYS`

## 来源
提炼自 [DarkMask](https://github.com/Simiely/DarkMask)：
[DEVELOPMENT.md ②](https://github.com/Simiely/DarkMask/blob/main/DEVELOPMENT.md)（蒙版覆盖状态栏/刘海）
