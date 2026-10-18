"""Static-copy condition validation, measured loss and existing capture receipts."""
from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import _paths  # noqa: F401
from ergoqa import analyze, checks, png
from test_ergo_fixes import el
from ergoqa.snapshot import ADAPTATION_CONDITIONS, SnapshotError, load_run_dir, sha256_file, validate_adaptation, validate_run

FIXTURES = Path(__file__).parent / "fixtures" / "ergo"


def load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def record(kind: str = "text_spacing") -> dict:
    style = {"font_size": 16, "line_height": 20, "paragraph_after": 8, "letter_spacing": 0, "word_spacing": 0}
    changed_style = {"font_size": 16, "line_height": 24, "paragraph_after": 32, "letter_spacing": 1.92, "word_spacing": 2.56}
    state = {"index": 1, "selector": "#fixture-text", "kind": "text", "area": 100, "visible_area": 100, "visible_fraction": 1, "style": style}
    changed = dict(state, visible_area=75, visible_fraction=.75, style=changed_style, applied=True,
                   properties=["line_height", "paragraph_after", "letter_spacing", "word_spacing"])
    return {"kind": kind, "condition": copy.deepcopy(ADAPTATION_CONDITIONS[kind]),
            "source_snapshot_id": "S-R-sample-01-001", "baseline_snapshot_id": "S-baseline", "snapshot_id": "S-changed",
            "baseline_viewport_css": [360, 780], "viewport_css": [360, 780 if kind == "text_spacing" else 390], "dpr": 3,
            "status": "measured", "applied": True, "evaluable": True, "scan_capped": False, "gaps": [], "evaluated_elements": 1,
            "styles": {"live_rules": 2, "copy_rules": 3, "complete": True},
            "lost": [{"selector": "#fixture-text", "kind": "text", "reason": "text_clipped", "before": state, "after": changed}]}


def captures(rec: dict) -> dict[str, dict]:
    source = load("sample_snapshot.json")
    snaps = {source["snapshot_id"]: source}
    for key, kind, vp in (("baseline_snapshot_id", "baseline", rec["baseline_viewport_css"]),
                          ("snapshot_id", rec["kind"], rec["viewport_css"])):
        snap = copy.deepcopy(source)
        snap["snapshot_id"] = rec[key]
        snap["device"].update(viewport_css=vp, probe="adaptation")
        snap["adaptation"] = {"kind": kind, "source_snapshot_id": source["snapshot_id"], "condition": None if kind == "baseline" else rec["condition"]}
        snap["screenshot"].update(path=f"{rec[key]}.png", width_px=vp[0] * 3, height_px=vp[1] * 3)
        snaps[snap["snapshot_id"]] = snap
    return snaps


