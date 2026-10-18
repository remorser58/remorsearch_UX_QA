"""ergo-* document validation, run-directory loading and geometry helpers.

Screenshots are generated with ergoqa.png at test time; fixtures are authored
examples, not live captures.
"""
import copy
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

import _paths  # noqa: F401  (puts the skill folder on sys.path)
from ergoqa import png
from ergoqa.drivers.annotation import annotation_to_snapshot, validate_annotation
from ergoqa.snapshot import (SnapshotError, box_contains, box_edges, box_gap, box_overlap_area, element_by_id,
                             element_center, element_key, elements_by_role, load_document, load_run_dir,
                             parse_hex_color, parse_json, resolve_within, sha256_file, validate,
                             validate_profile, validate_run, validate_scenario, validate_snapshot)

FIXTURES = Path(__file__).parent / "fixtures" / "ergo"


def load(name):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def write_screenshot(path: Path, width=1080, height=2340):
    png.write_png(path, png.new_image(width, height, 3, (250, 250, 250)))


class ValidationTests(unittest.TestCase):
    def test_fixtures_are_valid(self):
        for name in ("sample_snapshot.json", "sample_scenario.json", "sample_profile.json", "sample_run/run.json",
                     "sample_run/S-R-sample-01-000.json", "sample_run/S-R-sample-01-001.json"):
            with self.subTest(name):
                self.assertEqual(validate(load(name)), [])

    def test_unknown_schema_and_non_objects_fail_closed(self):
        snap = load("sample_snapshot.json")
        snap["schema_version"] = "ergo-snapshot.v2"
        self.assertTrue(validate(snap))
        self.assertTrue(validate_snapshot(snap))
        self.assertTrue(validate([]))
        self.assertTrue(validate_run(load("sample_snapshot.json")))
        self.assertTrue(validate_snapshot("not a dict"))

    def assertInvalid(self, validator, doc, fragment):
        errors = validator(doc)
        self.assertTrue(any(fragment in e for e in errors), f"{fragment!r} not in {errors}")

    def test_malformed_snapshots(self):
        base = load("sample_snapshot.json")
        cases = [
            (lambda s: s["elements"][0]["box"].update(w=-1), "box.w"),
            (lambda s: s["elements"][0]["box"].update(x="16"), "box.x"),
            (lambda s: s.update(step_index=True), "step_index"),
            (lambda s: s.update(step_index=1.5), "step_index"),
            (lambda s: s["elements"][0].update(roles=["hero"]), "unknown role"),
            (lambda s: s["elements"][0].update(color_fg="red"), "color_fg"),
            (lambda s: s["elements"][0].update(source="guess"), "source"),
            (lambda s: s["elements"][0].update(interactive="yes"), "interactive"),
            (lambda s: s["elements"][1].update(id=s["elements"][0]["id"]), "duplicate element id"),
            (lambda s: s.pop("focus_point"), "focus_point"),
            (lambda s: s["screenshot"].update(path="../outside.png"), "screenshot.path"),
            (lambda s: s["screenshot"].update(path="/etc/passwd"), "screenshot.path"),
            (lambda s: s["screenshot"].update(path="C:/x.png"), "screenshot.path"),
            (lambda s: s["screenshot"].update(sha256="ABC"), "sha256"),
            (lambda s: s["screenshot"].update(width_px=0), "width_px"),
            (lambda s: s["device"].update(viewport_css=[360]), "viewport_css"),
            (lambda s: s["device"].update(orientation="sideways"), "orientation"),
            (lambda s: s["surface"].update(kind="fax"), "surface.kind"),
            (lambda s: s.update(captured_at="2026-09-28 12:00"), "captured_at"),
            (lambda s: s.update(elements={}), "elements"),
            (lambda s: s.update(notes=[1]), "notes[0]"),
        ]
        for mutate, fragment in cases:
            doc = copy.deepcopy(base)
            mutate(doc)
            with self.subTest(fragment):
                self.assertInvalid(validate_snapshot, doc, fragment)

    def test_malformed_runs(self):
        base = load("sample_run/run.json")
        cases = [
            (lambda r: r.update(status="done"), "status"),
            (lambda r: r.update(mode="auto"), "mode"),
            (lambda r: r["steps"][0].update(t_end_ms=-1), "t_end_ms"),
            (lambda r: r["steps"][0].update(t_start_ms=200), "t_end_ms"),
            (lambda r: r["steps"][0].update(result="maybe"), "result"),
            (lambda r: r["steps"][0]["action"].update(action="teleport"), "action"),
            (lambda r: r["flash_samples"][0].update(mean_luminance=1.5), "mean_luminance"),
            (lambda r: r["persona_notes"][0].update(confusion="no"), "confusion"),
            (lambda r: r.pop("steps"), "steps"),
            (lambda r: r.update(success="yes"), "success"),
        ]
        for mutate, fragment in cases:
            doc = copy.deepcopy(base)
            mutate(doc)
            with self.subTest(fragment):
                self.assertInvalid(validate_run, doc, fragment)

    def test_malformed_scenarios(self):
        base = load("sample_scenario.json")
        cases = [
            (lambda s: s["steps"].append({"action": "tap"}), "target"),
            (lambda s: s["steps"].append({"action": "wait"}), "ms"),
            (lambda s: s["steps"].append({"action": "type", "target": "#q"}), "text"),
            (lambda s: s["steps"].append({"action": "fly"}), "action"),
            (lambda s: s["steps"].append({"action": "tap", "target": "hotspot:nope"}), "unknown hotspot"),
            (lambda s: s["steps"].append({"action": "tap", "target": 42}), "target"),
            (lambda s: s["targets"].update(hero=["#x"]), "unknown role"),
            (lambda s: s.update(device_ids=[]), "device_ids"),
            (lambda s: s["surface"].pop("url"), "url"),
            (lambda s: s["hotspots"].append(copy.deepcopy(s["hotspots"][0])), "duplicate hotspot"),
        ]
        for mutate, fragment in cases:
            doc = copy.deepcopy(base)
            mutate(doc)
            with self.subTest(fragment):
                self.assertInvalid(validate_scenario, doc, fragment)

    def test_irreversible_role_is_accepted_wherever_roles_are(self):
        # docs/ergonomic-swarm-spec.md includes `irreversible` and audience
        # scenario-stubs emit targets.irreversible; the validators must accept it.
        doc = load("sample_scenario.json")
        doc["targets"]["irreversible"] = ["#pay"]
        self.assertEqual(validate_scenario(doc), [])
        doc["hotspots"].append({"id": "h-ir", "name": "탈퇴", "box": {"x": 0, "y": 0, "w": 10, "h": 10},
                                "roles": ["irreversible"]})
        self.assertEqual(validate_scenario(doc), [])
        snap = load("sample_snapshot.json")
        snap["elements"][0]["roles"] = ["irreversible"]
        self.assertEqual(validate_snapshot(snap), [])

    def test_malformed_profiles(self):
        base = load("sample_profile.json")
        cases = [
            (lambda p: p["attributes"].update(device_id="nokia-3310"), "unknown device"),
            (lambda p: p["attributes"].update(grip="claw"), "grip"),
            (lambda p: p["attributes"]["vision"].update(cvd_severity=2), "cvd_severity"),
            (lambda p: p["attributes"]["context"].update(free_hands=3), "free_hands"),
            (lambda p: p.update(origin="survey"), "origin"),
            (lambda p: p.update(persona_ref={"dataset": "x"}), "persona_ref.revision"),
        ]
        for mutate, fragment in cases:
            doc = copy.deepcopy(base)
            mutate(doc)
            with self.subTest(fragment):
                self.assertInvalid(validate_profile, doc, fragment)

    def test_strict_json(self):
        with self.assertRaisesRegex(SnapshotError, "duplicate"):
            parse_json('{"a": 1, "a": 2}')
        with self.assertRaisesRegex(SnapshotError, "non-finite"):
            parse_json('{"a": NaN}')
        with self.assertRaisesRegex(SnapshotError, "invalid JSON"):
            parse_json("{")


class RunDirTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.run_dir = Path(self.tmp.name) / "R-sample-01"
        shutil.copytree(FIXTURES / "sample_run", self.run_dir)
        for name in ("S-R-sample-01-000.png", "S-R-sample-01-001.png"):
            write_screenshot(self.run_dir / name)

    def edit(self, name, mutate):
        path = self.run_dir / name
        doc = json.loads(path.read_text(encoding="utf-8"))
        mutate(doc)
        path.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")

    def test_loads_sorted_snapshots_with_resolved_paths(self):
        run, snaps = load_run_dir(self.run_dir)
        self.assertEqual(run["run_id"], "R-sample-01")
        self.assertEqual([s["snapshot_id"] for s in snaps], ["S-R-sample-01-000", "S-R-sample-01-001"])
        for snap in snaps:
            resolved = Path(snap["screenshot"]["resolved_path"])
            self.assertTrue(resolved.is_file())
            self.assertEqual(resolved.parent, self.run_dir.resolve())

    def test_sha256_is_verified(self):
        good = sha256_file(self.run_dir / "S-R-sample-01-000.png")
        self.edit("S-R-sample-01-000.json", lambda s: s["screenshot"].update(sha256=good))
        load_run_dir(self.run_dir)
        self.edit("S-R-sample-01-000.json", lambda s: s["screenshot"].update(sha256="0" * 64))
        with self.assertRaisesRegex(SnapshotError, "SHA-256"):
            load_run_dir(self.run_dir)

    def test_missing_and_mismatched_screenshots(self):
        (self.run_dir / "S-R-sample-01-001.png").unlink()
        with self.assertRaisesRegex(SnapshotError, "not found"):
            load_run_dir(self.run_dir)
        run, snaps = load_run_dir(self.run_dir, verify_screenshots=False)
        self.assertEqual(len(snaps), 2)
        write_screenshot(self.run_dir / "S-R-sample-01-001.png", 540, 1170)
        with self.assertRaisesRegex(SnapshotError, "540x1170"):
            load_run_dir(self.run_dir)
        (self.run_dir / "S-R-sample-01-001.png").write_bytes(b"not a png")
        with self.assertRaisesRegex(SnapshotError, "readable PNG"):
            load_run_dir(self.run_dir)

    def test_path_traversal_and_symlinks_are_rejected(self):
        outside = Path(self.tmp.name) / "outside.png"
        write_screenshot(outside)
        self.edit("S-R-sample-01-000.json", lambda s: s["screenshot"].update(path="../outside.png"))
        with self.assertRaisesRegex(SnapshotError, "screenshot.path"):
            load_run_dir(self.run_dir)
        self.edit("S-R-sample-01-000.json", lambda s: s["screenshot"].update(path="link.png"))
        os.symlink(outside, self.run_dir / "link.png")
        with self.assertRaisesRegex(SnapshotError, "symlink"):
            load_run_dir(self.run_dir)
        with self.assertRaises(SnapshotError):
            resolve_within(self.run_dir, "a/../../x.png")

    def test_cross_run_and_dangling_references(self):
        self.edit("S-R-sample-01-001.json", lambda s: s.update(run_id="R-other"))
        with self.assertRaisesRegex(SnapshotError, "run_id"):
            load_run_dir(self.run_dir)
        self.edit("S-R-sample-01-001.json", lambda s: s.update(run_id="R-sample-01"))
        self.edit("run.json", lambda r: r["steps"][0].update(after="S-R-sample-01-009"))
        with self.assertRaisesRegex(SnapshotError, "missing snapshot"):
            load_run_dir(self.run_dir)

    def test_invalid_documents_fail_to_load(self):
        self.edit("run.json", lambda r: r.update(schema_version="ergo-run.v0"))
        with self.assertRaisesRegex(SnapshotError, "expected ergo-run.v1"):
            load_run_dir(self.run_dir)
        with self.assertRaises(SnapshotError):
            load_run_dir(Path(self.tmp.name) / "missing")
        with self.assertRaises(SnapshotError):
            load_document(FIXTURES / "sample_run" / "run.json", "ergo-snapshot.v1")


