---
tags: [ae, render, mask]
date: 2026-08-03
status: stable
related: []
source: https://github.com/Simiely/starry-sky-generator/blob/main/DEVELOPMENT.md
---
# AE 渲染顺序：Effect → Mask

**TL;DR**：AE 渲染顺序是 **Effect → Mask**（Effect 先应用，Mask 后裁剪结果）。对带 Mask 的层加 Gaussian Blur 效果，模糊边缘会被 Mask 裁剪掉。做粒子/形状模糊时：圆形/多边形用 **Mask Feather**（mask 自身属性，不受顺序影响），无 Mask 的正方形才用 Gaussian Blur。

## 问题

- 对带 Mask 的层加 Gaussian Blur 效果 → 模糊边缘被 Mask 裁剪，效果不自然

## 根因

- AE 渲染管线：Effect 先应用 → Mask 再裁剪 → 所以 Mask 裁掉了效果

## 解决

| 场景 | 方案 |
|---|---|
| 圆形 / 多边形粒子（有 Mask） | **Mask Feather**（mask 自身属性，在 Mask 内部生效） |
| 正方形粒子（无 Mask） | Gaussian Blur 效果 |

## 预防

- 做模糊/效果前先确认目标层有没有 Mask；有 Mask 优先用 Mask 自身的属性（Feather/Expansion）
- **注意**：Mask Expansion 是 **1D 属性**，Mask Feather 是 **2D 属性**（赋值方式不同）
