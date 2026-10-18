"""Pre-registered evaluation runner: per-product configurations and verdict guards."""

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

import _paths  # noqa: F401  (puts the skill folder and its scripts on sys.path)

import ergo_eval  # noqa: E402

EXAMPLE = _paths.SKILL / "examples" / "audience" / "transit-card.audience.json"


def suite_two_products_one_device() -> dict:
    doc_a = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    doc_b = copy.deepcopy(doc_a)
    doc_b["audience_id"] = "AU-b"
    for seg in doc_b["segments"]:
        seg["age_bands"] = {"60s": 0.5, "70s+": 0.5}
    scenarios = {}
    for slug in ("alpha", "beta"):
        for v in ("a", "b"):
            sid = f"SC-x-{slug}-{v}"
            scenarios[sid] = {"scenario_id": sid, "device_ids": ["galaxy-s24"], "surface": {"kind": "web"}}
    return {"suite": Path("/tmp/x"), "scenarios": scenarios, "paths": {}, "keys": {},
            "key": {"defects": [], "decoys": [], "clean_controls": []},
            "product_of": {sid: sid.split("-")[2] for sid in scenarios}, "audiences": {"alpha": doc_a, "beta": doc_b}}


class Configurations(unittest.TestCase):
    def test_budgets_are_per_product_even_on_a_shared_device(self) -> None:
        old = ergo_eval.C5_SEEDS
        ergo_eval.C5_SEEDS = 2
        try:
            configs, registry, groups, _ = ergo_eval.configurations(suite_two_products_one_device())
        finally:
            ergo_eval.C5_SEEDS = old
        for budget in ergo_eval.BUDGETS:
            for product in ("alpha", "beta"):
                self.assertLessEqual(len(configs[f"C4@{budget}"][product]), budget)
                self.assertLessEqual(len(configs[f"C5@{budget}#0"][product]), budget)
        self.assertNotEqual(configs["C4@6"]["alpha"], configs["C4@6"]["beta"])
        self.assertEqual(configs["C1"]["alpha"], configs["C1"]["beta"])  # the default persona of the shared device
        self.assertTrue(all(pid in registry for by in configs.values() for ids in by.values() for pid in ids))

    def test_findings_use_only_the_runs_product_profiles(self) -> None:
        cache = {"analyses": [{"scenario_id": "SC-x-beta-a", "run_id": "R1", "profiles_evaluated": ["P-a", "P-b"],
                               "observations": [{"id": "O1", "check_id": "PT-01", "profile_id": "P-a", "passed": False, "run_id": "R1",
                                                 "element_key": "#x|x", "severity": "P2", "measurement": {}, "message_ko": "", "selectors": ["#x"]}]}],
                 "product_of": {"SC-x-beta-a": "beta"},
                 "registry": {"P-a": {"profile_id": "P-a", "attributes": {"device_id": "galaxy-s24", "orientation": "portrait"}},
                              "P-b": {"profile_id": "P-b", "attributes": {"device_id": "galaxy-s24", "orientation": "portrait"}}}}
        findings, used = ergo_eval._findings(cache, {"alpha": ["P-a"], "beta": ["P-b"]})
        self.assertEqual(findings, [])  # P-a belongs to product alpha, the run is product beta
        self.assertEqual([p["profile_id"] for p in used], ["P-b"])


