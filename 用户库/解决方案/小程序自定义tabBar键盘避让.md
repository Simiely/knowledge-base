---
tags: [miniprogram, ui, keyboard]
date: 2026-08-12
status: stable
related: [解决方案/小程序iPad大屏适配.md]
source: https://github.com/Simiely/collab-plan-miniprogram/blob/main/CHANGELOG.md
---
# 小程序自定义 tabBar 的键盘避让体系

**TL;DR**：自定义 tabBar 的小程序里，输入弹层（面板/表单）用 `adjust-position=false` 关闭系统自动顶起，改听 `bindkeyboardheightchange` 手动抬高面板（底部 = 键盘高度 − tabBar 高度，收起归 0），否则键盘会顶乱自定义 tabBar 或遮挡输入框。

## 问题
底部弹层面板（清单面板 / 批量导入）输入时，键盘弹起把页面顶乱：自定义 tabBar 被顶起错位，或输入框被键盘遮挡。

## 根因
小程序默认 `adjust-position=true` 会整体上移页面——对原生 tabBar 没问题，但自定义 tabBar 是页面内容的一部分，一起被顶起 → 布局错乱；且默认行为只保证输入框可见，不感知自定义 tabBar 占位。

## 解决
键盘避让体系定版（collab-plan-miniprogram v0.7.6）：
1. **弹层容器**：`adjust-position=false` —— 不顶起页面（含自定义 tabBar 保持原位）
2. **手动抬高**：`bindkeyboardheightchange` 监听键盘高度，面板 `bottom = 键盘高度 − tabBar 高度`；键盘收起时归 0
3. **表单输入框**：`cursor-spacing` 按需设置（密码框 / 标题 20，补充说明 100；短输入不带）——控制光标与输入框底部的间距
4. 区分场景：底部弹层用「关闭自动 + 手动抬高」；普通页内表单保持默认即可

## 预防
1. 用了自定义 tabBar，就要接管键盘避让：默认 `adjust-position` 的顶起行为与自定义 tabBar 冲突
2. 弹层类交互统一「关自动顶起 + `keyboardheightchange` 手动算 bottom」模板，别每个页面各写一套
3. 验证清单：键盘弹起 → tabBar 不位移、输入框不被遮、键盘收起 → 面板复位归 0

## 来源
提炼自 [collab-plan-miniprogram](https://github.com/Simiely/collab-plan-miniprogram) CHANGELOG v0.7.6（键盘避让体系定版）。
