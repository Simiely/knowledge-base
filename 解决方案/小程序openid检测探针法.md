---
tags: [miniprogram, cloudbase]
date: 2026-08-03
status: stable
related: [微信云开发双向同步架构与防循环.md]
source: https://github.com/Simiely/potty-training-miniprogram/blob/main/DEV.md
---
# 小程序 openid 检测：探针法（无需云函数）

**TL;DR**：客户端识别"当前用户是谁"用探针法——写入一条带 `_probe:true` 标记的临时记录，读取云数据库自动注入的 `_openid`（必为当前账号）后立即删除，零残留、100% 可靠，无需部署云函数。

## 问题
需要区分"这条记录是不是我创建的"（如历史页只对自己的记录显示删除/编辑按钮）。云数据库每行自动带 `_openid` 字段，但客户端无法直接读取自己的 openid。

## 根因
方案演进中踩的坑：
1. **deviceId**（本地生成 UUID）：清缓存/换设备后变化 → 同一用户无法管理自己旧记录
2. **云函数 `getWXContext().OPENID`**：100% 可靠，但「上传并部署」在某些账号/环境权限下不可用
3. **多数票检测**（读最近 10 条取出现最多的 `_openid`）：多人混合记录时误判——他人记录更近/更多时，把当前用户误判为他人 openid

## 解决
**探针法**（纯客户端，无云函数）：
- `add` 一条临时记录（`_probe: true`）→ 立即 `doc(id).get()` 读其自动注入的 `_openid`（必为当前账号）→ 立即 remove
- 优先级：内存 → Storage 缓存 → 探针法探测并写回
- 读取记录时 `filter(r => !r._probe)` 双保险清理；探针前先 `where({_probe: exists})` 清理历史残留

## 预防
- 客户端识别当前用户一律探针法，别用多数票/deviceId
- 探针记录必须带标记 + 用完即删 + 读取时过滤，避免残留垃圾数据

## 来源
提炼自 [potty-training-miniprogram](https://github.com/Simiely/potty-training-miniprogram)：
[DEV.md #19](https://github.com/Simiely/potty-training-miniprogram/blob/main/DEV.md)（探针法）、[#11](https://github.com/Simiely/potty-training-miniprogram/blob/main/DEV.md)（多数票缺陷）
