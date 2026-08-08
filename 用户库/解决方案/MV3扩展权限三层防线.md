---
tags: [extension, mv3, permission]
date: 2026-08-03
status: stable
related: []
source: https://github.com/Simiely/edge-multi-account-cookie/blob/main/DEVELOPMENT.md
---
# MV3 扩展权限三层防线

**TL;DR**：**`cookies` 权限不包含主机权限**（官方原文：cookies permission does not imply host permissions）——`chrome.cookies.getAll()` 返回空数组**不报错**，永远检测不到权限缺失。三层防线：`activeTab`（点击时临时权限）+ `optional_host_permissions`（按需申请）+ **`chrome.permissions.contains()` 主动检测**（不等 API 报错）。

## 问题

- `chrome.cookies.getAll({domain})` 返回 `[]`，无任何报错，只有 0 个 Cookie
- 用户以为扩展坏了，实际是没拿到主机权限

## 根因

- MV3 中 `cookies` 权限**不隐含主机权限**；`scripting` 也是独立 permission 必须显式声明
- 空数组不报错 → 无法靠错误回调发现

## 解决

```json
"permissions": ["cookies", "scripting", "activeTab", "contextMenus"],
"optional_host_permissions": ["<all_urls>"]
```

```js
// ✅ 主动检测，不等 API 报错
const hasPerm = await chrome.permissions.contains({ origins: [`*://${domain}/*`] });
if (!hasPerm) { /* 引导用户点授权按钮 */ }
```

## 预防

- 涉及 cookies/host 权限的功能一律先 `contains` 检测，再决定是否引导授权
- 权限最小化：不用 `<all_urls>`（安装即授权所有网站），用 activeTab + optional 按需申请
- `scripting`/`contextMenus` 等独立权限记得在 manifest 显式声明（**Edge 的 contextMenus 必须声明，Chrome 文档说不需要但 Edge 需要**）
