---
tags: [extension, storage, id]
date: 2026-08-03
status: stable
related: []
source: https://github.com/Simiely/edge-multi-account-cookie/blob/main/DEVELOPMENT.md
---
# 浏览器扩展重装保留数据：manifest key 固定扩展 ID

**TL;DR**：`chrome.storage.local` **按扩展 ID 隔离**。加载解压缩扩展时若 manifest 没有 `key` 字段，每次生成**随机扩展 ID** → 重装后旧数据全部被隔离丢失。**在 manifest 加 `key`（RSA 公钥 SPKI Base64）固定扩展 ID**，重装/升级后数据保留。

## 问题

- 删除扩展重新加载后，账号数据还在但密码丢失（storage 按 ID 隔离）

## 根因

- 无 `key` 的解压扩展每次加载生成随机 ID，旧 ID 的数据被隔离

## 解决

```json
"key": "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA..."
```

```bash
# 生成方式（key.pem 私钥不提交 Git）
openssl genrsa 2048 | openssl pkcs8 -topk8 -nocrypt > key.pem
openssl rsa -pubout -outform DER -in key.pem -out pubkey.der
# pubkey.der base64 后放入 manifest "key" 字段
```

## 预防

- 需要持久化数据的扩展，**发布前就加好 `key`**（加了之后再改会变 ID，导致已发布用户数据丢失）
- key.pem 私钥绝不提交 Git（加入 .gitignore），否则他人可伪造你的扩展 ID
