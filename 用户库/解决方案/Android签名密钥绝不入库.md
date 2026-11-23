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

## 反向回流：存量项目「已知风险但不迁移」要写清（2026-11-23）

[dashwidget](https://github.com/Simiely/dashwidget) 复核时确认：仓库与 git 历史内仍有 `keystore/dashwidget.jks`，但 `app/build.gradle` 已不在源码写死密码，改走 `keystore.properties` 注入、无凭据时 release 回退 debug 签名。

彻底清除要 `git filter-repo` 重写历史 + 轮换密钥 + 用户重新安装，代价是**失去 v3.1 起各版的覆盖安装能力**。因此该项目的明确决定是：登记为已知风险、**默认不迁移**，并在 AGENTS / 技术栈规则 / README 三处写同一口径，不靠「悄悄留着」。

给存量仓库的口径：规范约束的是「新项目绝不入库」；已经入库的要写清 **风险 + 迁移代价 + 明确决定**，而不是一刀切删除或只字不提。另注意 CI workflow 里也不该明文写 `storePassword` / `keyPassword`，这类字符串同样属于凭证。

## 来源
提炼自 [meituan-bike-reminder](https://github.com/Simiely/meituan-bike-reminder)：
[DEVELOPMENT.md ①④⑦](https://github.com/Simiely/meituan-bike-reminder/blob/main/DEVELOPMENT.md)（签名密钥入库 / git 历史清除）；
2026-11-23 反向回流自 [dashwidget](https://github.com/Simiely/dashwidget) 的「已知风险 / 默认不迁移」评估。
