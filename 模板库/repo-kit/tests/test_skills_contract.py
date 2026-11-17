"""`skills` profile 的 SKILL.md 契约：与 Agent Skills 官方规范对齐。

为什么单独建这个测试：`skills` profile 自 2.0 起就存在，但**从未被任何仓库使用过**，
契约因此没被真实校验过。2.7.3 首次拿官方规范（agentskills.io/specification）比对，
发现两处过宽：

- `description.maxLength` 写的 1200，官方是 **1024**
- `name.pattern` 允许尾连字符与连续连字符（`my-skill-`、`a--b`），官方明确禁止

这两类错误在仓里看不出来——描述写长一点、名字多打一个连字符，检查器都会放行，
直到技能被加载器拒绝才暴露。
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


class SkillContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="repo-kit-skill-test-"))
        self.root = self.tmp / "repo"
        self.root.mkdir()
        # 最小可用的 link-only 骨架 + skills 配置
        (self.root / "schema").mkdir()
        (self.root / "tools/repo-kit").mkdir(parents=True)
        shutil.copy2(ROOT / "schema/skills.schema.json", self.root / "schema/skills.schema.json")
        shutil.copy2(ROOT / "schema/frontmatter.schema.json", self.root / "schema/frontmatter.schema.json")
        shutil.copy2(ROOT / "scripts/check_repo.py", self.root / "tools/repo-kit/check_repo.py")
        self.write_taxonomy()
        (self.root / "README.md").write_text("# demo\n", encoding="utf-8")

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def write_taxonomy(self) -> None:
        tax = {
            "version": "2.7.3", "name": "demo",
            "include": [], "generated_files": [],
            "frontmatter_exempt": {"names": [], "paths": ["*.md", "**/*.md"]},
            "skills": {
                "glob": "skills/**/SKILL.md",
                "schema": "schema/skills.schema.json",
                "name_matches_dir": True,
                "min_description": 40,
            },
            "types": ["tutorial"], "kinds": ["note"], "statuses": ["active"],
            "tiers": ["standard"], "confidences": ["high"],
            "topics": ["governance"], "relations": ["depends-on"],
            "review_days": 180, "ignore": [],
        }
        (self.root / "schema/taxonomy.json").write_text(
            json.dumps(tax, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def skill(self, dirname: str, name: str, description: str) -> None:
        d = self.root / "skills" / dirname
        d.mkdir(parents=True, exist_ok=True)
        (d / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: {description}\n---\n\n# {name}\n",
            encoding="utf-8")

    def run_check(self) -> str:
        proc = subprocess.run(
            [sys.executable, str(self.root / "tools/repo-kit/check_repo.py"), "--root", str(self.root)],
            capture_output=True, text=True,
        )
        return proc.stdout + proc.stderr

    # -- name -------------------------------------------------------------
    def test_valid_name_passes(self):
        self.skill("pdf-processing", "pdf-processing", "处理 PDF 的文本与表格提取。" * 3)
        self.assertNotIn("SKILL_SCHEMA", self.run_check())

    def test_trailing_hyphen_rejected(self):
        """官方规范：name 不能以连字符结尾。"""
        self.skill("pdf-processing-", "pdf-processing-", "处理 PDF 的文本与表格提取。" * 3)
        self.assertIn("SKILL_SCHEMA", self.run_check())

    def test_double_hyphen_rejected(self):
        """官方规范：name 不能有连续连字符。"""
        self.skill("pdf--processing", "pdf--processing", "处理 PDF 的文本与表格提取。" * 3)
        self.assertIn("SKILL_SCHEMA", self.run_check())

    def test_uppercase_rejected(self):
        self.skill("PDF", "PDF", "处理 PDF 的文本与表格提取。" * 3)
        self.assertIn("SKILL_SCHEMA", self.run_check())

    def test_name_must_match_dir(self):
        self.skill("dir-name", "other-name", "处理 PDF 的文本与表格提取。" * 3)
        self.assertIn("SKILL_NAME_DIR", self.run_check())

    # -- description ------------------------------------------------------
    def test_description_over_1024_rejected(self):
        """官方上限 1024；2.7.2 之前写的是 1200，会放行超限描述。"""
        self.skill("long-desc", "long-desc", "字" * 1100)
        self.assertIn("SKILL_SCHEMA", self.run_check())

    def test_description_under_1024_passes(self):
        self.skill("ok-desc", "ok-desc", "字" * 1000)
        self.assertNotIn("SKILL_SCHEMA", self.run_check())

    def test_description_below_house_minimum_warns(self):
        """min_description 是本仓约定（官方无下限），超短描述应被 SKILL_DESC_SHORT 拦下。"""
        self.skill("short-desc", "short-desc", "太短")
        self.assertIn("SKILL_DESC_SHORT", self.run_check())


if __name__ == "__main__":
    unittest.main()
