---
tags: [web, safari, performance]
date: 2026-08-03
status: stable
related: []
source: https://github.com/Simiely/learning-platform/blob/main/DEV.md
---
# 关键 JS 库本地托管，不用 CDN

**TL;DR**：Safari 智能追踪防护（Tracking Prevention）会阻止 CDN 域的 localStorage/Web Storage 访问，导致 CDN 引入的 JS 库脚本挂起卡顿。关键 JS 库下载到本地 `static/` 同域托管最可靠。

## 问题
页面突然变得非常卡顿，控制台报：
```
Tracking Prevention blocked access to storage for https://cdn.jsdelivr.net/.../alpine.min.js
```

## 根因
Safari 智能追踪防护默认拦截第三方域（CDN）对本地存储的访问。Alpine.js 等库启动时会访问 localStorage，被拦截后脚本执行挂起。

## 解决
将 Alpine.js 从 CDN 下载到 `static/js/alpine.min.js`，模板改用 `{% static 'js/alpine.min.js' %}`。同域静态文件不受追踪防护限制。

## 预防
- 关键 JS 库（框架、状态库、交互库）不用 CDN，下载到项目本地托管
- 排查"CDN 脚本卡顿"先看 Console 是否有 Tracking Prevention 拦截字样

## 来源
提炼自 [learning-platform](https://github.com/Simiely/learning-platform)：
[DEV.md](https://github.com/Simiely/learning-platform/blob/main/DEV.md)（Safari Tracking Prevention 一节）
