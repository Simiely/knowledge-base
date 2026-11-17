"""豁免 frontmatter 的统一键（`frontmatter_exempt`）与旧键兼容。

2.6.0 之前，「哪些文件不要求 frontmatter」有四种写法（context_files /
exempt_basenames / entry_files / link_only_files），check_repo 与 generate 各实现一遍。
2.7.0 起统一为 `frontmatter_exempt: {names, paths}`，旧键继续生效但报 WARN。
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


class ExemptTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="repo-kit-exempt-test-"))
        self.root = self.tmp / "kit"
        shutil.copytree(
            ROOT, self.root,
            ignore=shutil.ignore_patterns("__pycache__", ".git", ".venv", "*.pyc"),
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    # -- helpers ----------------------------------------------------------
    def tax(self) -> dict:
        return json.loads((self.root / "schema/taxonomy.json").read_text(encoding="utf-8"))

    def save_tax(self, tax: dict) -> None:
        (self.root / "schema/taxonomy.json").write_text(
            json.dumps(tax, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    def check(self) -> str:
        proc = subprocess.run(
            [sys.executable, str(self.root / "scripts/check_repo.py"), "--root", str(self.root)],
            capture_output=True, text=True,
        )
        return proc.stdout + proc.stderr

    def generate(self, *args: str) -> str:
        proc = subprocess.run(
            [sys.executable, str(self.root / "scripts/generate.py"), "--root", str(self.root), *args],
            capture_output=True, text=True,
        )
        return proc.stdout + proc.stderr

    def make_plain(self, rel: str) -> None:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"# {path.stem}\n\n无 frontmatter 的页面。\n", encoding="utf-8")

    # -- 新键 -------------------------------------------------------------
    def test_names_match_any_depth(self):
        """names 按文件名匹配，任意层级都算豁免。"""
        self.make_plain("docs/deep/nested/NOTES.md")
        tax = self.tax()
        tax["frontmatter_exempt"] = {"names": ["NOTES.md"], "paths": []}
        self.save_tax(tax)
        out = self.check()
        self.assertNotIn("NOTES.md", out.split("REPO CHECK")[0],
                         "names 应让任意层级的 NOTES.md 免 frontmatter")

    def test_paths_use_glob(self):
        """paths 按相对路径 glob 匹配，不跨层时不会误伤同名文件。"""
        self.make_plain("rules/a.md")
        self.make_plain("other/rules/a.md")
        tax = self.tax()
        tax["frontmatter_exempt"] = {"names": [], "paths": ["rules/**"]}
        self.save_tax(tax)
        out = self.check()
        self.assertIn("other/rules/a.md", out,
                      "paths 只应豁免 rules/ 下的文件，不该波及 other/rules/")

    def test_generate_uses_same_rule(self):
        """生成器与校验器共用同一判定：豁免文件不进入页面集合。

        必须用「带合法 frontmatter」的文件来测——没有 frontmatter 的文件本来就不会
        进页面集合，豁免与否都一样，测不出差别。
        """
        src = (self.root / "docs/usage.md").read_text(encoding="utf-8")
        fenced = src.split("---", 2)
        self.assertTrue(src.startswith("---") and len(fenced) >= 3)
        fm = fenced[1].replace("id: docs.usage", "id: notes.free")
        page = f"---{fm}---\n# free\n\n正文。\n"
        (self.root / "notes").mkdir(exist_ok=True)
        (self.root / "notes/free.md").write_text(page, encoding="utf-8")

        tax = self.tax()
        tax["frontmatter_exempt"] = {"names": [], "paths": []}
        self.save_tax(tax)
        with_page = self.generate("--check")

        tax["frontmatter_exempt"] = {"names": ["free.md"], "paths": []}
        self.save_tax(tax)
        without_page = self.generate("--check")

        def pages(text: str) -> int:
            return int(text.split("pages=")[1].split(")")[0])

        self.assertEqual(pages(with_page) - pages(without_page), 1,
                         "豁免后页面数应少 1，说明生成器与校验器用了同一判定")

    # -- 旧键兼容 ---------------------------------------------------------
    def test_legacy_keys_still_work_but_warn(self):
        """旧键继续生效，并给出一条 TAXONOMY_LEGACY_KEY 提示。"""
        self.make_plain("LEGACY.md")
        tax = self.tax()
        tax.pop("frontmatter_exempt", None)
        tax["context_files"] = ["AGENTS.md"]
        tax["exempt_basenames"] = ["README.md", "CHANGELOG.md", "LEGACY.md"]
        self.save_tax(tax)
        out = self.check()
        self.assertIn("TAXONOMY_LEGACY_KEY", out)
        self.assertIn("exempt_basenames", out)
        self.assertNotIn("FM_MISSING          LEGACY.md", out,
                         "旧键仍应让 LEGACY.md 免 frontmatter")


if __name__ == "__main__":
    unittest.main()
