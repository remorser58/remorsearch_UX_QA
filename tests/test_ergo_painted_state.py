"""Actual paint invariance and bounded PC-02/PC-03 evidence."""

from __future__ import annotations

import copy
import json
import os
import unittest
from unittest.mock import patch
from pathlib import Path

import _paths  # noqa: F401

from ergoqa import analyze, checks, report
from ergoqa.snapshot import validate_snapshot
from test_ergo_fixes import ctx, el, profile


def paint_part(key, color, background="#ffffff", kind="boundary", shape=None):
    return {"key": key, "color": color, "background": background, "kind": kind, "shape": shape,
            "box": {"x": 10, "y": 10, "w": 24, "h": 24}}


def painted(parts=(), gaps=(), decorative=False):
    return {"source": "dom-solid-v1", "parts": list(parts), "gaps": list(gaps), "decorative": decorative}


def switch(eid="switch", **extra):
    return el(eid, "switch", (10, 10, 48, 36), interactive=True, tag="button", **extra)


class PaintedState(unittest.TestCase):
    def test_unused_foreground_never_changes_nontext_verdict(self):
        parts = [paint_part("self:fill", "#eeeeee"), paint_part("self:border", "#eeeeee")]
        for foreground in ("#111111", "#eeeeee", "#d32f2f"):
            target = switch(fg=foreground, paint=painted(parts))
            result = [o for o in checks.check_contrast(ctx([target])) if o.check_id == "PC-02"]
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0].measurement["value"], 1.16)

    def test_dark_label_cannot_identify_pale_track_or_thumb(self):
        target = switch(text="Notifications", paint=painted([
            paint_part("self:text", "#111111", kind="text"),
            paint_part("self/0:fill", "#eeeeee"),
            paint_part("self/0/0:fill", "#dddddd", "#eeeeee"),
        ]))
        observations = [o for o in checks.check_contrast(ctx([target])) if o.check_id == "PC-02"]
        self.assertEqual({o.measurement["kind"] for o in observations}, {"self/0:fill", "self/0/0:fill"})

    def test_svg_pale_and_disabled_exemption(self):
        target = switch(paint=painted([paint_part("self/0/0:fill", "#eeeeee", kind="graphic", shape="rect|24|24")]))
        self.assertEqual(len(checks.check_contrast(ctx([target]))), 1)
        target["enabled"] = False
        self.assertEqual(checks.check_contrast(ctx([target])), [])

    def test_actual_svg_channels_colour_only_and_visible_redundancy(self):
        for channel in ("fill", "stroke"):
            a = switch("a", paint=painted([paint_part(f"self/0/0:{channel}", "#d32f2f", kind="graphic", shape="rect|24|24")]))
            b = switch("b", paint=painted([paint_part(f"self/0/0:{channel}", "#388e3c", kind="graphic", shape="rect|24|24")]))
            self.assertEqual(len(checks.check_colour_only(ctx([a, b], profile(cvd="deutan")))), 1)
            a["name"] = "✓"  # not visible; does not exempt paint evidence
            self.assertEqual(len(checks.check_colour_only(ctx([a, b], profile(cvd="deutan")))), 1)
            a["text"] = "✕"
            b["text"] = "✓"
            self.assertEqual(checks.check_colour_only(ctx([a, b], profile(cvd="deutan"))), [])

    def test_distinct_shape_decorative_disabled_and_unknown_not_asserted(self):
        a = switch("a", paint=painted([paint_part("self/0/0:fill", "#d32f2f", kind="graphic", shape="rect|24|24")]))
        b = switch("b", paint=painted([paint_part("self/0/0:fill", "#388e3c", kind="graphic", shape="circle|12")]))
        self.assertEqual(checks.check_colour_only(ctx([a, b], profile(cvd="deutan"))), [])
        b["paint"]["parts"][0]["shape"] = "rect|24|24"
        for condition in ("decorative", "disabled", "gap"):
            item = copy.deepcopy(b)
            if condition == "decorative":
                item["paint"]["decorative"] = True
            elif condition == "disabled":
                item["enabled"] = False
            else:
                item["paint"]["gaps"] = ["unknown_background"]
            self.assertEqual(checks.check_colour_only(ctx([a, item], profile(cvd="deutan"))), [])
        unknown = switch(paint=painted([paint_part("self:fill", "#eeeeee")], gaps=["pseudo_paint"]))
        self.assertEqual(checks.check_contrast(ctx([unknown])), [])

    def test_pc01_unchanged_and_legacy_controls_do_not_use_unused_fg(self):
        text = el("text", "paragraph", (10, 10, 200, 40), text="Legible text", fg="#eeeeee")
        self.assertEqual([o.check_id for o in checks.check_contrast(ctx([text]))], ["PC-01"])
        target = switch(border="#eeeeee", container="#ffffff", fg="#111111")
        self.assertEqual([o.check_id for o in checks.check_contrast(ctx([target]))], ["PC-02"])

    def test_typed_metadata_rejects_malformed_paint(self):
        snapshot = ctx([switch(paint=painted([paint_part("self:fill", "#eeeeee")]))]).snapshot
        snapshot.update(schema_version="ergo-snapshot.v1", run_id="R-1", captured_at="2026-10-02T00:00:00Z",
                        screenshot={"path": "S.png", "sha256": None, "width_px": 360, "height_px": 780})
        snapshot["device"]["dpr"] = 3
        self.assertEqual(validate_snapshot(snapshot), [])
        for field, value in (("parts", [False]), ("parts", [paint_part("self:fill", "#eeeeee")] * 17),
                             ("gaps", ["invention"]), ("decorative", "true"), ("source", "claimed_pixels")):
            bad = copy.deepcopy(snapshot)
            bad["elements"][0]["paint"][field] = value
            self.assertTrue(any(".paint" in error for error in validate_snapshot(bad)))
        bad = copy.deepcopy(snapshot)
        bad["elements"][0]["paint"]["parts"][0]["color"] = "url(secret)"
        self.assertTrue(any(".paint" in error for error in validate_snapshot(bad)))

    def test_unverified_paint_reaches_report_without_passing_observation(self):
        c = ctx([switch(paint=painted(gaps=["unknown_background"]))])
        run = {**c.run, "profile_id": c.profile["profile_id"], "device": c.snapshot["device"],
               "surface": c.snapshot["surface"], "status": "completed", "success": True,
               "started_at": "2026-10-02T00:00:00Z", "ended_at": "2026-10-02T00:00:01Z"}
        with patch.object(analyze, "load_run_dir", return_value=(run, [c.snapshot])):
            result = analyze.analyze_run("owned-synthetic", [c.profile], gaze_enabled=False)
        self.assertTrue(any("PC-02/PC-03 paint unverified (unknown_background)" in s for s in result["limitations"]))
        self.assertFalse(any(o["check_id"] in ("PC-02", "PC-03") for o in result["observations"]))
        self.assertIn("paint unverified (unknown_background)", report.render([], [c.profile], [result]))


