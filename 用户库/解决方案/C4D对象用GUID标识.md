---
tags: [c4d, sdk, object]
date: 2026-08-03
status: stable
related: []
source: https://github.com/Simiely/c4d-mesh-face-sorter/blob/main/DEVELOPMENT.md
---
# C4D 对象标识用 GUID 不用名称

**TL;DR**：C4D 场景中**对象名称不唯一**（可同名），按名称查找会返回第一个匹配导致选中错误；用 `GetGUID()` 作为唯一标识保存和查找。

## 问题

- 场景有多个同名对象时，点击列表某行选中错误对象
- 排序/筛选后按名称找回对象不可靠

## 根因

- `_find_object(doc, name)` 返回第一个同名匹配的对象，与目标对象不是同一个

## 解决

```python
# 扫描时保存 GUID
guid = cur.GetGUID()
# 查找时用 GUID 精确匹配
obj = _find_object(doc, guid)
```

## 预防

- C4D 对象唯一标识一律用 `GetGUID()`（或对象指针），名称只作显示用途
- 涉及"列表行 → 场景对象"映射的功能，数据层保存 GUID，事件处理用 GUID 匹配
