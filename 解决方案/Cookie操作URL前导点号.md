---
tags: [extension, cookie, url]
date: 2026-08-03
status: stable
related: [解决方案/MV3扩展权限三层防线.md]
source: https://github.com/Simiely/edge-multi-account-cookie/blob/main/DEVELOPMENT.md
---
# Cookie 操作 URL 前导点号处理

**TL;DR**：Cookie 的 `domain` 字段以 `.` 开头（`.example.com`），直接拼 URL 得到 `http://.example.com/`（**非法 URL**），`cookies.set/remove` **静默失败**。操作前必须 `slice(1)` 去掉前导点号。

## 问题

- 清除 Cookie 后仍有 15/17 个残留，用户仍处于登录状态（无任何报错）

## 根因

- `domain` 前导点号导致 URL 非法，remove 静默失败

## 解决

```js
function cookieUrl(cookie) {
  const domain = cookie.domain.startsWith('.') ? cookie.domain.slice(1) : cookie.domain;
  return `${cookie.secure ? 'https' : 'http'}://${domain}${cookie.path || '/'}`;
}
```

## 预防

- 所有 `cookies.set()` 和 `cookies.remove()` 的 URL 构造统一走 `cookieUrl()` 处理前导点号
- 判断成功与否不能只看"没报错"——用返回值确认（remove 返回 null 表示失败）
