"""Offline acceptance tests for the self-contained Remorsearch distribution."""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
import zipfile

import _paths

REPO = _paths.REPO
SCRIPT = REPO / "scripts/build_insane_search_bundle.py"
BASE_TEXT = """---
name: insane-search
description: >
  Read blocked links and media using their original access methods.
metadata:
  short-description: Original local input
---

# Insane Search

## Original URL route

An ordinary URL request uses [the original route](references/fallback.md).
The original route's wording and resource files must survive integration.
"""


def load_builder():
    # The builder is a repository tool, not part of the engine's scripts package.
    script_path = str(SCRIPT.parent)
    sys.path.insert(0, script_path)
    try:
        spec = importlib.util.spec_from_file_location("insane_search_bundle_builder", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.remove(script_path)


def make_base(root: Path) -> Path:
    root.mkdir()
    (root / "SKILL.md").write_text(BASE_TEXT, encoding="utf-8")
    (root / "references").mkdir()
    (root / "references/fallback.md").write_text("# Original route\n\n## Public method\n\ncurl https://example.com/public\n", encoding="utf-8")
    return root


def source_snapshot(root: Path) -> dict:
    return {path.relative_to(root).as_posix(): (path.read_bytes(), path.stat().st_mtime_ns)
            for path in root.rglob("*") if path.is_file()}


class BundleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.builder = load_builder()

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="insane-search-bundle-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.base = make_base(self.root / "base")
        self.output = self.root / "distribution"

    def build(self):
        return self.builder.build(self.base, self.output)

    def launcher(self, *args, root=None, cwd=None):
        skill = root or self.output / "remorsearch-ux-qa"
        environment = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
        return subprocess.run([sys.executable, str(skill / "scripts/remorsearch.py"), *args],
                              cwd=cwd or self.root, env=environment, text=True,
                              capture_output=True, timeout=60)

    def test_input_is_preserved_and_original_entrypoint_is_retained(self):
        before = source_snapshot(self.base)
        self.build()
        self.assertEqual(source_snapshot(self.base), before)
        skill = self.output / "remorsearch-ux-qa"
        self.assertEqual((skill / "references/insane-search/SOURCE.md").read_bytes(),
                         (self.base / "SKILL.md").read_bytes())
        self.assertEqual((skill / "references/insane-search/references/fallback.md").read_bytes(),
                         (self.base / "references/fallback.md").read_bytes())
        self.assertEqual((skill / "SKILL.md").read_bytes(), (_paths.SKILL / "SKILL.md").read_bytes())
        manifest = json.loads((skill / self.builder.MANIFEST).read_text())
        self.assertEqual(manifest["engine"]["directory"], ".")
        self.assertEqual(manifest["toolkit"]["directory"], "references/insane-search")

    def test_checked_in_toolkit_builds_without_an_installed_skill(self):
        before = source_snapshot(self.builder.SEARCH_SOURCE)
        self.builder.build(None, self.output)
        skill = self.output / "remorsearch-ux-qa"
        manifest = json.loads((skill / self.builder.MANIFEST).read_text())
        self.assertTrue(manifest["toolkit"]["matches_recorded_snapshot"])
        recorded = json.loads((self.builder.SEARCH_SOURCE / "PROVENANCE.json").read_text())
        self.assertEqual(manifest["toolkit"]["files"], recorded["files"])
        provenance = json.loads((skill / "references/insane-search/PROVENANCE.json").read_text())
        self.assertEqual(provenance["snapshot_date"], recorded["snapshot_date"])
        for relative, receipt in recorded["files"].items():
            target = "SOURCE.md" if relative == "SKILL.md" else relative
            raw = (skill / "references/insane-search" / target).read_bytes()
            self.assertEqual(self.builder.digest(raw), receipt["sha256"])
            self.assertEqual(len(raw), receipt["bytes"])
        self.assertEqual(source_snapshot(self.builder.SEARCH_SOURCE), before)
        self.assertEqual((skill / "references/insane-search/upstream-LICENSE").read_bytes(),
                         (REPO / "integrations/insane-search/upstream-LICENSE").read_bytes())

    def test_default_and_explicit_original_bytes_produce_identical_archives(self):
        self.builder.build(None, self.output)
        shutil.rmtree(self.base)
        shutil.copytree(self.builder.SEARCH_SOURCE, self.base)
        (self.base / "SOURCE.md").rename(self.base / "SKILL.md")
        for name in ("PROVENANCE.json", "upstream-LICENSE"):
            (self.base / name).unlink()
        other = self.root / "explicit-original"
        self.builder.build(self.base, other)
        self.assertEqual((self.output / self.builder.ARCHIVE_NAME).read_bytes(),
                         (other / self.builder.ARCHIVE_NAME).read_bytes())

    def test_missing_linked_search_method_is_a_packaging_error(self):
        (self.base / "references/fallback.md").unlink()
        with self.assertRaises(self.builder.BuildError):
            self.build()
        self.assertFalse(self.output.exists())

    def test_bundle_has_one_skill_and_resolvable_engine_reading_manifest(self):
        self.build()
        skill = self.output / "remorsearch-ux-qa"
        self.assertEqual([path.relative_to(skill).as_posix() for path in skill.rglob("SKILL.md")], ["SKILL.md"])
        engine = skill
        self.assertTrue((engine / "agents/openai.yaml").is_file())
        self.assertTrue((engine / "SKILL.md").is_file())
        manifest = json.loads((engine / "references/reading.json").read_text())
        for mode in manifest["modes"].values():
            self.assertEqual(mode["before_first_action"][0], "SKILL.md")
            for field in ("before_first_action", "before_external_page", "lookup_only"):
                for relative in mode[field]:
                    self.assertTrue((engine / relative).is_file(), relative)
        for relative in ("scripts/ux_research.py", "scripts/ux_loop.py", "scripts/validate_bundle.py",
                         "uxresearch/data/routes.json", "examples/research/run_fixture.py",
                         "examples/loop/packet.json", "drivers/web/package-lock.json"):
            self.assertTrue((engine / relative).is_file(), relative)
        self.assertEqual((engine / "uxresearch/data/routes.json").read_bytes(),
                         (_paths.SKILL / "uxresearch/data/routes.json").read_bytes())

    def test_build_is_offline(self):
        with mock.patch("socket.socket", side_effect=AssertionError("Build attempted network I/O")), \
                mock.patch("subprocess.run", side_effect=AssertionError("Build launched an external command")):
            self.build()
        self.assertTrue(self.builder.verify_output(self.output)["valid"])

    def test_relocated_identical_inputs_produce_identical_archives(self):
        first = self.build()
        archive = (self.output / self.builder.ARCHIVE_NAME).read_bytes()
        other_base = self.root / "different source path"
        shutil.copytree(self.base, other_base)
        for path in other_base.rglob("*"):
            if path.is_file():
                os.utime(path, (1, 1))
        second_output = self.root / "different output path"
        second = self.builder.build(other_base, second_output)
        self.assertEqual(first["payload_sha256"], second["payload_sha256"])
        self.assertEqual(archive, (second_output / self.builder.ARCHIVE_NAME).read_bytes())
        with zipfile.ZipFile(self.output / self.builder.ARCHIVE_NAME) as zipped:
            names = zipped.namelist()
            self.assertEqual(names, sorted(set(names)))
            self.assertTrue(all(info.date_time == (1980, 1, 1, 0, 0, 0) for info in zipped.infolist()))
        raw_manifest = (self.output / "remorsearch-ux-qa/manifest.remorsearch.json").read_text()
        self.assertNotIn(str(self.base), raw_manifest)
        self.assertNotIn(str(REPO), raw_manifest)

    def test_source_license_and_engine_mit_notice_survive(self):
        supplied_license = b"A supplied publisher license retained without substitution.\n"
        (self.base / "LICENSE").write_bytes(supplied_license)
        self.build()
        skill = self.output / "remorsearch-ux-qa"
        self.assertEqual((skill / "references/insane-search/LICENSE").read_bytes(), supplied_license)
        self.assertEqual((skill / "LICENSE").read_bytes(),
                         (REPO / "LICENSE").read_bytes())
        manifest = json.loads((skill / self.builder.MANIFEST).read_text())
        self.assertEqual(manifest["toolkit"]["license_files"], ["LICENSE"])

    def test_unlicensed_input_is_identified_without_assigning_engine_license(self):
        self.build()
        skill = self.output / "remorsearch-ux-qa"
        manifest = json.loads((skill / self.builder.MANIFEST).read_text())
        self.assertEqual(manifest["toolkit"]["license_files"], [])
        self.assertNotIn("license", manifest["toolkit"])
        self.assertFalse(manifest["toolkit"]["matches_recorded_snapshot"])
        provenance = json.loads((skill / "references/insane-search/PROVENANCE.json").read_text())
        self.assertIsNone(provenance["source_repository"])
        self.assertIsNone(provenance["snapshot_date"])
        self.assertIn("does not grant or assert redistribution rights", manifest["toolkit"]["redistribution_note"])

    def test_changed_missing_and_unexpected_files_are_rejected(self):
        self.build()
        skill = self.output / "remorsearch-ux-qa"
        path = skill / "uxresearch/data/routes.json"
        original = path.read_bytes()
        path.write_bytes(b"{}")
        self.assertFalse(self.builder.verify_output(skill)["valid"])
        result = self.launcher("research", "--help")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        path.unlink()
        self.assertTrue(any("Missing file" in problem for problem in self.builder.verify_output(skill)["problems"]))
        path.write_bytes(original)
        (skill / "scripts/unregistered.py").write_text("raise RuntimeError('unexpected')\n")
        self.assertTrue(any("Unexpected file" in problem for problem in self.builder.verify_output(skill)["problems"]))

    def test_documented_runtime_state_does_not_mask_packaged_source_changes(self):
        self.build()
        skill = self.output / "remorsearch-ux-qa"
        for relative in ("drivers/web/node_modules/playwright/index.js",
                         "uxresearch/__pycache__/cli.cpython.pyc",
                         ".ux-loop/demo/checkpoint.json",
                         ".ux-research/run/state.json",
                         ".ergo-bench/results.json",
                         ".ergo-runs/run.json"):
            path = skill / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"runtime state")
        self.assertTrue(self.builder.verify_output(self.output)["valid"])
        source = skill / "drivers/web/package-lock.json"
        source.write_bytes(source.read_bytes() + b"\n")
        self.assertFalse(self.builder.verify_output(skill)["valid"])
        unexpected = skill / "scripts/node_modules/unregistered.js"
        unexpected.parent.mkdir(parents=True)
        unexpected.write_text("unregistered source")
        self.assertTrue(any("Unexpected file: scripts/node_modules" in problem
                            for problem in self.builder.verify_output(skill)["problems"]))

    def test_archive_changes_and_extra_members_are_rejected(self):
        self.build()
        archive = self.output / self.builder.ARCHIVE_NAME
        with zipfile.ZipFile(archive, "a") as zipped:
            zipped.writestr("remorsearch-ux-qa/unregistered.txt", "unexpected")
        result = self.builder.verify_output(self.output)
        self.assertFalse(result["valid"])
        self.assertTrue(any("Unexpected archive member" in problem for problem in result["problems"]))

    def test_duplicate_and_unsafe_manifest_fields_are_rejected(self):
        self.build()
        skill = self.output / "remorsearch-ux-qa"
        path = skill / self.builder.MANIFEST
        raw = path.read_text()
        path.write_text('{"schema_version":"duplicate",' + raw.lstrip()[1:])
        result = self.builder.verify_output(skill)
        self.assertFalse(result["valid"])
        self.assertIn("Duplicate manifest key", " ".join(result["problems"]))
        manifest = json.loads(raw)
        manifest["files"]["../outside"] = {"bytes": 0, "sha256": "0" * 64}
        manifest["payload_sha256"] = self.builder.helper()["payload_digest"](manifest["files"])
        path.write_text(json.dumps(manifest))
        result = self.builder.verify_output(skill)
        self.assertFalse(result["valid"])
        self.assertIn("unsafe", " ".join(result["problems"]))

    def test_source_symlinks_nested_skills_and_reserved_paths_are_rejected(self):
        outside = self.root / "outside"
        outside.mkdir()
        (outside / "secret.txt").write_text("must not be copied")
        link = self.base / "references/external"
        link.symlink_to(outside, target_is_directory=True)
        with self.assertRaises(self.builder.BuildError):
            self.build()
        link.unlink()
        nested = self.base / "assets/nested/SKILL.md"
        nested.parent.mkdir(parents=True)
        nested.write_text("nested discovery")
        with self.assertRaises(self.builder.BuildError):
            self.build()
        shutil.rmtree(self.base / "assets")
        (self.base / self.builder.MANIFEST).write_text("existing integration")
        with self.assertRaises(self.builder.BuildError):
            self.build()
        self.assertFalse(self.output.exists())

    def test_output_never_overwrites_or_recurses_into_source(self):
        self.output.mkdir()
        sentinel = self.output / "keep.txt"
        sentinel.write_text("user data")
        with self.assertRaises(self.builder.BuildError):
            self.build()
        self.assertEqual(sentinel.read_text(), "user data")
        for target in (self.base / "build", _paths.SKILL / "bundle-test-output"):
            with self.assertRaises(self.builder.BuildError):
                self.builder.build(self.base, target)
            self.assertFalse(target.exists())

    def test_bad_frontmatter_fails_before_creating_output(self):
        for text in (BASE_TEXT.replace("name: insane-search", "name: another-skill"),
                     "# Missing frontmatter\n", "\ufeff" + BASE_TEXT):
            with self.subTest(text=text[:40]):
                (self.base / "SKILL.md").write_text(text, encoding="utf-8")
                with self.assertRaises(self.builder.BuildError):
                    self.build()
                self.assertFalse(self.output.exists())

    def test_extracted_bundle_runs_without_checkout_base_or_original_output(self):
        if sys.version_info < (3, 10):
            self.skipTest("Bundled engine requires Python 3.10+")
        self.build()
        relocated = self.root / "relocated installation"
        with zipfile.ZipFile(self.output / self.builder.ARCHIVE_NAME) as zipped:
            zipped.extractall(relocated)
        skill = relocated / "remorsearch-ux-qa"
        shutil.rmtree(self.output)
        shutil.rmtree(self.base)
        caller = self.root / "another-project"
        caller.mkdir()
        result = self.launcher("ref", "SKILL.md", "components", root=skill, cwd=caller)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("persona-qa", result.stdout)
        result = self.launcher("ref", "references/insane-search/SOURCE.md",
                               "original-url-route", root=skill, cwd=caller)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("references/fallback.md", result.stdout)
        result = self.launcher("ref", "references/insane-search/references/fallback.md",
                               "public-method", root=skill, cwd=caller)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("curl https://example.com/public", result.stdout)
        self.assertNotIn("Section IDs:", result.stdout)
        result = self.launcher("paths", root=skill, cwd=caller)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["engine_directory"], str(skill))
        result = self.launcher("research", "--help", root=skill, cwd=caller)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("gate", result.stdout)
        result = self.launcher("research", "--not-a-command", root=skill, cwd=caller)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        result = self.launcher("smoke", root=skill, cwd=caller)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        smoke = json.loads(result.stdout)
        self.assertTrue(smoke["passed"])
        self.assertFalse(smoke["live_integrations_executed"])
        self.assertTrue(smoke["invented_content"])
        self.assertEqual([check["exit"] for check in smoke["checks"]], [0, 0])
        self.assertIn('"network_requests": 0', smoke["checks"][0]["stdout"])
        result = self.launcher("verify", root=skill, cwd=caller)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse(list(skill.rglob("__pycache__")))
        self.assertEqual(list(caller.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
