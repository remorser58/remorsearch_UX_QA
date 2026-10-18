"""The release file list: what a user installs, what it weighs, and what must never ship.

Three groups, all offline checks against scripts/release_files.py:

  * The list is the skills/remorsearch-ux-qa/ tree minus what the skill does not need
    at run time (the pinned driver node_modules, caches and local run folders);
    documented synthetic self-test fixtures remain installed. Every entry exists on disk, the order is sorted, and
    the printed total matches the file sizes.
  * Files the shipped tools read at run time stay listed, so an exclusion cannot
    silently swallow a mode.
  * The denylist flags every internal note and folder, and the script exits 1 when a
    shipped file matches one — but not when the file sits in a pruned tree.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import _paths  # noqa: F401  (puts the skill folder on sys.path)

REPO = _paths.REPO
SKILL = _paths.SKILL
SCRIPT = REPO / "scripts" / "release_files.py"

# Files the shipped tools read while doing their job, one per lane: the entry point,
# the loop smoke the README tells a user to run, the pinned driver install, and the
# demo fixtures that smoke reads.
RUN_TIME_FILES = (
    "SKILL.md",
    "references/insane-search/SOURCE.md",
    "references/insane-search/references/public-api.md",
    "references/insane-search/PROVENANCE.json",
    "references/insane-search/upstream-LICENSE",
    "scripts/smoke_loop.py",
    "drivers/web/package-lock.json",
    "examples/loop/packet.json",
    "uxloop/io.py",
    "drivers/web/fixtures/inspect.html",
    "drivers/web/selftest.mjs",
)
PRUNED_PARTS = ("node_modules", "__pycache__", ".pytest_cache", ".ux-loop", ".ux-research")
PRUNED_PATHS = ()
DENIED_PATHS = (
    "skills/remorsearch-ux-qa/HANDOFF.md",
    "skills/remorsearch-ux-qa/COORDINATION.md",
    "skills/remorsearch-ux-qa/docs/handoff/design.md",
    "skills/remorsearch-ux-qa/references/WP9-PROGRESS.md",
    "skills/remorsearch-ux-qa/reports/FINAL-REPORT.md",
    "skills/remorsearch-ux-qa/_evidence/bundle.json",
    "skills/remorsearch-ux-qa/_bench/suite.json",
    "skills/remorsearch-ux-qa/.omo/tasks.json",
    "skills/remorsearch-ux-qa/.omc/state.json",
)


def load_release_files():
    spec = importlib.util.spec_from_file_location("release_files", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_script(*arguments):
    return subprocess.run(
        [sys.executable, str(SCRIPT)] + [str(argument) for argument in arguments],
        capture_output=True, text=True,
    )


class ReleaseListTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_release_files()
        cls.files = cls.module.release_files(SKILL)

    def test_every_listed_file_exists_under_the_skill_folder(self):
        for path, size in self.files:
            self.assertTrue(path.startswith("skills/remorsearch-ux-qa/"), path)
            on_disk = REPO / path
            self.assertTrue(on_disk.is_file(), path)
            self.assertEqual(on_disk.stat().st_size, size, path)

    def test_the_list_is_sorted_and_unique(self):
        paths = [path for path, _ in self.files]
        self.assertEqual(paths, sorted(set(paths)))

    def test_pruned_trees_are_absent(self):
        for path, _ in self.files:
            relative = path[len("skills/remorsearch-ux-qa/"):]
            for part in PRUNED_PARTS:
                self.assertNotIn(part, Path(path).parts, path)
            for pruned in PRUNED_PATHS:
                self.assertFalse(relative.startswith(pruned), path)

    def test_run_time_files_stay_listed(self):
        listed = {path for path, _ in self.files}
        for relative in RUN_TIME_FILES:
            self.assertIn(f"skills/remorsearch-ux-qa/{relative}", listed, relative)

    def test_the_script_prints_each_file_and_a_total(self):
        result = run_script()
        self.assertEqual(result.returncode, 0, result.stderr)
        lines = result.stdout.splitlines()
        listed, total = lines[:-1], lines[-1]
        self.assertEqual(len(listed), len(self.files))
        self.assertEqual(
            sum(int(line.split()[0]) for line in listed),
            sum(size for _, size in self.files),
        )
        self.assertRegex(total, rf"^{len(self.files)} files, {sum(size for _, size in self.files)} bytes total$")


class DenylistTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_release_files()

    def test_internal_notes_and_folders_are_flagged(self):
        for path in DENIED_PATHS:
            self.assertTrue(self.module.denylist_problems(path), path)

    def test_shipped_files_are_not_flagged(self):
        for path, _ in load_release_files().release_files(SKILL):
            self.assertEqual(self.module.denylist_problems(path), [], path)

    def test_files_a_user_may_install_are_not_flagged(self):
        for path in ("skills/remorsearch-ux-qa/SKILL.md",
                     "skills/remorsearch-ux-qa/references/research/workflow.md",
                     "skills/remorsearch-ux-qa/scripts/ux_loop.py",
                     "skills/remorsearch-ux-qa/drivers/web/read_page.mjs"):
            self.assertEqual(self.module.denylist_problems(path), [], path)

    def test_a_denylisted_file_in_the_tree_fails_the_script(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            tree = {
                "skills/remorsearch-ux-qa/SKILL.md": "entry point",
                "skills/remorsearch-ux-qa/_evidence/secret.json": "{}",
                "skills/remorsearch-ux-qa/node_modules/playwright/index.js": "// pinned",
                "skills/remorsearch-ux-qa/node_modules/.omo/state.json": "{}",
            }
            for relative, content in tree.items():
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content, encoding="utf-8")
            result = run_script(root)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("skills/remorsearch-ux-qa/_evidence/secret.json", result.stderr)
            self.assertNotIn("node_modules", result.stdout)
            self.assertNotIn(".omo", result.stderr)  # pruned before the denylist runs
            self.assertIn("2 files, 13 bytes total", result.stdout)

    def test_a_clean_tree_exits_zero(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            target = root / "skills/remorsearch-ux-qa/SKILL.md"
            target.parent.mkdir(parents=True)
            target.write_text("entry point", encoding="utf-8")
            result = run_script(root)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("1 files, 11 bytes total", result.stdout)

    def test_missing_skill_is_not_a_successful_empty_release(self):
        with tempfile.TemporaryDirectory() as folder:
            result = run_script(folder)
            self.assertEqual(result.returncode, 1)
            self.assertNotIn("0 files", result.stdout)

    def test_symlinked_files_and_directories_cannot_ship_outside_content(self):
        for directory in (False, True):
            with self.subTest(directory=directory), tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                skill = root / "skills/remorsearch-ux-qa"
                skill.mkdir(parents=True)
                (skill / "SKILL.md").write_text("entry point", encoding="utf-8")
                outside = root / "private"
                if directory:
                    outside.mkdir()
                    (outside / "secret.txt").write_text("not for release", encoding="utf-8")
                else:
                    outside.write_text("not for release", encoding="utf-8")
                (skill / "linked").symlink_to(outside, target_is_directory=directory)
                result = run_script(root)
                self.assertEqual(result.returncode, 1)
                self.assertNotIn("not for release", result.stdout)


if __name__ == "__main__":
    unittest.main()