class GeometryTests(unittest.TestCase):
    def test_box_helpers(self):
        a = {"x": 0, "y": 0, "w": 10, "h": 10}
        self.assertEqual(box_edges(a), (0, 0, 10, 10))
        self.assertEqual(element_center({"box": a}), (5, 5))
        self.assertEqual(box_gap(a, {"x": 5, "y": 5, "w": 10, "h": 10}), 0)  # overlap
        self.assertEqual(box_gap(a, {"x": 10, "y": 0, "w": 5, "h": 5}), 0)  # touching
        self.assertEqual(box_gap(a, {"x": 14, "y": 2, "w": 5, "h": 5}), 4)  # horizontal
        self.assertEqual(box_gap(a, {"x": 0, "y": -8, "w": 5, "h": 5}), 3)  # vertical, above
        self.assertEqual(box_gap(a, (13, 14, 1, 1)), 5)  # diagonal 3-4-5
        self.assertEqual(box_gap({"box": a}, {"box": (13, 14, 1, 1)}), 5)
        self.assertEqual(box_overlap_area(a, (5, 5, 10, 10)), 25)
        self.assertTrue(box_contains(a, 10, 10))
        self.assertFalse(box_contains(a, 10.1, 5))
        with self.assertRaises(TypeError):
            box_gap(a, "box")

    def test_element_lookup(self):
        snap = load("sample_snapshot.json")
        self.assertEqual([e["id"] for e in elements_by_role(snap, "primary")], ["el-12"])
        self.assertEqual([e["id"] for e in elements_by_role(snap, "critical_message")], ["el-13"])
        self.assertEqual([e["id"] for e in elements_by_role(snap, "alert", field="role")], ["el-13"])
        self.assertEqual(elements_by_role(snap, "hud"), [])
        self.assertEqual(element_by_id(snap, "el-12")["name"], "결제하기")
        self.assertEqual(element_key(element_by_id(snap, "el-12")), "#pay|결제하기")
        with self.assertRaises(ValueError):
            elements_by_role(snap, "primary", field="tag")

    def test_parse_hex_color(self):
        self.assertEqual(parse_hex_color("#1a73e8"), (26, 115, 232))
        self.assertEqual(parse_hex_color("#fff"), (255, 255, 255))
        self.assertEqual(parse_hex_color("#00000080"), (0, 0, 0, 128))
        with self.assertRaises(ValueError):
            parse_hex_color("rgb(0,0,0)")


