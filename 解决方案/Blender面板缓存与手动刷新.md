---
tags: [blender, panel, cache]
date: 2026-08-03
status: stable
related: []
source: https://github.com/Simiely/blender-mesh-face-sorter/blob/main/DEVELOPMENT.md
---
# Blender 面板缓存与手动刷新

**TL;DR**：Blender Panel 的 `draw()` 高频调用 + `depsgraph_update_post` 每帧触发，自动刷新会让大场景卡死。**用纯手动刷新**（用户点按钮才重扫，`load_post` 换文件时唯一自动失效）；缓存存原始数据，排序即时完成（昂贵操作与廉价操作解耦）。

## 问题

- 自动监听场景变化刷新列表 → 大场景卡死
- 切换排序方式需要重新扫描吗

## 根因

- `depsgraph_update_post` 每帧触发，在 Panel draw() 高频调用模型下扫描是重负载
- 扫描 O(n) 且昂贵（遍历所有物体、读 mesh 数据），排序 O(n log n) 便宜（纯内存操作）

## 解决

1. **纯手动刷新**：增删物体后用户点「刷新列表」才重扫；唯一自动失效是 `load_post`（换文件清缓存）
2. **缓存粒度**：缓存存原始扫描 stats，排序在 `collect_mesh_stats()` 即时完成——切换排序不重扫，只重排缓存

## 预防

- 不要轻易改回自动刷新；"让用户掌控刷新时机"比"智能自动刷新"更可靠
- 昂贵操作与廉价操作解耦：扫描只做一次，排序/过滤等廉价操作随时可切
