---
tags: [android, webview, network, http]
date: 2026-11-24
status: stable
related: [本地工具服务跨域被拦需开CORS.md]
source: https://github.com/Simiely/dashwidget/blob/main/DEVELOPMENT.md
---
# Android 9 起明文 HTTP 默认被阻断，页面加载不出来

**TL;DR**：`targetSdk ≥ 28` 且未声明 `android:networkSecurityConfig` 时，WebView / 网络库加载 http 主框架会被系统以 `net::ERR_CLEARTEXT_NOT_PERMITTED` 直接拦下。用户能保存 URL 却永远加载不出来；显式放行明文，并让主框架错误即时可见。

## 问题
内网 / 自建服务常是 `http://192.168.x.x` 或 `http://host:port`。App 里这类看板能保存、点预览却始终生成不出画面，https 站点完全正常；错误提示要空等 30 秒才显示「页面加载超时，已保留旧图」，完全看不出真实原因。

## 根因
1. **系统默认策略**：Android 9（API 28）起 `cleartextTrafficPermitted` 默认 false，`targetSdk ≥ 28` 的应用加载 http 主框架被拦，不是页面或服务器的问题
2. **校验与加载不对等**：URL 校验只要求 `startsWith("http")`，http 能存但必加载失败——保存成功给了用户错误的安全感
3. **错误只写日志不终态**：`onReceivedError` 只记日志、不结束等待循环，用户看到的是超时而不是 `ERR_CLEARTEXT_NOT_PERMITTED`
4. **牵连 Cookie**：清 Cookie 时把 URL 写死成 `https://$host/`，http 站点「重新登录」清不干净

## 解决
1. 新增 `res/xml/network_security_config.xml`，`base-config cleartextTrafficPermitted="true"`，在 `<application>` 用 `android:networkSecurityConfig` 引用；地址由用户任意填写、无法枚举域名，只能全局放行
2. **不放宽 TLS**：HTTPS 与证书校验保持系统默认，`onReceivedSslError` 继续 cancel；http 页面跳到自签名 HTTPS 仍会被拦，是另一处策略
3. 主框架错误即时写入可读原因并结束等待，后台链路同样补错误日志
4. 清 Cookie 按原始 scheme 构造 URL，别写死 https
5. 所有 WebView 继承 application 级配置，不用逐个改 settings

## 预防
- 凡是「用户自填 URL / 内网地址」的功能，先把 http 场景列进验收清单；Android 9 是分水岭
- 错误回调必须改变状态机，不能只打日志；否则用户看到的是超时而不是根因
- 全局放行明文的代价要写进文档：App 内任何 http 请求都被允许，日后可按域名收紧
- 改了 Manifest 时，若仓库有「Manifest 与基线快照逐字节一致」的静态校验，必须同步快照文件，否则 CI 红

## 来源
提炼自 [dashwidget](https://github.com/Simiely/dashwidget) v3.10 修复（见 [DEVELOPMENT.md](https://github.com/Simiely/dashwidget/blob/main/DEVELOPMENT.md) 与 [CHANGELOG.md](https://github.com/Simiely/dashwidget/blob/main/CHANGELOG.md)）。同类「本地服务被拦」参见 [本地工具服务跨域被拦需开CORS](./本地工具服务跨域被拦需开CORS.md)。