class AnnotationDriverTests(unittest.TestCase):
    def test_annotation_without_file(self):
        snap = annotation_to_snapshot(load("sample_annotation.json"), run_id="R-vision", captured_at="2026-09-28T00:00:00Z")
        self.assertEqual(validate_snapshot(snap), [])
        self.assertTrue(all(e["source"] == "vision" for e in snap["elements"]))
        self.assertTrue(any("estimated" in n for n in snap["notes"]))
        self.assertTrue(any("not verified" in n for n in snap["notes"]))
        self.assertEqual(snap["geometry_basis"], "estimated")
        self.assertEqual(snap["surface"]["kind"], "game")
        self.assertEqual((snap["screenshot"]["width_px"], snap["screenshot"]["height_px"]), (1080, 2340))
        jump = snap["elements"][1]
        self.assertEqual(jump["box"], {"x": 300.0, "y": 600.0, "w": 64.0, "h": 64.0})
        self.assertTrue(jump["interactive"])
        self.assertFalse(snap["elements"][2]["interactive"])  # role "status" is not interactive by default
        self.assertEqual(snap["elements"][0]["roles"], ["primary"])

    def test_annotation_with_verified_file_and_px_boxes(self):
        ann = load("sample_annotation.json")
        ann["box_units"] = "screenshot_px"
        ann["elements"][0]["box"] = {"x": 48, "y": 2100, "w": 984, "h": 144}
        with tempfile.TemporaryDirectory() as tmp:
            write_screenshot(Path(tmp) / "annotated.png")
            snap = annotation_to_snapshot(ann, base_dir=tmp)
            self.assertEqual(snap["screenshot"]["sha256"], sha256_file(Path(tmp) / "annotated.png"))
            self.assertEqual(snap["elements"][0]["box"], {"x": 16.0, "y": 700.0, "w": 328.0, "h": 48.0})
            ann["screenshot"] = "../annotated.png"
            with self.assertRaises(SnapshotError):
                annotation_to_snapshot(ann, base_dir=tmp)
            ann["screenshot"] = "missing.png"
            with self.assertRaisesRegex(SnapshotError, "not found"):
                annotation_to_snapshot(ann, base_dir=tmp)

    def test_invalid_annotations(self):
        base = load("sample_annotation.json")
        cases = [
            (lambda a: a.update(device_id="nokia"), "device_id"),
            (lambda a: a.update(viewport_css=[0, 1]), "viewport_css"),
            (lambda a: a["elements"][0].update(roles=["hero"]), "roles"),
            (lambda a: a["elements"][0].update(box=[1, 2, 3]), "box"),
            (lambda a: a["elements"][0].update(color_fg="blue"), "color_fg"),
            (lambda a: a.update(screenshot="/abs.png"), "screenshot"),
            (lambda a: a.update(box_units="mm"), "box_units"),
        ]
        for mutate, fragment in cases:
            ann = copy.deepcopy(base)
            mutate(ann)
            with self.subTest(fragment):
                self.assertTrue(any(fragment in e for e in validate_annotation(ann)))
                with self.assertRaises(SnapshotError):
                    annotation_to_snapshot(ann)


if __name__ == "__main__":
    unittest.main()
