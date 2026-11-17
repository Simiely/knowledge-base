#!/usr/bin/env python3
"""把 taxonomy.json 里「四种豁免写法」迁移到 `frontmatter_exempt`。

为什么不用 json.dump 整文件重写：那会把所有数组重排成多行，一个语义迁移变成
上百行格式 diff（2.5.x 期间踩过一次）。这里做**文本手术**：只删旧键、只插新键，
其余字节原样保留。

用法：
    python scripts/migrate-taxonomy.py --root <repo> --check   # 只打印 diff
    python scripts/migrate-taxonomy.py --root <repo> --write   # 落盘
    python scripts/migrate-taxonomy.py --root <repo>           # 默认 --check
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

OLD_KEYS = ["context_files", "exempt_basenames", "entry_files", "link_only_files",
            "slugger", "summary_policy"]
NEW_KEY = "frontmatter_exempt"


def split_keys(tax: dict) -> tuple[list[str], list[str]]:
    """按 check_repo.resolve_exempt 的同一规则归一化（不依赖 import，保持工具独立）。"""
    names: list[str] = []
    paths: list[str] = []

    cfg = tax.get(NEW_KEY)
    if isinstance(cfg, dict):
        names += [str(x) for x in (cfg.get("names") or [])]
        paths += [str(x) for x in (cfg.get("paths") or [])]
    elif isinstance(cfg, list):
        for item in cfg:
            text = str(item)
            (paths if "/" in text else names).append(text)

    for key in ("context_files", "exempt_basenames"):
        names += [str(x) for x in (tax.get(key) or [])]
    for item in tax.get("entry_files") or []:
        text = str(item)
        (paths if "/" in text else names).append(text)
    paths += [str(x) for x in (tax.get("link_only_files") or [])]

    return sorted(set(names)), sorted(set(paths))


def find_block(lines: list[str], key: str) -> tuple[int, int] | None:
    """定位顶层键 `key` 的 [起, 止) 行区间；找不到返回 None。"""
    start = None
    for i, line in enumerate(lines):
        if line.lstrip().startswith(f'"{key}":'):
            start = i
            break
    if start is None:
        return None

    depth = 0
    for i in range(start, len(lines)):
        depth += lines[i].count("[") + lines[i].count("{")
        depth -= lines[i].count("]") + lines[i].count("}")
        if depth <= 0:
            return start, i + 1
    return start, len(lines)


def fix_commas(lines: list[str]) -> None:
    """就地修正顶层成员之间的逗号（删键/插键之后唯一的破坏面）。"""
    for i in range(len(lines) - 1):
        cur = lines[i].rstrip()
        if not cur or cur.endswith(("{", "[", ",")):
            continue
        j = i + 1
        while j < len(lines) and not lines[j].strip():
            j += 1
        if j >= len(lines):
            continue
        nxt = lines[j]
        if nxt.startswith('  "') or nxt.startswith("  }"):
            lines[i] = cur + "," if nxt.startswith('"') else cur


def strip_dangling_comma(lines: list[str]) -> None:
    """最后一个成员后面不允许有逗号。"""
    for i, line in enumerate(lines):
        stripped = line.rstrip()
        if not stripped.endswith(","):
            continue
        j = i + 1
        while j < len(lines) and not lines[j].strip():
            j += 1
        if j < len(lines) and lines[j].lstrip().startswith("}"):
            lines[i] = stripped[:-1]


def _array(indent: str, key: str, vals: list[str]) -> list[str]:
    if not vals:
        return [f'{indent}"{key}": [],']
    out = [f'{indent}"{key}": [']
    for i, v in enumerate(vals):
        comma = "," if i < len(vals) - 1 else ""
        out.append(f"{indent}  {json.dumps(v, ensure_ascii=False)}{comma}")
    out.append(f"{indent}],")
    return out


def render_block(names: list[str], paths: list[str], indent: str) -> list[str]:
    out = [f'{indent}"{NEW_KEY}": {{']
    out += _array(indent + "  ", "names", names)
    out += _array(indent + "  ", "paths", paths)
    out[-1] = out[-1].rstrip(",")          # 块内最后一个键不能带逗号
    out.append(f"{indent}}},")
    return out


def migrate_text(text: str) -> tuple[str, bool]:
    tax = json.loads(text)
    if NEW_KEY in tax and not any(k in tax for k in OLD_KEYS):
        return text, False

    names, paths = split_keys(tax)
    lines = text.splitlines()

    for key in OLD_KEYS:
        block = find_block(lines, key)
        if block:
            start, end = block
            del lines[start:end]

    fix_commas(lines)

    # 插在 "include" 之后（没有就插在 "name" 之后，再没有就插在开头 '{' 之后）
    anchor = None
    for key in ("include", "name"):
        block = find_block(lines, key)
        if block:
            anchor = block[1]
            break
    if anchor is None:
        anchor = 1
    # 给前一个键补逗号
    prev = anchor - 1
    while prev >= 0 and not lines[prev].strip():
        prev -= 1
    if prev >= 0 and not lines[prev].rstrip().endswith((",", "{", "[")):
        lines[prev] = lines[prev].rstrip() + ","
    lines[anchor:anchor] = render_block(names, paths, "  ")
    fix_commas(lines)
    strip_dangling_comma(lines)

    out = "\n".join(lines) + ("\n" if text.endswith("\n") else "")
    json.loads(out)  # 解析失败直接抛，避免写出坏文件
    return out, True


def main() -> int:
    ap = argparse.ArgumentParser(description="taxonomy 迁移工具")
    ap.add_argument("--root", required=True, help="仓库根目录")
    ap.add_argument("--check", action="store_true", help="只报告，不写（默认）")
    ap.add_argument("--write", action="store_true", help="落盘")
    args = ap.parse_args()

    path = Path(args.root) / "schema" / "taxonomy.json"
    if not path.exists():
        print(f"TAXONOMY: 不存在 {path}", file=sys.stderr)
        return 2

    before = path.read_text(encoding="utf-8")
    after, changed = migrate_text(before)
    names, paths = split_keys(json.loads(after))

    if not changed:
        print(f"TAXONOMY: 已是新写法（names={len(names)}, paths={len(paths)}）")
        return 0

    print(f"TAXONOMY: 待迁移 names={len(names)} paths={len(paths)}")
    old_set = set(json.loads(before))
    removed = [k for k in OLD_KEYS if k in old_set]
    print(f"  删除键: {', '.join(removed) or '无'}")
    print(f"  新增键: {NEW_KEY}")
    if args.write:
        path.write_text(after, encoding="utf-8")
        print(f"  已写入 {path}")
    else:
        import difflib
        diff = list(difflib.unified_diff(
            before.splitlines(), after.splitlines(),
            fromfile="migrate:before", tofile="migrate:after", lineterm="", n=2,
        ))
        for line in diff[:40]:
            print("  " + line)
        if len(diff) > 40:
            print(f"  ... 共 {len(diff)} 行差异")
        print("  （--check 模式未落盘）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
