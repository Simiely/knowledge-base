---
tags: [ae, expression, i18n]
date: 2026-08-03
status: stable
related: []
source: https://github.com/Simiely/CircleDiffusion/blob/main/圆形扩散插件开发计划.md
---
# AE 表达式跨语言兼容

**TL;DR**：**AE 表达式里绝对不能写中文名**（`effect("扩散速度")` 在非中文版 AE 会失效）。策略：①控制器层的 effect 用**索引** `effect(2)(1)`（脚本按固定顺序添加，索引稳定）；②图层引用/属性访问用 **matchName**（+ fallback）；③UI 字符串用中文、表达式全部用英文。

## 问题

- 表达式里写中文 effect 名，在英文版 AE / 不同语言环境失效
- 属性 matchName 在不同 AE 版本有差异

## 根因

- 表达式是跨语言执行的，中文 UI 名 ≠ 表达式可用的标识符
- 本地化版本属性路径与英文文档不同

## 解决

```javascript
// ❌ 绝对不能用：表达式里写中文名
effect("扩散速度")(1)

// ✅ 控制器层用索引（脚本按固定顺序添加效果，索引不会变）
effect(2)(1)   // 第 2 个效果 = Diffusion Speed

// ✅ 图层引用用 matchName
thisComp.layer("Ctrl_Diffusion")

// ✅ 属性访问用 matchName + fallback
prop.property("ADBE Vector Ellipse Size")
```

**分层策略**：

| 层 | 语言/方式 |
|---|---|
| UI 字符串 | 全部中文 |
| 表达式代码 | 全部英文 |
| 控制器 effect 引用 | 索引 `effect(N)(1)`（已知顺序） |
| 图层/属性引用 | matchName + 候选 fallback |

**脚本侧找生成的图层（不靠名字）——diff 前后引用**：

```javascript
// AE 中文版会把生成的图层名也本地化（"Audio Amplitude"→"音频振幅"）
// 执行命令前记录所有 layer，执行后找不在原集合里的那层
var before = {};
for (var i = 1; i <= comp.numLayers; i++) before[comp.layer(i).index] = true;
app.executeCommand(2100);  // Convert Audio to Keyframes
for (var j = 1; j <= comp.numLayers; j++) {
    if (!before[comp.layer(j).index]) { /* 这就是生成的新层 */ }
}
```

## 预防

- 生成代码时脚本侧用中文做 UI，表达式侧一律英文/索引
- 控制器层效果按固定顺序添加（脚本内统一管理），表达式用索引最稳
- `fx(name, def)` 帮助函数只用于非控制器的效果引用（如 Glow/Echo），生成含 fallback 的三元表达式
