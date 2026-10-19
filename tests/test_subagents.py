"""The first-run choice of the subagent model and reasoning effort.

The menu logic is tested without a terminal: keys move and choose, a plain prompt
takes numbers, the saved file round-trips, --show tells an agent whether this is the
first run, and the installer saves flag values without asking and asks nothing
without a terminal.
"""
from __future__ import annotations

import importlib.util
import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

import _paths  # noqa: F401

SCRIPT = _paths.SKILL / "scripts" / "subagents.py"
spec = importlib.util.spec_from_file_location("subagents", SCRIPT)
subagents = importlib.util.module_from_spec(spec)
spec.loader.exec_module(subagents)


class MenuTests(unittest.TestCase):
    def test_keys_move_wrap_jump_and_choose(self):
        index, done = 0, False
        for key in ("up", "down", "down", "3", "j"):
            index, done = subagents.step(index, key, 5)
        self.assertEqual((index, done), (3, False))
        self.assertEqual(subagents.step(4, "down", 5), (0, False))
        self.assertEqual(subagents.step(2, "enter", 5), (2, True))
        self.assertEqual(subagents.step(2, "9", 5), (2, False))

    def test_plain_prompt_takes_a_number_or_keeps_the_default(self):
        rows = [("a", ""), ("b", ""), ("c", "")]
        answers = iter(["x", "3"])
        with redirect_stdout(io.StringIO()):
            self.assertEqual(subagents.select_numbered("t", rows, 0, ask=lambda _: next(answers)), 2)
            self.assertEqual(subagents.select_numbered("t", rows, 1, ask=lambda _: ""), 1)


class SavedChoiceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.env = mock.patch.dict(os.environ, {"XDG_CONFIG_HOME": self.tmp.name, "CODEX_HOME": self.tmp.name})
        self.env.start()

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()

    def run_main(self, *args):
        out = io.StringIO()
        with redirect_stdout(out):
            code = subagents.main(list(args))
        return code, out.getvalue()

    def test_show_exits_3_until_a_choice_is_saved(self):
        self.assertEqual(self.run_main("--show")[0], 3)
        self.assertEqual(self.run_main("--host", "codex", "--model", "gpt-x", "--effort", "high")[0], 0)
        code, out = self.run_main("--show")
        self.assertEqual(code, 0)
        saved = json.loads(out)
        self.assertEqual(saved["roles"]["operator"], {"model": "gpt-x", "effort": "high", "agent_type": None})
        self.assertEqual(saved["roles"]["judge"]["model"], "gpt-x")
        self.assertEqual(oct(subagents.config_path().stat().st_mode & 0o777), "0o600")

    def test_an_identifier_with_shell_characters_is_refused(self):
        with mock.patch("sys.stderr", io.StringIO()):
            self.assertEqual(self.run_main("--model", "gpt; rm -rf ~")[0], 2)
        self.assertIsNone(subagents.load_config())

    def test_codex_choices_come_from_the_listed_models_in_the_cache(self):
        Path(self.tmp.name, "models_cache.json").write_text(json.dumps({"models": [
            {"slug": "m-listed", "display_name": "M", "visibility": "list", "default_reasoning_level": "medium",
             "supported_reasoning_levels": [{"effort": "low"}, {"effort": "medium"}]},
            {"slug": "m-hidden", "visibility": "hide"}]}), encoding="utf-8")
        options = subagents.host_options("codex")
        self.assertEqual([m["id"] for m in options["models"]], ["m-listed"])
        self.assertEqual(options["efforts"], ["low", "medium"])


class InstallerTests(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.spec_from_file_location("remorsearch_install", _paths.REPO / "scripts" / "install.py")
        self.installer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.installer)

    def args(self, **kw):
        base = {"target": "codex", "subagent_model": None, "subagent_effort": None, "no_prompt": False}
        return mock.Mock(**{**base, **kw})

    def test_flags_save_without_asking(self):
        with mock.patch.object(self.installer.subprocess, "run") as run:
            run.return_value.returncode = 0
            record = self.installer.choose_subagents(Path("/skill"), self.args(subagent_model="m", subagent_effort="high"))
        command = run.call_args.args[0]
        self.assertEqual(command[-4:], ["--model", "m", "--effort", "high"])
        self.assertTrue(record["asked"])

    def test_without_a_terminal_nothing_is_asked(self):
        with mock.patch.object(self.installer.subprocess, "run") as run, \
                mock.patch("sys.stdin", io.StringIO()):
            record = self.installer.choose_subagents(Path("/skill"), self.args())
        run.assert_not_called()
        self.assertFalse(record["asked"])


if __name__ == "__main__":
    unittest.main()
