---
tags: [extension, mv3, service-worker]
date: 2026-08-03
status: stable
related: []
source: https://github.com/Simiely/edge-multi-account-cookie/blob/main/DEVELOPMENT.md
---
# MV3 Service Worker 注册规范

**TL;DR**：MV3 的 Service Worker 三个硬性要求——①`background.service_worker` 必须是**字符串**（不能是数组）；②**不能有** `background.persistent` 字段；③**监听器必须在顶层同步注册**（放在 promise/回调里可能丢失）。

## 问题

- `Cannot read properties of undefined (reading 'onClicked')`
- `Service worker registration failed. Status code: 15`

## 根因

1. `type: "module"` 但没有实际 import/export → Edge 解析失败
2. 监听器注册在异步回调内 → SW 启动时序下可能丢失

## 解决

```json
"background": {
  "service_worker": "background.js"
}
```

```js
// ✅ 顶层同步注册
chrome.runtime.onInstalled.addListener(() => { ... });

// ❌ 异步回调内注册（可能丢失）
chrome.storage.local.get(["key"], ({ key }) => {
  chrome.action.onClicked.addListener(handleClick);
});
```

## 预防

- 没有 import/export 就不加 `type: "module"`
- 所有 `chrome.*` 事件监听器放脚本顶层，不放 promise/回调
- 注册失败（Status code 15）先查这两项
