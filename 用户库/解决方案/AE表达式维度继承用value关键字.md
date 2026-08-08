---
tags: [ae, expression, 2d3d]
date: 2026-08-03
status: stable
related: []
source: https://github.com/Simiely/AudioScale/blob/main/DEVELOPMENT.md
---
# AE 表达式维度继承用 value 关键字

**TL;DR**：向 3D 图层的 Scale/Position 写 2 维数组会触发 `SetDimensionsSeparated` 内部验证故障（崩溃）。**表达式用 `value` 关键字继承当前维度**（`v = value; v[0]=...; v[1]=...; v`）——2D 得 `[x,y]`，3D 得 `[x,y,z]`（Z 自动保留）。别碰 `dimensionsSeparated`，别 `setValue` 数组。

## 问题

- `scaleProp.dimensionsSeparated = false` → 崩
- `scaleProp.setValue([100, 100])` → 依然崩（2 维数组赋给 3D 层，AE 尝试切换维度模式触发 AEGP 验证错误）

## 解决

```javascript
v = value;            // 2D: [x,y]  3D: [x,y,z]
v[0] = baseScale + s;
v[1] = baseScale + s;
v                    // 3D 层的 Z 保持原值
```

## 预防

- 可能遇到 2D/3D 混合的属性（Scale / Position / Anchor Point）统一用 value 继承维度模式
- **永远不要**在脚本侧切换 `dimensionsSeparated`，也不要给 3D 层 setValue 2 维数组
- 表达式返回的数组维度必须与属性当前维度一致
