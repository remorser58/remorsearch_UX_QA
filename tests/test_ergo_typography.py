"""Glyph-metric provenance, legacy policy and real-browser XAG unit regression."""

from __future__ import annotations

import copy
import json
import sys
import unittest
from dataclasses import replace
from pathlib import Path

import _paths  # noqa: F401

from ergoqa import checks
from ergoqa.devices import mm_per_css_px
from ergoqa.hf.perception import visual_angle_arcmin
from ergoqa.snapshot import validate_font_metrics, validate_snapshot
from test_ergo_fixes import ctx, el


def metrics(body: float = 19.0) -> dict:
    return {"method": "canvas-textmetrics-v1", "unit": "css_px", "status": "matched_font", "body_height_px": body,
            "probes": {"cap_H_px": 15.0, "x_height_px": 11.0, "body_Hg_px": 19.0, "hangul_px": 18.0},
            "limitations": ["dom_ink_unmeasured", "font_fallback_unverified"]}


def unavailable(reason: str = "mixed_font_or_style") -> dict:
    return {**metrics(), "status": "unavailable", "body_height_px": None, "probes": None,
            "limitations": ["dom_ink_unmeasured", "font_fallback_unverified", reason]}


def text_item(eid: str = "text", size: float = 22.0, **extra) -> dict:
    return el(eid, "paragraph", (10, 20, 300, 50), text="Hg", tag="p", size=size, roles=("hud",), **extra)


def xag_result(items: list[dict]) -> list:
    return [o for o in checks.check_text_size(ctx(items, device_id="desktop-1920")) if o.model.startswith("xag-101")]


