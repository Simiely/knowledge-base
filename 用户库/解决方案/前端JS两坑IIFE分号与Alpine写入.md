---
tags: [web, javascript, alpine]
date: 2026-08-03
status: stable
related: []
source: https://github.com/Simiely/learning-platform/blob/main/DEV.md
---
# IIFE 缺分号致整段 JS 崩溃 + Alpine 写入必须走 this

**TL;DR**：两个前端 JS 高频坑：① IIFE 前的上一语句缺分号 → 整段 script 后续代码全部终止（`(intermediate value)(...) is not a function`）；② Alpine 修改嵌套对象属性必须走 `this.xxx` 路径，局部变量直接改不触发响应式。

## 问题 1：IIFE 缺分号
卡片模式完全不工作：图片不显示、翻卡缩放全失效。Console：
```
Uncaught TypeError: (intermediate value)(...) is not a function
```
**根因**：`window.closeZoom = function(){...}` 末尾缺 `;`，紧接着 `(function initZoom(){...})()` → JS 把 `}(function(){})()` 当成对 undefined 的调用。
**关键**：这一行错误导致**整个 script 标签的后续代码全部终止**，后续函数永远不执行。
**修复**：IIFE 前确保上一语句已 `;` 终止。
**识别**：`(intermediate value)(...) is not a function` 几乎总是缺分号的 IIFE 解析错误。

## 问题 2：Alpine 响应式写入
练习模式 iPad 图片焦点不生效，始终显示 iPhone 焦点。
**根因**：Alpine 3 的 Proxy 需要**通过 `this.xxx` 路径写入**才触发依赖追踪：
```javascript
var q = this.currentQuestion;  // q 是原始对象引用
q.image_position = newPos;     // ❌ 不触发 Alpine 响应式
this.currentQuestion.image_position = newPos;  // ✅
```
**修复**：写入必须走 `this`，读取可用局部变量。

## 预防
- 写 JS 时每个语句块结束后确认分号；新加 IIFE 时检查前一语句
- 一个 JS 错误会阻止同一 script 标签后续所有代码——调试先看 Console 第一条红错
- Alpine 中"改了不生效"优先怀疑是否绕过了 `this` 写入

## 来源
提炼自 [learning-platform](https://github.com/Simiely/learning-platform)：
[DEV.md](https://github.com/Simiely/learning-platform/blob/main/DEV.md)（IIFE 缺分号 / Alpine 响应式赋值两节）
