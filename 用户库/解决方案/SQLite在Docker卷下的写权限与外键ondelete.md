---
tags: [sqlite, docker, orm, fastapi]
date: 2026-10-27
status: stable
related: []
source: docs/03-踩坑与排错.md @ Simiely/homekeeper（仓库已于 2026-10-27 删除，内容已提炼留存）
---
# SQLite 在 Docker 卷下的写权限与外键 ondelete 策略

**TL;DR**：两个坑一起来 —— ① 容器里挂宿主目录后写入报 `unable to open database file`，根因是**目录属主/权限**，不是 SQLite 配置；② 删分类/位置抛 `FOREIGN KEY constraint failed`，根因是**建表时没定 `ondelete`**，SQLite 默认是 `RESTRICT`。

## 问题

容器化后第一件事就是踩这两下：

```
sqlite3.OperationalError: unable to open database file
```
```
sqlite3.IntegrityError: FOREIGN KEY constraint failed
```

## 根因

1. **卷权限**：`./data:/app/data` 挂进来的是宿主机的目录，属主是宿主的 uid。容器内进程若不是 root、uid 又没对齐，就没有写权限 —— SQLite 连"打开"都失败，报的是 open 错误，**极易误判成路径写错**。
2. **外键策略**：`ForeignKey("categories.id")` 不写 `ondelete` 时，SQLite 采用默认行为（拒绝删除被引用的父行）。业务上"删分类但物品要留着"和"删分类连同物品一起删"是两种完全不同的需求，但**不写就都没有**，只会在运行时 500。

## 解决

```dockerfile
RUN mkdir -p /app/data && chmod 777 /app/data
```

```python
# 删分类/位置后物品保留、仅解除关联：
ForeignKey("categories.id", ondelete="SET NULL")
# 若要级联删除：
ForeignKey("categories.id", ondelete="CASCADE")
```

更正规的做法是**建表时就把 uid/gid 对齐**（入口脚本 chown 后降权运行，PUID/PGID 模式），`chmod 777` 只是让容器先跑起来的手段。

## 预防

- 权限问题的排查顺序：**先看容器内进程 uid 与挂载目录属主**，再怀疑路径、再怀疑 SQLite 参数。反过来查会绕很久。
- 外键策略属于**建模决策**，必须在写 `ForeignKey` 的同一行确定，别留给运行时发现 —— 有物品引用时，接口是返回 409 还是级联删除，是产品行为而不是实现细节。
- 同类项目复核清单：① 数据目录在镜像里先建好并给权限 ② 挂载卷用宿主本地盘（WAL 在 SMB/NFS 上不可靠）③ 每个外键都显式写 `ondelete`。

## 来源

提炼自 拾光集（`Simiely/homekeeper`）`docs/03-踩坑与排错.md` §1、§10；仓库已于 2026-10-27 删除，完整历史备份见本地 `homekeeper-2026-10-27.bundle`。
