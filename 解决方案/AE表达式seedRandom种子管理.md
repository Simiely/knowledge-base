---
tags: [ae, expression, random]
date: 2026-08-03
status: stable
related: []
source: https://github.com/Simiely/starry-sky-generator/blob/main/DEVELOPMENT.md
---
# AE 表达式 seedRandom 种子管理

**TL;DR**：粒子/批量随机一律用 `seedRandom(index + seed + OFFSET, true)`。三条规则：①**不同属性用不同 offset**（生命周期 1000 / 位置 2000 / 颜色 3000 / 目标 5000 / 密度 6000 / 时间偏移 8000 / 缩放 9000 / 模糊 10000）；②**同一属性跨表达式用相同 offset**（如 Position 和 Opacity 共读生命周期）；③`timeless=true` 防每帧漂移。改种子值可整体重置所有分布。

## 问题

- 粒子位置/大小/颜色随机互相影响（共用种子流）
- 随机值随时间漂移（每帧不同，动画闪烁错乱）
- 想整体重置随机分布需要改很多地方

## 根因

- 多个属性共用一个 `seedRandom` 流，后取的随机值受前面影响
- 未用 timeless 模式时，表达式每帧推进随机序列

## 解决

```javascript
// 不同属性不同 offset（隔离随机流）
seedRandom(index + seed + 2000, true);  // 位置
seedRandom(index + seed + 3000, true);  // 颜色
seedRandom(index + seed + 10000, true); // 模糊

// 同一属性跨表达式相同 offset（保证同步）
seedRandom(index + seed + 1000, true);  // Position 和 Opacity 共读生命周期
```

## 预防

- 新增随机属性时：分配**新 offset**（不与现有冲突），并在文档记录
- 同一属性的多个表达式（如位置在 Position/Opacity 都要用）用**相同 offset**
- `timeless=true` 是必须的（每个粒子每帧得到相同随机值）
- 种子值做成参数（`Ctrl_Starfield` 滑块），改种子 = 一键重置所有分布
