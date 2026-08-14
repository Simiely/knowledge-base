---
tags: [ae, api, sdk]
date: 2026-08-14
status: stable
related: ["AE2026中文版matchName兼容"]
source: https://github.com/Simiely/AE-Rolling-Lyrics/blob/main/DEVELOPMENT.md
---
# AE 脚本给图层挂效果的正确 API

**TL;DR**：给图层添加效果（Slider Control 等）必须用 `layer.property("ADBE Effect Parade").addProperty("ADBE Slider Control")`；**`layer.effects` 在 AE 2026 真机取不到，访问会报 "undefined 不是对象"**。添加效果与取参数都走候选 fallback（matchName / 中文 / 英文）。

## 问题

- `layer.effects.addProperty("ADBE Slider Control")` 在真机运行报 `undefined 不是对象`（第 372 行），而 Node mock 测试里自造了 `layer.effects` 属性，测试全绿、真机必炸
- 取滑块参数直接 `effect("Slider Control").property(1)` 在部分版本/环境下也不可靠

## 根因

- ExtendScript 里效果容器不是 `layer.effects`（那是表达式层的写法），脚本层要按属性路径取：`layer.property("ADBE Effect Parade")`
- 中文版 AE 的 matchName / 显示名与英文文档有差异（见「AE2026中文版matchName兼容」），单一候选名可能取不到

## 解决

```javascript
// 安全添加效果：候选 matchName 逐个尝试
function addPropertySafe(parent, candidates) {
    for (var c = 0; c < candidates.length; c++) {
        try {
            var prop = parent.addProperty(candidates[c]);
            if (prop) return prop;
        } catch (e) {}
    }
    return null;
}

// 安全取子属性（效果名/参数名多候选 fallback）
function getPropertySafe(parent, candidates) {
    for (var c = 0; c < candidates.length; c++) {
        try {
            var prop = parent.property(candidates[c]);
            if (prop) return prop;
        } catch (e) {}
    }
    return null;
}

// 用法：挂 Slider Control
var fxGroup = getPropertySafe(layer, ["ADBE Effect Parade", "Effects"]);
var fx = addPropertySafe(fxGroup, ["ADBE Slider Control", "ADBE Slider Control-0001", "滑块控制"]);
fx.name = "间距";                                  // 效果名（显示名，中文版 AE 可中文）
var sp = getPropertySafe(fx, ["ADBE Slider Control-0001", "滑块", "Slider"]);
sp.setValue(140);                                  // 设初值

// Checkbox Control（开关）同理：["ADBE Checkbox Control", "ADBE Checkbox Control-0001", "复选框控制"]
// 参数候选：["ADBE Checkbox Control-0001", "复选框", "Checkbox"]
```

## 预防

- 所有 AE 属性访问统一走 `addPropertySafe` / `getPropertySafe`，不硬编码单一 matchName
- **mock 模拟必须忠于真实 AE API**——不要在 mock 里自造真实 AE 不存在的属性（如 `layer.effects`），否则测试会掩盖真机问题
- 效果名中文时，表达式用 `effect("中文名")(1)` 引用（仅中文版 AE；非中文版需英文名）
- 表达式读滑块值 `thisComp.layer("X").effect("效果名")(1)` 是有效的（表达式侧按参数索引 1 取滑块）

## 来源

提炼自 [AE-Rolling-Lyrics](https://github.com/Simiely/AE-Rolling-Lyrics)（v3.6.1 真机报错修复）+ [starry-sky-generator](https://github.com/Simiely/starry-sky-generator)（addPropertySafe/getPropertySafe 原创实现）
