---
tags: [css, layout, chromium]
date: 2026-10-27
status: stable
related: []
source: docs/03-踩坑与排错.md @ Simiely/homekeeper（仓库已于 2026-10-27 删除，内容已提炼留存）
---
# 列方向 flex 容器必须显式 nowrap，否则子项被拉伸

**TL;DR**：容器已有 `flex-wrap: wrap`（常见于卡片基类），子容器覆盖成 `flex-direction: column` 却**没改 wrap** —— Chromium 下会把每个 flex item 拉到约 220px 高，与内容完全无关。修法：列方向容器一律补 `flex-wrap: nowrap`。

## 问题

添加页「数量与状态」分组内容实测只有 93px，容器却渲染成 215px，整页高度异常。样式里没写任何 height。

```css
.card       { display: flex; flex-wrap: wrap; }          /* 基类，横向卡片用 */
.add-form   { display: flex; flex-direction: column; }    /* 只改了方向 */
```

## 根因

- `flex-wrap: wrap` 在**行方向**下是正常的多行换行；
- 一旦方向变成 `column`，`wrap` 的语义变成"**列满高就换列**"，主轴是竖直方向；
- 容器高度未定（`height: auto`）时，Chromium 会按可用空间把 flex item 拉伸分配，实测稳定在 ~220px 一档 —— 与子元素内容多少无关，`div` / `fieldset` 都一样。

## 解决

```css
.add-form { display: flex; flex-direction: column; flex-wrap: nowrap; }
```

其他 `.card`（筛选栏等）保留 `wrap` 是**期望行为**，不要全局改掉基类。

## 预防

- **覆盖 `flex-direction` 时必须一起审 `flex-wrap`** —— 这两个属性不是独立的，方向决定 wrap 的语义。
- 排查手法（比盲改样式快）：量内容子元素的 `top/bottom`，若**组高 ≫ 内容高**，把这个容器从 flex 父级里拿出来对比 —— 离开 flex 就正常 = 容器问题，不是元素自身问题。
- 这类"不报错、但布局错"的问题优先用无头浏览器读 `getComputedStyle` 定位（见 `复用模式/无头Edge与CDP做前端自动化验证.md`），比截图肉眼比对可靠。

## 来源

提炼自 拾光集（`Simiely/homekeeper`）`docs/03-踩坑与排错.md` §20；仓库已于 2026-10-27 删除，完整历史备份见本地 `homekeeper-2026-10-27.bundle`。