class Typography(unittest.TestCase):
    def test_equal_em_different_body_and_negative_control(self) -> None:
        rows = xag_result([text_item("above", font_metrics=metrics(20.0)), text_item("below", font_metrics=metrics(16.0))])
        self.assertEqual([o.passed for o in rows], [True, False])
        self.assertEqual([o.severity for o in rows], [None, "P2"])
        self.assertTrue(all(o.measurement["metric"] == "displayed_text_ink_body" for o in rows))
        self.assertTrue(all(o.measurement["conformance"] == "not_assessed" and not o.measurement["dom_ink_measured"] for o in rows))

    def test_fixed_probe_cannot_supply_actual_body(self) -> None:
        value = metrics(12.0)
        value["probes"]["body_Hg_px"] = 30.0
        row = xag_result([text_item(font_metrics=value)])[0]
        self.assertFalse(row.passed)
        self.assertEqual(row.measurement["value"], 12.0)

    def test_unknown_or_invalid_metadata_never_fabricates_verdict(self) -> None:
        for value in (unavailable(), unavailable("transform_or_zoom"), {}, {**metrics(), "body_height_px": float("nan")}):
            with self.subTest(value=value):
                rows = checks.check_text_size(ctx([text_item(size=10, font_metrics=value)], device_id="desktop-1920"))
                self.assertEqual(len(rows), 1)
                self.assertIsNone(rows[0].measurement["value"])
                self.assertIsNone(rows[0].severity)
                self.assertFalse(rows[0].passed)
                self.assertEqual(rows[0].extra["verdict"], "inconclusive")

    def test_old_small_hud_retains_policy_warning_separate_from_xag_gap(self) -> None:
        rows = checks.check_text_size(ctx([text_item(size=16)], device_id="desktop-1920"))
        gap = next(o for o in rows if o.model == "xag-101-unverified-v1")
        warning = next(o for o in rows if o.model == "hud-em-policy-v1")
        self.assertIsNone(gap.severity)
        self.assertEqual(warning.severity, "P2")
        self.assertFalse(warning.passed)
        self.assertEqual(warning.measurement["threshold"], 18.0)
        self.assertNotIn("guideline", warning.measurement)
        self.assertNotIn("verdict", warning.extra)
        self.assertEqual(warning.measurement["conformance"], "not_assessed")

    def test_game_surface_uses_body_even_without_hud_role(self) -> None:
        target = text_item(font_metrics=metrics(16.0))
        target["roles"] = []
        context = ctx([target], device_id="desktop-1920")
        context.snapshot["surface"]["kind"] = "game"
        self.assertTrue(any(o.model == "xag-101-canvas-estimate-v1" and not o.passed for o in checks.check_text_size(context)))

    def test_pc04_proxy_and_glyph_angles_use_explicit_vertical_scale(self) -> None:
        target = el("body", "paragraph", (10, 20, 200, 30), text="본문 글자 크기를 살펴보는 문장입니다", size=9, font_metrics=metrics(7.0))
        context = ctx([target])
        context.device = replace(context.device, display_mm=(60.0, 180.0))
        row = checks.check_text_size(context)[0]
        self.assertEqual(row.measurement["basis"], "project_policy")
        self.assertEqual(row.measurement["metric"], "css_em")
        self.assertEqual(row.measurement["conformance"], "not_assessed")
        distance = row.measurement["viewing_distance_mm"]
        expected = visual_angle_arcmin(7 * mm_per_css_px(context.device, "y"), distance)
        self.assertAlmostEqual(row.measurement["font_metric_angles_arcmin"]["displayed_body"], expected, places=3)
        self.assertNotIn("ISO", row.message_ko)
        self.assertNotIn("Apple HIG 11pt", row.message_ko)

    def test_optional_snapshot_metadata_validates_and_legacy_still_loads(self) -> None:
        snap = json.loads((Path(__file__).parent / "fixtures/ergo/sample_snapshot.json").read_text())
        self.assertEqual(validate_snapshot(snap), [])
        snap["elements"][0]["font_metrics"] = metrics()
        self.assertEqual(validate_snapshot(snap), [])
        cases = [("body_height_px", True), ("body_height_px", -1), ("body_height_px", float("inf")),
                 ("unit", "device_px"), ("method", "pixel-measured"), ("probes", {"body_Hg_px": 18.0}),
                 ("limitations", ["dom_ink_unmeasured"]), ("status", "measured"), ("text", "PRIVATE-SENTINEL")]
        for field, value in cases:
            bad = copy.deepcopy(snap)
            bad["elements"][0]["font_metrics"][field] = value
            with self.subTest(field=field):
                self.assertTrue(any("font_metrics" in error for error in validate_snapshot(bad)))
        self.assertEqual(validate_font_metrics(unavailable()), [])
        self.assertTrue(validate_font_metrics({**unavailable(), "body_height_px": 18.0}))


def verify_capture(filename: str) -> None:
    capture = json.loads(Path(filename).read_text())
    items = capture["elements"]
    for item in items:
        if "font_metrics" in item:
            assert not validate_font_metrics(item["font_metrics"]), item["selector"]
    before = [{k: v for k, v in item.items() if k != "font_metrics"} for item in items]
    before_rows, after_rows = xag_result(before), xag_result(items)
    by_id = {o.element_ids[0]: o for o in after_rows}
    by_selector = {item["selector"]: by_id[item["id"]] for item in items if item["id"] in by_id}
    for item in items:
        if item["font_metrics"]["status"] != "matched_font" or item["selector"] not in by_selector:
            continue
        row = by_selector[item["selector"]]
        assert row.measurement["value"] == item["font_metrics"]["body_height_px"]
        assert row.passed == (row.measurement["value"] >= row.measurement["threshold"])
        assert row.severity == (None if row.passed else "P2")
    assert not by_selector["#arial16"].passed and by_selector["#above"].passed
    for selector in ("#mixed", "#transformed", "#zoomed", "#vertical", "#pseudo", "#private"):
        assert by_selector[selector].extra["verdict"] == "inconclusive"
        assert by_selector[selector].severity is None
    assert all(o.extra["verdict"] == "inconclusive" for o in before_rows)
    print(json.dumps({"before": [o.to_dict(i) for i, o in enumerate(before_rows)],
                      "after": [o.to_dict(i) for i, o in enumerate(after_rows)]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--capture":
        verify_capture(sys.argv[2])
    else:
        unittest.main()
