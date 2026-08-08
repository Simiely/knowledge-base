---
tags: [blender, ui, cjk]
date: 2026-08-03
status: stable
related: []
source: https://github.com/Simiely/blender-mesh-face-sorter/blob/main/DEVELOPMENT.md
---
# Blender CJK 字符串宽度截断

**TL;DR**：中文名称在 Blender UI 中占 2 个字符宽度，用 `len()` 固定截断会导致列表参差不齐。**按显示宽度截断**：`ord(ch) > 0x2E80`（CJK Radicals Supplement 起点）算 2 宽度，其余算 1。

## 问题

- 中文物体名称在 UI 中占用宽度是英文字符的 2 倍，固定字符截断导致显示参差不齐

## 解决

```python
def _display_width(s):
    return sum(2 if ord(ch) > 0x2E80 else 1 for ch in s)

def _truncate_name(name, max_width):
    # 按显示宽度截断，超宽补 "…"
```

- `0x2E80` 覆盖中日韩统一表意文字及扩展区
- `…`（U+2026）被正确识别为宽度 1，无截断误差

## 预防

- 中文 UI 场景（名称截断、对齐、表格列宽）统一用显示宽度计算，不用 `len()`
- 对 CJK 友好的处理对所有中文界面工具都有价值（AE/C4D/Blender 通用）
