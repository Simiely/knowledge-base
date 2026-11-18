"""spec_version 的兼容边界：补丁版本差异不构成不兼容（2.8.1）。

背景：`SPEC_VERSION` 曾是完整三段比较，于是发一个只改措辞的 PATCH 版规范后，
任何把 lock 刷到新补丁版的仓库都会立刻 `SPEC_NEWER` ERROR——自己的仓库先红，
逼着「发规范」与「升 kit」必须同步，否则全 fleet 一起挂。
2.8.1 起按主次版本比较：补丁只是澄清，不报。
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC_VERSION = re.search(
    r'SPEC_VERSION = "([\d.]+)"', (ROOT / "scripts/check_repo.py").read_text(encoding="utf-8")
).group(1)


def bump(version: str, *, major: int = 0, minor: int = 0, patch: int = 0) -> str:
    a, b, c = (int(x) for x in version.split("."))
    return f"{a + major}.{b + minor}.{c + patch}"


class SpecVersionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = Path(tempfile.mkdtemp(prefix="repo-kit-spec-test-"))
        cls.root = cls.tmp / "kit"
        shutil.copytree(
            ROOT, cls.root,
            ignore=shutil.ignore_patterns("__pycache__", ".git", ".venv", "*.pyc"),
        )
        cls.lock = cls.root / "schema" / "kit.lock.json"

    @classmethod
    def tearDownClass(cls) -> None:
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def run_with(self, spec_version) -> tuple[set[str], set[str]]:
        lock = {"kit": "repo-kit", "version": "0.0.0", "profile": "link-only"}
        if spec_version is not None:
            lock["spec_version"] = spec_version
        self.lock.write_text(json.dumps(lock) + "\n", encoding="utf-8")
        proc = subprocess.run(
            [sys.executable, str(self.root / "scripts/check_repo.py"), "--root", str(self.root), "--json"],
            capture_output=True, text=True,
        )
        data = json.loads(proc.stdout)
        errors = {i["code"] for i in data["items"] if i["severity"] == "ERROR"}
        warnings = {i["code"] for i in data["items"] if i["severity"] == "WARN"}
        return errors, warnings

    def test_patch_difference_is_not_an_error(self) -> None:
        """补丁版本落后或超前都不报——本次修复的核心。"""
        for v in (bump(SPEC_VERSION, patch=-1), bump(SPEC_VERSION, patch=1)):
            with self.subTest(spec=v):
                errors, warnings = self.run_with(v)
                self.assertNotIn("SPEC_NEWER", errors)
                self.assertNotIn("SPEC_OUTDATED", errors | warnings)

    def test_minor_behind_is_warning(self) -> None:
        errors, warnings = self.run_with(bump(SPEC_VERSION, minor=-1))
        self.assertNotIn("SPEC_OUTDATED", errors)
        self.assertIn("SPEC_OUTDATED", warnings)

    def test_major_behind_is_error(self) -> None:
        errors, _ = self.run_with(bump(SPEC_VERSION, major=-1))
        self.assertIn("SPEC_OUTDATED", errors)

    def test_minor_ahead_is_error(self) -> None:
        errors, _ = self.run_with(bump(SPEC_VERSION, minor=1))
        self.assertIn("SPEC_NEWER", errors)

    def test_missing_and_malformed(self) -> None:
        errors, warnings = self.run_with(None)
        self.assertIn("SPEC_MISSING", warnings)
        errors, _ = self.run_with("2.1")
        self.assertIn("SPEC_FORMAT", errors)


if __name__ == "__main__":
    unittest.main()
