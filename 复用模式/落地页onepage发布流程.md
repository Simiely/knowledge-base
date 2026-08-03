---
tags: [web, workflow, github]
date: 2026-08-03
status: stable
related: [模板/插件Release打包模板.md]
---
# 落地页标准发布流程（onepage）

**TL;DR**：落地页（landing page）固定走 onepage 分支开发 → 迁移到 `main/onepage/` 目录 → 删除分支 → 清理 releases。全流程 5 步，避免分支与发布混乱。

## 问题

多个项目（blender-mesh-face-sorter、c4d-mesh-face-sorter、AE-Lyrics-Animator 等）的落地页发布流程不一致，容易产生残留分支、失效 release 链接。

## 根因

发布方式不统一：有时直接改 main，有时用分支，releases 只增不减导致旧版本链接混乱。

## 解决

标准流程（每次发布照此执行）：

1. 在 `onepage` 分支上开发/修改落地页
2. 测试通过后，迁移到 `main` 分支的 `onepage/` 目录
3. 删除 `onepage` 分支
4. 清理 releases：删除过期版本，只保留最新
5. 在 README / projects.json 中同步更新入口链接

## 预防

- 落地页改动一律从 onepage 分支发起，不直接改 main
- 发布后自查：访问 `simiely.github.io/<repo>/onepage/` 确认可访问
- 若出现下载缓存问题，用 raw 链接 + Ctrl+F5 强刷验证
