"""repo-kit v2.2 新能力测试；v2.1 回归仍在 test_check_repo.py。"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class V22Test(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="repo-kit-v22-test-"))
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
        path.write_text(text, encoding="utf-8", newline="\n")

    def replace(self, rel: str, old: str, new: str) -> None:
        self.write(rel, self.read(rel).replace(old, new, 1))

    def append(self, rel: str, text: str) -> None:
        self.write(rel, self.read(rel) + text)

    def tax_update(self, fn) -> None:
        tax = json.loads(self.read("schema/taxonomy.json"))
        fn(tax)
        self.write("schema/taxonomy.json", json.dumps(tax, ensure_ascii=False, indent=2) + "\n")

    def run_check(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(self.root / "scripts/check_repo.py"), "--root", str(self.root), *args],
            capture_output=True, text=True,
        )

    def check_json(self, *args: str) -> dict:
        proc = self.run_check("--json", *args)
        return json.loads(proc.stdout)

    def codes(self, severity: str = "ERROR") -> set[str]:
        return {i["code"] for i in self.check_json()["items"] if i["severity"] == severity}

    # -- context / exempt -------------------------------------------------
    def test_context_files_are_not_pages(self) -> None:
        self.tax_update(lambda t: t.update({"context_files": ["AGENTS.md"]}))
        self.write("plugins/A/AGENTS.md", "# A 的局部规则\n\n- 只影响 A\n")
        self.assertNotIn("FM_MISSING", self.codes())

    def test_exempt_basenames_are_not_pages(self) -> None:
        self.tax_update(lambda t: t.update({"exempt_basenames": ["README.md"]}))
        self.write("plugins/A/README.md", "# A\n")
        self.assertNotIn("FM_MISSING", self.codes())

    # -- report lifecycle -------------------------------------------------
    def test_report_kind_skips_stale(self) -> None:
        self.write(
            "docs/report.md",
            "---\n"
            "id: docs.report\n"
            "title: 一次性报告\n"
            "summary: 测试 report 生命周期。\n"
            "type: explanation\n"
            "kind: report\n"
            "status: active\n"
            'owner: "@platform"\n'
            "topics: [governance]\n"
            "source_type: doc\n"
            "source: docs/usage.md\n"
            "last_reviewed: 2020-01-01\n"
            "related: []\n"
            "---\n"
            "# 一次性报告\n",
        )
        self.append("docs/index.md", "\n[报告](report.md)\n")
        self.assertNotIn("STALE", self.codes())

    # -- multi-source -----------------------------------------------------
    def test_sources_multi_valid(self) -> None:
        self.replace(
            "docs/index.md",
            "related: []",
            'sources: ["doc:docs/usage.md", "code:scripts/check_repo.py"]\nrelated: []',
        )
        self.assertEqual(self.check_json()["errors"], 0)

    def test_sources_multi_missing(self) -> None:
        self.replace(
            "docs/index.md",
            "related: []",
            'sources: ["doc:docs/missing.md"]\nrelated: []',
        )
        self.assertIn("SOURCE_MISSING", self.codes())

    # -- co-change --------------------------------------------------------
    def _enable_co_change(self) -> None:
        cfg = json.loads(self.read("schema/sources.json"))
        entry = cfg["code"][0]
        entry["co_change"] = True
        entry["co_change_docs"] = ["examples/code/docs/config.md"]
        self.write("schema/sources.json", json.dumps(cfg, ensure_ascii=False, indent=2) + "\n")

    def test_co_change_requires_docs(self) -> None:
        self._enable_co_change()
        changed = self.tmp / "changed.txt"
        changed.write_text("examples/code/config.py\n", encoding="utf-8")
        data = self.check_json("--changed-files", str(changed))
        self.assertIn(
            "TRUTH_DOCS_NOT_UPDATED",
            {i["code"] for i in data["items"] if i["severity"] == "ERROR"},
        )

    def test_co_change_passes_when_docs_changed(self) -> None:
        self._enable_co_change()
        changed = self.tmp / "changed.txt"
        changed.write_text("examples/code/config.py\nexamples/code/docs/config.md\n", encoding="utf-8")
        data = self.check_json("--changed-files", str(changed))
        self.assertNotIn(
            "TRUTH_DOCS_NOT_UPDATED",
            {i["code"] for i in data["items"] if i["severity"] == "ERROR"},
        )

    def test_allow_truth_only(self) -> None:
        self._enable_co_change()
        changed = self.tmp / "changed.txt"
        changed.write_text("examples/code/config.py\n", encoding="utf-8")
        data = self.check_json("--changed-files", str(changed), "--allow-truth-only")
        self.assertNotIn(
            "TRUTH_DOCS_NOT_UPDATED",
            {i["code"] for i in data["items"] if i["severity"] == "ERROR"},
        )

    # -- output formats ---------------------------------------------------
    def test_sarif_output(self) -> None:
        self.replace("docs/index.md", "related: []", 'related: ["docs.missing:see-also"]')
        proc = self.run_check("--format", "sarif")
        data = json.loads(proc.stdout)
        self.assertEqual(data["version"], "2.1.0")
        results = data["runs"][0]["results"]
        rel = next(r for r in results if r["ruleId"] == "REL_TARGET")
        self.assertEqual(rel["level"], "error")
        self.assertEqual(rel["locations"][0]["physicalLocation"]["artifactLocation"]["uri"], "docs/index.md")
        self.assertIn("repoKit/v1", rel["partialFingerprints"])

    def test_github_output(self) -> None:
        self.replace("docs/index.md", "related: []", 'related: ["docs.missing:see-also"]')
        proc = self.run_check("--format", "github")
        self.assertIn("::error file=docs/index.md", proc.stdout)

    def test_baseline_v2_fingerprint(self) -> None:
        self.replace("docs/index.md", "related: []", "topics: [growth]\nrelated: []")
        baseline = self.tmp / "baseline-v2.json"
        self.run_check("--write-baseline", str(baseline), "--baseline-format", "v2")
        data = json.loads(baseline.read_text(encoding="utf-8"))
        self.assertEqual(data["version"], 2)
        self.assertTrue(all("fingerprint" in i for i in data["items"]))
        result = self.check_json("--baseline", str(baseline))
        self.assertEqual(result["errors"], 0)
        self.assertGreaterEqual(result["baselined"], 1)

    # -- summary policy / slugger ----------------------------------------
    def test_summary_policy_off_by_default(self) -> None:
        self.replace("docs/index.md", "summary: 人工导航枢纽；生成索引见 _generated/index.md。\n", "")
        self.assertNotIn("SUMMARY_MISSING", self.codes("WARN"))
        data = self.check_json("--strict-summary")
        self.assertIn("SUMMARY_MISSING", {i["code"] for i in data["items"] if i["severity"] == "WARN"})

    def test_slugger_github_option(self) -> None:
        self.tax_update(lambda t: t.update({"slugger": "github"}))
        self.append("docs/usage.md", "\n[配置](../examples/code/docs/config.md#运行时配置)\n")
        self.assertNotIn("ANCHOR_BROKEN", self.codes())

    # -- skills profile ---------------------------------------------------
    def _write_skill(self, name: str = "demo", description: str | None = None, dirname: str = "demo") -> None:
        desc = description or ("演示技能：" + "用于验证 SKILL.md 的 name/description 契约。" * 2)
        self.write(
            f"skills/{dirname}/SKILL.md",
            "---\n"
            f"name: {name}\n"
            f"description: {desc}\n"
            "agent_created: true\n"
            "---\n"
            "# Demo\n",
        )

    def test_skill_profile_valid(self) -> None:
        self._write_skill()
        self.assertEqual(self.check_json()["errors"], 0)

    def test_skill_profile_requires_name(self) -> None:
        self.write(
            "skills/demo/SKILL.md",
            "---\n"
            "description: 只有描述，没有 name。\n"
            "---\n"
            "# Demo\n",
        )
        self.assertIn("SKILL_SCHEMA", self.codes())

    def test_skill_profile_name_matches_dir(self) -> None:
        self._write_skill(name="other", dirname="demo")
        self.assertIn("SKILL_NAME_DIR", self.codes())

    def test_skill_profile_description_min_length(self) -> None:
        self._write_skill(description="太短")
        self.assertIn("SKILL_DESC_SHORT", self.codes())

    def test_skill_profile_links_are_checked(self) -> None:
        self._write_skill()
        self.append("skills/demo/SKILL.md", "\n[坏链接](missing.md)\n")
        self.assertIn("LINK_BROKEN", self.codes())

    def test_link_only_reference_needs_no_frontmatter(self) -> None:
        self.tax_update(lambda t: t.update({"link_only_files": ["skills/**/references/*.md"]}))
        self.write("skills/demo/references/notes.md", "# 长资料\n\n不需要 frontmatter。\n")
        self.assertNotIn("FM_MISSING", self.codes())

    # -- v2.1 compatibility ----------------------------------------------
    def test_v21_style_page_still_valid(self) -> None:
        self.write(
            "docs/v21.md",
            "---\n"
            "id: docs.v21\n"
            "title: v2.1 风格页\n"
            "type: explanation\n"
            "kind: note\n"
            "status: active\n"
            'owner: "@platform"\n'
            "source_type: doc\n"
            "source: docs/usage.md\n"
            "last_reviewed: 2026-11-11\n"
            "related: []\n"
            "---\n"
            "# v2.1 风格页\n",
        )
        self.append("docs/index.md", "\n[v2.1](v21.md)\n")
        self.assertEqual(self.check_json()["errors"], 0)


    # -- v2.3 pitfall -----------------------------------------------------
    PITFALL_FM = (
        "---\n"
        "id: docs.pitfall.demo\n"
        "title: 演示坑\n"
        "summary: 一句话说清会踩什么。\n"
        "type: how-to\n"
        "kind: pitfall\n"
        "status: active\n"
        'owner: "@platform"\n'
        "severity: high\n"
        "symptom: 运行命令后报找不到配置。\n"
        "cause: 配置写在了被忽略的目录里。\n"
        "detect: 检查配置是否位于 include 范围内。\n"
        "avoid: 配置只放在 docs/ 下。\n"
        "recover: 把配置移回 docs/ 并重新生成。\n"
        "applies_to: [docs.usage]\n"
        "source_type: doc\n"
        "source: docs/usage.md\n"
        "last_reviewed: 2026-11-11\n"
        "related: []\n"
        "---\n"
        "# 演示坑\n\n正文。\n"
    )

    def _link_pitfall(self) -> None:
        self.append("docs/index.md", "\n[演示坑](pitfall-demo.md)\n")

    def test_pitfall_valid(self) -> None:
        self.write("docs/pitfall-demo.md", self.PITFALL_FM)
        self._link_pitfall()
        self.assertEqual(self.check_json()["errors"], 0)
        self.assertNotIn("ORPHAN", self.codes("WARN"))

    def test_pitfall_missing_field(self) -> None:
        self.write("docs/pitfall-demo.md", self.PITFALL_FM)
        self.replace("docs/pitfall-demo.md", "detect: 检查配置是否位于 include 范围内。\n", "")
        self.append("docs/index.md", "\n[演示坑](pitfall-demo.md)\n")
        self.assertIn("PITFALL_FIELD", self.codes())

    def test_pitfall_unknown_target(self) -> None:
        self.write("docs/pitfall-demo.md", self.PITFALL_FM.replace("docs.usage", "docs.missing"))
        self._link_pitfall()
        self.assertIn("PITFALL_TARGET", self.codes())

    def test_pitfall_self_target(self) -> None:
        self.write(
            "docs/pitfall-demo.md",
            self.PITFALL_FM.replace("applies_to: [docs.usage]", "applies_to: [docs.pitfall.demo]"),
        )
        self._link_pitfall()
        self.assertIn("PITFALL_SELF", self.codes())

    def test_pitfall_resolved_skips_stale(self) -> None:
        self.write(
            "docs/pitfall-demo.md",
            self.PITFALL_FM.replace("status: active", "status: resolved")
            .replace("last_reviewed: 2026-11-11", "last_reviewed: 2020-01-01"),
        )
        self._link_pitfall()
        self.assertNotIn("STALE", self.codes())

    def test_pitfall_applies_to_skill(self) -> None:
        self._write_skill()
        self.write("docs/pitfall-demo.md", self.PITFALL_FM.replace("docs.usage", "demo"))
        self._link_pitfall()
        self.assertEqual(self.check_json()["errors"], 0)

    def test_pitfall_index_generated(self) -> None:
        self.write("docs/pitfall-demo.md", self.PITFALL_FM)
        self._link_pitfall()
        proc = subprocess.run(
            [sys.executable, str(self.root / "scripts/generate.py"), "--root", str(self.root), "--write"],
            capture_output=True, text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        text = self.read("docs/_generated/pitfalls.md")
        self.assertIn("演示坑", text)
        self.assertIn("high", text)
        self.assertIn("`docs.usage`", text)
        check = subprocess.run(
            [sys.executable, str(self.root / "scripts/generate.py"), "--root", str(self.root), "--check"],
            capture_output=True, text=True,
        )
        self.assertEqual(check.returncode, 0, check.stdout)


if __name__ == "__main__":
    unittest.main()
