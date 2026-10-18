"""CLI contract: explicitly supplied --scenario files must bind every analyzed or attached run."""

from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import _paths  # noqa: F401  (puts the skill folder on sys.path)
from test_ergo_pipeline import make_run  # the owned synthetic recorded run fixture

from ergoqa import cli
from ergoqa.profiles import sample_profiles


def scenario_doc(scenario_id: str) -> dict:
    return {
        "schema_version": "ergo-scenario.v1",
        "scenario_id": scenario_id,
        "surface": {"kind": "web", "url": "http://127.0.0.1/checkout.html"},
        "task_goal_ko": "결제를 완료한다",
        "device_ids": ["galaxy-s24"],
        "targets": {"primary": ["#pay"], "destructive": ["#delete"], "critical_message": ["#error"]},
        "steps": [{"action": "tap", "target": "#pay"}],
        "timing_windows": [{"id": "toast-1", "selector": "#toast", "measure": "visible_duration"}],
        "success": {"selector_visible": "#done"},
    }


class ScenarioBindingContract(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.run_dir = make_run(self.root)
        self.profiles_path = self.root / "profiles.json"
        self.profiles_path.write_text(json.dumps({"profiles": sample_profiles(3, 7, ["galaxy-s24"])}), encoding="utf-8")
        self.matching = self.root / "scenario-matching.json"
        self.matching.write_text(json.dumps(scenario_doc("SC-checkout"), ensure_ascii=False), encoding="utf-8")
        self.mismatching = self.root / "scenario-mismatching.json"
        self.mismatching.write_text(json.dumps(scenario_doc("SC-other"), ensure_ascii=False), encoding="utf-8")

    def run_cli(self, *argv):
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            code = cli.main(list(argv))
        return code, stdout.getvalue(), stderr.getvalue()

    def analyze(self, *scenario_args):
        return self.run_cli("analyze", "--runs", str(self.run_dir), "--profiles", str(self.profiles_path),
                            "--no-gaze", "--out", str(self.root / "analyses.json"), *scenario_args)

    def analyses(self):
        return json.loads((self.root / "analyses.json").read_text(encoding="utf-8"))["analyses"]

    def test_matching_scenario_is_bound_and_reaches_run_health(self):
        code, _, err = self.analyze("--scenario", str(self.matching))
        self.assertEqual(code, cli.EXIT_OK, err)
        # The declared timing window only produces this note through the bound scenario.
        self.assertTrue(any("toast-1" in note for note in self.analyses()[0]["limitations"]))

    def test_omitted_scenario_mode_stays_valid(self):
        code, _, err = self.analyze()
        self.assertEqual(code, cli.EXIT_OK, err)
        self.assertFalse(any("toast-1" in note for note in self.analyses()[0]["limitations"]))

    def test_mismatched_scenario_is_rejected_for_analyze_and_swarm(self):
        code, _, err = self.analyze("--scenario", str(self.mismatching))
        self.assertEqual(code, cli.EXIT_USAGE, err)
        self.assertIn("'SC-checkout'", err)
        self.assertIn("omit --scenario", err)
        self.assertFalse((self.root / "analyses.json").exists())
        code, _, err = self.run_cli("swarm", "--runs", str(self.run_dir), "--profiles", str(self.profiles_path),
                                    "--scenario", str(self.mismatching), "--no-gaze",
                                    "--out", str(self.root / "swarm-out"))
        self.assertEqual(code, cli.EXIT_USAGE, err)
        self.assertIn("'SC-checkout'", err)
        self.assertFalse((self.root / "swarm-out").exists())

    def test_conflicting_duplicate_scenario_ids_are_rejected(self):
        clash = self.root / "scenario-clash.json"
        doc = scenario_doc("SC-checkout")
        doc["task_goal_ko"] = "다른 과제"
        clash.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
        code, _, err = self.analyze("--scenario", str(self.matching), "--scenario", str(clash))
        self.assertEqual(code, cli.EXIT_USAGE, err)
        self.assertIn("conflicting duplicate scenario id 'SC-checkout'", err)
        self.assertFalse((self.root / "analyses.json").exists())
        code, _, err = self.analyze("--scenario", str(self.matching), "--scenario", str(self.matching))
        self.assertEqual(code, cli.EXIT_OK, err)  # an identical repeat stays idempotent

    def test_explicit_paths_yielding_no_valid_scenarios_are_rejected(self):
        invalid = self.root / "scenario-invalid.json"
        invalid.write_text(json.dumps({"schema_version": "ux-audience-draft.v1", "scenario_id": "SC-checkout"}),
                           encoding="utf-8")
        empty_dir = self.root / "scenarios-empty"
        empty_dir.mkdir()
        for scenario_arg in (str(invalid), str(empty_dir)):
            code, _, err = self.analyze("--scenario", scenario_arg)
            self.assertEqual(code, cli.EXIT_USAGE, err)
            self.assertIn("no valid ergo-scenario.v1 documents", err)
            self.assertIn("omit --scenario", err)
            self.assertFalse((self.root / "analyses.json").exists())

    def test_attach_rejects_a_scenario_file_that_does_not_match_the_run(self):
        qa = json.loads((Path(__file__).parent / "fixtures" / "valid-bundle.json").read_text(encoding="utf-8"))
        qa["records"]["findings"][0]["severity"] = "P2"  # no second-pass reviews needed for this rejection
        qa_path = self.root / "qa.json"
        qa_path.write_text(json.dumps(qa, ensure_ascii=False), encoding="utf-8")
        out_path = self.root / "attached.json"
        code, _, err = self.run_cli("attach", "--bundle", str(qa_path), "--runs", str(self.run_dir),
                                    "--profiles", str(self.profiles_path), "--scenario", str(self.mismatching),
                                    "--bind", "scenario-1=EP-01", "--receipts-dir", str(self.root / "receipts"),
                                    "--no-gaze", "--out", str(out_path))
        self.assertEqual(code, cli.EXIT_USAGE, err)
        self.assertIn("'SC-checkout'", err)
        self.assertFalse(out_path.exists())
        self.assertFalse((self.root / "receipts").exists())


if __name__ == "__main__":
    unittest.main()
