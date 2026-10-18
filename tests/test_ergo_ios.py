"""Focused XCUITest import trust-boundary checks."""
from __future__ import annotations

import hashlib
import io
import json
import plistlib
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timezone
from pathlib import Path

import _paths  # noqa: F401
from ergoqa import cli, png
from ergoqa.profiles import sample_profiles
from ergoqa.snapshot import load_run_dir, validate_snapshot

CAPTURE_ID = "0F0D3F3C-2F6F-4F2F-9F2F-0F0F0F0F0F0F"
SECOND_CAPTURE_ID = "3D3D5F5F-7B7B-4D4D-8E8E-2A3B4C5D6E7F"
START = datetime(2026, 1, 1, 12, tzinfo=timezone.utc)


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def make_evidence(root: Path) -> Path:
    evidence = root / "evidence"
    shots = evidence / "screenshots"
    shots.mkdir(parents=True)
    png.write_png(shots / "shot", png.new_image(1179, 2556, 3, (255, 255, 255)))
    capture = {
        "schema_version": "xcuitest-capture.v1", "capture_id": CAPTURE_ID,
        "capture_name": "release surface", "png_attachment_name": f"rq-native-{CAPTURE_ID}.png",
        "application_id": "com.example.product", "application_id_source": "test-target-configuration",
        "captured_at_start": "2026-01-01T12:00:10Z", "captured_at_end": "2026-01-01T12:00:11Z",
        "image_source": "device_screen",
        "viewport": {"x": 0, "y": 0, "width": 393, "height": 852},
        "image": {"width_px": 1179, "height_px": 2556, "scale": 3},
        "elements": [
            {"id": "xcui-1", "type": "XCUIElementType(rawValue: 2)", "identifier": "", "label": "Product", "enabled": True,
             "frame": {"x": 0, "y": 0, "width": 393, "height": 852}},
            {"id": "xcui-2", "parent_id": "xcui-1", "type": "XCUIElementType(rawValue: 9)", "identifier": "save", "label": "저장",
             "enabled": True, "frame": {"x": -50, "y": 700, "width": 44, "height": 44}},
            {"id": "xcui-3", "parent_id": "xcui-1", "type": "XCUIElementType(rawValue: 75)", "identifier": "cell", "label": "항목",
             "enabled": True, "frame": {"x": 20, "y": 120, "width": 0, "height": 40}},
        ],
    }
    write_json(shots / "typed", capture)
    second_capture = dict(capture, capture_id=SECOND_CAPTURE_ID,
                          png_attachment_name=f"rq-native-{SECOND_CAPTURE_ID}.png")
    write_json(shots / "typed2", second_capture)
    (shots / "shot2").write_bytes((shots / "shot").read_bytes())
    device = {"deviceId": "SIM", "deviceName": "iPhone 15", "modelName": "iPhone 15", "osVersion": "18.0", "platform": "iOS Simulator"}
    attachments = [
        {"suggestedHumanReadableName": f"rq-native-{CAPTURE_ID}_0_UUID.json", "exportedFileName": "typed",
         "timestamp": START.timestamp() + 11.2, **device},
        {"suggestedHumanReadableName": f"rq-native-{CAPTURE_ID}_0_UUID.png", "exportedFileName": "shot",
         "timestamp": START.timestamp() + 11.3, **device},
        {"suggestedHumanReadableName": f"rq-native-{SECOND_CAPTURE_ID}_0_UUID.json", "exportedFileName": "typed2",
         "timestamp": START.timestamp() + 11.4, **device},
        {"suggestedHumanReadableName": f"rq-native-{SECOND_CAPTURE_ID}_0_UUID.png", "exportedFileName": "shot2",
         "timestamp": START.timestamp() + 11.5, **device},
    ]
    write_json(shots / "manifest.json", [{"testIdentifier": "SurfaceTests/testSurface()", "attachments": attachments}])
    summary = {"devicesAndConfigurations": [{"device": device, "failedTests": 1, "passedTests": 0, "skippedTests": 0}],
               "failedTests": 1, "passedTests": 0, "skippedTests": 0, "result": "Failed",
               "startTime": START.timestamp(), "finishTime": START.timestamp() + 60}
    write_json(evidence / "test-summary.json", summary)
    case = {"nodeType": "Test Case", "name": "testSurface()", "nodeIdentifier": "SurfaceTests/testSurface()", "result": "Failed"}
    write_json(evidence / "test-results.json", {"devices": [device], "testNodes": [{"children": [{"children": [case]}]}]})
    (evidence / "DerivedData" / "Product.app").mkdir(parents=True)
    with (evidence / "DerivedData" / "Product.app" / "Info.plist").open("wb") as stream:
        plistlib.dump({"CFBundleIdentifier": "com.example.product", "CFBundleShortVersionString": "1.0", "CFBundleVersion": "1"}, stream)
    (evidence / "Result.xcresult").mkdir()
    with (evidence / "Result.xcresult" / "Info.plist").open("wb") as stream:
        plistlib.dump({"rootId": {"hash": "result-root"}}, stream)
    (evidence / "metadata.txt").write_text("xcode_version=Xcode 26.0\n", encoding="utf-8")
    (evidence / "fixture-origin.txt").write_text("synthetic://fixture\n", encoding="utf-8")
    hashed = [shots / "manifest.json", shots / "typed", shots / "shot", shots / "typed2", shots / "shot2",
              evidence / "test-summary.json", evidence / "test-results.json", evidence / "DerivedData" / "Product.app" / "Info.plist",
              evidence / "Result.xcresult" / "Info.plist", evidence / "metadata.txt", evidence / "fixture-origin.txt"]
    ledger = "".join(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.resolve()}\n" for path in hashed)
    (evidence / "artifact-sha256.txt").write_text(ledger, encoding="utf-8")
    return evidence


class IOSImportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.evidence = make_evidence(self.root)

    def cli(self, *argv: str):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = cli.main(list(argv))
        return code, out.getvalue(), err.getvalue()

    def import_args(self, out: Path, **overrides: str):
        values = {"evidence": str(self.evidence), "out": str(out), "device": "iphone-15", "scenario_id": "SC-ios",
                  "profile_id": "EP-ios", "capture_id": CAPTURE_ID.upper(), "route": "/release",
                  "fixture_id": "fixture-1", "fixture_kind": "synthetic_app_data"}
        values.update(overrides)
        args = ["ios-import"]
        args.extend(arg for key, value in values.items() for arg in ("--" + key.replace("_", "-"), value))
        return args

    def test_actual_shaped_triplet_imports_and_analysis_stays_conservative(self):
        runs = self.root / "runs"
        profiles = sample_profiles(1, 7, ["iphone-15"])
        profiles_path = self.root / "profiles.json"
        write_json(profiles_path, {"profiles": profiles})
        code, _, err = self.cli(*self.import_args(runs, profile_id=profiles[0]["profile_id"]))
        self.assertEqual(code, cli.EXIT_OK, err)
        run_dir = next(child for child in runs.iterdir() if (child / "run.json").is_file())
        run, snapshots = load_run_dir(run_dir)
        self.assertEqual(len(snapshots), 1)
        self.assertEqual(snapshots[0]["ios_source"]["capture_id"], CAPTURE_ID)
        self.assertEqual(snapshots[0]["ios_source"]["image_source"], "device_screen")
        self.assertNotIn("console_errors", snapshots[0])
        second_runs = self.root / "runs-second"
        code, _, err = self.cli(*self.import_args(second_runs, profile_id=profiles[0]["profile_id"], capture_id=SECOND_CAPTURE_ID))
        self.assertEqual(code, cli.EXIT_OK, err)
        second_run_dir = next(child for child in second_runs.iterdir() if (child / "run.json").is_file())
        second_run, second_snapshots = load_run_dir(second_run_dir)
        self.assertNotEqual(run["run_id"], second_run["run_id"])
        self.assertNotEqual(snapshots[0]["snapshot_id"], second_snapshots[0]["snapshot_id"])
        self.assertEqual((run["status"], run["success"]), ("completed", None))
        self.assertEqual(run["ios_import"]["test"]["result"], "fail")
        self.assertTrue(run["ios_import"]["selected_capture_only"])
        self.assertEqual(run["ios_import"]["route"], "/release")
        button = snapshots[0]["elements"][1]
        self.assertEqual((button["box"]["x"], button["in_viewport"]), (-50.0, False))
        cell = snapshots[0]["elements"][2]
        self.assertEqual((cell["role"], cell["interactive"], cell["box"]["w"]), ("row", False, 0.0))
        self.assertFalse(cell["in_viewport"])
        self.assertEqual((cell["visible"], cell["visible_geometry"]), (None, "unsupported"))
        self.assertTrue(all(element["font_size_px"] is None and element["color_fg"] is None for element in snapshots[0]["elements"]))
        analysis = self.root / "analysis.json"
        code, _, err = self.cli("analyze", "--runs", str(run_dir), "--profiles", str(profiles_path), "--no-gaze", "--out", str(analysis))
        self.assertEqual(code, cli.EXIT_OK, err)
        result = json.loads(analysis.read_text())["analyses"][0]
        self.assertEqual(result["health"], "degraded")
        self.assertEqual(run["steps"], [])
        self.assertTrue(any("화면 표시 여부를 측정하지 않았습니다" in limitation for limitation in result["limitations"]))
        invalid = json.loads((run_dir / (snapshots[0]["snapshot_id"] + ".json")).read_text())
        invalid["elements"][1]["visible_geometry"] = "measured"
        invalid["elements"][1]["visible_box"] = invalid["elements"][1]["box"]
        problems = validate_snapshot(invalid)
        self.assertIn("$.elements[1].visible: may be null only when visible_geometry is unsupported and visible_box is null", problems)

        typed_path = self.evidence / "screenshots" / "typed"
        typed_doc = json.loads(typed_path.read_text())
        typed_doc.pop("image_source")
        write_json(typed_path, typed_doc)
        ledger_path = self.evidence / "artifact-sha256.txt"
        ledger_path.write_text(
            ledger_path.read_text().replace(
                next(line for line in ledger_path.read_text().splitlines() if line.endswith(str(typed_path.resolve()))),
                f"{hashlib.sha256(typed_path.read_bytes()).hexdigest()}  {typed_path.resolve()}",
            ) + "\n",
            encoding="utf-8",
        )
        application_runs = self.root / "runs-application"
        code, _, err = self.cli(*self.import_args(application_runs, profile_id=profiles[0]["profile_id"]))
        self.assertEqual(code, cli.EXIT_OK, err)
        application_run = next(child for child in application_runs.iterdir() if (child / "run.json").is_file())
        _, application_snapshots = load_run_dir(application_run)
        self.assertEqual(application_snapshots[0]["ios_source"]["image_source"], "application")

    def test_join_or_measurement_forgery_is_rejected(self):
        typed = self.evidence / "screenshots" / "typed"
        manifest = self.evidence / "screenshots" / "manifest.json"
        shot = self.evidence / "screenshots" / "shot"
        summary = self.evidence / "test-summary.json"
        results = self.evidence / "test-results.json"
        ledger = self.evidence / "artifact-sha256.txt"
        originals = {path: path.read_bytes() for path in (typed, manifest, shot, summary, results, ledger)}

        def restore():
            for path, data in originals.items():
                path.write_bytes(data)

        def edit(path, changer):
            doc = json.loads(path.read_text())
            changer(doc)
            write_json(path, doc)

        def rehash(path):
            lines = ledger.read_text(encoding="utf-8").splitlines()
            target = str(path.resolve())
            updated = [(hashlib.sha256(path.read_bytes()).hexdigest() + "  " + target) if line.endswith(target) else line
                       for line in lines]
            ledger.write_text("\n".join(updated) + "\n", encoding="utf-8")

        cases = {
            "ambiguous test": lambda: (edit(results, lambda d: d["testNodes"][0]["children"][0]["children"].append(dict(d["testNodes"][0]["children"][0]["children"][0]))), rehash(results)),
            "rebound capture": lambda: (edit(typed, lambda d: d.update(capture_id=SECOND_CAPTURE_ID, png_attachment_name=f"rq-native-{SECOND_CAPTURE_ID}.png")),
                                        rehash(typed)),
            "stale summary": lambda: edit(summary, lambda d: d.update(finishTime=d["finishTime"] + 1)),
            "stale results": lambda: edit(results, lambda d: d["testNodes"][0]["children"][0]["children"][0].update(name="forged()")),
            "cross build": lambda: (edit(typed, lambda d: d.update(application_id="com.other.product")), rehash(typed)),
            "bad image source": lambda: (edit(typed, lambda d: d.update(image_source="rescaled")), rehash(typed)),
            "exact pro model": lambda: (edit(summary, lambda d: d["devicesAndConfigurations"][0]["device"].update(modelName="iPhone 15 Pro")),
                                        edit(results, lambda d: d["devices"][0].update(modelName="iPhone 15 Pro")), rehash(summary), rehash(results)),
            "path escape": lambda: (edit(manifest, lambda d: d[0]["attachments"][1].update(exportedFileName="../shot")), rehash(manifest)),
            "png mismatch": lambda: (edit(typed, lambda d: d["image"].update(height_px=2555)), rehash(typed)),
            "invalid dpr": lambda: (edit(typed, lambda d: d["image"].update(scale=2.625)), rehash(typed)),
            "nearest device": lambda: None,
        }
        for name, mutate in cases.items():
            with self.subTest(name):
                mutate()
                code, _, err = self.cli(*self.import_args(self.root / ("reject-" + name.replace(" ", "-")), device="iphone-15-pro-max" if name == "nearest device" else "iphone-15"))
                self.assertEqual(code, cli.EXIT_USAGE, err)
                restore()
        typed.write_text(originals[typed].decode().replace('"width": 393', '"width": 1e999'), encoding="utf-8")
        code, _, err = self.cli(*self.import_args(self.root / "reject-geometry"))
        self.assertEqual(code, cli.EXIT_USAGE, err)
        restore()
        shot.write_bytes(originals[shot] + b"x")
        code, _, err = self.cli(*self.import_args(self.root / "reject-hash"))
        self.assertEqual(code, cli.EXIT_USAGE, err)
        restore()


if __name__ == "__main__":
    unittest.main()
