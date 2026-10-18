"""Measurement-derived recommendations for PT-02/PT-04/RH-01 (SIT-05 slice).

The advice layer must quote the supporting observations' own measurement — model
output and declared assumptions labelled separately from the defect grade —
while pass/fail, severity, tiers and counts stay exactly as the checks computed
them, and the derived text must reach the rendered report and the QA-bundle
proposals labelled per profile, never as one profile's numbers copied to every
persona.
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
import _paths  # noqa: E402,F401

from ergoqa import analyze, checks, params, report, swarm  # noqa: E402
from ergoqa.devices import get_device  # noqa: E402
from ergoqa.hf import pointing  # noqa: E402
from ergoqa.profiles import _finalise  # noqa: E402
from test_ergo_fixes import ctx, el, profile  # noqa: E402
from test_ergo_pipeline import AttachBridgeTests, make_run  # noqa: E402

REF = params.TOUCH_TARGET_ONE_HAND_MM


def walker(pid="EP-W", device_id="galaxy-s24"):
    p = profile(pid, device_id=device_id, grip="one_hand_right")
    p["attributes"]["context"]["mobility"] = "walking"
    return _finalise(p, get_device(device_id))


def seated_70s_cradle(pid="EP-O"):
    p = profile(pid, grip="cradle_right", age_band="70s+")
    return _finalise(p, get_device("galaxy-s24"))


def sigma_profile(pid, k):
    p = profile(pid, grip="one_hand_right")
    p["attributes"]["motor"]["touch_sigma_multiplier"] = k
    return p


def pay_button(box=(150, 600, 44, 44)):
    return el("pay", "button", box, text="결제", interactive=True, roles=("primary",), tag="button")


class EquivalentSquareTests(unittest.TestCase):
    """pointing.equivalent_square_mm: bounded monotone bisection, k=1 reference,
    nothing-found-within-the-bound reported as None (unknown), never a giant size."""

    def test_k1_returns_the_reference_itself(self) -> None:
        self.assertEqual(pointing.equivalent_square_mm(REF, 1.0), REF)

    def test_attainable_size_reaches_the_reference_and_is_minimal(self) -> None:
        target = pointing.dual_gaussian_hit_probability(REF, REF, 1.0)
        for k in (1.1, 1.2, 1.3, 1.4, 1.5, 1.6):
            with self.subTest(k=k):
                size = pointing.equivalent_square_mm(REF, k)
                self.assertIsNotNone(size)
                self.assertGreaterEqual(pointing.dual_gaussian_hit_probability(size, size, k), target)
                self.assertLess(pointing.dual_gaussian_hit_probability(size - 0.2, size - 0.2, k), target)

    def test_sizes_grow_monotonically_with_the_multiplier(self) -> None:
        previous = REF
        for k in (1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6):
            size = pointing.equivalent_square_mm(REF, k)
            self.assertIsNotNone(size, k)
            self.assertGreaterEqual(size, previous)
            previous = size

    def test_beyond_bound_none_is_unknown_not_never(self) -> None:
        # k = 1.62 and 1.65 do have matching squares (45.3 / 68.2 mm) — outside the
        # 40 mm advice bound. None therefore only means "unknown within the bound",
        # never a claim that no size can ever match or that size cannot help.
        for k, beyond in ((1.62, 45.316), (1.65, 68.233)):
            self.assertIsNone(pointing.equivalent_square_mm(REF, k), k)
            self.assertAlmostEqual(pointing.equivalent_square_mm(REF, k, max_mm=10000.0), beyond, delta=0.05)
        self.assertIsNone(pointing.equivalent_square_mm(REF, 1.82, max_mm=10000.0))  # saturated: no square at all

    def test_unattainable_bounds_are_unknown_not_a_giant_size(self) -> None:
        for k in (1.62, 1.69, 1.8, 1.82, 2.25):  # beyond the search bound, and saturated
            self.assertIsNone(pointing.equivalent_square_mm(REF, k), k)
        # A tighter bound turns an otherwise attainable size into unknown too.
        self.assertIsNone(pointing.equivalent_square_mm(REF, 1.5, max_mm=20.0))
        self.assertAlmostEqual(pointing.equivalent_square_mm(REF, 1.4, max_mm=25.0), 18.4, delta=0.2)

    def test_rejects_impossible_arguments(self) -> None:
        for bad in ((0, 1.0), (9.2, 0), (9.2, 1.0, 9.2)):
            with self.assertRaises(ValueError):
                pointing.equivalent_square_mm(*bad)


class Pt04AdviceDataTests(unittest.TestCase):
    """PT-04 records the same-hit-probability square only as typed advice data; the
    verdict it was already going to give (pass/fail, severity) is untouched."""

    def pt04(self, prof, box=(150, 600, 44, 44)):
        return [o for o in checks.check_touch_accuracy(ctx([pay_button(box)], prof=prof)) if o.check_id == "PT-04"][0]

    def test_failed_band_target_records_same_error_square(self) -> None:
        prof = walker()  # one-hand thumb 1.3 x walking 1.4 = 1.82
        o = self.pt04(prof)
        self.assertFalse(o.passed)
        self.assertEqual(o.severity, "P3")  # platform-size target: SIT-01 cap, as before
        self.assertTrue(o.measurement["profile_only"])
        same = o.measurement["same_error_square"]
        self.assertEqual(same["reference_mm"], REF)
        self.assertEqual(same["reference_sigma_multiplier"], 1.0)
        self.assertEqual(same["sigma_multiplier"], o.measurement["sigma_multiplier"])
        self.assertFalse(same["found_within_search_bound"])  # no match inside the 40 mm bound
        self.assertIsNone(same["equivalent_square_mm"])
        self.assertEqual(same["search_bound_mm"], pointing.EQUIV_SQUARE_SEARCH_MAX_MM)

    def test_reference_probability_is_stored_and_distinct_from_the_baseline(self) -> None:
        prof = seated_70s_cradle()
        o = self.pt04(prof)
        same = o.measurement["same_error_square"]
        # The 9.2 mm reference square's own miss at k=1 (~0.46%), computed with the
        # same model — distinct from the actual 8.07 mm target's baseline (~1.08%).
        self.assertEqual(same["reference_miss_probability"],
                         round(1.0 - pointing.dual_gaussian_hit_probability(REF, REF, 1.0), 5))
        self.assertAlmostEqual(same["reference_miss_probability"], 0.0046295, places=6)
        self.assertLess(same["reference_miss_probability"], o.measurement["baseline_miss_probability"])
        self.assertAlmostEqual(o.measurement["baseline_miss_probability"], 0.0108, places=4)

    def test_attainable_case_records_the_size(self) -> None:
        prof = seated_70s_cradle()  # k = 1.3
        o = self.pt04(prof)
        self.assertFalse(o.passed)
        same = o.measurement["same_error_square"]
        self.assertTrue(same["found_within_search_bound"])
        self.assertEqual(same["equivalent_square_mm"], 15.0)  # solver 14.975 rounded up
        k = prof["attributes"]["motor"]["touch_sigma_multiplier"]
        self.assertGreaterEqual(pointing.dual_gaussian_hit_probability(same["equivalent_square_mm"], same["equivalent_square_mm"], k),
                                pointing.dual_gaussian_hit_probability(REF, REF, 1.0))

    def test_printed_minimum_rounds_up_and_reaches_the_reference(self) -> None:
        # k = 1.5 solves at 24.148... mm; 24.1 falls short of the reference, so a
        # minimum wording must round upward (24.2).
        target = pointing.dual_gaussian_hit_probability(REF, REF, 1.0)
        o = self.pt04(sigma_profile("EP-K15", 1.5))
        same = o.measurement["same_error_square"]
        self.assertEqual(same["equivalent_square_mm"], 24.2)
        self.assertGreaterEqual(pointing.dual_gaussian_hit_probability(24.2, 24.2, 1.5), target)
        self.assertLess(pointing.dual_gaussian_hit_probability(24.1, 24.1, 1.5), target)

    def test_passed_or_out_of_band_targets_get_no_advice_data(self) -> None:
        base = self.pt04(profile(grip="cradle_right"))  # k = 1: passes as before
        self.assertTrue(base.passed)
        self.assertNotIn("same_error_square", base.measurement)
        small = self.pt04(walker(), box=(150, 600, 34, 34))  # 6.2 mm: below the 7-9.2 band
        self.assertEqual(small.severity, "P2")  # unchanged verdict, no advice band
        self.assertNotIn("same_error_square", small.measurement)

    def test_game_control_advice_requires_a_primary_or_used_target(self) -> None:
        target = el("game", "button", (150, 600, 44, 44), interactive=True, roles=("game_control",), tag="button")
        unused = checks.check_touch_accuracy(ctx([target], prof=walker()))[0]
        used = checks.check_touch_accuracy(ctx([target], prof=walker(), path_ids=("game",)))[0]
        self.assertEqual((unused.passed, unused.severity), (used.passed, used.severity))
        self.assertNotIn("same_error_square", unused.measurement)
        self.assertIn("same_error_square", used.measurement)


class Pt02CriterionTests(unittest.TestCase):
    def pt02(self, prof, box):
        return [o for o in checks.check_target_size(ctx([pay_button(box)], prof)) if o.check_id == "PT-02"][0]

    def test_criterion_names_the_exact_failed_tier(self) -> None:
        floor = self.pt02(profile(), (150, 600, 12, 12))  # ~2.2 mm
        self.assertEqual((floor.severity, floor.measurement["criterion"]), ("P1", "platform_floor"))
        mid = self.pt02(profile(), (150, 600, 36, 36))  # ~6.6 mm
        self.assertEqual((mid.severity, mid.measurement["criterion"]), ("P2", "platform_min"))
        one_hand = self.pt02(profile(grip="one_hand_right"), (150, 600, 44, 44))  # ~8.1 mm
        self.assertEqual((one_hand.severity, one_hand.measurement["criterion"]), ("P3", "one_hand_reference"))
        self.assertEqual(one_hand.measurement["threshold"], REF)
        w, h = one_hand.measurement["value"]
        self.assertLess(min(w, h), REF)  # the measured size backs the failed criterion


class Rh01AdviceDataTests(unittest.TestCase):
    def test_measurement_carries_grip_and_zone(self) -> None:
        top = el("pay", "button", (10, 60, 60, 48), text="결제", interactive=True, roles=("primary",), tag="button")
        obs = [o for o in checks.check_reach(ctx([top], profile(grip="one_hand_right"))) if o.check_id == "RH-01"][0]
        self.assertFalse(obs.passed)
        self.assertEqual(obs.measurement["grip"], "one_hand_right")
        self.assertIn(obs.measurement["zone"], checks.ZONE_KO)


class SwarmAdviceTests(unittest.TestCase):
    @staticmethod
    def _analysis(observations, profiles):
        dicts = []
        for index, obs in enumerate(observations):
            record = obs.to_dict(index)
            record["selectors"] = [f"#{obs.element_ids[0]}"] if obs.element_ids else []
            record["context_selectors"] = []
            dicts.append(record)
        return {"scenario_id": "SC-1", "run_id": "R-1",
                "profiles_evaluated": [p["profile_id"] for p in profiles], "observations": dicts}

    def _findings(self, observations, profiles):
        return swarm.aggregate([self._analysis(observations, profiles)], profiles)

    def test_pt04_finding_recommends_from_the_same_error_square(self) -> None:
        prof = walker()
        finding = self._findings(checks.check_touch_accuracy(ctx([pay_button()], prof)), [prof])[0]
        self.assertEqual(finding["check_id"], "PT-04")
        static = checks.CATALOG["PT-04"].recommendation_ko
        text = finding["recommendation_ko"]
        self.assertIn(f"{prof['profile_id']} 조건:", text)
        # this target's baseline vs profile risk, from the same measurement
        base = finding["measurement"]["baseline_miss_probability"]
        self.assertIn(f"기준 모델(k=1) {base * 100:.1f}%", text)
        self.assertIn(f"이 조건 {finding['measurement']['value'] * 100:.1f}%", text)
        self.assertIn(f"σ배수 {prof['attributes']['motor']['touch_sigma_multiplier']:.2f}, 선언된 가정", text)
        # the reference square carries its OWN miss probability (~0.46%), never the
        # actual target's baseline (~1.1%)
        ref_p = finding["measurement"]["same_error_square"]["reference_miss_probability"]
        self.assertIn(f"기준 모델의 9.2mm 정사각형은 예측 놓침 {ref_p * 100:.2f}%", text)
        self.assertIn("탐색 범위 안에서는 해당 크기를 찾지 못했습니다", text)  # unknown within the bound, spelled out
        self.assertIn("범위 밖의 값은 미확인", text)  # not a universal-unattainability claim
        self.assertNotIn("도달하지 못합니다", text)
        self.assertIn(static, text)  # static guidance (the alternatives) kept after the derived part

    def test_pt04_attainable_advice_names_the_equivalent_size(self) -> None:
        prof = seated_70s_cradle()
        finding = self._findings(checks.check_touch_accuracy(ctx([pay_button()], prof)), [prof])[0]
        size = finding["measurement"]["same_error_square"]["equivalent_square_mm"]
        text = finding["recommendation_ko"]
        self.assertIn(f"{prof['profile_id']} 조건: ", text)
        self.assertIn(f"최소 {size:.1f}mm 정사각형입니다", text)
        self.assertIn("접근성 요구치 아님", text)

    def test_same_severity_profiles_get_own_labelled_advice_not_copies(self) -> None:
        seated = seated_70s_cradle(pid="EP-SEATED")  # k = 1.3 -> 15.0 mm square
        walking = walker(pid="EP-WALKING")  # k = 1.82 -> none within the 40 mm bound
        pay = pay_button()
        observations = (checks.check_touch_accuracy(ctx([pay], seated))
                        + checks.check_touch_accuracy(ctx([pay], walking)))
        forward = next(f for f in self._findings(observations, [seated, walking]) if f["check_id"] == "PT-04")
        reverse = next(f for f in self._findings(list(reversed(observations)), [walking, seated]) if f["check_id"] == "PT-04")
        self.assertEqual(forward["severity"], "P3")
        self.assertEqual(reverse["severity"], "P3")  # grading untouched either way
        self.assertEqual(forward["recommendation_ko"], reverse["recommendation_ko"])  # order-independent
        text = forward["recommendation_ko"]
        self.assertIn("EP-SEATED 조건:", text)
        self.assertIn("EP-WALKING 조건:", text)
        seated_part, walking_part = text.split("EP-WALKING 조건:")
        self.assertIn("최소 15.0mm", seated_part)
        self.assertNotIn("찾지 못했습니다", seated_part)
        self.assertIn("찾지 못했습니다", walking_part)
        self.assertNotIn("15.0mm", walking_part)

    def test_identical_evidence_across_profiles_shares_one_labelled_segment(self) -> None:
        a, b = walker(pid="EP-A"), walker(pid="EP-B")  # same k, same advice data
        pay = pay_button()
        observations = (checks.check_touch_accuracy(ctx([pay], a))
                        + checks.check_touch_accuracy(ctx([pay], b)))
        finding = next(f for f in self._findings(observations, [a, b]) if f["check_id"] == "PT-04")
        text = finding["recommendation_ko"]
        self.assertIn("EP-A, EP-B 조건: ", text)  # one shared segment, both ids named
        self.assertEqual(text.count("예측 놓침 확률"), 1)  # not duplicated per profile

    def test_pt02_finding_quotes_estimated_size_and_criterion(self) -> None:
        prof = profile(grip="one_hand_right")
        finding = self._findings(checks.check_target_size(ctx([pay_button()], prof)), [prof])[0]
        self.assertEqual(finding["check_id"], "PT-02")
        w, h = finding["measurement"]["value"]
        threshold = finding["measurement"]["threshold"]
        text = finding["recommendation_ko"]
        self.assertIn(f"{prof['profile_id']} 조건: ", text)
        self.assertIn(f"{w:.1f}×{h:.1f}mm", text)
        self.assertIn(f"짧은 변 {min(w, h):.1f}mm", text)
        self.assertIn(f"{threshold:g}mm에 미달했습니다", text)
        self.assertIn("Parhi 2006", text)  # the one-hand 9.2 mm criterion is named
        # DOM/catalog-estimated wording — never a physical-measurement claim
        self.assertIn("기록된 타깃 상자를 기기 카탈로그 밀도로 환산", text)
        self.assertNotIn("DOM 상자", text)
        self.assertIn("카탈로그 밀도로 환산한 추정치", text)
        self.assertNotIn("실측", text)
        self.assertIn("44pt/48dp와 정확히 일치하는 단위 환산이 아니", text)  # mm vs pt/dp caveat
        self.assertIn(checks.CATALOG["PT-02"].recommendation_ko, text)

    def test_rh01_finding_quotes_grip_zone_difficulty_as_model_prediction(self) -> None:
        prof = profile(grip="one_hand_right")
        top = el("pay", "button", (10, 60, 60, 48), text="결제", interactive=True, roles=("primary",), tag="button")
        finding = self._findings(checks.check_reach(ctx([top], prof)), [prof])[0]
        self.assertEqual(finding["check_id"], "RH-01")
        text = finding["recommendation_ko"]
        self.assertIn(f"{prof['profile_id']} 조건: ", text)
        self.assertIn("도달 모델 예측", text)  # a model prediction, never a measurement
        self.assertNotIn("측정(모델", text)
        self.assertIn("오른손 한 손(엄지) 파지", text)
        self.assertIn(f"난이도 {finding['measurement']['value']:.2f}", text)
        self.assertIn("비보정", text)
        self.assertIn(checks.CATALOG["RH-01"].recommendation_ko, text)

    def test_observations_without_advice_fields_keep_the_static_text(self) -> None:
        obs = [{"id": "OB-1", "check_id": "PT-04", "element_key": "#b|x", "profile_id": "EP-W", "passed": False, "severity": "P3",
                "run_id": "R-1", "measurement": {"name": "miss_probability", "value": 0.04, "unit": "probability",
                                                 "threshold": 0.03, "comparator": "<"},
                "message_ko": "m", "model": "bi-zhai-2016-dual-gaussian", "selectors": ["#b"], "context_selectors": []}]
        finding = swarm.aggregate([{"scenario_id": "SC-1", "run_id": "R-1", "profiles_evaluated": ["EP-W"],
                                    "observations": obs}], [walker()])[0]
        self.assertEqual(finding["recommendation_ko"], checks.CATALOG["PT-04"].recommendation_ko)

    def test_advice_adds_no_findings_and_changes_no_severity(self) -> None:
        prof = walker()
        observations = checks.check_target_size(ctx([pay_button()], prof)) + checks.check_touch_accuracy(ctx([pay_button()], prof))
        findings = self._findings(observations, [prof])
        self.assertEqual([(f["check_id"], f["severity"]) for f in findings],
                         [("PT-02", "P3"), ("PT-04", "P3")])  # exactly the pre-advice verdicts


class AdvicePropagationTests(unittest.TestCase):
    """The derived text survives report rendering and the QA-bundle proposals,
    per profile: each persona's proposal quotes its own observation."""

    @classmethod
    def setUpClass(cls) -> None:
        import tempfile

        cls.tmp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.tmp.name)
        cls.run_dir = make_run(cls.root)
        # The fixture's pay button (90 x 44 px) is wide enough to pass every size
        # rule; make it 44 x 44 px so the PT-02/PT-04 advice bands apply. The
        # screenshots are receipts of the capture, not of box geometry.
        for index in (0, 1):
            path = cls.run_dir / f"S-R-1-{index:03d}.json"
            doc = json.loads(path.read_text(encoding="utf-8"))
            for element in doc["elements"]:
                if element["id"] == "pay":
                    element["box"] = {"x": 10, "y": 250, "w": 44, "h": 44}
            path.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
        cls.profiles = [walker(pid="EP-01"), seated_70s_cradle(pid="EP-02")]
        cls.analysis = analyze.analyze_run(cls.run_dir, cls.profiles, None, cross_profile=True, gaze_enabled=False)
        cls.findings = swarm.aggregate([cls.analysis], cls.profiles)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def test_report_renders_the_derived_recommendations(self) -> None:
        text = report.render(self.findings, self.profiles, [self.analysis])
        self.assertIn("모델 동등 크기 비교", text)  # PT-04
        self.assertIn("짧은 변", text)  # PT-02
        self.assertIn("파지", text)  # RH-01 grip context
        self.assertIn("EP-01 조건:", text)  # per-profile labels reach the report
        self.assertIn("EP-02 조건:", text)

    def test_qa_attach_proposals_carry_per_profile_text(self) -> None:
        import copy

        from ergoqa.qa_attach import attach_run

        qa = json.loads((Path(__file__).parent / "fixtures" / "valid-bundle.json").read_text(encoding="utf-8"))
        qa["records"]["findings"][0]["severity"] = "P2"
        # Bind the cross-profile (analytical) persona to its own scenario copy so the
        # attach can evaluate both profiles, as the bridge contract requires.
        qa["records"]["scenarios"].append({"id": "scenario-1-copy", "persona_id": "persona-1", "task": "ergo 분석 대조"})
        reviews = [dict(AttachBridgeTests.SECOND_PASS, finding_id=f"ERGO-{f['id']}@R-1@{pid}")
                   for f in self.findings if f["severity"] in ("P0", "P1") for pid in f["triggered_profiles"]]
        out = attach_run(copy.deepcopy(qa), self.run_dir, self.profiles, {"scenario-1": "EP-01", "scenario-1-copy": "EP-02"},
                         receipts_root=self.root / "receipts", gaze_enabled=False, second_pass=reviews or None,
                         cross_profile=True)
        proposals = [p for p in out["records"]["proposals"] if str(p["id"]).startswith("ERGO-")]
        self.assertTrue(proposals)
        # The aggregate finding itself labels both profiles' evidence.
        pt04 = next(f for f in self.findings if f["check_id"] == "PT-04")
        self.assertIn("EP-01 조건:", pt04["recommendation_ko"])
        self.assertIn("EP-02 조건:", pt04["recommendation_ko"])
        # Each persona's proposal quotes its own observation, never a copy of the
        # other's numbers (walker k=1.82: unknown within the bound; seated k=1.3:
        # 15.0 mm minimum).
        walker_text = next(p["summary"] for p in proposals if p["id"].endswith("@EP-01") and "동등 크기 비교" in p["summary"])
        seated_text = next(p["summary"] for p in proposals if p["id"].endswith("@EP-02") and "동등 크기 비교" in p["summary"])
        self.assertTrue(walker_text.startswith("EP-01 조건: "))
        self.assertIn("찾지 못했습니다", walker_text)
        self.assertNotIn("15.0mm", walker_text)
        self.assertTrue(seated_text.startswith("EP-02 조건: "))
        self.assertIn("최소 15.0mm", seated_text)
        self.assertNotIn("찾지 못했습니다", seated_text)
        # PT-02 estimated geometry still propagates.
        pt02 = [p for p in proposals if "mm에 미달했습니다" in p["summary"]]
        self.assertTrue(pt02)
        finding = next(f for f in self.findings if f["check_id"] == "PT-02")
        self.assertIn(f"{finding['measurement']['value'][0]:.1f}×{finding['measurement']['value'][1]:.1f}mm", pt02[0]["summary"])


if __name__ == "__main__":
    unittest.main()
