---
tags: [node, web, proxy, router]
date: 2026-10-31
status: stable
related: []
source: https://github.com/Simiely/agent-workbench/blob/main/DEVELOPMENT.md
---
# 平台反代下API绝对路径失效

**TL;DR**：工具被平台反代到子路径（如 `/tool/xxx/`）时，前端写死 `/api/...` 会打到平台根 → 404；接口前缀必须按页面自身路径在运行时推导。

## 问题

本地直连 `http://127.0.0.1:8151/` 一切正常；部署到平台 `/tool/agent-workbench/` 后，页面空数据、所有「添加」都失败。服务端 `/health` 正常、存储目录可写，服务端日志里**根本收不到这些请求**。

## 根因

前端把接口写成绝对路径 `/api/...`。浏览器按**站点根**解析以 `/` 开头的路径，而不是按页面所在子路径：

- 直连根路径：`/api/...` → 工具自己 ✅
- 反代子路径：`/api/...` → `平台域名/api/...` → 平台根没有该路由 → 404 ❌

反代「剥前缀转发」只对 `/tool/xxx/*` 生效，`/api/*` 不匹配前缀，自然不会进到工具进程。

## 解决

用页面自身路径算前缀，所有请求拼在它后面：

```js
var API_BASE = (function () {
  var p = location.pathname || '/';
  if (/\/[^/]*\.html?$/i.test(p)) p = p.replace(/[^/]+$/, ''); // 去掉 index.html
  if (p.charAt(p.length - 1) !== '/') p += '/';
  return p;
})();

fetch(API_BASE + 'api/query?db=tasks');
```

平台若注入全局变量（如 `window.__BASE__`），可作为首选来源，路径推导作 fallback。

同时把失败提示带上服务端 `error` 原文，否则只剩「添加失败」四个字，无法区分 404（路径错）与 500（磁盘/权限）。

## 预防

- 前端代码里**不允许**出现裸的 `/api/...`，统一走运行时前缀变量
- 测试必须覆盖「子路径挂载」：本地起最小反代（无斜杠 302 补 `/` + 剥前缀转发），断言所有 API 请求都带前缀
- 「本地全绿、上线全挂」先怀疑路径基准，而不是数据、权限或缓存
- 服务端 `/health` 顺手暴露存储可写性与数据目录，部署排障少走一轮

## 来源

提炼自 [agent-workbench](https://github.com/Simiely/agent-workbench) v1.0.1 修复：
[DEVELOPMENT.md](https://github.com/Simiely/agent-workbench/blob/main/DEVELOPMENT.md)
