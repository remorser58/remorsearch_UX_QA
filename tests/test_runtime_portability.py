"""A relocated CLI must load its own helpers and reject unsupported interpreters."""
from __future__ import annotations

import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest

import _paths


class RuntimePortabilityTests(unittest.TestCase):
    def test_unrelated_scripts_package_cannot_shadow_bundled_validator(self):
        with tempfile.TemporaryDirectory() as directory:
            other = Path(directory) / "scripts"
            other.mkdir()
            (other / "__init__.py").write_text("raise RuntimeError('unrelated scripts loaded')\n")
            environment = {**os.environ, "PYTHONPATH": directory, "PYTHONDONTWRITEBYTECODE": "1"}
            result = subprocess.run(
                [sys.executable, str(_paths.SKILL / "scripts/ux_loop.py"), "--help"],
                cwd=directory, env=environment, capture_output=True, text=True, timeout=20)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("usage:", result.stdout)

    def test_every_main_cli_rejects_old_python_before_engine_import(self):
        probe = (
            "import runpy,sys; path=sys.argv[1]; "
            "sys.argv=[path,'--help']; sys.version_info=(3,9,6); "
            "runpy.run_path(path,run_name='__main__')"
        )
        for script in ("ux_research.py", "ux_loop.py", "ergo_qa.py"):
            with self.subTest(script=script):
                result = subprocess.run(
                    [sys.executable, "-c", probe, str(_paths.SKILL / "scripts" / script)],
                    capture_output=True, text=True, timeout=20)
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertIn("Python 3.10 or newer is required", result.stderr)
                self.assertNotIn("Traceback", result.stderr)

    def test_discovery_hint_runs_with_quoted_relocated_paths(self):
        probe = (
            "import runpy,sys; path,interpreter=sys.argv[1:3]; "
            "sys.argv=[path,'--help']; sys.version_info=(3,9,6); "
            "sys.executable=interpreter; runpy.run_path(path,run_name='__main__')"
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            runtime = root / "runtime's $probe"
            runtime.mkdir()
            interpreter = runtime / "python3"
            interpreter.symlink_to(sys.executable)
            skill = root / "skill's $probe"
            skill.mkdir()
            helper = skill / "find_runtime.py"
            shutil.copy2(_paths.SKILL / "scripts/find_runtime.py", helper)
            caller = root / "caller"
            caller.mkdir()
            environment = {**os.environ, "HOME": str(root / "home"), "PATH": str(runtime),
                           "probe": "must-not-expand", "PYTHONDONTWRITEBYTECODE": "1"}
            for name in ("ux_research.py", "ux_loop.py", "ergo_qa.py"):
                with self.subTest(script=name):
                    launcher = skill / name
                    shutil.copy2(_paths.SKILL / "scripts" / name, launcher)
                    result = subprocess.run(
                        [sys.executable, "-c", probe, str(launcher), str(interpreter)],
                        cwd=caller, env=environment, capture_output=True, text=True, timeout=20)
                    self.assertEqual(result.returncode, 2, result.stderr)
                    command = result.stderr.splitlines()[-1]
                    self.assertEqual(shlex.split(command), [str(interpreter), str(helper)])
                    discovered = subprocess.run(
                        ["/bin/sh", "-c", command], cwd=caller, env=environment,
                        capture_output=True, text=True, timeout=30)
                    self.assertEqual(discovered.returncode, 0, discovered.stderr)
                    self.assertIsNotNone(json.loads(discovered.stdout)["python"])


if __name__ == "__main__":
    unittest.main()
