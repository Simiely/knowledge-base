---
tags: [node, web, async]
date: 2026-08-03
status: stable
related: []
source: https://github.com/Simiely/workbuddy-credits-tool/blob/main/docs/问题记录/刷新按钮无限转圈.md
---
# 请求必须带超时与 UI 状态 finally 恢复

**TL;DR**：所有网络请求必须有超时保护；按钮/加载状态的恢复必须走 `finally`，否则接口挂起时 UI 永远卡在加载态。

## 问题
点击「刷新」后按钮一直转圈，看起来卡死，接口明明挂了却没有任何反馈。

## 根因
两层漏洞叠加：
1. 服务端请求无超时，第三方接口慢/挂起时请求永不返回
2. 前端无兜底，按钮状态依赖正常流程恢复，异常路径上永远不恢复

## 解决
双层超时 + finally 兜底：
- **服务端**：单账号请求 8s 超时（`AbortController`），超时报"接口响应超时"，单个失败不拖累其他
- **前端**：整体 12s 超时，超时报"刷新超时，请重试"
- **UI 状态**：loading 标志单点控制（`setBusy()`），任何路径（成功/失败/超时）都走 `finally` 恢复

## 预防
- 所有请求必须带超时，这是异步编程的基本盘
- 按钮/加载状态用单点控制函数，恢复逻辑只写在 `finally` 里，杜绝"某个路径忘了恢复"

## 来源
提炼自 [workbuddy-credits-tool](https://github.com/Simiely/workbuddy-credits-tool)：
[刷新按钮无限转圈.md](https://github.com/Simiely/workbuddy-credits-tool/blob/main/docs/问题记录/刷新按钮无限转圈.md)
