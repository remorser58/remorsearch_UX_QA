"""Offline safeguards for the single-command installer.

These tests never run npm or download a browser. They check the decisions the
installer must get right before it acts: Node 22 detection, destination safety
(symlinks, unrelated folders, source overlap), the payload contract of a fresh
install, full preservation of user state on update, and rollback when driver
preparation fails before activation.
"""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest
from unittest import mock

import _paths  # noqa: F401  (keeps test discovery aligned with the other suites)

REPO = _paths.REPO
INSTALL_SCRIPT = REPO / "scripts" / "install.py"
MODES = ("research", "persona-qa", "ergonomics", "loop")
RUN_SENTINEL = ".ux-loop/run-checkpoint.json"
RUN_SENTINEL_BODY = '{"checkpoint": "user run record"}'


def load_installer():
    spec = importlib.util.spec_from_file_location("remorsearch_install", INSTALL_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def succeed(command, cwd, env):
    return subprocess.CompletedProcess(command, 0, "recorded", "")


def fail(command, cwd, env):
    return subprocess.CompletedProcess(command, 1, "", "simulated npm failure")


class NodeVersionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.installer = load_installer()

    def test_supported_and_unsupported_versions_are_parsed(self):
        parse = self.installer.parse_node_version
        self.assertEqual(parse("v22.23.3"), 22)
        self.assertEqual(parse("22.0.0"), 22)
        self.assertEqual(parse("v26.8.1"), 26)
        self.assertIsNone(parse(""))
        self.assertIsNone(parse("not a version"))
        self.assertIsNone(parse("22"))

    def test_target_destination_uses_one_skill_folder_per_host(self):
        home = Path("/fake-home")
        codex = self.installer.target_destination("codex", home)
        claude = self.installer.target_destination("claude", home)
        self.assertEqual(codex, home / ".codex/skills/remorsearch-ux-qa")
        self.assertEqual(claude, home / ".claude/skills/remorsearch-ux-qa")
        self.assertEqual(codex.name, "remorsearch-ux-qa")

    def test_target_and_destination_are_mutually_exclusive(self):
        with self.assertRaises(SystemExit) as caught:
            self.installer.main(["--target", "codex", "--destination", "/tmp/x"])
        self.assertEqual(caught.exception.code, 2)


class DestinationGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.installer = load_installer()

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="remorsearch-install-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.home = self.root / "home"
        self.repo = self.root / "repo"
        self.home.mkdir()
        self.repo.mkdir()

    def problems(self, destination):
        return self.installer.destination_problems(
            destination, home=self.home, repo=self.repo)

    def test_a_fresh_destination_is_accepted(self):
        self.assertEqual(self.problems(self.root / "skills/remorsearch-ux-qa"), [])

    def test_an_empty_existing_folder_is_accepted(self):
        destination = self.root / "empty"
        destination.mkdir()
        self.assertEqual(self.problems(destination), [])

    def test_the_root_and_home_are_refused(self):
        self.assertIn("filesystem root", "; ".join(self.problems(Path("/"))))
        self.assertIn("home directory itself", "; ".join(self.problems(self.home)))

    def test_overlapping_the_source_repository_is_refused(self):
        inside = self.problems(self.repo / "nested")
        ancestor = self.problems(self.repo.parent)
        self.assertIn("overlaps the source repository", "; ".join(inside))
        self.assertIn("overlaps the source repository", "; ".join(ancestor))

    def test_symlinked_components_and_destinations_are_refused(self):
        real = self.root / "real"
        real.mkdir()
        link = self.root / "link"
        link.symlink_to(real, target_is_directory=True)
        self.assertIn("symlinked path component", "; ".join(self.problems(link / "skill")))
        self.assertIn("the destination itself is a symlink",
                      "; ".join(self.problems(link)))

    def test_files_in_the_path_are_refused(self):
        blocked = self.root / "not-a-directory"
        blocked.write_text("x", encoding="utf-8")
        self.assertIn("path component is not a directory",
                      "; ".join(self.problems(blocked / "skill")))

    def test_an_unrelated_existing_folder_is_refused(self):
        destination = self.root / "unrelated"
        destination.mkdir()
        (destination / "other-skill.md").write_text("x", encoding="utf-8")
        self.assertIn("unrelated folder", "; ".join(self.problems(destination)))

    def test_an_owned_installation_is_recognized(self):
        destination = self.root / "remorsearch-ux-qa"
        destination.mkdir()
        (destination / "SKILL.md").write_text("---\nname: remorsearch-ux-qa\n---\n",
                                               encoding="utf-8")
        (destination / "manifest.remorsearch.json").write_text(
            json.dumps({"engine": {"name": "remorsearch-ux-qa"}}), encoding="utf-8")
        self.assertEqual(self.problems(destination), [])

    def test_a_manifest_for_another_skill_is_not_owned(self):
        destination = self.root / "other"
        destination.mkdir()
        (destination / "SKILL.md").write_text("---\nname: other\n---\n", encoding="utf-8")
        (destination / "manifest.remorsearch.json").write_text(
            json.dumps({"engine": {"name": "other"}}), encoding="utf-8")
        self.assertIn("unrelated folder", "; ".join(self.problems(destination)))


class InstallSkillTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.installer = load_installer()

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="remorsearch-install-tree-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.destination = self.root / "installed"
        self.node = str(self.root / "node22" / "node")
        self.npm_cli = str(self.root / "node22" / "npm-cli.js")

    def install(self, runner=succeed):
        return self.installer.install_skill(
            self.destination, node=self.node, npm_cli=self.npm_cli,
            home=self.root / "home", repo=REPO, runner=runner,
            progress=lambda *_: None)

    def verify_installed_launcher(self):
        environment = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
        return subprocess.run(
            [sys.executable, str(self.destination / "scripts/remorsearch.py"), "verify"],
            text=True, capture_output=True, env=environment, timeout=120)

    def test_fresh_install_lands_one_verified_skill_with_every_component(self):
        result = self.install()
        self.assertEqual(Path(result["skill_directory"]), self.destination.resolve())
        self.assertIsNone(result["backup"])
        self.assertEqual(sorted(self.destination.rglob("SKILL.md")),
                         [self.destination / "SKILL.md"])
        manifest = json.loads((self.destination / "manifest.remorsearch.json")
                              .read_text(encoding="utf-8"))
        self.assertEqual(manifest["payload_sha256"], result["payload_sha256"])
        self.assertEqual(manifest["engine"]["name"], "remorsearch-ux-qa")
        for mode in MODES:
            self.assertTrue((self.destination / "references" / mode / "workflow.md").is_file(),
                            mode)
        self.assertTrue((self.destination / "references/insane-search/SOURCE.md").is_file())
        verification = self.verify_installed_launcher()
        self.assertEqual(verification.returncode, 0, verification.stderr)
        self.assertTrue(json.loads(verification.stdout)["valid"])

    def test_updating_archives_every_user_record_and_symlink(self):
        self.install()
        notes = self.destination / "operator-notes.md"
        notes.write_text("local edit", encoding="utf-8")
        sentinel = self.destination / RUN_SENTINEL
        sentinel.parent.mkdir()
        sentinel.write_text(RUN_SENTINEL_BODY, encoding="utf-8")
        link = self.destination / "linked-notes.md"
        link.symlink_to("operator-notes.md")
        result = self.install()
        backup = Path(result["backup"])
        self.assertTrue(backup.is_file())
        self.assertEqual(backup.suffixes[-2:], [".tar", ".gz"])
        self.assertEqual(backup.stat().st_mode & 0o777, 0o600)
        self.assertFalse(backup.with_name(backup.name + ".partial").exists())
        self.assertEqual(list(backup.parent.glob(".remorsearch-backup-*")), [])
        with tarfile.open(backup) as archive:
            self.assertEqual(
                archive.extractfile("operator-notes.md").read(),
                b"local edit")
            self.assertEqual(
                archive.extractfile(RUN_SENTINEL).read().decode("utf-8"),
                RUN_SENTINEL_BODY)
            recorded_link = archive.getmember("linked-notes.md")
            self.assertTrue(recorded_link.issym())
            self.assertEqual(recorded_link.linkname, "operator-notes.md")
        self.assertFalse(notes.exists())
        self.assertFalse(sentinel.exists())
        self.assertFalse(link.exists())
        self.assertTrue(backup.parent.samefile(self.destination.parent))
        verification = self.verify_installed_launcher()
        self.assertEqual(verification.returncode, 0, verification.stderr)

    def test_an_unrelated_destination_is_refused_without_writing(self):
        self.destination.mkdir()
        (self.destination / "unrelated.txt").write_text("x", encoding="utf-8")
        with self.assertRaises(self.installer.InstallError):
            self.install()
        self.assertTrue((self.destination / "unrelated.txt").exists())
        self.assertEqual(list(self.destination.iterdir()),
                         [self.destination / "unrelated.txt"])

    def test_a_symlinked_destination_is_refused(self):
        real = self.root / "real-skill"
        real.mkdir()
        self.destination.symlink_to(real, target_is_directory=True)
        with self.assertRaises(self.installer.InstallError):
            self.install()

    def test_a_destination_inside_the_repository_is_refused(self):
        inside = REPO / "install-target-for-tests"
        with self.assertRaises(self.installer.InstallError):
            self.installer.install_skill(inside, node=self.node, npm_cli=self.npm_cli,
                                         home=self.root / "home", repo=REPO,
                                         runner=succeed, progress=lambda *_: None)
        self.assertFalse(inside.exists())

    def test_payload_corruption_after_driver_setup_never_activates(self):
        self.install(succeed)
        marker = self.destination / "operator-notes.md"
        marker.write_text("still here", encoding="utf-8")

        def corrupting_runner(command, cwd, env):
            (Path(cwd).parent.parent / "SKILL.md").write_text("corrupted",
                                                               encoding="utf-8")
            return subprocess.CompletedProcess(command, 0, "recorded", "")

        with self.assertRaises(self.installer.InstallError):
            self.install(corrupting_runner)
        self.assertEqual(marker.read_text(encoding="utf-8"), "still here")
        self.assertTrue((self.destination / "SKILL.md").is_file())
        self.assertEqual(list(self.root.glob(".remorsearch-install-*")), [])
        self.assertEqual(list(self.root.glob("*.backup-*.tar.gz")), [])


class DriverFailureTests(unittest.TestCase):
    """A failed driver preparation must never touch an existing installation."""

    @classmethod
    def setUpClass(cls):
        cls.installer = load_installer()

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="remorsearch-driver-failure-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.destination = self.root / "installed"
        self.node = str(self.root / "node22" / "node")
        self.npm_cli = str(self.root / "node22" / "npm-cli.js")

    def install(self, runner):
        return self.installer.install_skill(
            self.destination, node=self.node, npm_cli=self.npm_cli,
            home=self.root / "home", repo=REPO, runner=runner,
            progress=lambda *_: None)

    def leftovers(self):
        return (list(self.root.glob(".remorsearch-install-*"))
                + list(self.root.glob("*.backup-*.tar.gz"))
                + list(self.root.glob("*.backup-*.zip"))
                + list(self.root.glob(".remorsearch-previous-*")))

    def test_a_failed_driver_setup_rolls_back_to_the_previous_installation(self):
        self.install(succeed)
        marker = self.destination / "operator-notes.md"
        marker.write_text("still here", encoding="utf-8")
        sentinel = self.destination / RUN_SENTINEL
        sentinel.parent.mkdir()
        sentinel.write_text(RUN_SENTINEL_BODY, encoding="utf-8")
        link = self.destination / "linked-notes.md"
        link.symlink_to("operator-notes.md")
        with self.assertRaises(self.installer.DriverError):
            self.install(fail)
        self.assertEqual(marker.read_text(encoding="utf-8"), "still here")
        self.assertEqual(sentinel.read_text(encoding="utf-8"), RUN_SENTINEL_BODY)
        self.assertTrue(link.is_symlink())
        self.assertEqual(os.readlink(link), "operator-notes.md")
        self.assertTrue((self.destination / "SKILL.md").is_file())
        self.assertEqual(self.leftovers(), [])

    def test_a_failed_driver_setup_leaves_no_fresh_destination(self):
        with self.assertRaises(self.installer.DriverError):
            self.install(fail)
        self.assertFalse(self.destination.exists())
        self.assertEqual(self.leftovers(), [])

    def test_driver_commands_run_inside_the_staged_skill_with_node_first(self):
        recorded = []

        def runner(command, cwd, env):
            recorded.append((command, Path(cwd), env))
            return subprocess.CompletedProcess(command, 0, "recorded", "")

        result = self.install(runner)
        self.assertTrue((self.destination / "SKILL.md").is_file())
        self.assertTrue(recorded)
        for command, cwd, env in recorded:
            self.assertEqual(cwd.name, "web")
            staging = cwd.parent.parent
            self.assertTrue(staging.name.startswith(".remorsearch-install-"), staging)
            self.assertEqual(staging.parent, self.destination.parent)
            self.assertTrue(env["PATH"].startswith(str(Path(self.node).parent) + os.pathsep))
        self.assertEqual(recorded[0][0][0], self.node)
        self.assertEqual(Path(recorded[0][0][1]).name, "npm-cli.js")
        self.assertEqual(result["driver"]["playwright"], "recorded")


class NpmCliTests(unittest.TestCase):
    """npm runs as the CLI JavaScript entry on the verified Node.js 22."""

    @classmethod
    def setUpClass(cls):
        cls.installer = load_installer()

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="remorsearch-npm-cli-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.node_bin = self.root / "node22" / "bin"
        self.node_bin.mkdir(parents=True)
        self.node = str(self.node_bin / "node")

    def test_a_symlinked_npm_resolves_to_the_cli_entry(self):
        cli = self.root / "npm-cli.js"
        cli.write_text("require('./npm.js')\n", encoding="utf-8")
        link = self.node_bin / "npm"
        link.symlink_to(cli)
        with mock.patch("shutil.which", lambda name: str(link)):
            resolved, problem = self.installer.find_npm_cli(self.node)
        self.assertIsNone(problem)
        self.assertEqual(resolved, cli.resolve())

    def test_a_shell_wrapper_is_rejected_instead_of_using_another_node(self):
        wrapper = self.node_bin / "npm"
        wrapper.write_text("#!/bin/sh\nexec /other/node node_modules/npm/bin/npm-cli.js\n",
                           encoding="utf-8")
        with mock.patch("shutil.which", lambda name: str(wrapper)):
            resolved, problem = self.installer.find_npm_cli(self.node)
        self.assertIsNone(resolved)
        self.assertIn("npm CLI JavaScript entry", problem)

    def test_a_missing_sibling_falls_back_to_path_and_reports_clearly(self):
        (self.node_bin / "node").write_text("#!/bin/sh\n", encoding="utf-8")
        with mock.patch("shutil.which", lambda name: None):
            resolved, problem = self.installer.find_npm_cli(self.node)
        self.assertIsNone(resolved)
        self.assertIn("npm CLI JavaScript entry", problem)


if __name__ == "__main__":
    unittest.main()
