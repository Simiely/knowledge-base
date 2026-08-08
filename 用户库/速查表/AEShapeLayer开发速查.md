---
tags: [ae, shape-layer, api]
date: 2026-08-03
status: stable
related: [解决方案/AE表达式跨语言兼容.md]
source: https://github.com/Simiely/CircleDiffusion/blob/main/圆形扩散插件开发计划.md
---
# AE Shape Layer 开发速查

**TL;DR**：Shape Layer 是 AE 脚本生成图形的高效方案——**1 个 Shape Layer + N 个 Shape Group** 管全部图形（图层数 O(1)），每个 Group 可含独立 Ellipse/Stroke/Transform。Ellipse 的 Size 属性是**直径** `[2R, 2R]`（不是半径）。

## matchName 速查

| 组件 | matchName | 说明 |
|---|---|---|
| 根 Contents 组 | `ADBE Root Vectors Group` | Shape Layer 的内容容器 |
| Shape Group | `ADBE Vector Group` | 独立形状组（每组可含独立 Stroke） |
| 组内 Containers | `ADBE Vectors Group` | Group 的 Contents 子属性 |
| 椭圆路径 | `ADBE Vector Shape - Ellipse` | 圆环的路径元素 |
| 椭圆 Size | `ADBE Vector Ellipse Size` | **2D 属性 [宽, 高]，是直径** |
| 椭圆 Position | `ADBE Vector Ellipse Position` | 2D 属性，路径位置偏移 |
| 矩形路径 | `ADBE Vector Shape - Rect` | 方形粒子形状 |
| 星形路径 | `ADBE Vector Shape - Star` | 星形粒子形状 |
| 填充 | `ADBE Vector Graphic - Fill` | 粒子填充 |
| 描边 | `ADBE Vector Graphic - Stroke` | 圆环描边 |
| 描边宽度 | `ADBE Vector Stroke Width` | 1D 属性 |
| 描边颜色 | `ADBE Vector Stroke Color` | 4D RGBA 属性 |
| 组透明度 | `ADBE Vector Group Opacity` | 单组整体透明度 |
| Group Transform | `ADBE Vector Transform Group` | 组的变换（Position 等） |
| Trim Paths | `ADBE Vector Filter - Trim` | 路径裁剪（做弧形线） |

## 关键代码（多 Group 方案）

```javascript
var shapeLayer = comp.layers.addShape();
shapeLayer.name = "扩散_线";
var contents = shapeLayer.property("ADBE Root Vectors Group");

for (var i = 0; i < ringCount; i++) {
    var group = contents.addProperty("ADBE Vector Group");
    group.name = "Ring_" + i;
    var groupContents = group.property("ADBE Vectors Group");

    var ellipse = groupContents.addProperty("ADBE Vector Shape - Ellipse");
    var sizeProp = ellipse.property("ADBE Vector Ellipse Size");
    sizeProp.expression = ringSizeExpr(i);  // 半径表达式

    var stroke = groupContents.addProperty("ADBE Vector Graphic - Stroke");
    var widthProp = stroke.property("ADBE Vector Stroke Width");
    widthProp.expression = strokeWidthExpr();
}
```

## 预防

- Size 属性是直径 `[2R, 2R]`，别把半径当直径写
- 每个 Group 独立挂表达式（Size/Stroke/Transform），可实现每环独立控制
- 所有距离参数建议用合成较短边的百分比 → **分辨率无关**