class Verdicts(unittest.TestCase):
    def test_interval_rule(self) -> None:
        self.assertEqual(ergo_eval._verdict(0.6, [0.52, 0.7], 0.5), "pass")
        self.assertEqual(ergo_eval._verdict(0.3, [0.2, 0.45], 0.5), "fail")
        self.assertEqual(ergo_eval._verdict(0.55, [0.4, 0.7], 0.5), "inconclusive")
        self.assertEqual(ergo_eval._verdict(None, [None, None], 0.5), "not_run")

    def test_degenerate_inputs_are_not_run(self) -> None:
        per = [{"id": "D-1", "detected_strict": True, "detected_lenient": True, "profile_condition": {}, "differential_matches_condition": None}]
        score = {"per_defect": per, "clean_control_units_by_severity": {"P0": 0, "P1": 0, "P2": 0, "P3": 0}}
        key = {"defects": [{"id": "D-1", "scenario_id": "S", "category": "reach"}], "clean_controls": []}
        h = ergo_eval.hypotheses({"C2": score, "C4@10": score, "C4@14": score}, key)
        self.assertEqual(h["H2"]["verdict"], "not_run")  # no C5 seeds
        self.assertEqual(h["H3"]["verdict"], "not_run")  # no C3
        self.assertEqual(h["H4"]["verdict"], "not_run")  # no clean scenarios
        self.assertEqual(h["H5"]["verdict"], "not_run")  # no conditioned defects
        self.assertEqual(h["H7"]["verdict"], "not_run")  # no C3

    def test_paired_bootstrap_is_symmetric_for_constant_differences(self) -> None:
        d = ergo_eval._paired_diff({"a": 1.0, "b": 1.0}, {"a": 0.0, "b": 0.0}, ["a", "b"])
        self.assertEqual(d["diff"], 1.0)
        self.assertEqual(d["ci95"], [1.0, 1.0])


class Amendment3(unittest.TestCase):
    def test_poisson_and_newcombe_reference_values(self) -> None:
        from ergoqa import bench
        self.assertAlmostEqual(bench.poisson_upper(0, 10), 0.369, places=3)   # Garwood: 3.689
        self.assertAlmostEqual(bench.poisson_upper(7, 10), 1.442, places=2)   # 14.42
        same = [True] * 14 + [False] * 6
        r = bench.newcombe_paired(same, same)
        self.assertEqual(r["diff"], 0.0)
        self.assertLess(r["ci95"][0], 0.0)  # no discordant pairs still leaves an interval
        self.assertEqual(bench.newcombe_paired([], [])["diff"], None)

    def test_twin_discrimination(self) -> None:
        from ergoqa import bench
        key = {"defects": [{"id": "D-1", "scenario_id": "S-a", "category": "pointing", "element_selector": "#b", "profile_condition": {}},
                           {"id": "D-2", "scenario_id": "S-a", "category": "reach", "element_selector": "#c", "profile_condition": {}}]}
        f = lambda sid, sel, cat: {"id": f"{sid}{sel}{cat}", "scenario_id": sid, "category": cat, "element_key": f"{sel}|x",  # noqa: E731
                                   "selectors": [sel], "context_selectors": [], "triggered_profiles": ["P"], "tier": "finding"}
        findings = [f("S-a", "#b", "pointing"), f("S-a", "#c", "reach"), f("S-b", "#c", "reach")]
        d = bench.discrimination(key, findings, [{"profile_id": "P", "attributes": {}}], {"S-a": "S-b"})
        self.assertEqual(d["recall_discriminating"], 0.5)  # D-2 is flagged in the clean twin too
        self.assertEqual(d["non_discriminating"], 1)
        self.assertEqual(d["youden_by_category"]["reach"]["youden_j"], 0.0)

    def test_fixed_sequence_stops_at_first_failure(self) -> None:
        per = [{"id": f"D-{i}", "detected_strict": True, "detected_lenient": True, "profile_condition": {}, "differential_matches_condition": None}
               for i in range(20)]
        noisy = {"per_defect": per, "clean_control_units_by_severity": {"P0": 0, "P1": 1, "P2": 0, "P3": 0},
                 "recall_strict_by_operating_point": {"p0_p1": 1.0, "p0_p2": 1.0, "all": 1.0}, "clean_control_units": 1}
        key = {"defects": [{"id": f"D-{i}", "scenario_id": "S", "category": "reach"} for i in range(20)], "clean_controls": [{"scenario_id": "C"}]}
        out = ergo_eval.confirmatory({"C2": noisy, "C3": noisy, "C4@14": noisy}, key, clean_n=4)
        self.assertEqual(out["N"]["verdict"], "fail")  # a P1 unit on a clean page
        self.assertEqual(out["H7'"]["confirmatory_status"], "descriptive (sequence stopped earlier)")



