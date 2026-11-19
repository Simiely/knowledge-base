#!/usr/bin/env python3
"""knowledge-base 自身的标准自检：把手写口径变成可机读断言。

本地与 CI 调用同一份代码，避免两处各写一份判定又互相漂移。

用法：
    python tools/verify-standard.py                    # 检查当前仓库
    python tools/verify-standard.py --self-test        # 正对照：确认断言真的会红
    python tools/verify-standard.py --strict-baseline  # 额外验证基线 commit 可达
                                                       # （CI 浅克隆下不要加，会误报）

退出码：0 = PASS，1 = FAIL，2 = 用法错误。
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parents[1]

CHECKS = []


def check(ok, msg, errs):
    if not ok:
        errs.append(msg)


def read_json(root, rel):
    return json.loads((root / rel).read_text(encoding="utf-8"))


def read_text(root, rel):
    return (root / rel).read_text(encoding="utf-8")


def verify(root, strict_baseline=False):
    """返回 (错误列表, 跳过说明列表)。"""
    errs, skips = [], []

    def j(rel):
        try:
            return read_json(root, rel)
        except (OSError, ValueError) as e:
            errs.append(f"{rel} 读取失败：{e}")
            return {}

    def t(rel):
        try:
            return read_text(root, rel)
        except OSError as e:
            errs.append(f"{rel} 读取失败：{e}")
            return ""

    tax = j("schema/taxonomy.json")
    lock = j("schema/kit.lock.json")
    kitsrc = j("模板库/repo-kit/schema/taxonomy.json")
    spec = j("模板库/单项目规范/spec.json")

    # ① 三个版本真源必须两两一致。
    #    根 taxonomy 是仓自有配置，不进 kit.lock.files，但仍应与锁描述同一 kit 版本。
    if tax and lock:
        check(tax.get("version") == lock.get("version"),
              f"KIT SKEW: taxonomy.version={tax.get('version')} kit.lock.version={lock.get('version')}", errs)
    if kitsrc and lock:
        check(kitsrc.get("version") == lock.get("version"),
              f"KIT 源与锁不一致：kit 源 {kitsrc.get('version')} / 本仓锁 {lock.get('version')}", errs)
    if spec and lock:
        check(spec.get("version") == lock.get("spec_version"),
              f"SPEC SKEW: spec.json {spec.get('version')} / kit.lock.spec_version {lock.get('spec_version')}", errs)

    # ② 校验器常量跟上规范版本（两份副本都要查，防止只改一边）。
    for rel in ("tools/repo-kit/check_repo.py", "模板库/repo-kit/scripts/check_repo.py"):
        m = re.search(r'SPEC_VERSION\s*=\s*"([^"]+)"', t(rel))
        check(m is not None and spec and m.group(1) == spec.get("version"),
              f"{rel} 的 SPEC_VERSION 未跟上 spec.json（{spec.get('version') if spec else '?'}）", errs)
        k = re.search(r'KIT_VERSION\s*=\s*"([^"]+)"', t(rel))
        check(k is not None and lock and k.group(1) == lock.get("version"),
              f"{rel} 的 KIT_VERSION 未跟上 kit.lock.json（{lock.get('version') if lock else '?'}）", errs)

    # ③ profile 集合：目录 = 脚手架 ValidateSet = 安装器 ValidateSet。
    prof_dir = root / "模板库/新项目模板/profiles"
    if prof_dir.is_dir():
        profiles = sorted(p.name for p in prof_dir.iterdir() if p.is_dir())
        check(len(profiles) > 0, "profiles/ 目录为空（空输入不能静默通过）", errs)
        for rel in ("模板库/新项目模板/新建仓库.ps1", "tools/update-repo-kit.ps1"):
            m = re.search(r"ValidateSet\(([^)]+)\)", t(rel))
            declared = sorted(x.strip().strip("'\"") for x in m.group(1).split(",")) if m else []
            check(declared == profiles,
                  f"{rel} 的 ValidateSet={declared} 与 profiles/ 目录 {profiles} 不符", errs)
        check("knowledge" in profiles, "profiles/ 缺 knowledge（CI 的 template-smoke 必须覆盖四个）", errs)
    else:
        errs.append("模板库/新项目模板/profiles/ 不存在")

    # ④ CI 接线：四个 profile 都要出现在 workflow 里。
    wf = t(".github/workflows/repo-check.yml")
    for prof in ("monorepo", "skills", "knowledge", "link-only"):
        check(f"-Profile {prof}" in wf, f"CI 的 template-smoke 未覆盖 profile: {prof}", errs)
    check("verify-standard.py" in wf, "self-check 未接入 tools/verify-standard.py", errs)

    # ⑤ AGENTS 基线行：格式合法 + 与 CHANGELOG 最新版本日期一致。
    agents = t("AGENTS.md")
    m = re.search(r"文档基线[^\n]*?(\d{4}-\d{2}-\d{2})[^\n]*?`([0-9a-f]{7,40})`", agents)
    check(m is not None, "AGENTS.md 基线行缺日期或 commit hash（格式应为 YYYY-MM-DD + 反引号短 sha）", errs)
    if m:
        date, sha = m.group(1), m.group(2)
        cl = t("CHANGELOG.md")
        cm = re.search(r"^## v[\d.]+ — (\d{4}-\d{2}-\d{2})", cl, re.M)
        check(cm is not None and cm.group(1) == date,
              f"AGENTS 基线日期 {date} 与 CHANGELOG 最新版本日期 {cm.group(1) if cm else '缺失'} 不一致", errs)
        check(re.fullmatch(r"[0-9a-f]{7,40}", sha) is not None,
              f"AGENTS 基线 commit hash 格式非法：{sha}", errs)

        if strict_baseline:
            r = subprocess.run(["git", "cat-file", "-e", sha + "^{commit}"],
                               cwd=root, capture_output=True)
            check(r.returncode == 0, f"AGENTS 基线 commit {sha} 在本仓历史中不可达", errs)
        else:
            skips.append(f"基线 {sha} 仅校验格式（CI 为浅克隆；深验加 --strict-baseline）")

    return errs, skips


def self_test():
    """正对照：注入已知错误，确认断言真的会红；再确认空输入不会静默通过。"""
    src = DEFAULT_ROOT
    results = []

    with tempfile.TemporaryDirectory(prefix="verify-standard-") as td:
        tmp = Path(td)
        needed = [
            "schema/taxonomy.json", "schema/kit.lock.json",
            "模板库/repo-kit/schema/taxonomy.json", "模板库/单项目规范/spec.json",
            "tools/repo-kit/check_repo.py", "模板库/repo-kit/scripts/check_repo.py",
            "模板库/新项目模板/新建仓库.ps1", "tools/update-repo-kit.ps1",
            ".github/workflows/repo-check.yml", "AGENTS.md", "CHANGELOG.md",
        ]
        for rel in needed:
            dst = tmp / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src / rel, dst)
        shutil.copytree(src / "模板库/新项目模板/profiles", tmp / "模板库/新项目模板/profiles",
                        ignore=shutil.ignore_patterns("__pycache__"))

        def run(label):
            e, _ = verify(tmp)
            results.append((label, e))
            return e

        base = run("基线（未注入）")
        check(not base, f"未注入时不应报错：{base}", [])

        # 正对照 1：只改 taxonomy.version，skew 必须被抓到。
        p = tmp / "schema/taxonomy.json"
        d = json.loads(p.read_text(encoding="utf-8"))
        d["version"] = "0.0.0"
        p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        red = run("注入 KIT SKEW")
        check(any("KIT SKEW" in x for x in red),
              "正对照失败：改坏 taxonomy.version 后断言没有报 KIT SKEW", [])

        # 恢复，再测空输入：删掉 taxonomy.json 必须报错，不能静默 PASS。
        shutil.copy2(src / "schema/taxonomy.json", p)
        p.unlink()
        empty = run("删除 taxonomy.json（空输入）")
        check(any("读取失败" in x for x in empty),
              "空输入失败：缺 taxonomy.json 时断言静默通过", [])

    errs = []
    for label, e in results:
        print(f"  [{label}] {'PASS' if not e else 'FAIL'} ({len(e)} 条)")
        for x in e:
            print(f"      ::error:: {x}")
    # 断言三条控制都按预期发生
    labels = {l: e for l, e in results}
    check(not labels.get("基线（未注入）"), "基线未通过", errs)
    check(any("KIT SKEW" in x for x in labels.get("注入 KIT SKEW", [])),
          "正对照未触发 KIT SKEW", errs)
    check(any("读取失败" in x for x in labels.get("删除 taxonomy.json（空输入）", [])),
          "空输入未拒绝", errs)

    for e in errs:
        print("::error:: " + e)
    print("STANDARD SELF-TEST: " + ("PASS (基线绿 / 注入红 / 空输入拒绝)" if not errs else "FAIL"))
    return 1 if errs else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=str(DEFAULT_ROOT), help="要检查的仓库根目录")
    ap.add_argument("--self-test", action="store_true", help="跑正对照，确认断言真的会红")
    ap.add_argument("--strict-baseline", action="store_true", help="额外验证基线 commit 可达（CI 浅克隆勿用）")
    args = ap.parse_args()

    if args.self_test:
        return self_test()

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"::error:: 仓库根目录不存在：{root}")
        return 2

    errs, skips = verify(root, strict_baseline=args.strict_baseline)
    for e in errs:
        print("::error:: " + e)
    for s in skips:
        print("  SKIP: " + s)
    print("STANDARD CHECK: " + ("PASS" if not errs else f"FAIL ({len(errs)})"))
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
