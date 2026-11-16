"""v2.5.x 三个语义的回归测试：entry_files、generated_files 三态、baseline 清理。

这三个都是「改过一次、但当时没有测试」的地方：
- entry_files：2.5.0 让 DEVELOPMENT.md 进扫描时引入
- generated_files：2.5.1 做取舍、2.5.2 修显式空列表的误判
- --prune-baseline：2.5.3 新增
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class SemanticsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="repo-kit-v25-test-"))
        self.root = self.tmp / "kit"
        shutil.copytree(
            ROOT, self.root,
            ignore=shutil.ignore_patterns("__pycache__", ".git", ".venv", "*.pyc"),
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    # -- helpers ----------------------------------------------------------
    def run_script(self, script: str, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(self.root / "scripts" / script), "--root", str(self.root), *args],
            capture_output=True, text=True,
        )

    def tax(self) -> dict:
        return json.loads((self.root / "schema/taxonomy.json").read_text(encoding="utf-8"))

    def save_tax(self, tax: dict) -> None:
        (self.root / "schema/taxonomy.json").write_text(
            json.dumps(tax, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    # -- entry_files ------------------------------------------------------
    def test_entry_files_skip_frontmatter_but_still_check_links(self):
        """entry_files 里的文件不要求 frontmatter，但它的链接必须照常被检查。

        这是 2.5.0 的核心取舍：DEVELOPMENT.md 进扫描意味着「开始查它的链接」，
        如果顺便漏掉链接检查，那这次改动就白做了。
        """
        (self.root / "DEVELOPMENT.md").write_text(
            "# DEVELOPMENT\n\n[坏链](docs/nope.md)\n", encoding="utf-8"
        )
        tax = self.tax()
        tax["entry_files"] = list(tax.get("entry_files") or []) + ["DEVELOPMENT.md"]
        self.save_tax(tax)

        proc = self.run_script("check_repo.py")
        out = proc.stdout + proc.stderr
        self.assertNotIn("FM_MISSING          DEVELOPMENT.md", out,
                         "entry_files 里的文件不应被要求 frontmatter")
        self.assertIn("LINK_BROKEN", out)
        self.assertIn("DEVELOPMENT.md", out,
                      "entry_files 里的文件仍必须做链接检查")

    # -- generated_files 三态 ---------------------------------------------
    def test_generated_files_absent_means_all(self):
        tax = self.tax()
        tax.pop("generated_files", None)
        self.save_tax(tax)
        proc = self.run_script("generate.py", "--write")
        self.assertIn("GENERATED: 5 files", proc.stdout)

    def test_generated_files_empty_means_none(self):
        """显式空列表 = 一个都不生成（2.5.2 修的正是这里：曾被当成「没声明」全量生成）。"""
        before = (self.root / "AGENTS.md").read_text(encoding="utf-8")
        tax = self.tax()
        tax["generated_files"] = []
        self.save_tax(tax)
        proc = self.run_script("generate.py", "--write")
        self.assertIn("GENERATED: 0 files", proc.stdout)
        self.assertEqual(before, (self.root / "AGENTS.md").read_text(encoding="utf-8"),
                         "显式空列表时不应改写任何文件")

    def test_generated_files_subset_only_writes_those(self):
        tax = self.tax()
        tax["generated_files"] = ["llms.txt"]
        self.save_tax(tax)
        proc = self.run_script("generate.py", "--write")
        self.assertIn("GENERATED: 1 files", proc.stdout)

    # -- baseline 清理 ----------------------------------------------------
    def test_prune_baseline_drops_stale_keeps_live(self):
        """失效条目被删、仍命中的被留。"""
        # 造一个真问题（坏链），让它进 baseline
        (self.root / "DEVELOPMENT.md").write_text(
            "# DEVELOPMENT\n\n[坏链](docs/nope.md)\n", encoding="utf-8"
        )
        tax = self.tax()
        tax["include"] = list(tax.get("include") or []) + ["DEVELOPMENT.md"]
        self.save_tax(tax)
        baseline = self.root / "schema" / "test-baseline.json"
        self.run_script("check_repo.py", "--write-baseline", str(baseline), "--baseline-format", "v2")

        data = json.loads(baseline.read_text(encoding="utf-8"))
        self.assertTrue(data["items"], "baseline 应为非空")
        # 再加一条永远不存在的条目
        data["items"].append({"code": "LINK_DIR", "file": "README.md",
                              "message": "早已静音的规则", "fingerprint": "deadbeefdeadbeef"})
        baseline.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        proc = self.run_script("check_repo.py", "--prune-baseline", str(baseline))
        self.assertIn("dropped=1", proc.stdout)
        after = json.loads(baseline.read_text(encoding="utf-8"))
        self.assertEqual(len(after["items"]), len(data["items"]) - 1)
        self.assertNotIn("deadbeefdeadbeef", json.dumps(after))


if __name__ == "__main__":
    unittest.main()
