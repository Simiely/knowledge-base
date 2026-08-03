---
tags: [ae, scriptui, ui]
date: 2026-08-03
status: stable
related: []
---
# ScriptUI 布局两坑

**TL;DR**：ScriptUI 面板布局两个高频坑——① `edittext.alignment = "fill"` 单字符串只作用垂直轴，必须用 `["fill", "center"]` 双轴格式；② AE dockable Panel 宽度由主 UI 控制，`minimumSize` / `preferredSize` 对面板实际宽度无效。

## 问题

- 输入框填了 `alignment = "fill"` 却没有水平撑满，布局错乱
- 设置面板 `preferredSize` 后宽度不变

## 根因

1. `alignment` 单字符串只作用垂直轴；水平填充必须用双轴数组 `["fill", "center"]`
2. dockable Panel 模式下面板宽度由 AE 主 UI 控制，`minimumSize`/`preferredSize` 不生效

## 解决

```javascript
// 输入框水平撑满 + 垂直居中
edittext.alignment = ["fill", "center"];
```

- 面板宽度：靠控件自身固定宽度（如标签 110px）+ 双轴 fill 撑满剩余空间实现整洁布局
- 不要在 Panel 模式下依赖 preferredSize 控制面板宽度

## 预防

- 写布局前先明确每个控件的对齐需求，fill 用双轴数组形式
- 面板宽度问题优先查控件布局，而不是调 preferredSize
- 多个 fill 叠加会导致宽度失控（如 `alignChildren="fill"` + 控件 `alignment="fill"` 双重重叠），布局写完检查 fill 层级
