---
tags: [miniprogram, wxml, render]
date: 2026-08-12
status: stable
related: [解决方案/小程序不用blockwxif配对.md]
source: https://github.com/Simiely/collab-plan-miniprogram/blob/main/CHANGELOG.md
---
# 小程序 wxml 不支持动态事件名

**TL;DR**：`wxml` 里事件名必须是静态字符串——`bind:tap="{{cond ? 'a' : 'b'}}"` 不会被解析为二选一，而是被当成字面量方法名（`"{{cond ? 'a' : 'b'}}"` 整体），事件**完全不触发**、静默失效。多态分流请写在 JS 方法内部。

## 问题
todo/list 批量选择失效、清单长按复制失效——点击毫无反应，控制台无报错，排查半天找不到原因。

## 根因
WXML 模板不支持动态事件绑定。`bind:tap="{{cond ? 'a' : 'b'}}"` 编译后事件名就是那段模板字符串本身（字面量），小程序找 `{{cond ? 'a' : 'b'}}` 这个方法当然不存在 → 事件不触发且静默（无 warn 无 error）。

## 解决
事件名静态化：`bind:tap="onTap"` 固定一个方法，条件分流的逻辑放进 JS：
```js
onTap(e) {
  const { type } = e.currentTarget.dataset; // 用 data-* 传标识
  type === 'batch' ? this.handleBatch() : this.handleCopy();
}
```
用 `data-*` 自定义属性（`data-type="batch"`）传分支标识，而不是动态拼事件名。

## 预防
1. 牢记：**wxml 事件绑定 = 静态方法名**，任何"根据条件绑不同事件"的想法都改为 JS 内分流
2. 批量渲染 + 多交互模式的列表，先想清楚事件模型：统一入口 + `data-*` 区分，别在模板里玩花样
3. 出现"点击无反应"先怀疑模板语法：动态绑定（事件名 / 属性名）是静默失效重灾区

## 来源
提炼自 [collab-plan-miniprogram](https://github.com/Simiely/collab-plan-miniprogram) CHANGELOG v0.7.5 P-7 修复（wxml 动态事件名 bug）。
