"""repo-kit v2.0 回归测试：覆盖 v1 的已知误报/漏报。"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class KitTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="repo-kit-v2-test-"))
        self.root = self.tmp / "kit"
        shutil.copytree(
            ROOT, self.root,
            ignore=shutil.ignore_patterns("__pycache__", ".git", ".venv", "*.pyc"),
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    # -- helpers ----------------------------------------------------------
    def read(self, rel: str) -> str:
        return (self.root / rel).read_text(encoding="utf-8")

    def write(self, rel: str, text: str) -> None:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def replace(self, rel: str, old: str, new: str) -> None:
        self.write(rel, self.read(rel).replace(old, new, 1))

    def append(self, rel: str, text: str) -> None:
        self.write(rel, self.read(rel) + text)

    def check(self) -> dict:
        proc = subprocess.run(
            [sys.executable, str(self.root / "scripts/check_repo.py"), "--root", str(self.root), "--json"],
            capture_output=True, text=True,
        )
        return json.loads(proc.stdout)

    def codes(self, severity: str = "ERROR") -> set[str]:
        return {i["code"] for i in self.check()["items"] if i["severity"] == severity}

    def generate_check(self) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(self.root / "scripts/generate.py"), "--root", str(self.root), "--check"],
            capture_output=True, text=True,
        )

    # -- negative control -------------------------------------------------
    def test_baseline_passes(self) -> None:
        data = self.check()
        self.assertEqual(data["errors"], 0, data["items"])
        self.assertEqual(data["warnings"], 0, data["items"])
        self.assertEqual(self.generate_check().returncode, 0)

    # -- false positives fixed -------------------------------------------
    def test_code_fence_link_ignored(self) -> None:
        self.append("docs/usage.md", "\n```markdown\n[示例](does-not-exist.md)\n```\n")
        self.assertNotIn("LINK_BROKEN", self.codes())

    def test_inline_code_link_ignored(self) -> None:
        self.append("docs/usage.md", "\n反例：`[示例](does-not-exist.md)`\n")
        self.assertNotIn("LINK_BROKEN", self.codes())

    def test_source_line_anchor_ignored(self) -> None:
        self.append("docs/usage.md", "\n[配置源码](../examples/code/config.py#L3)\n")
        self.assertNotIn("ANCHOR_BROKEN", self.codes())

    def test_duplicate_heading_anchor_accepted(self) -> None:
        self.append(
            "docs/usage.md",
            "\n## FAQ\n\n内容一\n\n## FAQ\n\n内容二\n\n[第二个 FAQ](#faq-1)\n",
        )
        self.assertNotIn("ANCHOR_BROKEN", self.codes())

    def test_readme_only_inbound_is_not_orphan(self) -> None:
        self.write(
            "docs/newpage.md",
            "---\n"
            "id: docs.newpage\n"
            "title: 新页\n"
            "summary: 只从 README 入链的页面。\n"
            "type: explanation\n"
            "kind: note\n"
            "status: active\n"
            'owner: "@platform"\n'
            "topics: []\n"
            "source_type: doc\n"
            "source: docs/usage.md\n"
            "last_reviewed: 2026-11-11\n"
            "related: []\n"
            "---\n"
            "# 新页\n",
        )
        self.append("README.md", "\n[新页](docs/newpage.md)\n")
        self.assertNotIn("ORPHAN", self.codes("WARN"))

    # -- false negatives fixed -------------------------------------------
    def test_camelcase_truth_drift(self) -> None:
        self.replace("examples/code/config.py", '"maxRetries": 9', '"maxRetriesNew": 9')
        self.assertIn("TRUTH_DRIFT", self.codes())

    def test_source_commit_invalid(self) -> None:
        self.replace("examples/code/docs/config.md", "source_commit: 7eaf524c", "source_commit: nope")
        self.assertTrue({"SCHEMA", "SOURCE_COMMIT_FORMAT"} & self.codes())

    def test_superseded_requires_superseded_by(self) -> None:
        self.replace("examples/knowledge/note-b.md", "status: active", "status: superseded")
        self.assertIn("SUPERSEDED_MISSING", self.codes())

    def test_nested_frontmatter_rejected(self) -> None:
        self.replace("docs/index.md", "related: []\n---", "related: []\nmeta:\n  nested: true\n---")
        self.assertIn("FM_STRUCTURE", self.codes())

    def test_second_full_spec_rejected(self) -> None:
        self.write(
            "CLAUDE.md",
            "# 第二份完整规则\n\n"
            "- 规则一：复制所有命令\n"
            "- 规则二：复制所有禁令\n"
            "- 规则三：复制所有报错表\n"
            "- 规则四：复制所有清单\n"
            "- 规则五：复制所有关系\n",
        )
        self.assertIn("ENTRY_DUP", self.codes())

    def test_source_directory_rejected(self) -> None:
        self.replace("docs/index.md", "source: docs/usage.md", "source: docs")
        self.assertIn("SOURCE_NOT_FILE", self.codes())

    def test_confidence_vocab(self) -> None:
        self.replace("docs/index.md", "related: []", "confidence: very-high\nrelated: []")
        self.assertIn("VOCAB", self.codes())

    # -- relation semantics ----------------------------------------------
    def test_directed_relation_both_sides_rejected(self) -> None:
        self.replace(
            "examples/code/docs/retry.md",
            "related: []",
            'related: ["code.config.settings:depends-on"]',
        )
        self.assertIn("REL_BOTH_SIDES", self.codes())

    def test_symmetric_relation_both_sides_allowed(self) -> None:
        self.replace(
            "docs/concepts/ssot.md",
            "related: []",
            'related: ["docs.concepts.types:see-also"]',
        )
        self.assertNotIn("REL_BOTH_SIDES", self.codes())

    # -- ADR --------------------------------------------------------------
    def test_adr_duplicate_rejected(self) -> None:
        self.write(
            "docs/decisions/ADR-0001-another.md",
            "---\n"
            "id: docs.decisions.0001b\n"
            "title: 重复编号\n"
            "summary: 测试 ADR 编号唯一性。\n"
            "type: explanation\n"
            "kind: decision\n"
            "status: active\n"
            'owner: "@platform"\n'
            "topics: [governance]\n"
            "source_type: doc\n"
            "source: docs/decisions/ADR-0001-v2-architecture.md\n"
            "last_reviewed: 2026-11-11\n"
            "related: []\n"
            "---\n"
            "# 重复编号\n",
        )
        self.assertIn("ADR_DUP", self.codes())

    # -- generator --------------------------------------------------------
    def test_generated_stale_detected(self) -> None:
        self.replace("docs/usage.md", "title: 使用说明", "title: 使用说明（改）")
        proc = self.generate_check()
        self.assertEqual(proc.returncode, 1)
        self.assertIn("GENERATED_STALE", proc.stdout)

    # -- scope & templates -----------------------------------------------
    def test_include_scope_excludes_other_docs(self) -> None:
        tax = json.loads(self.read("schema/taxonomy.json"))
        tax["include"] = ["docs/**"]
        self.write("schema/taxonomy.json", json.dumps(tax, ensure_ascii=False, indent=2) + "\n")
        self.write("plugins/scratch.md", "# 没有 frontmatter 的插件草稿\n")
        self.assertNotIn("FM_MISSING", self.codes())

    def test_template_files_skipped(self) -> None:
        self.write("schema/bad.template.md", "# 模板\n\n[坏链接](missing.md)\n")
        self.assertNotIn("FM_MISSING", self.codes())
        self.assertNotIn("LINK_BROKEN", self.codes())

    def test_agents_template_override(self) -> None:
        self.write("schema/agents.template.md", "# Custom {{PAGES}}\n\n{{TYPES}}\n")
        proc = subprocess.run(
            [sys.executable, str(self.root / "scripts/generate.py"), "--root", str(self.root), "--write"],
            capture_output=True, text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertRegex(self.read("AGENTS.md"), r"^# Custom \d+\n")
        self.assertEqual(self.generate_check().returncode, 0)

    # -- baseline ---------------------------------------------------------
    def test_baseline_suppresses_known_errors(self) -> None:
        self.replace("docs/index.md", "related: []", "topics: [growth]\nrelated: []")
        baseline = self.tmp / "baseline.json"
        subprocess.run(
            [
                sys.executable, str(self.root / "scripts/check_repo.py"),
                "--root", str(self.root), "--write-baseline", str(baseline),
            ],
            capture_output=True, text=True, check=True,
        )
        proc = subprocess.run(
            [
                sys.executable, str(self.root / "scripts/check_repo.py"),
                "--root", str(self.root), "--baseline", str(baseline), "--json",
            ],
            capture_output=True, text=True,
        )
        data = json.loads(proc.stdout)
        self.assertEqual(data["errors"], 0, data["items"])
        self.assertGreaterEqual(data["baselined"], 1)

    def test_baseline_does_not_hide_new_errors(self) -> None:
        self.replace("docs/index.md", "related: []", "topics: [growth]\nrelated: []")
        baseline = self.tmp / "baseline.json"
        subprocess.run(
            [
                sys.executable, str(self.root / "scripts/check_repo.py"),
                "--root", str(self.root), "--write-baseline", str(baseline),
            ],
            capture_output=True, text=True, check=True,
        )
        self.replace("examples/knowledge/note-a.md", "status: active", "status: superseded")
        proc = subprocess.run(
            [
                sys.executable, str(self.root / "scripts/check_repo.py"),
                "--root", str(self.root), "--baseline", str(baseline), "--json",
            ],
            capture_output=True, text=True,
        )
        data = json.loads(proc.stdout)
        self.assertGreaterEqual(data["errors"], 1)
        self.assertIn("SUPERSEDED_MISSING", {i["code"] for i in data["items"]})


if __name__ == "__main__":
    unittest.main()
