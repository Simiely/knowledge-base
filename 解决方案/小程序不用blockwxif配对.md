---
tags: [miniprogram, wxml, render]
date: 2026-08-03
status: stable
related: []
source: https://github.com/Simiely/potty-training-miniprogram/blob/main/DEV.md
---
# 小程序不用 block wx:if/else 配对（渲染崩溃）

**TL;DR**：`<block wx:if>/<block wx:else>` 配对是虚拟节点，微信框架 diff 在数据首次变更时会错配导致**页面崩溃/卡死**（非无害警告）。互斥 UI 态一律用两个独立 `<view wx:if>`。

## 问题
锁屏页点击「微信授权」后 `authorized` 从 false 变 true，页面闪退卡死；历史页异步加载后列表渲染异常。控制台报：
```
[渲染层错误] Expected updated data but get first rendering data
Error: SystemError (webviewScriptError)
```

## 根因
`<block>` 是虚拟节点（不产生 DOM），`<block wx:if>/<block wx:else>` 配对时，框架 diff 算法在数据首次变更为 true 时，把「首次渲染数据」与「更新数据」错误匹配。`lazyCodeLoading: "requiredComponents"` 启用时加剧。

**关键**：这与无害的 framework 层 warning 不同——这是导致页面崩溃的严重 Bug！

## 解决
```wxml
<!-- 修复前（崩溃） -->
<block wx:if="{{!authorized}}"><button>授权</button></block>
<block wx:else><view>密码键盘</view></block>

<!-- 修复后（正常） -->
<view wx:if="{{!authorized}}"><button>授权</button></view>
<view wx:if="{{authorized}}"><view>密码键盘</view></view>
```
核心原理：`<view>` 是真实 DOM 节点，框架能正确追踪其数据绑定和 diff。

## 预防
- 小程序中**永远不要用 `<block wx:if>/<block wx:else>` 配对**控制两种互斥 UI 态
- 能用 `<view>` 就用 `<view>`；`wx:else` 也尽量避免，改用独立的 `wx:if` 反向条件

## 来源
提炼自 [potty-training-miniprogram](https://github.com/Simiely/potty-training-miniprogram)：
[DEV.md #13](https://github.com/Simiely/potty-training-miniprogram/blob/main/DEV.md)
