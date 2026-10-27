---
tags: [python, auth, dependency, bcrypt]
date: 2026-10-27
status: stable
related: []
source: docs/03-踩坑与排错.md @ Simiely/homekeeper（仓库已于 2026-10-27 删除，内容已提炼留存）
---
# passlib 与 bcrypt 5.x 不兼容 → 改用 pbkdf2_sha256

**TL;DR**：`passlib 1.7.4` + `bcrypt 5.x` 下登录注册必炸（`ValueError: password cannot be longer than 72 bytes` + `module 'bcrypt' has no attribute '__about__'`）。两条出路：**降到 `bcrypt==4.0.1`**，或**改用 passlib 内置 `pbkdf2_sha256`**（零外部依赖，无长度限制）。

## 问题

自建账号系统，`requirements.txt` 里写了 `passlib[bcrypt]`，本地能装能跑，一升级依赖就全挂：

```
ValueError: password cannot be longer than 72 bytes
AttributeError: module 'bcrypt' has no attribute '__about__'
```

## 根因

- bcrypt 5.x 改了底层 API，并把 72 字节上限变成硬失败（旧版是静默截断）；
- passlib 1.7.4 已多年未更新（最后一次发布 2020 年），它按旧 API 去探测 `bcrypt.__about__.__version__` 并自行拼接待哈希内容，两头对不上；
- 这不是"配置问题"，是**两个库的版本契约破裂**，改参数无解。

## 解决

```python
# app/core/security.py
CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
```

```text
# requirements.txt —— 去掉 [bcrypt] 额外依赖
passlib>=1.7.4
```

- `pbkdf2_sha256` 是 passlib 纯 Python 实现，**不依赖外部 bcrypt 包**，也没有 72 字节限制；
- 对家庭自用 / 内网服务的威胁模型足够（OWASP 认可 PBKDF2）；
- 若坚持 bcrypt：固定 `bcrypt==4.0.1`，但要在依赖里**精确钉住**，否则下次 `pip install -U` 会再炸一次。

## 预防

- **密码哈希属于"依赖敏感区"**：要么用标准库（Python 的 `hashlib.scrypt`、Node 的 `crypto.scrypt`），要么精确锁版本。中间态最危险。
- `passlib[bcrypt]` 这种 extra 依赖是隐性升级点 —— **装的时候不报错，跑起来才报错**，CI 里必须有"真登录一次"的集成测试，只测 import 发现不了。
- 本项目最终采用的判断：**少一个原生依赖 = 少一个升级断裂点**，与「能用标准库就不装包」的总纲一致。

## 来源

提炼自 拾光集（`Simiely/homekeeper`）`docs/03-踩坑与排错.md` §4；仓库已于 2026-10-27 删除，完整历史备份见本地 `homekeeper-2026-10-27.bundle`。相关：`解决方案/Android签名密钥绝不入库.md`（同为凭证类决策）。