@unittest.skipUnless(os.environ.get("ERGO_PAINT_CAPTURES"), "real capture file provided by focused browser group")
class ActualPaintCaptures(unittest.TestCase):
    def test_frozen_browser_captures_feed_real_checks(self):
        captures = json.loads(Path(os.environ["ERGO_PAINT_CAPTURES"]).read_text())
        self.assertEqual(captures[0]["png_sha256"], captures[1]["png_sha256"])
        results = []
        for capture in captures:
            elements = capture["elements"]
            observations = checks.check_contrast(ctx(elements))
            ids = {eid for o in observations if o.check_id == "PC-02" for eid in o.element_ids}
            by_selector = {e["selector"]: e["id"] for e in elements}
            self.assertIn(by_selector["#unused"], ids)
            self.assertIn(by_selector["#child-pale"], ids)
            self.assertIn(by_selector["#svg-pale"], ids)
            self.assertIn(by_selector["#native-styled"], ids)
            self.assertIn(by_selector["#glyph-pale"], ids)
            self.assertNotIn(by_selector["#glyph-dark"], ids)
            for good in ("#child-good", "#disabled", "#gradient", "#native", "#hidden", "#transparent", "#capped"):
                if good in by_selector:
                    self.assertNotIn(by_selector[good], ids)
            cvd = checks.check_colour_only(ctx(elements, profile(cvd="deutan")))
            pairs = {frozenset(o.element_ids) for o in cvd}
            for a, b in (("#svg-red", "#svg-green"), ("#stroke-red", "#stroke-green"), ("#css-red", "#css-green")):
                self.assertIn(frozenset((by_selector[a], by_selector[b])), pairs)
            for a, b in (("#cue-red", "#cue-green"), ("#shape-red", "#shape-green")):
                self.assertNotIn(frozenset((by_selector[a], by_selector[b])), pairs)
            for a, b in (("#covered-red", "#covered-green"), ("#clip-red", "#clip-green")):
                self.assertNotIn(frozenset((by_selector[a], by_selector[b])), pairs)
            unused = next(o.measurement for o in observations if o.check_id == "PC-02" and by_selector["#unused"] in o.element_ids)
            results.append(unused)
        self.assertEqual(results[0], results[1])
        attribute_capture = json.loads(Path(os.environ["ERGO_PAINT_CAPTURES"]).with_name("painted-svg-attribute.json").read_text())
        by_selector = {e["selector"]: e["id"] for e in attribute_capture["elements"]}
        pair = frozenset((by_selector["#svg-red"], by_selector["#svg-green"]))
        observations = checks.check_colour_only(ctx(attribute_capture["elements"], profile(cvd="deutan")))
        self.assertTrue(any(frozenset(o.element_ids) == pair for o in observations))
        self.assertNotIn("UNUSED-PRIVATE-SHAPE", json.dumps(attribute_capture))


if __name__ == "__main__":
    unittest.main()
