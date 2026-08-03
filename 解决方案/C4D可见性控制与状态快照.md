---
tags: [c4d, sdk, visibility]
date: 2026-08-03
status: stable
related: []
source: https://github.com/Simiely/c4d-mesh-face-sorter/blob/main/DEVELOPMENT.md
---
# C4D 可见性控制与状态快照

**TL;DR**：C4D Python API 没有统一的「隐藏/显示」接口——`BaseObject.Hide()` **不存在**，`BIT_HIDDEN` 无效果；用 `SetEditorMode(MODE_OFF/ON)` 最可靠（配合 `BIT_IGNOREDRAW` 兼容）。做孤立显示这类临时操作，必须遵循「**第一次进入时保存快照 → 操作 → 退出时恢复并清空**」。

## 问题

- 点击隐藏按钮物体没反应（`Hide()` 报 AttributeError，被 try/except 静默吞掉）
- 老工程中 `BIT_IGNOREDRAW` 无效（对象属于 Layer，Layer 可见性覆盖对象级 Bit）
- 显示全部把用户之前手动隐藏的对象也显示出来
- 多次切换孤立对象后，显示全部只能恢复到最后一次状态

## 根因

- C4D 可见性层级：**Layer 级别 > 对象级别 > Bit 标志**，Bit 标志最不可靠
- 显示全部时强制 `MODE_UNDEF`，没保存孤立前原始状态
- 每次切换都 `clear()` 快照再保存，快照被反复重置

## 解决

1. 隐藏/显示统一用 `SetEditorMode(c4d.MODE_OFF)` / `SetEditorMode(c4d.MODE_ON)`，配合 `SetBit(BIT_IGNOREDRAW)` 兼容
2. 临时操作的状态快照：**只在第一次进入时保存**，退出时恢复并清空

```python
if not self._original_modes:   # 只在第一次独显时保存快照
    self._original_modes = snapshot()   # 保存所有对象编辑器模式 + BIT_IGNOREDRAW
```

## 预防

- 可见性功能先确认目标 API 存在，异常别静默吞掉
- 临时操作（孤立/预览/高亮）统一「保存快照 → 操作 → 恢复」模式，快照语义 = 保存「进入临时状态前那一刻」的完整状态，不是「每次切换时」的状态
