"""Exercise discovery using owned executables, never the developer's HOME."""
from __future__ import annotations

import contextlib
import importlib.util
import io
from functools import cached_property
import json
import os
from pathlib import Path
import shlex
import sys
import tempfile
import unittest

import _paths

SPEC = importlib.util.spec_from_file_location(
    "find_runtime", _paths.SKILL / "scripts/find_runtime.py")
assert SPEC is not None and SPEC.loader is not None
runtime = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = runtime
SPEC.loader.exec_module(runtime)


class RuntimeFixture:
    def __init__(self, case: unittest.TestCase) -> None:
        directory = tempfile.TemporaryDirectory()
        case.addCleanup(directory.cleanup)
        self.base = Path(directory.name).resolve()
        self.home = self.base / "home"
        self.home.mkdir()
        self.bin = self.base / "bin"
        self.bin.mkdir()
        self.settings = runtime.Search(
            home=self.home, path=(self.bin,), system_bins=(), timeout=1.0)


class FindRuntimeTests(unittest.TestCase):
    @cached_property
    def fixture(self) -> RuntimeFixture:
        return RuntimeFixture(self)

    def executable(self, relative, body, interpreter=sys.executable):
        path = self.fixture.base / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("#!" + interpreter + "\n" + body + "\n")
        path.chmod(0o700)
        return path

    def version(self, relative, version):
        return self.executable(relative, "printf '%s\\n' " + shlex.quote(version), "/bin/sh")

    def test_highest_python_wins_over_path_and_manager_order(self):
        self.version("bin/python3", "Python 3.9.6")
        self.version("home/.pyenv/versions/3.11.16/bin/python3", "Python 3.11.16")
        self.version("home/.local/share/uv/python/cpython-3.13-x/bin/python3",
                     "Python 3.13.9")
        highest = self.version(
            "home/.local/share/uv/python/cpython-3.13.15-x/bin/python3",
            "Python 3.13.15")
        self.version("home/.local/bin/python3.12", "Python 3.12.14")
        report = runtime.discover(self.fixture.settings)
        self.assertEqual(report["python"], {"path": str(highest), "version": "3.13.15"})

    def test_node22_selects_highest_patch_then_absolute_path(self):
        self.version("bin/node", "v24.1.0")
        self.version("home/.nvm/versions/node/v22.8.0/bin/node", "v22.8.0")
        first = self.version("home/.asdf/installs/nodejs/22.12.0/bin/node", "v22.12.0")
        self.version("home/.local/share/mise/installs/node/22.12.0/bin/node", "v22.12.0")
        report = runtime.discover(self.fixture.settings)
        self.assertEqual(report["node22"], {"path": str(first), "version": "22.12.0"})

    def test_missing_python_returns_exit_three_and_optional_node_gap(self):
        self.version("bin/python3", "Python 3.9.6")
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = runtime.main(self.fixture.settings)
        report = json.loads(output.getvalue())
        self.assertEqual(code, 3)
        self.assertIsNone(report["python"])
        self.assertIsNone(report["node22"])
        self.assertEqual({gap["runtime"]: gap["required"] for gap in report["gaps"]},
                         {"python": True, "node22": False})
        self.assertEqual(report["checked"][0]["status"], "unsupported")

    def test_missing_node_does_not_block_supported_python(self):
        self.version("bin/python3", "Python 3.10.0")
        with contextlib.redirect_stdout(io.StringIO()):
            code = runtime.main(self.fixture.settings)
        self.assertEqual(code, 0)

    def test_candidate_timeout_is_recorded_and_next_candidate_still_runs(self):
        self.executable("bin/python3", "import signal; signal.pause()")
        good = self.version("bin/python3.12", "Python 3.12.14")
        report = runtime.discover(self.fixture.settings)
        self.assertEqual(report["python"]["path"], str(good))
        self.assertEqual(next(item for item in report["checked"]
                              if item["path"] == str(self.fixture.bin / "python3"))["status"],
                         "timeout")

    def test_failed_and_malformed_probes_are_retained(self):
        failed = self.executable("bin/python3", "printf 'broken\\n'; exit 7", "/bin/sh")
        malformed = self.version("bin/python3.11", "Python 3.11.bad")
        denied = self.version("bin/python3.12", "Python 3.12.14")
        denied.chmod(0o600)
        report = runtime.discover(self.fixture.settings)
        facts = {item["path"]: item for item in report["checked"]}
        self.assertEqual(facts[str(failed)]["returncode"], 7)
        self.assertEqual(facts[str(failed)]["output"], "broken")
        self.assertEqual(facts[str(malformed)]["status"], "invalid-version")
        self.assertEqual(facts[str(denied)]["status"], "unavailable")
        self.assertIsNone(report["python"])

    def test_real_paths_are_deduplicated(self):
        actual = self.version("bin/python3.12", "Python 3.12.14")
        (self.fixture.bin / "python3").symlink_to(actual)
        report = runtime.discover(self.fixture.settings)
        self.assertEqual(len(report["checked"]), 1)
        self.assertEqual(report["python"]["path"], str(actual))

    def test_version_reported_on_stderr_is_supported(self):
        path = self.executable("bin/python3", "printf 'Python 3.11.16\\n' >&2", "/bin/sh")
        report = runtime.discover(self.fixture.settings)
        self.assertEqual(report["python"], {"path": str(path), "version": "3.11.16"})

    def test_path_search_stops_at_its_declared_bound(self):
        path = tuple(self.fixture.base / ("path" + str(index)) for index in range(33))
        outside = self.version("path32/python3", "Python 3.13.15")
        settings = runtime.Search(home=self.fixture.home, path=path, system_bins=())
        report = runtime.discover(settings)
        self.assertIsNone(report["python"])
        self.assertNotIn(str(outside), [item["path"] for item in report["checked"]])

    def test_trusted_manager_discovery_still_works_from_home(self):
        path = self.version("home/.local/share/uv/python/3.13.15/bin/python3",
                            "Python 3.13.15")
        previous = Path.cwd()
        self.addCleanup(os.chdir, previous)
        os.chdir(self.fixture.home)
        report = runtime.discover(self.fixture.settings)
        self.assertEqual(report["python"]["path"], str(path))

    def test_no_home_writes_or_recursive_target_discovery(self):
        self.version("bin/python3", "Python 3.12.14")
        marker = self.fixture.home / "unexpected-execution"
        self.executable("home/projects/product/bin/python3",
                        "from pathlib import Path; Path(" + repr(str(marker)) + ").touch()")
        before = {str(path): path.read_bytes() if path.is_file() else None
                  for path in self.fixture.home.rglob("*")}
        report = runtime.discover(self.fixture.settings)
        after = {str(path): path.read_bytes() if path.is_file() else None
                 for path in self.fixture.home.rglob("*")}
        self.assertEqual(before, after)
        self.assertEqual(len(report["checked"]), 1)
        self.assertFalse(marker.exists())

    def test_relative_path_and_current_workspace_candidates_are_not_executed(self):
        marker = self.fixture.base / "unexpected-execution"
        self.executable("workspace/python3",
                        "from pathlib import Path; Path(" + repr(str(marker)) + ").touch()")
        previous = Path.cwd()
        self.addCleanup(os.chdir, previous)
        os.chdir(self.fixture.base / "workspace")
        settings = runtime.Search(home=self.fixture.home, path=(Path("."), Path.cwd()),
                                  system_bins=(), timeout=0.2)
        report = runtime.discover(settings)
        self.assertIsNone(report["python"])
        self.assertFalse(marker.exists())

    def test_manager_and_system_layouts_are_bounded_and_supported(self):
        locations = (
            "home/.local/share/mise/installs/python/3.12.14/bin/python3",
            "home/.asdf/installs/python/3.12.14/bin/python3",
            "home/.local/share/fnm/node-versions/v22.12.0/installation/bin/node",
            "home/.volta/tools/image/node/22.12.0/bin/node",
            "system/python3.12",
        )
        for location in locations:
            with self.subTest(location=location):
                path = self.version(location, "v22.12.0" if location.endswith("/node")
                                    else "Python 3.12.14")
                settings = runtime.Search(home=self.fixture.home, path=(),
                                          system_bins=(self.fixture.base / "system",), timeout=0.2)
                report = runtime.discover(settings)
                self.assertIn(str(path), [item["path"] for item in report["checked"]])


if __name__ == "__main__":
    unittest.main()