class AdaptationTests(unittest.TestCase):
    def test_valid_metadata_and_legacy_runs(self):
        self.assertEqual(validate_run(load("sample_run/run.json")), [])
        for kind in ADAPTATION_CONDITIONS:
            self.assertEqual(validate_adaptation(record(kind)), [])

    def test_partial_content_loss_is_measured_and_deduped(self):
        for kind, cid in (("text_spacing", "RF-02"), ("short_height", "RF-03")):
            rec = record(kind)
            doc = {"run_id": "R-sample-01", "adaptation": [rec, rec]}
            obs = checks.check_adaptation(doc, {"profile_id": "P"}, captures(rec))
            self.assertEqual([(o.check_id, o.severity, o.snapshot_id) for o in obs], [(cid, "P2", "S-changed")])
            self.assertEqual(obs[0].to_dict(0)["basis"], "measured")
            self.assertEqual(obs[0].measurement["baseline_snapshot_id"], "S-baseline")

    def test_malformed_or_unapplied_import_never_produces_loss(self):
        mutations = [lambda r: r.update(dpr=float("nan")), lambda r: r.update(dpr=True),
                     lambda r: r["condition"].update(letter_spacing=.5), lambda r: r.update(evaluated_elements="1"),
                     lambda r: r.update(viewport_css=[320, 780]), lambda r: r.update(applied=False),
                     lambda r: r.update(scan_capped=True), lambda r: r.update(gaps=[{}]),
                     lambda r: r["styles"].update(copy_rules=0), lambda r: r["lost"][0]["after"].update(applied=False),
                     lambda r: r["lost"][0]["after"].update(properties=[{}]),
                     lambda r: r["lost"][0]["after"]["style"].update(letter_spacing=0),
                     lambda r: r["lost"][0]["after"].update(visible_fraction=1),
                     lambda r: r["lost"][0]["after"].update(index=2), lambda r: r.update(lost=[1])]
        for mutate in mutations:
            rec = record()
            mutate(rec)
            with self.subTest(rec=rec):
                self.assertTrue(validate_adaptation(rec))
                self.assertEqual(checks.check_adaptation({"run_id": "R-sample-01", "adaptation": [rec]}, {"profile_id": "P"}, captures(record())), [])

    def test_unmeasured_scans_and_absent_or_wrong_capture_have_no_finding(self):
        rec = record()
        snaps = captures(rec)
        for key in ("source_snapshot_id", "baseline_snapshot_id", "snapshot_id"):
            subset = {sid: s for sid, s in snaps.items() if sid != rec[key]}
            self.assertEqual(checks.check_adaptation({"run_id": "R-sample-01", "adaptation": [rec]}, {"profile_id": "P"}, subset), [])
        snaps["S-changed"]["adaptation"]["kind"] = "short_height"
        self.assertEqual(checks.check_adaptation({"run_id": "R-sample-01", "adaptation": [rec]}, {"profile_id": "P"}, snaps), [])
        rec.update(status="unevaluable", evaluable=False, applied=False, gaps=["styles_incomplete"], lost=[])
        self.assertEqual(validate_adaptation(rec), [])

    def test_loss_tolerance_does_not_hide_a_word_in_a_large_text_range(self):
        rec = record()
        before, after = (rec["lost"][0][k] for k in ("before", "after"))
        before.update(area=100000, visible_area=100000, visible_fraction=1)
        after.update(area=100000, visible_area=99999, visible_fraction=.99999)
        self.assertEqual(validate_adaptation(rec), [])
        self.assertTrue(checks.check_adaptation({"run_id": "R-sample-01", "adaptation": [rec]}, {"profile_id": "P"}, captures(rec)))

    def test_already_short_baseline_is_inapplicable(self):
        rec = record("short_height")
        rec.update(baseline_viewport_css=[360, 256], viewport_css=[360, 256], status="inapplicable",
                   applied=False, evaluable=False, evaluated_elements=0, baseline_snapshot_id=None, snapshot_id=None,
                   gaps=["baseline_already_short"], lost=[])
        self.assertEqual(validate_adaptation(rec), [])
        rec["baseline_viewport_css"] = [360, 500]
        self.assertTrue(validate_adaptation(rec))

    def test_auxiliary_captures_are_verified_and_excluded_from_live_checks(self):
        rec = record()
        source_dir = FIXTURES / "sample_run"
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            run = load("sample_run/run.json")
            run["adaptation"] = [rec]
            snaps = {s["snapshot_id"]: s for s in [json.loads(p.read_text()) for p in source_dir.glob("S-*.json")]}
            snaps.update(captures(rec))
            for snap in snaps.values():
                name = snap["screenshot"]["path"]
                png.write_png(directory / name, png.new_image(snap["screenshot"]["width_px"], snap["screenshot"]["height_px"], 3, (250, 250, 250)))
                snap["screenshot"]["sha256"] = sha256_file(directory / name)
                (directory / f"{snap['snapshot_id']}.json").write_text(json.dumps(snap))
            (directory / "run.json").write_text(json.dumps(run))
            profile = load("sample_profile.json")
            seen: list[tuple[str, str | None]] = []
            timing_maps: list[set[str]] = []

            def inspect(ctx):
                seen.append((ctx.snapshot["snapshot_id"], ctx.previous["snapshot_id"] if ctx.previous else None))
                return []

            timing = checks.check_run_timing

            def inspect_timing(run, profile, device, snap_map, scenario):
                timing_maps.append(set(snap_map))
                return timing(run, profile, device, snap_map, scenario)

            with patch.object(checks, "run_snapshot_checks", side_effect=inspect), patch.object(checks, "check_run_timing", side_effect=inspect_timing):
                result = analyze.analyze_run(directory, [profile], gaze_enabled=False)
            self.assertEqual(seen, [("S-R-sample-01-000", None), ("S-R-sample-01-001", "S-R-sample-01-000")])
            self.assertEqual(timing_maps, [{"S-R-sample-01-000", "S-R-sample-01-001"}])
            self.assertEqual([o["snapshot_id"] for o in result["observations"] if o["check_id"] == "RF-02"], ["S-changed"])
            from ergoqa.qa_attach import _receipt_for_snapshot
            loaded_run, loaded_snaps = load_run_dir(directory)
            changed = next(s for s in loaded_snaps if s["snapshot_id"] == "S-changed")
            receipt = _receipt_for_snapshot(loaded_run, changed)
            self.assertEqual(receipt["sha256"], changed["screenshot"]["sha256"])
            changed["device"]["viewport_css"] = [320, 780]
            (directory / "S-changed.json").write_text(json.dumps(changed))
            with self.assertRaises(SnapshotError):
                load_run_dir(directory)

    def test_large_clone_cannot_change_live_flash_verdict(self):
        profile = load("sample_profile.json")
        run = load("sample_run/run.json")
        run.update(steps=[], timing_windows=[{"id": "TW-1", "selector": "#flash", "starts_ms": [0, 100, 200, 300, 400],
                                              "appearances": 5, "intervals_ms": [50] * 5}])
        live = load("sample_snapshot.json")
        live["elements"] = [el("flash", "paragraph", (0, 0, 40, 40), text="decorative", bg="#ff0000", container="#ffffff")]
        aux = copy.deepcopy(live)
        aux["snapshot_id"] = "S-aux"
        aux["device"].update(probe="adaptation", viewport_css=[360, 390])
        aux["elements"][0]["box"].update(w=360, h=300)
        with patch.object(checks, "run_snapshot_checks", return_value=[]), patch.object(checks, "check_adaptation", return_value=[]):
            with patch.object(analyze, "load_run_dir", return_value=(run, [live])):
                before = analyze.analyze_run("fixture", [profile], gaze_enabled=False)
            with patch.object(analyze, "load_run_dir", return_value=(run, [live, aux])):
                after = analyze.analyze_run("fixture", [profile], gaze_enabled=False)
        select = lambda result: [{k: o[k] for k in ("check_id", "measurement", "severity", "passed", "snapshot_id")} for o in result["observations"]]
        self.assertEqual(select(before), select(after))
        self.assertTrue(all(o["passed"] for o in after["observations"] if o["check_id"] == "GM-04"))


if __name__ == "__main__":
    unittest.main()
