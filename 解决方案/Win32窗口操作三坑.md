---
tags: [windows, win32, csharp]
date: 2026-08-03
status: stable
related: []
source: https://github.com/Simiely/WindowTinter/blob/main/DEV.md
---
# Win32 窗口操作三坑：SetWindowPos 阻塞 / WinEvent 死循环 / hwnd TOCTOU

**TL;DR**：做窗口覆盖/蒙版/暗化类工具必读：① 跨进程 `SetWindowPos(SWP_FRAMECHANGED)` 会阻塞 UI 线程，用 `InvalidateRect`；② 改窗口样式会触发 WinEvent 回环，必须加变化守卫；③ hwnd 会被 OS 回收复用，操作前必须 `IsWindow` 再查。

## 问题
目标窗口切后台时程序卡死拖不动；前后台切换偶尔闪白；某些窗口设置透明度无效果。

## 根因（三个独立坑）
1. **`SetWindowPos(SWP_FRAMECHANGED)` 阻塞**：底层是同步 `SendMessage(WM_NCCALCSIZE)` 到目标进程，目标消息泵忙时 UI 线程卡死
2. **WinEvent 死循环**：`SetTargetAlpha → SetWindowLong(改 WS_EX_LAYERED) + InvalidateRect → 触发 EVENT_OBJECT_LOCATIONCHANGE → 回调 → 再改 → 🔄 无限回环`
3. **hwnd 回收复用**：窗口销毁后 hwnd 可能被 OS 回收给新窗口，`SetWindowLong` 前仅靠入口守卫不够（两次 Win32 调用之间有 TOCTOU 窗口）

## 解决
1. 用 `InvalidateRect` 替代 `SetWindowPos(SWP_FRAMECHANGED)`（异步、不阻塞、效果等同）；不用 ThreadPool 做跨进程窗口操作
2. 双重守卫：`Refresh()` 中 rect/visible 不变则不触发 OnUpdate（阻断位置回环）；`OnUpdate` 内部 `_lastBgAlpha` 与目标值比较不变则不调 SetTargetAlpha（阻断重复修改回环）
3. 每次 `SetWindowLong` 前重新 `IsWindow(hwnd)` 检查（不能只靠入口守卫）

## 预防
- 跨进程窗口操作：优先异步 API（InvalidateRect），避免同步 SendMessage
- 窗口事件监听：改状态前先判断"值是否真的变了"，用守卫拦截自触发回环
- hwnd 操作模式：操作前即时校验有效性，不缓存信任

## 来源
提炼自 [WindowTinter](https://github.com/Simiely/WindowTinter)：
[DEV.md ②③④](https://github.com/Simiely/WindowTinter/blob/main/DEV.md)（后台透明/死循环/闪白）等
