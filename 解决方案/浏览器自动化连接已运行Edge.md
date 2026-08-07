---
tags: [browser, automation, edge, cdp, windows]
date: 2026-08-07
status: stable
related: []
---
# 浏览器自动化连接已运行Edge：CDP 远程调试

**TL;DR**：AI 要"驾驶"一个用户看得见、已登录的浏览器（复用登录态、避免 headless 盲操作）时，让用户在 Edge 开 `edge://inspect/#remote-debugging` 的「允许远程调试」开关，然后 `agent-browser --cdp 9222` 连上去——不再自启 headless daemon。

## 问题
浏览器自动化工具（agent-browser CLI）默认自己启动一个 **headless** Chromium daemon：
- 用户**看不到窗口**，无法中途输入密码/验证码 → 登录型任务（NAS LuCI、ZeroTier Central）卡死
- `--headed` 只在 daemon **首次启动**时生效；一旦 daemon 已在跑，后续命令一律 `⚠ --headed ignored: daemon already running`，且 `close` 后下一条 `open` 又会自动拉起 headless daemon，反复重启还丢登录会话
- 逆向登录态（读 cookie / 扒 API token / 模拟点击）脆弱且耗时，属于绕远路

## 根因
- agent-browser 的 daemon 是**持久单例**，`--headed` 是 daemon 启动参数而非命令参数，错过了启动时机就改不了
- 需要"用户可见 + 用户可输密码 + 登录态延续"的场景，正确姿势是**接管用户已打开的浏览器**，而不是新开一个

## 解决（Edge 方案）
1. 用户打开 Edge，地址栏输入 `edge://inspect/#remote-debugging`
2. 勾选 **「Allow remote debugging for this browser instance」**（允许对此浏览器实例进行远程调试）
3. 页面显示 `Server running at: 127.0.0.1:9222` 即端口开启
4. AI 侧连接（任选其一）：
```bash
agent-browser --cdp 9222 snapshot          # 每次命令带 --cdp
agent-browser connect 9222                 # 连接一次，后续命令免 --cdp
agent-browser --auto-connect snapshot      # 自动发现（读 DevToolsActivePort / 探测 9222）
```
5. 之后 `open` / `snapshot` / `click` / `type` 全部作用于**用户那个 Edge 窗口**：看得见、登录态在、密码可直接让用户输。

### 附加坑：代理环境变量导致内网访问失败
本机 Clash 代理（`HTTP_PROXY=127.0.0.1:7890`）会污染 Chromium，访问内网（如 `192.168.2.1`）报 `net::ERR_NO_SUPPORTED_PROXIES`。绕开：
```bash
env -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY agent-browser --cdp 9222 open http://192.168.2.1/
# 或
agent-browser --proxy-bypass "*" open http://192.168.2.1/   # 需先 close 重启 daemon 才生效
```

## 预防
- 任务要"用户可见 / 要输密码 / 复用登录态" → **优先 CDP 接管已运行浏览器**（Edge/Chrome 均可），不要自启 daemon
- 调试端口是 `127.0.0.1:9222`，用 `--auto-connect` 免记端口；浏览器侧开关位置记 `edge://inspect/#remote-debugging`（Chrome 是 `chrome://inspect/#remote-debugging`）
- 带代理的本机跑浏览器自动化访问内网，先 `env -u` 清代理变量，别让 Clash 劫持内网流量

## 来源
实测提炼自 2026-08-07 ZeroTier 组网诊断（NAS iStoreOS `192.168.2.1`）：
agent-browser v0.27.0 + 官方 CDP 文档 https://agent-browser.dev/cdp-mode 与 Microsoft Edge DevTools MCP 文档（edge://inspect 远程调试开关）。
