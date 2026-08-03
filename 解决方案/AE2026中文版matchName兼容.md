---
tags: [ae, api, sdk]
date: 2026-08-03
status: stable
related: []
source: https://github.com/Simiely/AE-Lyrics-Animator/blob/main/DEVELOPMENT.md
---
# AE 2026 中文版 matchName 兼容

**TL;DR**：AE 2026 中文版属性面板显示中文，但 matchName 仍是英文，且与英文文档存在差异（Text Animators 组位置也变了）；属性访问一律用候选 fallback 列表，不要硬编码单一 matchName。

## 问题

按英文官方文档写的 `layer.property("ADBE Text Position")` 等在 AE 2026 中文版取不到，属性为 null。

## 根因

- 本地化版本中属性面板显示名是中文，但脚本操作依赖的 matchName 仍是英文，且部分路径与标准文档不同
- Text Animators 组在 AE 2026 中文版位于 `ADBE Text Properties` 内部，不再是图层的直接子属性

## 解决

1. 属性访问用候选 fallback 列表，逐个尝试（`addAnimProperty()` 统一处理）

```javascript
if (propType === "ADBE Text Position") candidates = [
    "ADBE Text Position", "ADBE Text Position 2D",
    "ADBE Text Position 3D", "Position", "位置"
];
```

2. Animators 组查找用备选路径（`findAnimatorsGroup()`）

```javascript
var animatorsGroup = layer.property("ADBE Text Animators");
if (!animatorsGroup) {
    var textProps = layer.property("ADBE Text Properties");
    animatorsGroup = textProps.property("ADBE Text Animators");
}
```

## 预防

- 所有 AE 属性访问统一走 fallback 函数，不硬编码单一 matchName
- 在 AE 2026 中文版实测后再发布；涉及属性路径的改动都要跑一遍 fallback 链

## 来源

提炼自 [AE-Lyrics-Animator](https://github.com/Simiely/AE-Lyrics-Animator)（v3.5）：
- [DEVELOPMENT.md §A1/A2](https://github.com/Simiely/AE-Lyrics-Animator/blob/main/DEVELOPMENT.md)（matchName 差异、Text Animators 组位置）
- 源码 `addAnimProperty()` / `findAnimatorsGroup()`（[歌词逐字散落动画工具.jsx](https://github.com/Simiely/AE-Lyrics-Animator/blob/main/歌词逐字散落动画工具.jsx)）
