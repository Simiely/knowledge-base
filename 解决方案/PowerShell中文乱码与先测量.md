---
tags: [windows, powershell, encoding]
date: 2026-08-03
status: stable
related: []
source: https://github.com/Simiely/windows-explorer-refresh-fix/blob/main/DEV-README.md
---
# PowerShell 脚本中文乱码 + 先测量再下结论

**TL;DR**：① PowerShell 5.1 按系统 ANSI 代码页（中文 Windows = GBK）解析 `.ps1`，无 BOM 的中文会乱码；`chcp 65001` 救不了（只改控制台输出代码页）。解决：脚本内输出全部用纯英文 ASCII。② 排障别把相关性当因果——先量化测量再下结论。

## 问题 1：编码乱码
PowerShell 脚本里的中文输出变成方块字。`chcp 65001` 无效。

**根因**：PowerShell 5.1 读取 `.ps1` 按系统 ANSI 代码页（GBK）解析，除非文件带 UTF-8 BOM。`.bat` 里的 `chcp 65001` 只改控制台输出代码页，不改变 PowerShell 读文件的方式。

**解决**：把 `.ps1` 内部所有输出改成纯英文 ASCII（逻辑不变）。任何代码页都不会乱码。`.bat` 启动器用相对路径 `%~dp0script.ps1`（不写死绝对路径——既泄露目录结构，下载到别人机器又失效）。

## 问题 2：误诊教训
资源管理器不自动刷新，第一直觉怪"映射网络盘拖垮外壳刷新消息泵"（社区常见说法）。

**根因**：没测量就下结论。实测 `ping` 1ms 零丢包、`net use` 正常、`Test-Path` 瞬连——网络盘假设被推翻，真凶是 Shell Bags 缓存损坏。

**解决**：任何"X 导致 Y"的假设，先用一行可量化的探测（ping / Test-Path 计时）验证再写结论。

## 预防
- 写 PowerShell 工具脚本：中文环境优先纯 ASCII 输出，或存 UTF-8 BOM
- 排障流程：假设 → 量化验证 → 结论，别信社区流传的"通说"

## 来源
提炼自 [windows-explorer-refresh-fix](https://github.com/Simiely/windows-explorer-refresh-fix)：
[DEV-README.md](https://github.com/Simiely/windows-explorer-refresh-fix/blob/main/DEV-README.md)（编码坑 / 误诊教训）
