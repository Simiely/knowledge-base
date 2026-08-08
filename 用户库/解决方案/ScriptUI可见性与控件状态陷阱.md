---
tags: [ae, scriptui, ui]
date: 2026-08-03
status: stable
related: [解决方案/ScriptUI布局两坑.md]
source: https://github.com/Simiely/starry-sky-generator/blob/main/DEVELOPMENT.md
---
# ScriptUI 可见性与控件状态陷阱

**TL;DR**：ScriptUI 三个高频陷阱——① Group `visible` 从 false 切 true 后**不触发父容器重排**（用 `layout(true)` 或把元素内嵌进同显同隐的 Group）；② `dropdownlist.removeAll()` 后 `selection` 变 null，**增删后必须重设 `selection`**；③ `var x = ctrl.add(...).preferredSize = [w,h]` 链式赋值**返回数组**（x 不是控件），赋值要分开写。

## 问题

- 显示/隐藏控件后，其他元素位置错乱、被覆盖
- 下拉菜单读取 `.selection.text` 返回 null，状态显示 "-"
- 设置控件尺寸后 `.text` 赋值无效

## 根因

1. ScriptUI 的 `visible` 变更不触发自动布局重算；statictext 初始空文字宽度为 0
2. `removeAll()` 后 selection 为 null，手动添加 item 后未恢复
3. 赋值表达式返回**被赋的值**（`[w,h]` 数组）而非控件对象

## 解决

```javascript
// 1. 可见性切换后强制重排
group.visible = true;
parentGroup.layout.layout(true);
// 或：把状态文字内嵌到同显同隐的 Group 内部（推荐，避免 z-order 问题）

// 2. 下拉增删后重设 selection
dd.removeAll();
for (...) dd.add("item", name);
dd.selection = 0;

// 3. 控件尺寸赋值分开写
var ctrl = ee.add("statictext", undefined, "100%");
ctrl.preferredSize = [40, 18];
```

## 预防

- 不要在可见性可变的 Group 之间放置独立 UI 元素
- 任何 Dropdown 的增删操作后必须重设 `selection`
- 链式赋值给变量时，先拿到控件对象再设属性
