---
tags: [c4d, dialog, ui]
date: 2026-08-03
status: stable
related: [解决方案/C4D2026SDK破坏性迁移清单.md]
source: https://github.com/Simiely/c4d-userdata-manager/blob/main/DEVELOPMENT.md
---
# C4D 动态列表控件方案（ListView 替代）

**TL;DR**：C4D 2026 移除了 ListView，用 **ScrollGroup + 动态控件**模拟多列列表。核心模式：`LayoutFlushGroup` 只清子控件不删组 + **每行独立 Group（cols=4, rows=1）保证行对齐** + 控件 ID 用「基准值 + 索引偏移」反推条目。

## 问题

- ListView 移除后需要动态多列列表
- 动态添加的条目垂直居中不对齐（Button/StaticText 高度计算方式不同）

## 根因

- `cols=4, rows=0` 的 grid flow 布局中，不同控件类型（Button/StaticText）高度计算不同，无法保证每行顶部对齐
- 重复 `GroupBegin` 已存在组不会更新布局参数（首次创建后固定）

## 解决（终版方案）

```python
# CreateLayout — 内容容器单列 + 可滚动
self.ScrollGroupBegin(_gScroll, flags=..., scrollflags=c4d.SCROLLGROUP_VERT)
self.GroupBegin(_gListContent, flags=c4d.BFH_SCALEFIT, cols=1, rows=0, title="")
self.GroupEnd()
self.GroupEnd()

# _refresh_list — 每行用独立 Group 包裹，保证行对齐
def _refresh_list(self):
    self.LayoutFlushGroup(_gListContent)
    for i, e in enumerate(self._entries):
        self.GroupBegin(0, flags=c4d.BFH_SCALEFIT, cols=4, rows=1, title="")
        self.GroupBorderSpace(0, 0, 0, 0)
        self.AddStaticText(..., inith=18, ...)   # 序号
        self.AddButton(..., inith=18, ...)       # 名称（可点击选中）
        self.AddStaticText(..., inith=18, ...)   # 类型
        self.AddStaticText(..., inith=18, ...)   # 默认值
        self.GroupEnd()
    self.LayoutChanged(_gScroll)
```

点击 Name Button 通过控件 ID 反推条目索引：

```python
if _ROW_BASE <= mid < _ROW_BASE + 9999:
    idx = (mid - _ROW_BASE) // _ROW_STRIDE
```

## 预防

- `LayoutFlushGroup` 只清空子控件，不删除组本身
- **不要对已存在组重复 `GroupBegin(id, ...)`**——布局参数（cols/rows/flags）首次创建时固定
- 刷新时机：`LayoutFlushGroup` → 添加控件 → `LayoutChanged(父group)`
- 内容容器 `cols=1, rows=0`（单列动态行）+ 每行独立 Group（`cols=4, rows=1`）+ 统一 `inith` + `GroupBorderSpace(0,0,0,0)` 消除行内边距
