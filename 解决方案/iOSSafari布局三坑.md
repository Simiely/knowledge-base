---
tags: [web, ios, safari, css]
date: 2026-08-03
status: stable
related: []
source: https://github.com/Simiely/learning-platform/blob/main/DEV.md
---
# iOS Safari 布局三坑：100vh / flex+min-height / safe-area

**TL;DR**：iOS Safari 上：① `100vh` 含地址栏高度且 bfcache 恢复用旧值 → 用 JS `--vh`；② body 不要 `display:flex` + `min-height` 同时用（塌缩 bug）；③ `viewport-fit=cover` 必须配套 `env(safe-area-inset-*)` 避让刘海/状态栏。

## 问题
iPad 竖屏第二次打开页面（bfcache 恢复）无法铺满屏幕、底部留白；iPhone 刘海机型导航栏和弹窗按钮被状态栏遮挡；旋转后再转回才恢复正常。

## 根因（三个独立坑叠加）
1. **`100vh` 包含地址栏高度**，且地址栏可见性会变；Safari **bfcache**（前进/后退缓存）恢复页面时用缓存的旧 `100vh` 计算值，与实际视口不匹配
2. **Safari flex + min-height 兼容 bug**：`body { display:flex; min-height: calc(var(--vh)*100) }` 时，子元素 `flex:1` 不会扩展到 min-height 高度，而是塌缩到内容高度
3. **`viewport-fit=cover` 无配套**：页面扩展到屏幕物理边缘，但没有 `env(safe-area-inset-*)` 避让，内容被刘海/状态栏遮挡

## 解决
- **JS 端**：`window.innerHeight * 0.01` → 设置 CSS 变量 `--vh`，`resize`/`orientationchange`（setTimeout 100ms）/`pageshow.persisted` 时重算
- **CSS 端**：容器用 `height: calc(var(--vh, 1vh) * 100 - 52px)`（降级 `100vh`）；**body 保持无 flex**（避免 min-height 塌缩）；`:root` 定义 `--safe-top/bottom: env(safe-area-inset-top/bottom, 0px)`，navbar/关闭按钮加 `padding-top: var(--safe-top)`

## 预防
- iOS 布局永远不要单独依赖 `100vh`，用 `var(--vh, 1vh)` 渐进增强
- `viewport-fit=cover` 必须配套 `env(safe-area-inset-*)`，只设 meta 不写 CSS 就会遮挡
- Safari 上 body 的 `flex` + `min-height` 组合是毒药，二选一
- 修改布局链后在 iPad/iPhone 真机验证，桌面 DevTools 模拟不够准

## 来源
提炼自 [learning-platform](https://github.com/Simiely/learning-platform)：
[DEV.md](https://github.com/Simiely/learning-platform/blob/main/DEV.md)（iOS Safari 100vh Bug / flex+min-height / Safe Area 三节）