class Amendment4(unittest.TestCase):
    """SIT-04: the conditional cut of the condition multipliers on heldout-2."""

    def finding(self, fid, scenario, check, element, severity="P3"):
        return {"id": fid, "scenario_id": scenario, "check_id": check, "element_key": element, "severity": severity, "tier": "finding",
                "category": "pointing", "basis": "model", "triggered_profiles": ["P"], "tested_profiles": ["P"], "title_ko": "x"}

    def score(self, per_defect, findings):
        return {"per_defect": per_defect, "_findings": findings}

    def key(self):
        return {"defects": [{"id": "D-walk", "profile_condition": {"context.mobility": "walking"}},
                            {"id": "D-old", "profile_condition": {"age_band": ["60s", "70s+"]}},
                            {"id": "D-left", "profile_condition": {"grip": "one_hand_left"}}],
                "clean_controls": [{"scenario_id": "C0"}, {"scenario_id": "C1"}, {"scenario_id": "C2"}]}

    def per(self, walk_checks, walk_named):
        row = lambda i, checks, named: {"id": i, "detected_strict": bool(checks), "differential_matches_condition": named, "matched_checks": checks}  # noqa: E731
        return [row("D-walk", walk_checks, walk_named), row("D-old", [], None), row("D-left", ["RH-01"], True)]

    def test_cut_when_no_attributed_detection_and_multiplier_only_noise(self) -> None:
        # Three clean screens with a PT-04 unit each; the PT-02 unit exists either way.
        on = [self.finding(f"F{i}", f"C{i}", "PT-04", f"#b{i}|x") for i in range(3)] + [self.finding("F9", "C0", "PT-02", "#z|x")]
        off = [self.finding("G9", "C0", "PT-02", "#z|x")]
        scores = {c: self.score(self.per(["PT-04"], False), on) for c in ("C3", "C4@14")}
        off_scores = {c: self.score(self.per(["PT-04"], False), off) for c in ("C3", "C4@14")}
        out = ergo_eval.sit04(scores, off_scores, self.key())
        self.assertEqual(out["configs"]["C3"]["conditioned_defects"], 2)
        self.assertEqual(out["configs"]["C3"]["clean_units_only_with_multipliers"], 3)
        self.assertEqual(out["verdict"], "cut")

    def test_keep_when_a_condition_is_named_through_pt04(self) -> None:
        on = [self.finding(f"F{i}", f"C{i}", "PT-04", f"#b{i}|x") for i in range(3)]
        scores = {c: self.score(self.per(["PT-04"], True), on) for c in ("C3", "C4@14")}
        off_scores = {c: self.score(self.per([], None), []) for c in ("C3", "C4@14")}
        out = ergo_eval.sit04(scores, off_scores, self.key())
        self.assertEqual(out["configs"]["C4@14"]["attributed_via_pt03_pt04"], 1)
        self.assertEqual(out["configs"]["C4@14"]["defects_lost_without_multipliers"], 1)
        self.assertEqual(out["verdict"], "keep")

    def test_variant_turns_off_only_condition_multipliers(self) -> None:
        from ergoqa import params
        from ergoqa.profiles import touch_sigma_multiplier
        saved = dict(params.TOUCH_SIGMA_MULT)
        try:
            for k in params.TOUCH_SIGMA_MULT:
                if k.startswith(ergo_eval.CONDITION_MULTIPLIERS):
                    params.TOUCH_SIGMA_MULT[k] = 1.0
            prof = {"attributes": {"grip": "one_hand_right", "age_band": "70s+", "motor": {"tremor": "mild"}, "context": {"mobility": "walking"}}}
            self.assertAlmostEqual(touch_sigma_multiplier(prof), saved["one_hand_thumb"])
        finally:
            params.TOUCH_SIGMA_MULT.clear()
            params.TOUCH_SIGMA_MULT.update(saved)


if __name__ == "__main__":
    unittest.main()
