---
tags: [android, security, git]
date: 2026-08-03
status: stable
related: []
source: https://github.com/Simiely/meituan-bike-reminder/blob/main/DEVELOPMENT.md
---
# Android 签名密钥绝不入库（含 git filter-repo 清除）

**TL;DR**：签名密钥/密码/凭证**永远从环境变量或本地忽略文件来，绝不写进 git**。已入库的密钥要彻底清除必须 `git filter-repo` 重写历史（`git rm` 不够），已泄露的密钥永久作废必须轮换。

## 问题
仓库里直接提交了 `release.keystore`，`build.gradle.kts` 明文写死 `storePassword`、`keyAlias`。任何人 clone 即可用同一把密钥签发「更新包」覆盖你的 App。

## 根因
把「能直接构建」的便利凌驾于「密钥保密」之上；以为私有仓库就安全。且 `git rm` 只改当前树，密钥仍留在所有历史提交里，`git log` + 旧 commit 随时能翻出。

## 解决
1. **密钥与密码绝不入库**：放 `keystore.properties`（加 `.gitignore`）+ 支持环境变量 `KEYSTORE_*` 注入（CI 用 Secret）
2. **已泄露密钥永久不可信**：`keytool` 生成新密钥轮换，并提醒用户重新安装
3. **彻底清除历史**：`git filter-repo --path <file> --invert-paths --force`（需 `pip install git-filter-repo`）→ `git push --force`；操作不可逆，重写前通知协作者重新 clone
4. 配置模板提交 `keystore.properties.example`，实际文件不入库

## 预防
- 任何带签名/凭证的仓库（Android / iOS / npm / 云服务），「能一键构建」和「凭证安全」必须分开
- 提交前检查：`git log --all --oneline -- <file>` 确认密钥从未进过历史

## 来源
提炼自 [meituan-bike-reminder](https://github.com/Simiely/meituan-bike-reminder)：
[DEVELOPMENT.md ①④⑦](https://github.com/Simiely/meituan-bike-reminder/blob/main/DEVELOPMENT.md)（签名密钥入库 / git 历史清除）
