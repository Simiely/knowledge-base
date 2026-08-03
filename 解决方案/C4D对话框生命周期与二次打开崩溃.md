---
tags: [c4d, sdk, dialog]
date: 2026-08-03
status: stable
related: []
source: https://github.com/Simiely/c4d-mesh-face-sorter/blob/main/DEVELOPMENT.md
---
# C4D 对话框生命周期与二次打开崩溃

**TL;DR**：C4D 异步对话框两个致命坑——① 对话框对象用局部变量会被垃圾回收导致面板空白，**CommandData 必须用 `self._dlg` 保持引用**；② 关闭后再打开崩溃，根因是 `RestoreLayout()` 尝试 `Open()` 已销毁的旧对话框，**直接 `return True` 不做事**。

## 问题

- 面板打开后完全空白，无任何控件
- 关闭后再次打开 → C4D 崩溃（栈：`Py_HashPointer` + `PyIter_Send`，Python 尝试 hash 已释放的 C4D 对象）

## 根因

1. `Execute()` 中用局部变量 `dlg = Dialog()`，函数返回后对象被 GC 回收，C4D 窗口失去 Python 回调连接 → 空白
2. 用户关闭对话框后 C4D 调用 `RestoreLayout()` 恢复布局，它却 `Open()` 一个已销毁的旧对话框 → 崩溃

## 解决

1. CommandData 保持对话框引用，Execute 改为切换式（打开/关闭）：

```python
if self._dlg is None or not self._dlg.IsOpen():
    self._dlg = Dialog()
    self._dlg.Open(...)
else:
    self._dlg.Close()
    self._dlg = None
```

2. `RestoreLayout` 直接 `return True`（不做任何操作），`dialogid=0` 避免与插件 ID 冲突

## 预防

- 对话框对象必须挂在 CommandData 实例上，不用局部变量（官方示例用 `global` 是偷懒做法）
- 异步对话框生命周期有两个入口（`Execute` 和 `RestoreLayout`），两个都要处理，`RestoreLayout` 是"第二次打开崩溃"的高发点
