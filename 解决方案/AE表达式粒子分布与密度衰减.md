---
tags: [ae, expression, random, particle]
date: 2026-08-03
status: stable
related: [解决方案/AE表达式seedRandom种子管理.md]
source: https://github.com/Simiely/CircleDiffusion/blob/main/圆形扩散插件开发计划.md
---
# AE 表达式粒子分布与密度衰减

**TL;DR**：让粒子"近线密集、远线稀疏"，用**幂函数整形均匀随机**：`biased = Math.pow(random(), falloff)`——`falloff > 1` 偏向 0（近目标密），`< 1` 偏向远处，`= 1` 均匀。配合 `seedRandom` 独立 offset 使用。分布要"线内外两侧"时，再加一个随机符号 `random() < 0.5 ? -1 : 1`。

## 问题

- 粒子全部分布在线的一侧（旧版 `offset = random(0, len)` 只取正方向）
- 想控制"靠近线密、远离线疏"的密度渐变

## 根因

- 均匀随机没有密度偏好；单一方向偏移没有对称性

## 解决

```javascript
// 密度衰减：幂函数将均匀随机映射到偏向 0 的分布
seedRandom(index + seed + 7000, true);
rawRandom = random();
biasedRandom = Math.pow(rawRandom, falloff);  // falloff>1 → 偏向 0（近线密）

// 内外两侧分布（-len ~ +len），随机符号
seedRandom(index + seed + 7500, true);
directionSign = random() < 0.5 ? -1 : 1;
offset = biasedRandom * collectionLen * directionSign;
```

**falloff 效果**：

```
falloff = 1.0 (均匀)   线|████████████████████████|  每个区间粒子数相等
falloff = 2.0 (近线密)  线|████████████████░░░░░░░░|  近线密集，远线稀疏
falloff = 4.0 (聚集)    线|████████████████████░░░░|  大部分粒子紧贴线
falloff = 0.5 (反分布)  线|██░░░░░░░░░░░░░░░░░░░░░░|  远处密（特殊效果）
```

## 预防

- 密度衰减用幂函数（单参数 falloff 控制分布形状，可做成滑块）
- 随机偏移、随机符号、随机角度等各用独立 seedRandom offset（见 seedRandom 种子管理条目）
- 分布需求先想清楚"偏向哪侧/是否对称"，再用对应数学映射
