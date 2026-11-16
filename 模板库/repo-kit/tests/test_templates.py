"""四份 CI 模板的语义不变量。

为什么是"语义"而不是逐行比对：逐行比对的期望值本身也要维护，等于换个地方抄一遍；
这里断言的是「无论怎么写，这几件事必须成立」，改漏一份或改错一处都会红。

背景：2.5.0 加 `--changed-since`、2.5.1 改依赖安装，两次都只改了两三份模板就提交了。
"""
from __future__ import annotations

import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
PROFILES = ROOT.parent / "新项目模板" / "profiles"
NAMES = ["monorepo", "skills", "knowledge", "link-only"]
GENERATING = {"monorepo", "skills", "knowledge"}      # 有 generate.py 的 profile
NO_TRUTH = {"knowledge", "link-only"}                 # 无 schema/sources.json 的 profile


def workflow(profile: str) -> dict:
    path = PROFILES / profile / ".github/workflows/repo-check.yml"
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def steps(profile: str) -> list[dict]:
    return workflow(profile)["jobs"]["invariants"]["steps"]


def runs(profile: str) -> list[str]:
    return [str(s.get("run", "")) for s in steps(profile)]


class TemplateInvariantTest(unittest.TestCase):
    def test_every_profile_checks_and_locks(self):
        """每份模板都必须跑校验器与锁校验。"""
        for profile in NAMES:
            with self.subTest(profile=profile):
                joined = "\n".join(runs(profile))
                self.assertIn("check_repo.py --root .", joined)
                self.assertIn("update-repo-kit.ps1 -Check", joined)

    def test_changed_since_requires_full_history(self):
        """用了 --changed-since 就必须 fetch-depth: 0，否则变更集恒为空、静默失效。"""
        for profile in NAMES:
            with self.subTest(profile=profile):
                uses_changed = any("--changed-since" in r for r in runs(profile))
                if not uses_changed:
                    continue
                checkout = next((s for s in steps(profile)
                                 if str(s.get("uses", "")).startswith("actions/checkout")), None)
                self.assertIsNotNone(checkout, "缺 actions/checkout")
                self.assertEqual(checkout.get("with", {}).get("fetch-depth"), 0,
                                 "--changed-since 需要 fetch-depth: 0")

    def test_generate_step_only_where_generator_exists(self):
        """只有带 generate.py 的 profile 才允许出现 generate 步骤。"""
        for profile in NAMES:
            with self.subTest(profile=profile):
                has_generate = any("generate.py" in r for r in runs(profile))
                self.assertEqual(has_generate, profile in GENERATING,
                                 f"{profile} 的 generate 步骤与 profile 能力不符")

    def test_no_truth_profiles_share_dependency_style(self):
        """无真源的两档（knowledge / link-only）依赖装法必须一致。

        A 档（有 sources.json）用显式装，因为代码仓的 requirements.txt 往往是构建清单；
        B 档的 requirements.txt 就是文档依赖，直接 -r 即可。两档内部必须统一。
        """
        dep = {}
        for profile in NAMES:
            step = next((s for s in steps(profile)
                         if "pip install" in str(s.get("run", ""))), None)
            self.assertIsNotNone(step, f"{profile} 缺依赖安装步骤")
            dep[profile] = str(step["run"]).strip()
        self.assertEqual(dep["knowledge"], dep["link-only"],
                         "无真源的两档依赖装法不一致")
        self.assertEqual(dep["monorepo"], dep["skills"],
                         "有真源的两档依赖装法不一致")
        self.assertNotEqual(dep["monorepo"], dep["knowledge"],
                            "两档依赖装法本应不同（A 档显式、B 档 -r）")


if __name__ == "__main__":
    unittest.main()
