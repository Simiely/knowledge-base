---
tags: [blender, undo, bpy]
date: 2026-08-03
status: stable
related: []
source: https://github.com/Simiely/blender-mesh-face-sorter/blob/main/DEVELOPMENT.md
---
# Blender UNDO 与 bpy.data 引用陷阱

**TL;DR**：Operator 里 `bpy.data.objects.remove()` 删除物体后，UNDO 恢复该物体时**缓存中的 Python 引用变成野指针** → 连锁 ReferenceError。Blender UNDO 对 `bpy.data` 操作深层耦合，与其修复不如避免——**让 Blender 原生 Delete 处理，插件只负责刷新**。

## 问题

`bl_options = {'REGISTER', 'UNDO'}` + `bpy.data.objects.remove()` → 用户撤销时缓存引用失效，连锁 ReferenceError，不稳定复现。

## 根因

- UNDO 恢复物体时，插件缓存里保存的 Python 对象引用已失效（野指针）
- 尝试 `invalidate_cache()` 提前调用、拓宽异常捕获到 `Exception`——仍不稳定

## 解决

**移除所有删除相关代码**：删除空网格改为用户手动 Delete + 点刷新；插件只负责扫描/缓存/展示，不碰 `bpy.data` 的删除操作。

## 预防

- 涉及 `bpy.data` 删除 + UNDO 的场景，先评估引用生命周期；缓存引用对象时要考虑 UNDO 恢复
- 与其在脆弱路径上打补丁，不如避免：让 Blender 原生机制处理删除，插件做"观察者"而非"操作者"
