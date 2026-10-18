"""Explicit task checks preserve execution evidence without claiming product success."""

import copy
import json
import tempfile
import unittest
from pathlib import Path

import _paths  # noqa: F401
from ergoqa import analyze, checks, report, swarm
from ergoqa.devices import get_device
from ergoqa.profiles import sample_profiles
from ergoqa.qa_attach import AttachError, attach_run
from ergoqa.snapshot import SnapshotError, load_run_dir, validate_run, validate_scenario
from test_ergo_pipeline import make_run
from validate_bundle import validate_bundle


def task_result(**updates):
    result = {"kind": "task_check", "id": "request-retained", "selector": "#pay", "property": "text",
              "checkpoint": 1, "step_index": 1, "snapshot_id": "S-R-1-001", "element_id": "pay",
              "passed": False, "result": "fail", "reason": None, "severity": "P1",
              "consequence": "필수 요청사항이 최종 결과에 유지되지 않았습니다."}
    return {**result, **updates}


class TaskValidationTests(unittest.TestCase):
    def test_scenario_contract_is_typed_bounded_and_fail_closed(self):
        fixture = Path(__file__).parent / "fixtures/ergo/sample_scenario.json"
        scenario = json.loads(fixture.read_text())
        scenario["steps"] = [{"action": "type", "target": "#memo", "text": "fixture", "redact": True}]
        authored = {"id": "memo-retained", "selector": "#memo", "property": "value", "from_step": 1,
                    "after_step": 1, "severity": "P2", "consequence": "요청사항을 유지해야 합니다."}
        scenario["success"] = {"task_checks": [authored]}
        self.assertEqual(validate_scenario(scenario), [])
        for changes in ({"expected": "duplicate"}, {"from_step": 2}, {"after_step": 2}, {"property": "checked"},
                        {"selector": "input[value='private']"}, {"selector": "input[ value='private']"},
                        {"selector": "input[v\\61lue='private']"}, {"selector": "#password"}, {"guess": True}):
            candidate = copy.deepcopy(scenario)
            candidate["success"]["task_checks"][0].update(changes)
            self.assertTrue(validate_scenario(candidate), changes)
        scenario["success"]["task_checks"].append(authored)
        self.assertTrue(validate_scenario(scenario))
        promoted = copy.deepcopy(scenario)
        promoted["success"]["task_checks"] = [{**authored, "redact": True}]
        del promoted["steps"][0]["target"]
        del promoted["steps"][0]["redact"]
        self.assertTrue(validate_scenario(promoted))

    def test_completed_task_failure_preserves_coverage_and_uncertainty(self):
        run = {"run_id": "R", "status": "completed", "success": False, "steps": [], "success_detail": {"criteria": [task_result()]}}
        health, notes = analyze.run_health(run, [], None)
        self.assertEqual(health, "ok")
        self.assertFalse(any("이후 화면은 검사되지" in note for note in notes))
        run["success_detail"]["criteria"] = [task_result(result="unevaluable", passed=None, reason="missing_target")]
        self.assertEqual(analyze.run_health(run, [], None)[0], "degraded")
        run["status"] = "blocked"
        self.assertEqual(analyze.run_health(run, [], None)[0], "failed")


class TaskEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.run_dir = make_run(self.root)
        self.profiles = sample_profiles(3, 7, ["galaxy-s24"])
        for path in [self.run_dir / "run.json", *self.run_dir.glob("S-*.json")]:
            doc = json.loads(path.read_text())
            doc.setdefault("surface", {})["build_id"] = "task-integrity-fixture-v1"
            path.write_text(json.dumps(doc))
        self.run = json.loads((self.run_dir / "run.json").read_text())
        self.run.update(success=False, success_basis="measured", success_detail={"criteria": [task_result()], "unevaluable": []})
        self.save_run()
        self.qa = json.loads((Path(__file__).parent / "fixtures/valid-bundle.json").read_text())
        self.qa["records"]["findings"][0]["severity"] = "P2"

    def tearDown(self):
        self.tmp.cleanup()

    def save_run(self):
        (self.run_dir / "run.json").write_text(json.dumps(self.run))

    def test_observed_failure_attaches_with_receipt_owner_and_second_pass(self):
        before = copy.deepcopy(self.qa)
        analysis = analyze.analyze_run(self.run_dir, self.profiles, cross_profile=True, gaze_enabled=False)
        task = [obs for obs in analysis["observations"] if obs["check_id"] == "TI-01"]
        self.assertEqual(len(task), 1)
        self.assertEqual(task[0]["profile_id"], "EP-01")
        self.assertEqual(task[0]["basis"], "measured")
        self.assertEqual(task[0]["measurement"]["snapshot_id"], "S-R-1-001")
        findings = swarm.aggregate([analysis], self.profiles)
        task_findings = [f for f in findings if f["check_id"] == "TI-01"]
        self.assertEqual(task_findings[0]["triggered_profiles"], ["EP-01"])
        self.assertEqual(task_findings[0]["tested_profiles"], ["EP-01"])
        self.assertEqual(task_findings[0]["profile_specific"], {})
        self.assertIn("명시한", report.render(findings, self.profiles, [analysis]))
        self.assertIn("값 비공개", report.render(findings, self.profiles, [analysis]))
        with self.assertRaisesRegex(AttachError, "P0/P1"):
            attach_run(self.qa, self.run_dir, self.profiles, {"scenario-1": "EP-01"}, receipts_root=self.root / "receipts", gaze_enabled=False)
        self.assertFalse((self.root / "receipts").exists())
        owner_analysis = analyze.analyze_run(self.run_dir, self.profiles, gaze_enabled=False)
        reviews = [{"finding_id": f"ERGO-{f['id']}@R-1@EP-01", "reviewer": "self", "task_completed": False,
                    "control_name": "결제하기", "omitted": ["필수 요청사항"], "severity": "agree", "inconclusive": False}
                   for f in swarm.aggregate([owner_analysis], self.profiles) if f["severity"] in ("P0", "P1")]
        attached = attach_run(self.qa, self.run_dir, self.profiles, {"scenario-1": "EP-01"}, receipts_root=self.root / "receipts",
                              second_pass=reviews, gaze_enabled=False)
        self.assertEqual(validate_bundle(attached, artifacts_root=self.root / "receipts"), [])
        self.assertEqual(self.qa, before)
        records = attached["records"]
        execution = next(r for r in records["runs"] if r.get("recorded_run_id") == "R-1")
        self.assertEqual(execution["status"], "completed")
        self.assertIs(execution["task_success"], False)
        observation = next(o for o in records["observations"] if o.get("check_id") == "TI-01")
        self.assertEqual(observation["receipt"]["build_id"], "task-integrity-fixture-v1")
        self.assertEqual(observation["snapshot_id"], "S-R-1-001")
        self.assertTrue((self.root / "receipts" / observation["receipt"]["artifact_path"]).is_file())
        model_findings = [f for f in records["findings"] if f.get("check_id") and checks.CATALOG[f["check_id"]].basis == "model"]
        self.assertTrue(all(f["verification_status"] == "unverified" for f in model_findings))

    def test_unknown_or_incomplete_failure_does_not_attach(self):
        for status, criterion in (("blocked", task_result()), ("failed", task_result()), ("completed", None),
                                  ("completed", task_result(passed=None, result="unevaluable", reason="missing_target"))):
            self.run.update(status=status, success_detail={"criteria": [criterion] if criterion else [], "unevaluable": []})
            self.save_run()
            with self.assertRaises(AttachError):
                attach_run(self.qa, self.run_dir, self.profiles, {"scenario-1": "EP-01"}, receipts_root=self.root / "receipts", gaze_enabled=False)

    def test_missing_capture_and_value_bearing_results_are_rejected(self):
        self.assertEqual(validate_run(self.run), [])
        self.run["success_detail"]["criteria"][0]["actual"] = "PRIVATE-SENTINEL"
        errors = validate_run(self.run)
        self.assertTrue(errors)
        self.assertNotIn("PRIVATE-SENTINEL", " ".join(errors))
        del self.run["success_detail"]["criteria"][0]["actual"]
        self.run["success_detail"]["criteria"][0]["snapshot_id"] = "S-missing"
        self.save_run()
        with self.assertRaisesRegex(SnapshotError, "task check capture"):
            load_run_dir(self.run_dir)

    def test_malformed_criteria_validate_without_crashing_the_loader(self):
        for criteria in (None, 1, True, [None], [1], ["untrusted criterion"]):
            with self.subTest(criteria=criteria):
                self.run["success_detail"]["criteria"] = criteria
                self.assertTrue(validate_run(self.run))
                self.save_run()
                with self.assertRaises(SnapshotError):
                    load_run_dir(self.run_dir)

    def test_direct_analysis_rejects_wrong_scenario_and_preserves_omitted_input(self):
        self.assertTrue(analyze.analyze_run(self.run_dir, self.profiles, gaze_enabled=False))
        for scenario in ({"schema_version": "ergo-scenario.v1", "scenario_id": "wrong"},
                         {"schema_version": "unknown", "scenario_id": self.run["scenario_id"]}):
            with self.assertRaisesRegex(ValueError, "scenario"):
                analyze.analyze_run(self.run_dir, self.profiles, scenario, gaze_enabled=False)

    def test_task_truth_and_capture_crossrefs_fail_closed(self):
        self.run["success"] = True
        self.assertTrue(validate_run(self.run))
        self.run["success_detail"]["criteria"][0].update(passed=None, result="unevaluable", reason="missing_target")
        self.assertTrue(validate_run(self.run))
        self.run["success"] = False
        self.run["success_detail"]["criteria"] = [task_result(checkpoint="final", step_index=0, snapshot_id="S-R-1-000")]
        self.save_run()
        with self.assertRaisesRegex(SnapshotError, "final task check"):
            load_run_dir(self.run_dir)
        self.run["success_detail"]["criteria"] = [task_result()]
        self.run["steps"][0]["after"] = "S-R-1-000"
        self.save_run()
        with self.assertRaisesRegex(SnapshotError, "after-capture"):
            load_run_dir(self.run_dir)


