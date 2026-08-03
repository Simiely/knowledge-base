---
tags: [node, web, cors]
date: 2026-08-03
status: stable
related: []
source: https://github.com/Simiely/workbuddy-credits-tool/blob/main/docs/问题记录/演示页跨域被拦.md
---
# 本地工具服务跨域被拦需开 CORS

**TL;DR**：本地工具被"其他端口页面"（预览服务、演示页）调用时属于跨域，服务端必须开 CORS，否则请求被浏览器拦截、永远 pending。

## 问题
自包含演示 HTML 由静态预览服务（如 `127.0.0.1:54359`）打开时，请求本地工具服务（如 `8080` 端口）点刷新无响应，按钮一直转；直连 8080 却正常。

## 根因
浏览器同源策略拦截跨域请求，本地工具服务端未返回 CORS 头，请求被浏览器静默拦截（表现就是"一直 pending"）。

## 解决
本地工具服务所有响应加 CORS 头，并放行预检请求：

```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, OPTIONS
Access-Control-Allow-Headers: Content-Type
OPTIONS 预检直接返回 204
```

## 预防
- 本地工具被"其他端口页面"调用时必须开 CORS（`*` 即可，本地工具无跨站风险）
- 排查"请求挂起"先分清：同源直连正常、跨域挂起 → 基本就是 CORS，看 Console 跨域报错

## 来源
提炼自 [workbuddy-credits-tool](https://github.com/Simiely/workbuddy-credits-tool)：
[演示页跨域被拦.md](https://github.com/Simiely/workbuddy-credits-tool/blob/main/docs/问题记录/演示页跨域被拦.md)
