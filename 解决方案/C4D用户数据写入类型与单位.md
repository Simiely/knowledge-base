---
tags: [c4d, userdata, sdk]
date: 2026-08-03
status: stable
related: []
source: https://github.com/Simiely/c4d-userdata-manager/blob/main/DEVELOPMENT.md
---
# C4D 用户数据写入：类型与单位

**TL;DR**：写入用户数据（User Data）描述有三个高频坑——① `DESC_DEFAULT` 类型必须与 C4D 数据类型匹配（DTYPE_REAL→float、DTYPE_LONG→int、BOOL→`int(bool(...))`）；② **PERCENT 内部 0-1 存储**（UI 0-100，写入必须 `/100`）；③ `DESC_UNIT` / `DESC_CUSTOMGUI` **只有有效值才写入**（写 0 会破坏渲染，FLOAT 显示为空）。

## 问题

- 默认值显示为 0 或无法修改
- FLOAT 参数在属性面板显示为空
- 预设强度=100 显示成 10000%

## 根因

1. `DESC_DEFAULT` 类型与 C4D 期望不一致（对 DTYPE_LONG 也用了 float）
2. PERCENT 单位类型（`DTYPE_REAL + DESC_UNIT_PERCENT`）C4D 内部用 0-1 存储（1.0 = 100%），按 0-100 直接写入
3. 不存在的常量 `_c()` fallback 为 0 后写入 `DESC_CUSTOMGUI=0`；无单位类型也写入 `DESC_UNIT=0`——**BaseContainer 中值为 0 ≠ 未设置**，会破坏渲染
4. `AddUserData()` 只创建描述定义，**不保证从 DESC_DEFAULT 初始化参数值**

## 解决

```python
# 1. 类型匹配
if self.dtype in (UDT.FLOAT, UDT.PERCENT, UDT.ANGLE):
    bc[c4d.DESC_DEFAULT] = float(self.default_v)  # DTYPE_REAL → float
elif self.dtype == UDT.INTEGER:
    bc[c4d.DESC_DEFAULT] = int(self.default_v)    # DTYPE_LONG → int

# 2. PERCENT 0-1 转换
bc[c4d.DESC_DEFAULT] = 100.0 / scale  # UI 100 → 内部 1.0

# 3. 只有有效单位才写入
if u != _DESC_UNIT_NONE:
    bc[c4d.DESC_UNIT] = u

# 4. AddUserData 后显式写入值
did = obj.AddUserData(bc)
if did is not None:
    obj[did] = entry.get_c4d_value()  # 统一转换入口
```

## 预防

- `build_bc()` 按 C4D 数据类型分开处理 DESC_DEFAULT；写参数值统一走 `get_c4d_value()` 转换
- PERCENT/BOOL 特殊处理（/100、bool→int）
- 不存在的常量 fallback 为 0 后不要写入 DESC_CUSTOMGUI/DESC_UNIT——让 C4D 用各类型默认控件（DTYPE_COLOR 默认就是颜色选择器）
- 每次 AddUserData 后必显式 `obj[did] = value`
