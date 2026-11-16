#!/usr/bin/env python3
"""repo-kit 发布工具：把「版本号」收敛到一处，其余副本由本脚本同步。

背景：2.5.x 期间版本号散在五个地方（taxonomy.version / taxonomy.name /
script argparse / script docstring / VERSION 文件），其中 VERSION 与 taxonomy.version
分别被脚手架和安装器读取——两者不一致时，新仓库与已装仓库会拿到不同版本号，
而且没有任何检查会发现。本脚本是那次事故的收尾。

用法：
    python scripts/release.py --check          # 只校验，不写（可进 CI）
    python scripts/release.py --version 2.7.0  # 同步所有副本并跑测试
    python scripts/release.py --version 2.7.0 --min-kit 2.7.0   # 同时抬 spec 的 min_kit
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
KIT = HERE.parent
SPEC_JSON = KIT.parent / "单项目规范" / "spec.json"
CHECK = HERE / "check_repo.py"
GENERATE = HERE / "generate.py"
TAXONOMY = KIT / "schema" / "taxonomy.json"
CHANGELOG = KIT / "CHANGELOG.md"

VER_RE = re.compile(r"^\d+\.\d+\.\d+$")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def kit_version() -> str:
    """权威版本：taxonomy.version（安装器与脚手架都读它）。"""
    return str(read_json(TAXONOMY)["version"])


def script_version(path: Path) -> str | None:
    m = re.search(r'KIT_VERSION = "([\d.]+)"', path.read_text(encoding="utf-8"))
    return m.group(1) if m else None


def check() -> int:
    current = kit_version()
    problems: list[str] = []

    name = read_json(TAXONOMY).get("name", "")
    if name != f"repo-kit v{current}":
        problems.append(f"taxonomy.name = {name!r}，应为 'repo-kit v{current}'")

    got = script_version(CHECK)
    if got is None:
        problems.append("check_repo.py: 找不到 KIT_VERSION 常量")
    elif got != current:
        problems.append(f"check_repo.py: KIT_VERSION = {got}，应为 {current}")

    # generate.py 不拥有版本常量，只引用；它若自己写死一份就又会漂移
    gen = GENERATE.read_text(encoding="utf-8")
    if "cr.KIT_VERSION" not in gen:
        problems.append("generate.py: 应引用 cr.KIT_VERSION，而不是自己维护版本号")
    if re.search(r'^KIT_VERSION\s*=', gen, re.M):
        problems.append("generate.py: 不应定义 KIT_VERSION（版本只由 check_repo.py 拥有）")

    if SPEC_JSON.exists():
        min_kit = read_json(SPEC_JSON).get("min_kit")
        if min_kit and tuple(map(int, min_kit.split("."))) > tuple(map(int, current.split("."))):
            problems.append(f"spec.json min_kit = {min_kit} 高于 kit 版本 {current}")

    if (KIT / "VERSION").exists():
        problems.append("VERSION 文件仍然存在——它已被 taxonomy.version 取代，应删除")

    if problems:
        print("RELEASE CHECK: FAIL")
        for p in problems:
            print(f"  - {p}")
        return 1
    print(f"RELEASE CHECK: PASS (v{current})")
    return 0


def write_version(new: str, min_kit: str | None) -> int:
    if not VER_RE.match(new):
        print(f"版本号格式不对：{new!r}（要 X.Y.Z）", file=sys.stderr)
        return 2

    tax = read_json(TAXONOMY)
    tax["version"] = new
    tax["name"] = f"repo-kit v{new}"
    TAXONOMY.write_text(json.dumps(tax, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    text = CHECK.read_text(encoding="utf-8")
    if "KIT_VERSION" not in text:
        print("check_repo.py: 缺 KIT_VERSION 常量，拒绝修改", file=sys.stderr)
        return 2
    CHECK.write_text(re.sub(r'KIT_VERSION = "[\d.]+"', f'KIT_VERSION = "{new}"', text, count=1),
                     encoding="utf-8")

    if min_kit:
        spec = read_json(SPEC_JSON)
        spec["min_kit"] = min_kit
        SPEC_JSON.write_text(json.dumps(spec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    text = CHANGELOG.read_text(encoding="utf-8")
    if f"## [{new}]" not in text:
        head, _, rest = text.partition("\n")
        stub = (
            f"\n## [{new}] - 待填\n\n### Changed\n\n- 待填\n\n"
        )
        CHANGELOG.write_text(head + "\n" + stub + rest.lstrip("\n"), encoding="utf-8")
        print(f"CHANGELOG: 已插入 [{new}] 空节")

    print(f"RELEASE: v{new} 已写入 taxonomy / check_repo.py" + (f" / min_kit={min_kit}" if min_kit else ""))
    return 0


def run_checks() -> int:
    for cmd in (
        [sys.executable, "-m", "unittest", "discover", "-s", "tests"],
        [sys.executable, str(HERE / "drift_probe.py"), "--root", str(KIT)],
        [sys.executable, str(CHECK), "--root", str(KIT)],
        [sys.executable, str(GENERATE), "--root", str(KIT), "--check"],
    ):
        proc = subprocess.run(cmd, cwd=KIT, capture_output=True, text=True)
        label = " ".join(Path(c).name for c in cmd[1:3]) or cmd[0]
        if proc.returncode != 0:
            print(f"CHECK FAILED: {' '.join(cmd)}", file=sys.stderr)
            print((proc.stdout + proc.stderr)[-1500:], file=sys.stderr)
            return 1
        tail = (proc.stdout or proc.stderr).strip().splitlines()[-1:] or [""]
        print(f"  OK  {label:<28}{tail[0][:70]}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="repo-kit 发布工具")
    ap.add_argument("--check", action="store_true", help="只校验所有副本的版本号是否一致")
    ap.add_argument("--version", default="", help="新版本号 X.Y.Z")
    ap.add_argument("--min-kit", default="", help="同时把 spec.json 的 min_kit 抬到该值")
    ap.add_argument("--skip-tests", action="store_true", help="跳过测试（仅本地调试用）")
    args = ap.parse_args()

    if args.check:
        return check()
    if not args.version:
        ap.print_help()
        return 2

    code = write_version(args.version, args.min_kit or None)
    if code != 0:
        return code
    if not args.skip_tests:
        print("跑验收：")
        if run_checks() != 0:
            return 1
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
