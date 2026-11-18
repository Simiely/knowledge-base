"""AGENTS.md 写入保护：手写入口不能被内置模板静默覆盖。

2.7.3 及更早的行为：存量仓库有手写 AGENTS.md、没有 schema/agents.template.md 时，
check_repo 报 4 条 GENERATED_MISSING 并提示跑 --write，照做就会把整份手写文件换成
内置兜底模板（实测 59 行 -> 31 行）。这组测试锁住 2.7.4 的 fail-closed 语义。
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

HANDWRITTEN = """# AGENTS.md · 手写入口

> 本仓特有规则：这段文字必须保留。

## 非协商
- 不要覆盖我。
"""


class AgentsGuardTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="repo-kit-agents-guard-"))
        self.root = self.tmp / "kit"
        shutil.copytree(
            ROOT, self.root,
            ignore=shutil.ignore_patterns("__pycache__", ".git", ".venv", "*.pyc"),
        )
        # copytree 会把 kit 自己的生成物一起带过来；本组测试只关心 AGENTS.md 的判定
        self.write("AGENTS.md", HANDWRITTEN)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    # -- helpers ----------------------------------------------------------
    def write(self, rel: str, text: str) -> None:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def read(self, rel: str) -> str:
        return (self.root / rel).read_text(encoding="utf-8")

    def run_generate(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(self.root / "scripts" / "generate.py"), "--root", str(self.root), *args],
            capture_output=True, text=True,
        )

    def run_check(self) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(self.root / "scripts" / "check_repo.py"), "--root", str(self.root)],
            capture_output=True, text=True,
        )

    def set_generated(self, value) -> None:
        tax_path = self.root / "schema/taxonomy.json"
        tax = json.loads(tax_path.read_text(encoding="utf-8"))
        if value is None:
            tax.pop("generated_files", None)
        else:
            tax["generated_files"] = value
        tax_path.write_text(json.dumps(tax, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # -- 拒绝覆盖 ---------------------------------------------------------
    def test_handwritten_agents_is_not_overwritten(self):
        """--write 必须整体拒绝，且不留下半套写入。"""
        self.write(
            "docs/another-note.md",
            "---\nid: docs.another-note\ntitle: 另一页\nsummary: t\ntype: explanation\n"
            "kind: note\nstatus: active\nowner: \"@simiely\"\nsource_type: doc\n"
            "source: README.md\nlast_reviewed: 2026-11-18\nrelated: []\n---\n\n# 另一页\n",
        )
        before_index = self.read("docs/_generated/index.md")
        proc = self.run_generate("--write")
        self.assertEqual(proc.returncode, 2, proc.stderr)
        self.assertIn("GENERATED_BLOCKED", proc.stderr)
        self.assertEqual(self.read("AGENTS.md"), HANDWRITTEN, "手写入口被改写了")
        self.assertEqual(self.read("docs/_generated/index.md"), before_index,
                         "拒绝写入时不应留下部分生成物")

    def test_check_mode_reports_blocked_not_stale(self):
        proc = self.run_generate("--check")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("GENERATED_BLOCKED", proc.stderr)
        self.assertIn("GENERATE CHECK: FAIL (blocked=AGENTS.md", proc.stdout)

    def test_check_repo_reports_blocked(self):
        """第一个跑到的工具就该说清真因，而不是只报「生成物缺失，请跑 --write」。"""
        proc = self.run_check()
        self.assertEqual(proc.returncode, 1)
        self.assertIn("GENERATED_BLOCKED", proc.stdout)
        self.assertIn("generate --write 会整轮拒绝写入", proc.stdout)

    def test_json_mode_exposes_blocked(self):
        proc = self.run_generate("--check", "--json")
        self.assertEqual(proc.returncode, 1)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["blocked"], ["AGENTS.md"])
        self.assertFalse(payload["written"])

    def test_marker_in_body_does_not_count_as_generated(self):
        """正文里引用「生成文件，勿手改」不能骗过守卫，只看前 5 行。"""
        self.write(
            "AGENTS.md",
            "# 手写入口\n\n本仓是手写的。\n\n## 约定\n- 生成文件，勿手改（这句是引用规范原文）\n",
        )
        proc = self.run_generate("--write")
        self.assertEqual(proc.returncode, 2, proc.stderr)
        self.assertIn("本仓是手写的", self.read("AGENTS.md"))

    # -- 允许写入的两条正路 -----------------------------------------------
    def test_template_present_allows_write(self):
        self.write("schema/agents.template.md", "# Custom {{PAGES}}\n")
        proc = self.run_generate("--write")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue(self.read("AGENTS.md").startswith("# Custom "))

    def test_agents_removed_from_generated_files_is_untouched(self):
        self.set_generated(["llms.txt", "docs/_generated/index.md"])
        proc = self.run_generate("--write")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(self.read("AGENTS.md"), HANDWRITTEN)

    def test_absent_agents_falls_back_to_template(self):
        (self.root / "AGENTS.md").unlink()
        proc = self.run_generate("--write")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("生成文件，勿手改", self.read("AGENTS.md"))

    # -- 兜底模板不再写死链接 ---------------------------------------------
    def test_fallback_omits_links_to_missing_docs(self):
        (self.root / "AGENTS.md").unlink()
        for rel in ("docs/usage.md", "docs/concepts/ssot.md", "docs/decisions/index.md"):
            path = self.root / rel
            if path.exists():
                path.unlink()
        proc = self.run_generate("--write")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        text = self.read("AGENTS.md")
        for dead in ("docs/usage.md", "docs/concepts/ssot.md", "docs/decisions/index.md"):
            self.assertNotIn(dead, text, f"缺失的 {dead} 仍被写进兜底模板")


if __name__ == "__main__":
    unittest.main()
