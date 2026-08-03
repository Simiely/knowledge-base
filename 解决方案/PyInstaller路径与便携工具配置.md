---
tags: [windows, desktop, pyinstaller, packaging]
date: 2026-08-03
status: stable
related: []
source: https://github.com/Simiely/oc-plugin-activator/blob/main/DEVELOP.md
---
# PyInstaller 打包路径陷阱 + 便携工具配置位置

**TL;DR**：PyInstaller 打包的 exe 运行时 `__file__` 指向临时解压目录（`C:\Temp\_MEIxxxxx`），必须用 `sys.executable` + `sys.frozen` 判断取真实路径；便携工具的配置应与 exe 同目录（`%AppData%` 适合安装版，便携版会造成"换目录配置丢失"）。

## 问题 1：PyInstaller 路径
打包成 exe 后，程序找不到同目录的配置文件/资源文件（如图标、config.json）。

**根因**：PyInstaller 的 `--onefile` 模式运行时把内容解压到 `C:\Temp\_MEIxxxxx` 临时目录，`__file__` 指向那里，不是 exe 所在目录。

**解决**：
```python
if getattr(sys, 'frozen', False):
    APP_DIR = os.path.dirname(os.path.abspath(sys.executable))
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))
```

## 问题 2：便携工具配置位置（C# / 通用）
v3.0.1 前配置存 `%AppData%\WindowTinter\`，用户下载新版 exe 到新目录后旧配置不被识别。

**解决**：配置与 exe 同目录：
```csharp
var configPath = Path.Combine(Path.GetDirectoryName(Environment.ProcessPath) ?? ".", "WindowTinter.settings.json");
```
同理资源路径（如 app.ico）也要用绝对路径——Windows 开机自启（注册表 Run）的工作目录是 `C:\Users\<用户名>`，相对路径找不到文件会崩。

## 预防
- PyInstaller 打包：凡读取同目录文件，一律走 `sys.executable` 目录
- 便携工具（解压即用）：配置/资源与 exe 同目录，用 `Path.GetDirectoryName(Environment.ProcessPath)`
- 开机自启的程序：资源路径必须绝对化（工作目录不可信）

## 来源
提炼自 [oc-plugin-activator](https://github.com/Simiely/oc-plugin-activator)（[DEVELOP.md ②](https://github.com/Simiely/oc-plugin-activator/blob/main/DEVELOP.md)）+ [WindowTinter](https://github.com/Simiely/WindowTinter)（[DEV.md ⑨⑳](https://github.com/Simiely/WindowTinter/blob/main/DEV.md)）
