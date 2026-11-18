"""skills 仓的链接按「安装后布局」解析（2.8.0）。

背景：有些技能仓把共享脚本放在仓库根目录的 scripts/，安装时把 skills/* 与
scripts/、docs/ 平铺到同一个 skills 根下。于是 SKILL.md 里写 ../scripts/x
在安装后是对的，在仓库里却会解析到 skills/scripts/x（不存在）。
2.8.0 前只能二选一：改链接（安装后断）或关掉检查（失去保护）。
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

SKILL = """---
name: demo
description: 这是一个用于测试安装布局链接解析的示例技能，触发词包括「测试链接」和「安装布局」。
---

# Demo

见 [共享脚本](../scripts/run.py) 与 [本地参考](references/notes.md)。
"""


class SkillsInstallPrefixTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="repo-kit-install-prefix-"))
        self.root = self.tmp / "repo"
        (self.root / "schema").mkdir(parents=True)
        (self.root / "tools/repo-kit").mkdir(parents=True)
        shutil.copy2(ROOT / "schema/skills.schema.json", self.root / "schema/skills.schema.json")
        shutil.copy2(ROOT / "schema/frontmatter.schema.json", self.root / "schema/frontmatter.schema.json")
        shutil.copy2(ROOT / "scripts/check_repo.py", self.root / "tools/repo-kit/check_repo.py")
        (self.root / "README.md").write_text("# demo\n", encoding="utf-8")
        (self.root / "scripts").mkdir()
        (self.root / "scripts/run.py").write_text("print('ok')\n", encoding="utf-8")
        (self.root / "skills/demo/references").mkdir(parents=True)
        (self.root / "skills/demo/references/notes.md").write_text("# notes\n", encoding="utf-8")
        (self.root / "skills/demo/SKILL.md").write_text(SKILL, encoding="utf-8")
        self.write_taxonomy(None)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def write_taxonomy(self, prefix: str | None) -> None:
        skills = {
            "glob": "skills/**/SKILL.md",
            "schema": "schema/skills.schema.json",
            "name_matches_dir": True,
            "min_description": 40,
        }
        if prefix is not None:
            skills["install_prefix"] = prefix
        tax = {
            "version": "2.8.0", "name": "demo",
            "include": ["skills/**/SKILL.md"], "generated_files": [],
            "frontmatter_exempt": {"names": [], "paths": []},
            "skills": skills,
            "types": ["tutorial"], "kinds": ["note"], "statuses": ["active"],
            "tiers": ["normal"], "confidences": ["high"],
            "topics": ["governance"], "relations": {}, "review_days": {"normal": 365},
            "ignore": [],
        }
        (self.root / "schema/taxonomy.json").write_text(
            json.dumps(tax, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def run_check(self) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(self.root / "tools/repo-kit/check_repo.py"), "--root", str(self.root)],
            capture_output=True, text=True,
        )

    def test_without_prefix_reports_broken(self):
        proc = self.run_check()
        self.assertEqual(proc.returncode, 1)
        self.assertIn("LINK_BROKEN", proc.stdout)
        self.assertIn("../scripts/run.py", proc.stdout)

    def test_prefix_resolves_shared_scripts(self):
        self.write_taxonomy("skills")
        proc = self.run_check()
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertNotIn("LINK_BROKEN", proc.stdout)

    def test_prefix_keeps_local_references_working(self):
        """技能目录内部的相对引用不受影响。"""
        self.write_taxonomy("skills")
        proc = self.run_check()
        self.assertNotIn("references/notes.md", proc.stdout)


if __name__ == "__main__":
    unittest.main()
