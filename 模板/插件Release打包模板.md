---
tags: [plugin, release, github]
date: 2026-08-03
status: stable
related: [解决方案/C4D2026移除的PythonSDK接口.md]
---
# GitHub Release 发布 zip 打包清单

**TL;DR**：插件发布时，Release 附件打包为 zip，**必须包含 .pyp 插件文件 + icon 图标**，方便用户一键安装。命名建议：`<插件名>-v<版本>.zip`。

## zip 内容结构

```
<插件名>-v1.2.4.zip
├── <插件名>.pyp        # 插件本体（C4D 插件必须）
├── icon.png / icon.tif # 图标
└── README.txt          # 安装说明（可选但推荐）
```

## 发布步骤

1. 代码提交 + 打 tag：`v1.2.4`
2. 在 GitHub Releases 创建对应版本
3. 上传 zip 附件（按上方结构打包）
4. Release 描述写清楚：版本变更 + 安装路径提示
   - C4D 插件安装路径示例：`D:\Tool\C4D\2026\2026\plugins\`
5. 更新仓库 README 与 DEVELOPMENT.md，记录本次关键问题与方案（便于回溯）

## 注意事项

- .pyp 需在对应版本 SDK 下编译验证后再发（C4D 2026 注意 SDK 兼容性，见 解决方案/C4D2026移除的PythonSDK接口.md）
- 附件命名带版本号，避免覆盖旧版本下载链接
