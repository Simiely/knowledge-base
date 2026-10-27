---
tags: [frontend, testing, puppeteer, cdp]
date: 2026-10-27
status: stable
related: []
source: docs/05-开发指南.md §无头浏览器自动化调试 @ Simiely/homekeeper（仓库已于 2026-10-27 删除，内容已提炼留存）
---
# 无头 Edge + CDP 做前端自动化验证

**TL;DR**：用 `puppeteer-core` 驱动**系统自带 Edge**（免下载 Chromium），真实点击/拖拽/登录，抓 `console` + `pageerror` + 4xx 响应，再读 DOM 与 `getComputedStyle` 断言。纯后端测试测不了交互，截图肉眼比对又太慢 —— 这是"改完前端自己验一遍"的最小成本方案。

## 适用场景

- 纯后端单测覆盖不到的前端交互：点击、弹窗、拖拽、视图切换、表单校验顺序；
- "不报错但结果不对"的问题（布局拉伸、样式未生效、状态没落库）；
- 需要在无人值守下拿到**可复核的证据**（截图 + 控制台输出）。

## 关键做法

### 1. 选型：puppeteer-core + 系统 Edge

| 组件 | 说明 |
| --- | --- |
| `puppeteer-core` | 只驱动、不内置 Chromium，体积小；装在**独立 node 工作区**，不污染项目 |
| 系统 `msedge.exe` | Windows 自带，`executablePath` 直接指过去，免下载浏览器 |

```bash
# 安装（仅一次）
npm install puppeteer-core --no-audit --no-fund
# 运行：必须用 NODE_PATH 指向该工作区的 node_modules，否则 require 找不到包
NODE_PATH="<workspace>/node_modules" node <脚本>.js
```

### 2. 四个必挂的监听（定位问题的命脉）

```js
page.on("console", (m) => { if (["error","warning"].includes(m.type())) console.log(`[${m.type()}]`, m.text()); });
page.on("pageerror", (e) => console.log("[pageerror]", e.message));
page.on("response", (r) => { if (r.status() >= 400) console.log(`[${r.status()}]`, r.url()); });
```

### 3. 交互：用 puppeteer 原生 API，不在 evaluate 里触发跳转

```js
await page.type("#username", user);
await Promise.all([
  page.waitForNavigation({ waitUntil: "networkidle2" }).catch(() => {}),
  page.click("#submit-btn"),
]);
```

### 4. 拖拽：鼠标轨迹插值，先触发再扫描

```js
await page.mouse.move(x1, y1); await page.mouse.down();
for (let i = 1; i <= 20; i++) {                       // 20 步插值模拟人手
  const t = i / 20;
  await page.mouse.move(x1 + (x2-x1)*t, y1 + (y2-y1)*t);
  await new Promise(r => setTimeout(r, 20));
}
await page.mouse.up();
```

### 5. 断言：读真实状态，不靠截图顺眼

```js
const state = await page.evaluate(() => ({
  btn:  document.querySelector("#loc-edit-toggle")?.textContent,
  zone: (() => { const z = document.querySelector(".loc-gap-zone");
    return z ? { display: getComputedStyle(z).display } : null; })(),
}));
```

## 已知坑（都踩过）

| 坑 | 说明 | 解法 |
| --- | --- | --- |
| `MODULE_NOT_FOUND` | 直接调 `node.exe` 不是 npm | 用 `npm.cmd install`，运行时补 `NODE_PATH` |
| `execution context destroyed` | 在 `evaluate` 里提交表单会触发导航，上下文被销毁 | 导航动作一律用 `page.type` / `page.click` + `Promise.all` 等导航 |
| 拖拽测不准 | 未进入拖拽态时间距没拉开，缝隙 < 20px 扫不到 | 先 `mouse.down` + 小位移触发，等 300ms 再扫描 |
| 401 假错误 | 登录前资源请求 401 属正常（重定向到登录页） | 过滤 `login.html` / `favicon.ico` / `net::ERR_ABORTED` |
| `querySelector` 找不到元素 | 页面未渲染完或视图未切换 | 先 `waitForSelector` 再 `evaluate` |

## 推荐工作流

```
改前端代码 → 语法检查 → 服务 200
  → 浏览器脚本：打开 → 登录 → 进目标视图
  → 模拟操作 → 抓 console / pageerror / 4xx
  → 读 DOM 状态 + 截图 → 对比预期
  → 修复 → 重跑 → 恢复测试数据（拖拽类会真实改数据，需还原）
```

## 来源

提炼自 拾光集（`Simiely/homekeeper`）`docs/05-开发指南.md` §无头浏览器自动化调试（Edge + CDP，4 个脚本 `basic_check` / `drag_test` / `edit_mode_test` / `drag_gap_test` 的实践总结）；仓库已于 2026-10-27 删除，完整历史备份见本地 `homekeeper-2026-10-27.bundle`。
