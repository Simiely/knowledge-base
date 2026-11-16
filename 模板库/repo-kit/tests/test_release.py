"""发布工具的一致性校验：版本号副本之间不允许漂移。

2.5.x 期间 `generate.py` 的版本号停在 2.5.2 而 kit 已是 2.5.3，
因为那段文字不参与任何检查。本测试把「不漂移」变成可执行断言。
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def release_check(root: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(root / "scripts/release.py"), "--check"],
        capture_output=True, text=True,
    )


class ReleaseCheckTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="repo-kit-release-test-"))
        self.root = self.tmp / "kit"
        shutil.copytree(
            ROOT, self.root,
            ignore=shutil.ignore_patterns("__pycache__", ".git", ".venv", "*.pyc"),
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_versions_are_consistent(self):
        proc = release_check(self.root)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("RELEASE CHECK: PASS", proc.stdout)

    def test_detects_hardcoded_version_in_generator(self):
        """生成器若自己写死版本号，必须被拦下。"""
        path = self.root / "scripts/generate.py"
        text = path.read_text(encoding="utf-8")
        path.write_text(
            text.replace('f"repo-kit v{cr.KIT_VERSION} 生成器"', '"repo-kit v0.0.0 生成器"', 1),
            encoding="utf-8",
        )
        proc = release_check(self.root)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("cr.KIT_VERSION", proc.stdout)

    def test_detects_version_file_resurrection(self):
        """VERSION 文件已被 taxonomy.version 取代；它若回来，说明有人在走老路。"""
        (self.root / "VERSION").write_text("9.9.9\n", encoding="utf-8")
        proc = release_check(self.root)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("VERSION", proc.stdout)


if __name__ == "__main__":
    unittest.main()
