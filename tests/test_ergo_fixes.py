"""Regression tests for fixes found by precision adjudication and the UEM review."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import _paths  # noqa: E402,F401  (puts the skill folder on sys.path)

from ergoqa import bench, checks, params, swarm  # noqa: E402
from ergoqa.devices import get_device  # noqa: E402
from ergoqa.hf import reach  # noqa: E402
from ergoqa.profiles import _finalise, sample_profiles, touch_sigma_multiplier  # noqa: E402
from ergoqa.snapshot import load_document, validate_snapshot  # noqa: E402


def el(eid, role, box, *, text="", name="", interactive=False, roles=(), fg="#111111", bg="#ffffff", size=16, weight=400,
       tag="div", border=None, container=None, **extra):
    out = {
        "id": eid, "role": role, "name": name or text, "text": text, "tag": tag, "selector": f"#{eid}",
        "box": dict(zip("xywh", box)), "interactive": interactive, "visible": True, "enabled": True, "in_viewport": True,
        "font_size_px": size, "font_weight": weight, "color_fg": fg, "color_bg": bg, "border_color": border,
        "container_bg": container, "roles": list(roles), "source": "dom",
    }
    out.update(extra)
    return out


def profile(pid="EP-T", device_id="galaxy-s24", grip="one_hand_right", **attrs):
    p = {
        "schema_version": "ergo-profile.v1", "profile_id": pid, "origin": "manual", "persona_ref": None, "label_ko": "",
        "attributes": {
            "age_band": attrs.get("age_band", "30s"), "handedness": "left" if grip.endswith("_left") else "right", "grip": grip,
            "thumb_length_mm": 0, "hand_percentile": 50, "device_id": device_id,
            "orientation": attrs.get("orientation", get_device(device_id).orientation),
            "vision": {"acuity": "normal", "presbyopia": attrs.get("presbyopia", False), "cvd": attrs.get("cvd", "none"), "cvd_severity": 1.0, "viewing_distance_mm": 0},
            "motor": {"tremor": "none", "touch_sigma_multiplier": 1.0, "touch_sigma_mm": 0.0},
            "context": {"mobility": "seated", "lighting": attrs.get("lighting", "indoor"), "free_hands": 1, "interruptions": False},
            "cognition": {"familiarity": "returning", "time_pressure": "low", "reading_wpm_ko": 0},
            "reaction_time_ms": 0,
        },
        "assumption_fields": [], "base_rate_refs": {},
    }
    return _finalise(p, get_device(device_id))


def ctx(elements, prof=None, device_id="galaxy-s24", previous=None, step=None, focus=None, run=None, path_ids=()):
    prof = prof or profile(device_id=device_id)
    device = get_device(device_id)
    snap = {"snapshot_id": "S-1", "step_index": 1, "surface": {"kind": "web", "url": "http://x/a"},
            "device": {"id": device_id, "viewport_css": list(device.viewport_css), "orientation": device.orientation},
            "elements": elements, "focus_point": focus}
    return checks.Context(run=run or {"run_id": "R-1", "steps": []}, snapshot=snap, previous=previous, step=step, profile=prof,
                          device=device, scenario=None, conspicuity=None, path_element_ids=set(path_ids))


class Occlusion(unittest.TestCase):
    def test_covered_and_inert_elements_are_not_usable(self) -> None:
        self.assertFalse(checks._usable({"occluded_fraction": 0.6}))
        self.assertFalse(checks._usable({"inert_by_modal": True}))
        self.assertTrue(checks._usable({"occluded_fraction": 0.2}))
        self.assertTrue(checks._usable({}))  # snapshots without layer fields (older drivers, Android)

    def test_contrast_skips_covered_text(self) -> None:
        low = el("t", "paragraph", (10, 10, 200, 20), text="흐린 글자입니다", fg="#bbbbbb", bg="#ffffff")
        self.assertTrue(any(o.check_id == "PC-01" for o in checks.check_contrast(ctx([low]))))
        low_covered = dict(low, occluded_fraction=1.0, occluded_by="#sheet")
        self.assertFalse(any(o.check_id == "PC-01" for o in checks.check_contrast(ctx([low_covered]))))

    def test_gaze_primary_ignores_disabled_state(self) -> None:
        pay = el("pay", "button", (10, 600, 340, 52), text="결제 처리 중…", interactive=True, roles=("primary",), tag="button", enabled=False)
        self.assertFalse([o for o in checks.check_gaze(ctx([pay])) if o.check_id == "GZ-01"])


class TabletReach(unittest.TestCase):
    def test_tablet_is_tablet_like_and_phone_is_not(self) -> None:
        self.assertTrue(reach.tablet_like(reach.geometry_for_device(get_device("galaxy-tab-s9"))))
        self.assertFalse(reach.tablet_like(reach.geometry_for_device(get_device("galaxy-s24"))))

    def test_one_hand_model_not_applied_to_tablets(self) -> None:
        button = el("play", "button", (12, 518, 56, 56), text="재생", interactive=True, roles=("primary",), tag="button")
        prof = profile(device_id="galaxy-tab-s9", grip="one_hand_right")
        # _finalise turns a one-hand tablet profile into a cradled grip.
        self.assertEqual(prof["attributes"]["grip"], "cradle_right")
        prof["attributes"]["grip"] = "one_hand_right"
        self.assertEqual(checks.check_reach(ctx([button], prof, "galaxy-tab-s9")), [])

    def test_tablet_two_thumbs_reach_side_bands_not_centre_bottom(self) -> None:
        geom = reach.geometry_for_device(get_device("galaxy-tab-s9"))
        side = reach.reach_score(10, geom.screen_h * 0.5, geom, "two_thumbs", 107)
        centre_bottom = reach.reach_score(geom.screen_w / 2, geom.screen_h - 10, geom, "two_thumbs", 107)
        self.assertIn(side["zone"], ("natural", "mild"))
        self.assertEqual(centre_bottom["zone"], "out")

    def test_sampled_tablet_profiles_have_no_one_hand_grip(self) -> None:
        profiles = sample_profiles(14, 11, ["galaxy-tab-s9"])
        self.assertFalse([p for p in profiles if p["attributes"]["grip"].startswith("one_hand")])
        self.assertTrue(any(p["attributes"]["grip"] == "cradle_left" for p in profiles))


class Denominators(unittest.TestCase):
    def test_tested_profiles_include_non_triggering_applicable_profiles(self) -> None:
        young = profile("EP-Y")
        old = profile("EP-O", age_band="60s", presbyopia=True)
        deutan = profile("EP-D", cvd="deutan")
        obs = [{"id": "OB-1", "check_id": "PC-04", "element_key": "#p|본문", "profile_id": "EP-O", "passed": False, "severity": "P3",
                "run_id": "R-1", "measurement": {"name": "font_visual_angle_arcmin", "value": 25, "unit": "arcmin", "threshold": 31.2, "comparator": ">="},
                "message_ko": "작음", "model": "visual-angle-v2", "selectors": ["#p"], "context_selectors": []}]
        analysis = {"scenario_id": "SC-1", "run_id": "R-1", "profiles_evaluated": ["EP-Y", "EP-O", "EP-D"], "observations": obs}
        finding = swarm.aggregate([analysis], [young, old, deutan])[0]
        self.assertEqual(finding["tested_profiles"], ["EP-D", "EP-O", "EP-Y"])
        self.assertEqual(finding["coverage_label"].split(" ")[0], "1/3")
        self.assertEqual(finding["profile_specific"].get("vision.presbyopia"), True)

    def test_scoped_finding_names_its_condition(self) -> None:
        normal, deutan = profile("EP-N"), profile("EP-D", cvd="deutan")
        obs = [{"id": "OB-1", "check_id": "PC-03", "element_key": "#dot|상태", "profile_id": "EP-D", "passed": False, "severity": "P2",
                "run_id": "R-1", "measurement": {"name": "cvd_delta_e2000", "value": 3, "unit": "dE00", "threshold": 10, "comparator": ">="},
                "message_ko": "구분 안 됨", "model": "m", "selectors": ["#dot"], "context_selectors": []}]
        finding = swarm.aggregate([{"scenario_id": "SC-1", "run_id": "R-1", "profiles_evaluated": ["EP-N", "EP-D"], "observations": obs}], [normal, deutan])[0]
        self.assertEqual(finding["tested_profiles"], ["EP-D", "EP-N"])  # normal vision is tested and passes
        self.assertEqual(finding["coverage_label"].split(" ")[0], "1/2")
        self.assertEqual(finding["profile_specific"].get("vision.cvd"), "deutan")  # the condition is named

    def test_inconclusive_profiles_are_not_negative_contrasts(self) -> None:
        young = profile("EP-Y")
        old = profile("EP-O", age_band="60s", presbyopia=True)
        failed = {"id": "OB-1", "check_id": "PC-04", "element_key": "#p|본문", "profile_id": "EP-O",
                  "passed": False, "severity": "P2", "run_id": "R-1",
                  "measurement": {"name": "font_visual_angle_arcmin", "value": 25, "unit": "arcmin", "threshold": 31.2, "comparator": ">="},
                  "message_ko": "작음", "model": "visual-angle-v2", "selectors": ["#p"], "context_selectors": []}
        unknown = dict(failed, id="OB-2", profile_id="EP-Y", severity=None, extra={"verdict": "inconclusive"},
                       measurement=dict(failed["measurement"], value=None))
        young_failed = dict(failed, id="OB-3", profile_id="EP-Y")
        young_passed = dict(young_failed, id="OB-4", passed=True, severity=None)
        specific = {"age_band": "60s", "vision.presbyopia": True}
        cases = [
            ("unknown_only", [failed, unknown], ["EP-O"], {}, ["OB-1"]),
            ("unknown_first", [unknown, failed], ["EP-O"], {}, ["OB-1"]),
            ("earlier_pass_later_unknown", [
                dict(failed, id="OB-5", snapshot_id="S-1", step_index=1, passed=True, severity=None),
                dict(young_passed, id="OB-6", snapshot_id="S-1", step_index=1),
                dict(failed, snapshot_id="S-2", step_index=2),
                dict(unknown, snapshot_id="S-2", step_index=2),
            ], ["EP-O"], {}, ["OB-1"]),
            ("failure_and_unknown", [failed, dict(unknown, profile_id="EP-O")], ["EP-O"], specific, ["OB-1"]),
            ("pass_and_unknown", [failed, unknown, young_passed], ["EP-O"], {}, ["OB-1"]),
            ("known_pass", [failed, young_passed], ["EP-O"], specific, ["OB-1"]),
            ("both_fail_and_unknown", [failed, unknown, young_failed], ["EP-O", "EP-Y"], {}, ["OB-1", "OB-3"]),
            ("all_fail", [failed, young_failed], ["EP-O", "EP-Y"], {}, ["OB-1", "OB-3"]),
            ("other_selector", [failed, dict(unknown, element_key="#q|본문")], ["EP-O"], specific, ["OB-1"]),
            ("other_check", [failed, dict(unknown, check_id="GZ-02")], ["EP-O"], specific, ["OB-1"]),
        ]
        for name, observations, triggered, differential, ids in cases:
            with self.subTest(name=name):
                analysis = {"scenario_id": "SC-1", "run_id": "R-1", "profiles_evaluated": ["EP-Y", "EP-O"],
                            "observations": observations, "limitations": ["PC-04 보류"]}
                finding = swarm.aggregate([analysis], [young, old])[0]
                self.assertEqual(finding["profile_specific"], differential)
                self.assertEqual(finding["severity"], "P2")
                self.assertEqual(finding["triggered_profiles"], triggered)
                self.assertEqual(finding["tested_profiles"], ["EP-O", "EP-Y"])
                self.assertEqual(finding["coverage_label"].split(" ")[0], f"{len(triggered)}/2")
                self.assertEqual(finding["observation_ids"], ids)
                self.assertEqual(finding["measurement"], failed["measurement"])
                self.assertEqual(analysis["limitations"], ["PC-04 보류"])
        self.assertFalse(unknown["passed"])
        self.assertIsNone(unknown["severity"])
        self.assertIsNone(unknown["measurement"]["value"])
        self.assertEqual(unknown["extra"]["verdict"], "inconclusive")

    def test_applicability(self) -> None:
        s24, desk = get_device("galaxy-s24"), get_device("desktop-1920")
        self.assertTrue(checks.applicable("PC-03", profile(cvd="deutan"), s24))
        self.assertTrue(checks.applicable("PC-03", profile(), s24))  # normal vision is evaluated and passes
        self.assertFalse(checks.applicable("PT-04", profile("EP-M", device_id="desktop-1920", grip="mouse_right"), desk))
        self.assertFalse(checks.applicable("RH-01", profile(grip="cradle_right"), s24))


class PersonaNotes(unittest.TestCase):
    def _run(self, run_id, family, channel):
        note = {"step_index": 2, "intent": "결제", "expected": "완료", "observed": "오류 문구가 무엇이 틀렸는지 말하지 않음", "confusion": True,
                "failure_class": "ux_issue", "anchor_snapshot_id": "S-2", "anchor_element_ids": ["el-5"], "anchor_selectors": ["#form-error"],
                "screen_key": "/pay#abcd", "corroborated_claimed": True}
        return {"run_id": run_id, "steps": [], "persona_notes": [note], "agent": {"model_family": family, "input_channel": channel}}

    def _finding(self, runs):
        prof = profile("EP-1")
        analyses = []
        for run in runs:
            obs = [o.to_dict(i) for i, o in enumerate(checks.check_run_timing(run, prof, get_device("galaxy-s24"), {}, None))]
            for o in obs:
                o["selectors"] = o.get("extra", {}).get("anchor_selectors", [])
                o["context_selectors"] = []
            analyses.append({"scenario_id": "SC-1", "run_id": run["run_id"], "profiles_evaluated": ["EP-1"], "observations": obs})
        return swarm.aggregate(analyses, [prof])

    def test_note_is_anchored_to_its_element(self) -> None:
        f = self._finding([self._run("R-1", "claude", "screenshot")])[0]
        self.assertTrue(f["element_key"].startswith("#form-error|"))
        self.assertEqual(f["selectors"], ["#form-error"])

    def test_claimed_corroboration_is_ignored_and_same_channel_does_not_count(self) -> None:
        f = self._finding([self._run("R-1", "claude", "screenshot"), self._run("R-2", "claude", "screenshot")])[0]
        self.assertEqual(f["tier"], "hypothesis")
        self.assertEqual(f["severity"], "P3")

    def test_different_channels_corroborate(self) -> None:
        f = self._finding([self._run("R-1", "claude", "screenshot"), self._run("R-2", "claude", "screenshot+a11y")])[0]
        self.assertEqual(f["tier"], "finding")
        self.assertEqual(f["severity"], "P2")
        self.assertEqual(f["measurement"]["corroboration"]["basis"], "channel")


class Units(unittest.TestCase):
    def test_findings_with_same_check_and_condition_merge(self) -> None:
        base = {"category": "perception", "basis": "model", "severity": "P3", "triggered_profiles": ["EP-O"], "tested_profiles": ["EP-O", "EP-Y"],
                "title_ko": "글자", "scenario_id": "SC-1", "check_id": "PC-04", "profile_specific": {"vision.presbyopia": True}}
        findings = [dict(base, id="EF-001", element_key="#a|a"), dict(base, id="EF-002", element_key="#b|b", severity="P2"),
                    dict(base, id="EF-003", element_key="#c|c", check_id="PC-01", profile_specific={})]
        units = swarm.units(findings)
        self.assertEqual(len(units), 2)
        merged = next(u for u in units if u["check_id"] == "PC-04")
        self.assertEqual(merged["instances"], ["EF-001", "EF-002"])
        self.assertEqual(merged["severity"], "P2")


class Bench(unittest.TestCase):
    def test_viewport_findings_match_only_page_level_keys_when_exact(self) -> None:
        f = {"element_key": "viewport|flash", "selectors": []}
        self.assertTrue(bench._selector_matches(f, "#bomb"))
        self.assertFalse(bench._selector_matches(f, "#bomb", exact_viewport=True))
        self.assertTrue(bench._selector_matches(f, "viewport", exact_viewport=True))

    def test_unit_metrics_present(self) -> None:
        key = {"suite": "t", "defects": [{"id": "D-1", "scenario_id": "SC-1", "category": "perception", "element_selector": "#a", "severity_min": "P3"}],
               "decoys": [], "clean_controls": [{"scenario_id": "SC-1-clean"}]}
        f = {"id": "EF-001", "scenario_id": "SC-1", "check_id": "PC-04", "category": "perception", "basis": "model", "severity": "P3",
             "element_key": "#a|a", "selectors": ["#a"], "triggered_profiles": ["EP-1"], "tested_profiles": ["EP-1"], "profile_specific": {}, "title_ko": "x"}
        g = dict(f, id="EF-002", scenario_id="SC-1-clean")
        scored = bench.score(key, [f, g], [profile("EP-1")])
        self.assertEqual(scored["matched_units"], 1)
        self.assertEqual(scored["clean_control_units"], 1)
        self.assertEqual(scored["validity_lb_units"], 0.5)
        self.assertEqual(scored["thoroughness_ci95"][1], 1.0)


class RuleFixes(unittest.TestCase):
    def test_secondary_game_control_out_of_reach_is_not_p2(self) -> None:
        # Top-left corner of a phone: out of reach for a right one-hand grip.
        pause = el("pause", "button", (8, 8, 44, 44), text="일시정지", interactive=True, roles=("game_control",), tag="button")
        jump = el("jump", "button", (8, 60, 44, 44), text="점프", interactive=True, roles=("game_control",), tag="button")
        obs = {o.element_key.split("|")[0]: o for o in checks.check_reach(ctx([pause, jump])) if o.check_id == "RH-01"}
        self.assertEqual(obs["#jump"].severity, "P2")
        self.assertEqual(obs["#pause"].severity, "P3")

    def test_numeric_keypad_is_not_choice_overload(self) -> None:
        keys = [el(f"k{i}", "button", (10 + (i % 3) * 110, 400 + (i // 3) * 50, 100, 44), text=str(i % 10), interactive=True, tag="button")
                for i in range(12)]
        self.assertEqual(checks.check_choice_overload(ctx(keys)), [])

    def test_unrelated_controls_of_similar_size_are_not_grouped(self) -> None:
        mixed = [el(f"c{i}", "button", (10 + i * 30, 400, 44, 44), text=f"{i}월", interactive=True, tag="button",
                    bg=("#ffffff" if i % 2 else "#eeeeee"), border=("#dddddd" if i % 3 else None)) for i in range(11)]
        self.assertEqual(checks.check_choice_overload(ctx(mixed)), [])

    def test_choices_group_by_container_even_when_one_is_selected(self) -> None:
        methods = [el(f"m{i}", "button", (10, 100 + i * 50, 340, 44), text=f"결제수단 {i}", interactive=True, tag="button",
                      bg=("#e8f0fe" if i == 0 else "#ffffff"), ancestor_ids=["pay-methods"],
                      sibling_scope_id="pay-methods", sibling_scope_status="measured") for i in range(10)]
        observed = checks.check_choice_overload(ctx(methods))
        self.assertEqual(len(observed), 1)
        self.assertEqual(observed[0].measurement["value"], 10)
        self.assertEqual(observed[0].measurement["grouping_basis"], "dom_sibling_structure")
        self.assertEqual(observed[0].measurement["grouping_status"], "measured")
        self.assertIn("alternative_semantics_unverified", observed[0].measurement["limitations"])
        template = load_document(ROOT / "tests/fixtures/ergo/sample_snapshot.json")
        self.assertEqual(validate_snapshot({**template, "elements": methods}), [])
        for scope in (None, 42, "", " ", "x" * 257):
            unknown = [{**item, "sibling_scope_id": scope, "sibling_scope_status": "unavailable"} for item in methods]
            with self.subTest(scope=scope):
                held = checks.check_choice_overload(ctx(unknown))
                self.assertEqual(len(held), 10)
                self.assertTrue(all(o.severity is None and o.extra.get("verdict") == "inconclusive"
                                    and o.measurement["value"] is None for o in held))
                errors = validate_snapshot({**template, "elements": unknown})
                self.assertEqual(bool(errors), scope is not None)
        fresh_null = [{**item, "sibling_scope_id": None} for item in methods]
        for item in fresh_null:
            item.pop("sibling_scope_status")
        self.assertTrue(all(o.extra.get("verdict") == "inconclusive" for o in checks.check_choice_overload(ctx(fresh_null))))
        self.assertEqual(validate_snapshot({**template, "elements": fresh_null}), [])
        no_boundary = [{**item, "sibling_scope_id": None, "sibling_scope_status": "none"} for item in methods]
        self.assertEqual(checks.check_choice_overload(ctx(no_boundary)), [])
        self.assertEqual(validate_snapshot({**template, "elements": no_boundary}), [])
        for status in ("unknown", None):
            invalid_status = [{**item, "sibling_scope_status": status} for item in methods]
            self.assertTrue(validate_snapshot({**template, "elements": invalid_status}))
            self.assertTrue(all(o.extra.get("verdict") == "inconclusive" for o in checks.check_choice_overload(ctx(invalid_status))))
        missing_id = [{k: v for k, v in item.items() if k != "sibling_scope_id"} for item in no_boundary]
        self.assertTrue(validate_snapshot({**template, "elements": missing_id}))
        self.assertTrue(all(o.extra.get("verdict") == "inconclusive" for o in checks.check_choice_overload(ctx(missing_id))))
        self.assertTrue(validate_snapshot({**template, "elements": [{**methods[0], "sibling_scope_id": None}]}))
        self.assertTrue(validate_snapshot({**template, "elements": [{**methods[0], "sibling_scope_status": "none"}]}))
        legacy = [{k: v for k, v in item.items() if k not in ("sibling_scope_id", "sibling_scope_status")} for item in methods]
        legacy_obs = checks.check_choice_overload(ctx(legacy))
        self.assertEqual(len(legacy_obs), 1)
        self.assertEqual(legacy_obs[0].measurement["grouping_basis"], "legacy_ancestor")
        self.assertEqual(legacy_obs[0].measurement["grouping_status"], "estimated")
        admin = []
        for row in range(6):
            admin += [el(f"edit-{row}", "button", (10, 100 + row * 48, 44, 32), text=f"회원 {row} 편집", interactive=True, tag="button",
                         ancestor_ids=["rows", "list-card"], sibling_scope_id=f"row-{row}"),
                      el(f"remove-{row}", "button", (62, 100 + row * 48, 44, 32), text=f"회원 {row} 삭제", interactive=True, tag="button",
                         ancestor_ids=["rows", "list-card"], sibling_scope_id=f"row-{row}")]
        self.assertEqual(checks.check_choice_overload(ctx(admin)), [])
        mixed = [el("back", "button", (8, 8, 44, 44), text="<", interactive=True, tag="button", ancestor_ids=["header"])]
        mixed += [el(f"d{i}", "button", (10 + i * 48, 100, 44, 44), text=f"{i + 1}", interactive=True, tag="button", ancestor_ids=["dates"]) for i in range(7)]
        mixed += [el(f"s{i}", "button", (10 + i * 48, 200, 44, 44), text="+-"[i], interactive=True, tag="button", ancestor_ids=["people"]) for i in range(2)]
        self.assertEqual(checks.check_choice_overload(ctx(mixed)), [])

    def test_text_labelled_custom_radio_is_exempt_from_boundary_contrast(self) -> None:
        card = el("opt", "radio", (10, 100, 300, 60), text="③ _count", interactive=True, tag="button", border="#eeeeee", container="#ffffff")
        # A visible glyph is required; unused CSS foreground on an empty button
        # does not identify it (the independent painted-state regression).
        faint_icon = el("icon", "button", (10, 200, 44, 44), text="×", interactive=True, tag="button", fg="#cccccc", border="#eeeeee", container="#ffffff")
        dark_icon = el("icon2", "button", (60, 200, 44, 44), text="×", interactive=True, tag="button", fg="#374151", border="#eeeeee", container="#ffffff")
        ids = {o.element_ids[0] for o in checks.check_contrast(ctx([card, faint_icon, dark_icon])) if o.check_id == "PC-02"}
        # The glyph identifies an icon-only button: a dark icon passes without a boundary.
        self.assertEqual(ids, {"icon"})

    def test_signed_amounts_are_a_state_cue(self) -> None:
        self.assertTrue(checks._state_cue("출금 −30,000원"))
        self.assertTrue(checks._state_cue("+12,000원"))
        self.assertFalse(checks._state_cue("09:30"))

    def test_critical_print_size_skips_button_labels(self) -> None:
        old = profile(age_band="60s", presbyopia=True, device_id="laptop-1440", grip="mouse_right")
        button = el("b", "button", (10, 10, 438, 52), text="휴대폰 간편인증으로 가입", interactive=True, tag="button", size=16, weight=700)
        para = el("p", "paragraph", (10, 100, 438, 52), text="휴대폰 간편인증으로 가입하면 바로 시작할 수 있어요", tag="p", size=13)
        hits = {o.element_ids[0] for o in checks.check_text_size(ctx([button, para], old, "laptop-1440")) if o.check_id == "PC-04"}
        self.assertNotIn("b", hits)
        self.assertIn("p", hits)

    def test_single_use_game_control_not_held_to_serial_size(self) -> None:
        pause = el("hs-pause", "hotspot", (335, 54, 44, 44), name="일시정지", interactive=True, roles=("game_control",), tag="hotspot")
        pause["selector"] = "hotspot:hs-pause"
        run = {"run_id": "R-1", "steps": [{"action": {"action": "tap", "target": "hotspot:hs-pause"}, "target_element_id": "hs-pause"}]}
        obs = checks.check_game_controls(ctx([pause], device_id="iphone-15", prof=profile(device_id="iphone-15"), run=run))
        self.assertTrue(all(o.passed for o in obs))
        jump = el("hs-jump", "hotspot", (300, 600, 44, 44), name="점프", interactive=True, roles=("game_control",), tag="hotspot")
        obs = checks.check_game_controls(ctx([jump], device_id="iphone-15", prof=profile(device_id="iphone-15"), run=run))
        self.assertTrue(any(not o.passed and o.severity == "P3" for o in obs))  # a gameplay control is serial

    def test_switch_keeps_boundary_contrast_even_with_label(self) -> None:
        sw = el("sw", "switch", (280, 100, 52, 32), text="알림 받기", interactive=True, tag="button", border="#eeeeee", container="#ffffff")
        self.assertTrue([o for o in checks.check_contrast(ctx([sw])) if o.check_id == "PC-02"])

    def test_toast_at_the_floor_is_not_flagged_for_jitter(self) -> None:
        run = {"run_id": "R-1", "steps": [], "timing_windows": [{"id": "toast", "selector": "#toast", "visible_ms": 3995.2, "kind": "transient_text", "text": "저장했어요"}]}
        obs = checks.check_run_timing(run, profile(), get_device("galaxy-s24"), {}, {"timing_windows": [{"id": "toast", "selector": "#toast", "kind": "transient_text"}]})
        self.assertTrue(all(o.passed for o in obs if o.check_id == "CG-02"))

    def test_tap_after_qte_closed_is_not_a_latency_finding(self) -> None:
        run = {"run_id": "R-1", "timing_windows": [{"id": "qte", "selector": "#qte", "kind": "qte", "starts_ms": [5042], "intervals_ms": [892]}],
               "steps": [{"step_index": 7, "action": {"action": "tap", "target": "hotspot:hs-boost"}, "target_element_id": "hs-boost",
                          "before": "S-6", "after": "S-7", "t_start_ms": 6106, "feedback_latency_ms": None, "result": "ok"}]}
        boost = el("hs-boost", "hotspot", (355, 436, 28, 28), interactive=True, roles=("game_control", "timed"), tag="hotspot")
        snaps = {"S-6": {"elements": [boost]}, "S-7": {"elements": [boost]}}
        obs = checks.check_run_timing(run, profile(device_id="iphone-15"), get_device("iphone-15"), snaps, None)
        self.assertFalse([o for o in obs if o.check_id == "CG-03" and not o.passed])


class SituationalTouch(unittest.TestCase):
    """Situational brief SIT-01..03 (decision log round 8)."""

    def walker(self, device_id="galaxy-s24"):
        p = profile("EP-W", device_id=device_id, grip="one_hand_right")
        p["attributes"]["context"]["mobility"] = "walking"
        return _finalise(p, get_device(device_id))

    def pt04(self, box, prof):
        pay = el("pay", "button", box, text="결제", interactive=True, roles=("primary",), tag="button")
        return [o for o in checks.check_touch_accuracy(ctx([pay], prof=prof)) if o.check_id == "PT-04"][0]

    def test_platform_size_target_is_p3_at_most_from_inflation_alone(self) -> None:
        # 44 x 44 CSS px on a Galaxy S24 is 8.1 mm: fine at k = 1, flagged only by thumb x walking.
        o = self.pt04((150, 600, 44, 44), self.walker())
        self.assertTrue(o.measurement["profile_only"])
        self.assertEqual(o.severity, "P3")
        saved = params.TOUCH_PROFILE_ONLY_P3_MIN_MM
        try:
            params.TOUCH_PROFILE_ONLY_P3_MIN_MM = None
            self.assertEqual(self.pt04((150, 600, 44, 44), self.walker()).severity, "P2")
        finally:
            params.TOUCH_PROFILE_ONLY_P3_MIN_MM = saved

    def test_target_below_platform_size_keeps_p2(self) -> None:
        o = self.pt04((150, 600, 34, 34), self.walker())  # 6.2 mm
        self.assertEqual(o.severity, "P2")

    def test_factors_multiply_by_default_and_add_in_variance_as_a_switch(self) -> None:
        p = self.walker()
        thumb, walk = params.TOUCH_SIGMA_MULT["one_hand_thumb"], params.TOUCH_SIGMA_MULT["mobility_walking"]
        self.assertAlmostEqual(touch_sigma_multiplier(p), thumb * walk)
        saved = params.TOUCH_SIGMA_COMBINE
        try:
            params.TOUCH_SIGMA_COMBINE = "additive"
            self.assertAlmostEqual(touch_sigma_multiplier(p), (1 + (thumb ** 2 - 1) + (walk ** 2 - 1)) ** 0.5)
            self.assertAlmostEqual(touch_sigma_multiplier(profile("EP-S", grip="cradle_right")), 1.0)
        finally:
            params.TOUCH_SIGMA_COMBINE = saved


class FeedbackNoticing(unittest.TestCase):
    def test_bold_icon_error_is_salient_even_on_a_flat_box(self) -> None:
        err = el("err", "alert", (20, 500, 320, 63), text="⚠ 1일 이체 한도를 넘었어요", fg="#b3261e", bg="#fdecec", container="#f2f4f6", weight=700,
                 roles=("error_message",))
        c = ctx([err])
        salient, info = checks._salient_change(c, err, new=True)
        self.assertTrue(salient)
        self.assertTrue(info["text_salient"])

    def test_toast_shown_with_a_new_screen_is_still_checked(self) -> None:
        before = {"surface": {"url": "http://x/a"}, "elements": [el(f"e{i}", "button", (10, 10 + i * 50, 100, 44)) for i in range(10)]}
        toast = el("toast", "status", (20, 700, 320, 60), text="평소보다 큰 금액이에요. 받는 분을 다시 확인해 주세요.", roles=("critical_message",),
                   fg="#ffffff", bg="#333333", container="#ffffff")
        now = [el("h", "heading", (10, 10, 200, 30), text="확인")] + [toast]
        c = ctx(now, previous=before, focus={"x": 180, "y": 120})
        c.snapshot["surface"] = {"url": "http://x/a"}
        c.scenario = {"timing_windows": [{"id": "t", "selector": "#toast", "kind": "transient_text"}]}
        self.assertTrue([o for o in checks.check_gaze(c) if o.check_id == "GZ-02"])
        c.scenario = {"timing_windows": []}
        self.assertFalse([o for o in checks.check_gaze(c) if o.check_id == "GZ-02"])

    def test_message_scrolled_out_of_view_is_not_new(self) -> None:
        # dev-2 clean pages: an error shown in view, then scrolled out by the driver's
        # pre-action scroll (or by the page), is the same message, not a new one.
        buttons = [el(f"e{i}", "button", (10, 10 + i * 50, 100, 44)) for i in range(8)]
        err_before = el("err", "alert", (20, -600, 320, 60), text="3번 문항에 답하지 않았습니다.", roles=("error_message",), in_viewport=False)
        err_after = el("err", "alert", (20, -600, 320, 60), text="3번 문항에 답하지 않았습니다.", roles=("error_message",), in_viewport=False)
        before = {"surface": {"url": "http://x/a"}, "elements": buttons + [err_before]}
        c = ctx(buttons + [err_after], previous=before, focus={"x": 60, "y": 200})
        c.snapshot["surface"] = {"url": "http://x/a"}
        self.assertFalse([o for o in checks.check_gaze(c) if o.check_id == "GZ-02"])
        # Hidden before (not rendered) and now shown off-screen: new, P1 for an error.
        hidden = dict(err_before, visible=False)
        c = ctx(buttons + [err_after], previous={"surface": {"url": "http://x/a"}, "elements": buttons + [hidden]}, focus={"x": 60, "y": 200})
        c.snapshot["surface"] = {"url": "http://x/a"}
        got = [o for o in checks.check_gaze(c) if o.check_id == "GZ-02"]
        self.assertEqual([(o.severity, o.measurement["new"]) for o in got], [("P1", True)])

    def test_app_scroll_of_half_a_screen_reorients_but_off_screen_still_counts(self) -> None:
        # A form that jumps to its first error: the tap point's content moved away, so
        # eccentricity from it is not measured; a message left off-screen still is.
        buttons = [el(f"e{i}", "button", (10, 10 + i * 50, 100, 44)) for i in range(8)]
        err = el("err", "alert", (20, 40, 320, 60), text="3번 문항에 답하지 않았습니다.", roles=("error_message",), weight=700,
                 fg="#b3261e", bg="#fdecec", container="#ffffff")
        far = el("far", "alert", (20, 900, 320, 60), text="아래 오류", roles=("error_message",), in_viewport=False)
        before = {"surface": {"url": "http://x/a", "scroll": {"x": 0, "y": 742}}, "elements": buttons}

        def gz(scroll_y, action="click"):
            c = ctx(buttons + [err, far], previous=before, focus={"x": 180, "y": 740}, step={"action": {"action": action}})
            c.snapshot["surface"] = {"url": "http://x/a", "scroll": {"x": 0, "y": scroll_y}}
            return sorted(o.element_key.split("|")[0] for o in checks.check_gaze(c) if o.check_id == "GZ-02")

        self.assertEqual(gz(51), ["#far"])  # app scrolled 691 px on a 780 px screen
        self.assertIn("#err", gz(700))  # a small scroll: the tap point still anchors the gaze
        self.assertIn("#err", gz(51, action="swipe"))  # the user scrolled: not an app jump

    def test_empty_live_region_slot_is_not_a_prior_message(self) -> None:
        # An error written into a pre-rendered empty role=alert slot, off-screen, is new (P1).
        buttons = [el(f"e{i}", "button", (10, 10 + i * 50, 100, 44)) for i in range(8)]
        slot = el("err", "alert", (20, -600, 320, 24), text="", roles=("error_message",), in_viewport=False)
        err = el("err", "alert", (20, -600, 320, 24), text="이메일 형식이 올바르지 않습니다", roles=("error_message",), in_viewport=False)
        c = ctx(buttons + [err], previous={"surface": {"url": "http://x/a"}, "elements": buttons + [slot]}, focus={"x": 60, "y": 200})
        c.snapshot["surface"] = {"url": "http://x/a"}
        got = [(o.severity, o.measurement.get("new")) for o in checks.check_gaze(c) if o.check_id == "GZ-02"]
        self.assertEqual(got, [("P1", True)])
        # A new but still empty slot is not a message.
        c = ctx(buttons + [slot], previous={"surface": {"url": "http://x/a"}, "elements": buttons}, focus={"x": 60, "y": 200})
        c.snapshot["surface"] = {"url": "http://x/a"}
        self.assertEqual([o for o in checks.check_gaze(c) if o.check_id == "GZ-02"], [])

    def test_app_scroll_keeps_declared_transients(self) -> None:
        buttons = [el(f"e{i}", "button", (10, 10 + i * 50, 100, 44)) for i in range(8)]
        toast = el("toast", "status", (20, 700, 320, 60), text="저장했어요", roles=("status",), fg="#ffffff", bg="#333333", container="#ffffff")
        before = {"surface": {"url": "http://x/a", "scroll": {"x": 0, "y": 742}}, "elements": buttons}
        c = ctx(buttons + [toast], previous=before, focus={"x": 180, "y": 60}, step={"action": {"action": "click"}})
        c.snapshot["surface"] = {"url": "http://x/a", "scroll": {"x": 0, "y": 51}}
        c.scenario = {"timing_windows": [{"id": "t", "selector": "#toast", "kind": "transient_text"}]}
        self.assertTrue([o for o in checks.check_gaze(c) if o.check_id == "GZ-02"])
        c.scenario = {"timing_windows": []}
        self.assertFalse([o for o in checks.check_gaze(c) if o.check_id == "GZ-02"])

    def test_screen_replacement_skips_feedback_noticing(self) -> None:
        before = {"surface": {"url": "http://x/a"}, "elements": [el(f"e{i}", "button", (10, 10 + i * 50, 100, 44)) for i in range(10)]}
        after_same = {"surface": {"url": "http://x/a"}, "elements": before["elements"][:9]}
        after_new = {"surface": {"url": "http://x/a"}, "elements": [el("r", "heading", (10, 10, 200, 30))]}
        self.assertFalse(checks._screen_changed(before, after_same))
        self.assertTrue(checks._screen_changed(before, after_new))


if __name__ == "__main__":
    unittest.main()


class CoveragePlan(unittest.TestCase):
    """Round 12: a low-vision stratum, and pointer devices skip touch-only strata."""

    def strata(self, device_id: str, count: int) -> list[str]:
        return [p.get("coverage_stratum") for p in sample_profiles(count, 11, [device_id])]

    def test_pointer_plan_skips_touch_only_strata_and_covers_low_vision(self) -> None:
        got = self.strata("laptop-1440", 7)
        self.assertEqual(got, ["mouse_right", "mouse_left", "keyboard_only", "cvd_deutan", "presbyopia_60s", "low_vision", "70s_plus"])

    def test_touch_plan_keeps_every_condition(self) -> None:
        got = self.strata("galaxy-s24", 14)
        for name in ("cvd_deutan", "presbyopia_60s", "tremor", "walking", "low_vision", "70s_plus", "small_hand"):
            self.assertIn(name, got)
        low = next(p for p in sample_profiles(14, 11, ["galaxy-s24"]) if p.get("coverage_stratum") == "low_vision")
        self.assertEqual(low["attributes"]["vision"]["acuity"], "low")

    def test_mixed_devices_put_touch_only_strata_on_the_phone(self) -> None:
        plan = sample_profiles(24, 11, ["galaxy-s24", "laptop-1440"])
        for p in plan:
            if p.get("coverage_stratum") in ("walking", "small_hand", "tremor"):
                self.assertEqual(p["attributes"]["device_id"], "galaxy-s24")


class PresbyopiaIsExplicit(unittest.TestCase):
    """Age is context; presbyopia is an explicit input or declared assumption."""

    def test_age_band_alone_never_sets_presbyopia(self) -> None:
        for seed in range(12):
            for p in sample_profiles(16, seed, ["galaxy-s24"]):
                if p["attributes"]["age_band"] in ("50s", "60s", "70s+"):
                    self.assertEqual(p["attributes"]["vision"]["presbyopia"],
                                     p.get("coverage_stratum") in ("presbyopia_60s", "70s_plus"),
                                     f"{p['profile_id']} (seed {seed})")

    def test_mutating_only_the_age_band_never_flips_presbyopia(self) -> None:
        profiles = sample_profiles(8, 3, ["galaxy-s24"])
        for p in profiles:
            attrs = p["attributes"]
            before = attrs["vision"]["presbyopia"]
            attrs["age_band"] = "70s+" if attrs["age_band"] != "70s+" else "20s"
            self.assertEqual(attrs["vision"]["presbyopia"], before)

    def test_explicit_presbyopia_coverage_still_works(self) -> None:
        plan = sample_profiles(14, 11, ["galaxy-s24"])
        for stratum in ("presbyopia_60s", "70s_plus"):
            p = next(q for q in plan if q.get("coverage_stratum") == stratum)
            self.assertTrue(p["attributes"]["vision"]["presbyopia"])
            self.assertEqual(p["attributes"]["age_band"], "60s" if stratum == "presbyopia_60s" else "70s+")

    def test_persona_record_age_does_not_set_presbyopia_but_an_explicit_flag_does(self) -> None:
        records = [{"dataset": "d", "revision": "1", "record_id": f"r{i}", "age_band": band}
                   for i, band in enumerate(("60s", "70s+", "50s"))]
        profiles = sample_profiles(3, 7, ["galaxy-s24"], persona_records=records)
        for p in profiles:
            self.assertFalse(p["attributes"]["vision"]["presbyopia"], p["profile_id"])
        explicit = [dict(record, presbyopia=True) for record in records]
        profiles = sample_profiles(3, 7, ["galaxy-s24"], persona_records=explicit)
        for p in profiles:
            self.assertTrue(p["attributes"]["vision"]["presbyopia"], p["profile_id"])

    def test_explicit_presbyopia_without_age_is_respected(self) -> None:
        for age in (None, "unknown", "20s"):
            record = {"dataset": "d", "revision": "1", "record_id": "r", "presbyopia": True}
            if age is not None:
                record["age_band"] = age
            prof = sample_profiles(1, 7, ["galaxy-s24"], persona_records=[record])[0]
            self.assertTrue(prof["attributes"]["vision"]["presbyopia"], age)
