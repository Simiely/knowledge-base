---
tags: [ae, text-animator, expression]
date: 2026-08-03
status: stable
related: []
---
# Range Selector 只用 Percent 模式

**TL;DR**：AE 文字动画器的 Range Selector 锁定字符范围，**统一用 Percent 模式**。Index 模式的 Start/End 在 AE 2026 是隐藏 3D 属性，`setValue()` 会报错；且 Selector 默认 Units 就是 Percent，只设 Index 值会被忽略。

## 问题

- 用 Index Start/End 逐字锁定字符时，`setValue()` 报错或设置被忽略，波浪/逐字效果失效
- 多个版本曾因此返工

## 根因

1. **Units 未切换**：Selector 默认 Units 为 `Percent`，此模式下 Index Start/End 属性被忽略，所有动画器作用于全部字符
2. **隐藏属性**：Index 模式 Start/End 在 AE 2026 是隐藏属性（3D 类型），`setValue()` 报错
3. **属性顺序脆弱**：硬编码索引（`property(4)`/`property(5)`）在不同 AE 版本中顺序可能不同

## 解决

Percent 模式按字符数等分百分比范围，精确锁定单个字符：

```javascript
var pStart = ((ci - 1) / textLen) * 100;
var pEnd   = (ci / textLen) * 100;
hPStart.setValue(pStart);
hPEnd.setValue(pEnd);
```

## 预防

- 逐字锁定一律 Percent 等分，不用 Index
- Index 模式需要额外设置 Units 且兼容性差，直接放弃
- `textIndex` 表达式变量在 AE 2026 也不可用，逐字效果用「每字符独立动画器 + 硬编码索引」实现
