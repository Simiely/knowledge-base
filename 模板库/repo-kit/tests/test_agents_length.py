"""AGENTS.md 的门面阈值：>150 行即 ERROR（规范 2.1.4，kit 2.9.0）。

背景：规范从 2.1.4 起把「150 词」澄清成「150 行」（按 `wc -l` 计），
但当时只是文字——97 个仓里有 3 个 700/244/226 行，没人被拦住。
2.9.0 把阈值变成可执行断言，并要求报错信息能指出「生成物要改模板」。
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


class AgentsLengthTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = Path(tempfile.mkdtemp(prefix="repo-kit-agents-len-"))
        cls.root = cls.tmp / "kit"
        shutil.copytree(
            ROOT, cls.root,
            ignore=shutil.ignore_patterns("__pycache__", ".git", ".venv", "*.pyc"),
        )

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def write_agents(self, lines: int) -> None:
        """写出一份恰好 N 行的 AGENTS.md。"""
        body = "# AGENTS.md · 项目规则\n\n" + "\n".join(f"- 规则 {i}" for i in range(lines - 2)) + "\n"
        path = self.root / "AGENTS.md"
        path.write_text(body, encoding="utf-8")
        self.assertEqual(len(path.read_text(encoding="utf-8").splitlines()), lines)

    def items(self) -> list[dict]:
        proc = subprocess.run(
            [sys.executable, str(self.root / "scripts/check_repo.py"), "--root", str(self.root), "--json"],
            capture_output=True, text=True,
        )
        return json.loads(proc.stdout)["items"]

    def too_long(self) -> list[dict]:
        return [i for i in self.items() if i["code"] == "AGENTS_TOO_LONG"]

    def test_150_lines_passes(self) -> None:
        self.write_agents(150)
        self.assertEqual(self.too_long(), [])

    def test_151_lines_fails_with_handwritten_hint(self) -> None:
        template = self.root / "schema/agents.template.md"
        if template.exists():
            template.unlink()
        self.write_agents(151)
        hits = self.too_long()
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["severity"], "ERROR")
        self.assertIn("151 行", hits[0]["message"])
        self.assertIn("rules/*.md", hits[0]["message"])
        self.assertNotIn("agents.template.md", hits[0]["message"])

    def test_generated_agents_points_to_template(self) -> None:
        (self.root / "schema/agents.template.md").write_text("# {{PAGES}}\n", encoding="utf-8")
        self.write_agents(200)
        hits = self.too_long()
        self.assertEqual(len(hits), 1)
        self.assertIn("agents.template.md", hits[0]["message"])
        self.assertIn("generate.py --write", hits[0]["message"])


if __name__ == "__main__":
    unittest.main()
