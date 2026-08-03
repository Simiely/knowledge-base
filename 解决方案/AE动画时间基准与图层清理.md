---
tags: [ae, script, expression]
date: 2026-08-03
status: stable
related: []
source: https://github.com/Simiely/CircleDiffusion/blob/main/圆形扩散插件开发计划.md
---
# AE 动画时间基准与图层清理

**TL;DR**：生成式脚本两个工程惯例——①**播放头对齐**：控制器层 `startTime = comp.time`（读播放头），所有表达式用 `t = time - ctrl.inPoint` 相对起点（动画从点"生成"那一刻开始，而不是 0 秒）；②**图层清理**：生成图层统一前缀命名（如 `扩散_` / `Ctrl_`），清理时从后往前遍历删除。

## 播放头对齐

```javascript
// 生成时读播放头位置
var startTime = comp.time;
var ctrl = comp.layers.addNull();
ctrl.startTime = startTime;          // 控制器 inPoint = 当前时间
ctrl.name = "Ctrl_Diffusion";

// 所有表达式统一引用 ctrl.inPoint
// t = time - ctrl.inPoint  → 动画相对起点
```

- **预防**：动画起始时间一律用控制器 inPoint 做基准，不硬编码 0

## 图层清理

```javascript
function removeGeneratedLayers(prefix) {
    var comp = getActiveComp();
    if (!comp) return;
    // 从后往前删（避免索引变化导致跳删）
    for (var i = comp.numLayers; i >= 1; i--) {
        var layer = comp.layer(i);
        if (layer.name.indexOf(prefix) === 0) {
            layer.remove();
        }
    }
}
// 一键清理：removeGeneratedLayers("扩散_"); removeGeneratedLayers("Ctrl_");
```

- **预防**：生成图层统一前缀命名；清理循环一律**倒序遍历**（正向删除索引前移会跳项）
