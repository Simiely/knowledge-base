---
tags: [fastapi, cors, static]
date: 2026-10-27
status: stable
related: []
source: docs/03-踩坑与排错.md @ Simiely/homekeeper（仓库已于 2026-10-27 删除，内容已提炼留存）
---
# FastAPI 静态挂载顺序与 CORS 凭据冲突

**TL;DR**：① `app.mount("/", StaticFiles(...))` **必须放在所有 `include_router` 之后**，否则 `/` 的通配挂载会把 `/api/*` 吞掉；② `allow_credentials=True` 与 `allow_origins=["*"]` **不能同时存在**，浏览器会直接拒绝，这是 CORS 规范禁止的组合而不是配置错误。

## 问题

前端与 API 同进程部署（FastAPI 同时托管 SPA 与 `/api`）时，两个症状经常同时出现：

- 调接口返回的是 HTML 首屏，或前端静态资源 404；
- 前端带 `Authorization` 头请求报 CORS 错；改成 `allow_origins=["*"]` 之后错误变成"凭据不能与通配来源同时使用"。

## 根因

1. **挂载顺序**：`StaticFiles` 挂在 `/` 上等于一条兜底路由，Starlette 按注册顺序匹配，先注册的通配挂载会截住后面所有路由。API 路由注册在它之后 → 永远匹配不到。
2. **CORS 规范**：`Access-Control-Allow-Origin: *` 与 `Access-Control-Allow-Credentials: true` 是互斥的，浏览器按规范拒绝（不是 bug，也不能靠放宽配置绕开）。而 `allow_credentials=True` 在"同源部署"时**根本不需要** —— 同源请求本来就会带上 Cookie。

## 解决

```python
# 1. 路由全部注册完，最后才挂静态
app.include_router(auth_router)
app.include_router(items_router)
app.mount("/", StaticFiles(directory="static", html=True), name="static")
```

```python
# 2. 同源部署：不需要 allow_credentials，去掉即可
app.add_middleware(CORSMiddleware, allow_origins=CORS_ORIGINS.split(","))
```

- **真需要跨域带凭据时**（如安卓 App / 独立前端域）：`allow_origins` 填**具体域名**（逗号分隔走 `.env`），永远不要用 `*`。
- 判断句：**这个请求是同源的吗？** 同源就不要开 CORS 凭据，开了只会把自己逼进互斥组合。

## 预防

- 静态挂载在 `main.py` 里永远写在文件末尾，并加注释说明"必须在路由之后"，否则下一个人重构时很容易顺手挪上去。
- CORS 来源走配置项（`CORS_ORIGINS`），默认空 = 不启用；本地/内网直连不配也能跑，跨域场景才显式收紧。生产环境禁止 `*`。
- 排错顺序：先看**返回内容类型**（HTML = 路由被静态吞了），再看**响应头是否带 ACAO**（带 `*` 又要求凭据 = 互斥），最后才怀疑业务代码。

## 来源

提炼自 拾光集（`Simiely/homekeeper`）`docs/03-踩坑与排错.md` §2、§3、§12；仓库已于 2026-10-27 删除，完整历史备份见本地 `homekeeper-2026-10-27.bundle`。
