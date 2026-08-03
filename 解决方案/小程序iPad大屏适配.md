---
tags: [miniprogram, responsive, ipad]
date: 2026-08-03
status: stable
related: []
source: https://github.com/Simiely/potty-training-miniprogram/blob/main/DEV.md
---
# 小程序 iPad 大屏适配：别信 CSS 媒体查询

**TL;DR**：小程序里 CSS `@media` 在 iPad 上**不命中**、`windowWidth` 不是物理宽。响应式判定用 `resizable:true` + `screenWidth`（物理宽）+ JS 挂 `.tablet` 类 + 后代选择器写平板样式 + px 覆盖。

## 问题
加了 `@media(min-width:768px)` 平板样式、改了 px，iPad 上界面始终不变、字巨大、没利用屏幕——"改了没变"反复发生。

## 根因（三层，每一层都是真因）
1. **缺 `resizable`**：`app.json` 没有 `"resizable": true` → iPad 被微信当 iPhone 等比放大（两侧黑边、手机布局拉满全屏）
2. **CSS 媒体查询不命中**：`@media(min-width:768px)` 在微信 iPad 模拟器下**不触发**（断点永远不满足）
3. **`windowWidth` 不是物理宽**：`wx.getWindowInfo().windowWidth` 在 iPad 上返回被限制为手机比例的「绘制区域宽度」（约 375~631px），`>=768` 永远 false

## 解决（最终落地）
- 判定平板用 **`screenWidth`**（物理屏总宽，iPad 横屏≈1366/竖屏≈1024），回退 `screenWidth || windowWidth || 375`
- 每页 `onLoad` 读 screenWidth → `setData({uiMode:'tablet'|'phone'})`，`onResize` 重算（支持旋转/分屏）
- wxml 根节点挂 `{{uiMode}}`；平板样式写成 **`.tablet` 后代选择器**（`.tablet .appbar-title`），由 JS 挂的类触发，100% 可靠
- 平板态字号/间距用 **px 重写**（rpx 在 iPad 占满屏时 1rpx≈1.82px 会被等比放大）
- **额外坑**：平板覆盖必须写进各页**自身** wxss 的 `.tablet` 块，放全局 `app.wxss` 会被页面基础规则反超

## 预防
- 小程序响应式：**优先 JS 判定 + 类切换，不要迷信 CSS 媒体查询**
- 记得 `resizable: true`；判定物理宽用 `screenWidth` 不用 `windowWidth`
- 平板样式和基础样式放同一层级的文件，避免被反超

## 来源
提炼自 [potty-training-miniprogram](https://github.com/Simiely/potty-training-miniprogram)：
[DEV.md #16](https://github.com/Simiely/potty-training-miniprogram/blob/main/DEV.md)、[#17](https://github.com/Simiely/potty-training-miniprogram/blob/main/DEV.md)