class NativeStateAckTests(unittest.TestCase):
    """feedback_native_state is validated and only a well-formed, timely ack suppresses CG-03."""

    @staticmethod
    def _run(native, *, window=1500.0, action="click"):
        step = {"step_index": 1, "action": {"action": action, "target": "#cb"}, "target_element_id": None,
                "point": {"x": 10, "y": 10}, "before": None, "after": None, "t_start_ms": 100, "t_end_ms": window + 100,
                "feedback_latency_ms": None, "feedback_window_ms": window, "result": "ok", "error": None}
        if native is not None:
            step["feedback_native_state"] = native
        return {"schema_version": "ergo-run.v1", "run_id": "R-native", "scenario_id": "SC-native", "profile_id": "EP-01",
                "driver": {"name": "t", "version": "0", "browser": None},
                "device": {"id": "desktop-1920", "viewport_css": [1920, 1080], "dpr": 1.0, "orientation": "landscape"},
                "mode": "scripted", "started_at": "2026-10-02T12:00:00Z", "ended_at": "2026-10-02T12:00:05Z",
                "status": "completed", "success": True, "steps": [step]}

    @staticmethod
    def _ack(**updates):
        native = {"source": "native_state_change", "via": "label_for", "type": "checkbox", "dom_id": "cb",
                  "before": False, "after": True, "changed": True, "event": "input", "latency_ms": 10}
        return {**native, **updates}

    def _cg03(self, run, snapshots=None):
        profile = {"profile_id": "EP-01", "attributes": {}}
        return [o for o in checks.check_run_timing(run, profile, get_device("desktop-1920"), snapshots or {}, None) if o.check_id == "CG-03"]

    def test_loader_rejects_malformed_native_state(self):
        cases = {
            "non_object": "native_state_change",
            "unknown_key": self._ack(extra="x"),
            "contradictory": self._ack(before=True, after=True),
            "no_event": self._ack(event=None),
            "latency_without_event": self._ack(event=None, latency_ms=10),
            "negative_latency": self._ack(latency_ms=-3),
            "string_latency": self._ack(latency_ms="any"),
            "wrong_type": self._ack(type="togglebox"),
            "wrong_via": self._ack(via="wrapper"),
            "wrong_source": self._ack(source="visual_change"),
            "wrong_event": self._ack(event="click"),
            "non_boolean_state": self._ack(before="false"),
            "outside_window": self._ack(latency_ms=1600),
            "non_boolean_changed": self._ack(changed="yes"),
            "boolean_latency": self._ack(latency_ms=True),
            "infinite_latency": self._ack(latency_ms=float("inf")),
            "non_boolean_stable": self._ack(stable="true"),
            "unchanged_with_event": self._ack(before=True, after=True, changed=False),
        }
        for name, native in cases.items():
            with self.subTest(case=name):
                self.assertTrue(validate_run(self._run(native)), name)
        self.assertEqual(validate_run(self._run(self._ack())), [])
        self.assertEqual(validate_run(self._run(None)), [])
        self.assertEqual(validate_run(self._run(self._ack(event=None, latency_ms=None))), [])
        for field, value in (("feedback_window_ms", None), ("feedback_window_ms", "1500"),
                             ("feedback_window_ms", float("inf")), ("feedback_window_ms", -1),
                             ("t_start_ms", None), ("t_end_ms", 105)):
            with self.subTest(field=field, value=value):
                run = self._run(self._ack())
                run["steps"][0][field] = value
                self.assertTrue(validate_run(run))
                self.assertFalse(self._cg03(run)[0].passed)
        run = self._run(self._ack(), action="press")
        self.assertTrue(validate_run(run))

    def test_cg03_timely_wellformed_ack_passes_and_slowness_is_banded(self):
        obs = self._cg03(self._run(self._ack(latency_ms=10)))[0]
        self.assertTrue(obs.passed)
        self.assertIsNone(obs.severity)
        self.assertEqual(obs.measurement["acknowledgment"], "native_state_change")
        self.assertEqual(obs.measurement["acknowledgment_ms"], 10)
        self.assertEqual(obs.measurement["native_state"], [False, True])
        self.assertFalse(obs.measurement["visible_paint_calibrated"])
        for latency, severity in ((500, "P3"), (1200, "P2"), (12000, "P1")):
            with self.subTest(latency=latency):
                slow = self._cg03(self._run(self._ack(latency_ms=latency), window=latency + 500))[0]
                self.assertFalse(slow.passed, latency)
                self.assertEqual(slow.severity, severity, latency)
                self.assertEqual(slow.measurement["acknowledgment_ms"], latency)

    def test_cg03_malformed_or_unchanged_native_state_stays_a_finding(self):
        cases = {
            "contradictory": self._ack(before=True, after=True),
            "no_event": self._ack(event=None),
            "negative_latency": self._ack(latency_ms=-3),
            "string_latency": self._ack(latency_ms="any"),
            "wrong_type": self._ack(type="togglebox"),
            "unstable": self._ack(stable=False),
            "outside_window": self._ack(latency_ms=1600),
            "unchanged": self._ack(before=False, after=False, changed=False, event=None, latency_ms=None),
            "unknown_key": self._ack(extra="x"),
            "non_boolean_stable": self._ack(stable="true"),
        }
        for name, native in cases.items():
            with self.subTest(case=name):
                obs = self._cg03(self._run(native))[0]
                self.assertFalse(obs.passed, name)
                self.assertEqual(obs.severity, "P2", name)
                self.assertNotEqual(obs.measurement.get("acknowledgment"), "native_state_change", name)
        # a non-object must not crash the checker
        obs = self._cg03(self._run("native_state_change"))[0]
        self.assertFalse(obs.passed)
        self.assertEqual(obs.severity, "P2")

    def test_direct_native_inputs_reach_the_ack_check_and_text_fields_keep_their_exemption(self):
        for role in ("checkbox", "radio"):
            with self.subTest(role=role):
                run = self._run(self._ack(type=role, via="direct", latency_ms=1200))
                step = run["steps"][0]
                step.update(before="S-before", target_element_id="el-1")
                snapshots = {"S-before": {"elements": [{"id": "el-1", "tag": "input", "role": role}]}}
                observation = self._cg03(run, snapshots)[0]
                self.assertFalse(observation.passed)
                self.assertEqual(observation.severity, "P2")
                self.assertEqual(observation.measurement["acknowledgment_ms"], 1200)
                del step["feedback_native_state"]
                self.assertFalse(self._cg03(run, snapshots)[0].passed)
        run = self._run(None)
        run["steps"][0].update(before="S-before", target_element_id="el-1")
        self.assertEqual(self._cg03(run, {"S-before": {"elements": [{"id": "el-1", "tag": "input", "role": "textbox"}]}}), [])

    def test_direct_native_checkbox_with_an_explicit_role_override_uses_native_latency(self):
        run = self._run(self._ack(via="direct", latency_ms=1200))
        run["steps"][0].update(before="S-before", target_element_id="el-1")
        snapshots = {"S-before": {"elements": [{"id": "el-1", "tag": "input", "role": "switch"}]}}
        observation = self._cg03(run, snapshots)[0]
        self.assertFalse(observation.passed)
        self.assertEqual(observation.severity, "P2")
        self.assertEqual(observation.measurement["acknowledgment_ms"], 1200)
        run["steps"][0]["feedback_native_state"] = self._ack(via="direct", event=None, latency_ms=None,
                                                         after=False, changed=False)
        self.assertFalse(self._cg03(run, snapshots)[0].passed)

    def test_valid_selected_native_radio_noop_is_inapplicable_without_exempting_failed_changes(self):
        selected = self._ack(type="radio", before=True, after=True, changed=False, event=None, latency_ms=None)
        for via in ("direct", "label_for", "nested_label"):
            with self.subTest(via=via):
                self.assertEqual(self._cg03(self._run({**selected, "via": via})), [])
        for native in ({**selected, "stable": False}, {**selected, "type": "checkbox"},
                       {**selected, "before": False, "after": False}, {**selected, "extra": "invalid"}, None):
            with self.subTest(native=native):
                observation = self._cg03(self._run(native))[0]
                self.assertFalse(observation.passed)
                self.assertEqual(observation.severity, "P2")
        slow_selection = self._cg03(self._run(self._ack(type="radio", latency_ms=1200)))[0]
        self.assertFalse(slow_selection.passed)
        self.assertEqual(slow_selection.severity, "P2")
        measured_delay = self._run(selected)
        measured_delay["steps"][0]["feedback_latency_ms"] = 1200
        self.assertEqual(self._cg03(measured_delay)[0].severity, "P2")

    def test_cg03_ack_only_covers_the_no_feedback_band(self):
        for latency in (1500, 12000):
            with self.subTest(latency=latency):
                run = self._run(self._ack(latency_ms=10))
                run["steps"][0]["feedback_latency_ms"] = latency
                obs = self._cg03(run)[0]
                self.assertNotEqual(obs.measurement.get("acknowledgment"), "native_state_change")


if __name__ == "__main__":
    unittest.main()
