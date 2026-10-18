"""End-to-end offline pipeline: recorded run -> analyze -> swarm -> bundle/report/bench."""

from __future__ import annotations

import copy
import io
import json
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from _paths import SKILL as ROOT  # noqa: E402,F401  (puts the skill folder on sys.path)

from ergoqa import analyze, bench, bundle, png, report, swarm  # noqa: E402
from ergoqa.profiles import sample_profiles  # noqa: E402
from ergoqa.snapshot import sha256_file  # noqa: E402
from validate_bundle import validate_bundle  # noqa: E402

W, H = 360, 780


def el(eid, role, box, *, name="", text="", selector=None, interactive=False, roles=(), fg="#111111", bg="#ffffff",
       size=16, weight=400, tag="div", border=None):
    return {
        "id": eid, "role": role, "name": name, "text": text, "tag": tag, "selector": selector or f"#{eid}",
        "box": dict(zip("xywh", box)), "interactive": interactive, "visible": True, "enabled": True, "in_viewport": True,
        "font_size_px": size, "font_weight": weight, "color_fg": fg, "color_bg": bg, "border_color": border,
        "roles": list(roles), "source": "dom",
    }


def base_elements():
    options = [
        el(f"opt-{i}", "button", (10 + (i % 4) * 86, 420 + (i // 4) * 50, 80, 44), name=f"옵션 {i}", text=f"옵션 {i}",
           interactive=True, tag="button", bg="#eeeeee")
        for i in range(12)
    ]
    return [
        el("title", "heading", (16, 70, 200, 28), text="주문 확인", size=20, weight=700),
        el("pay", "button", (10, 250, 90, 44), name="결제하기", text="결제하기", interactive=True, roles=("primary",),
           fg="#ffffff", bg="#1a73e8", tag="button", weight=700),
        el("delete", "button", (102, 250, 90, 44), name="전체 삭제", text="전체 삭제", interactive=True,
           roles=("destructive",), fg="#ffffff", bg="#d93025", tag="button"),
        el("close", "button", (336, 8, 16, 16), name="닫기", interactive=True, tag="button"),
        el("help", "button", (316, 8, 16, 16), name="도움말", interactive=True, tag="button"),
        el("hint", "text", (16, 310, 300, 14), text="배송은 영업일 기준 2~3일 소요됩니다.", size=11, fg="#9e9e9e"),
        el("dot-ok", "status", (16, 360, 12, 12), fg="#111111", bg="#388e3c"),
        el("dot-bad", "status", (36, 360, 12, 12), fg="#111111", bg="#d32f2f"),
        *options,
    ]


def write_png(path: Path) -> str:
    image = png.new_image(W, H, 3, (255, 255, 255))
    data = bytearray(image.data)
    for y in range(250, 294):
        for x in range(10, 100):
            i = (y * W + x) * 3
            data[i:i + 3] = bytes((26, 115, 232))
    png.write_png(path, png.make_image(W, H, 3, bytes(data)))
    return sha256_file(path)


def make_run(root: Path) -> Path:
    run_dir = root / "R-1"
    run_dir.mkdir()
    snaps = []
    for index in range(2):
        sid = f"S-R-1-{index:03d}"
        sha = write_png(run_dir / f"{sid}.png")
        elements = base_elements()
        if index == 1:
            elements.append(el("error", "alert", (16, 740, 200, 16), text="카드 정보를 확인해 주세요", size=12,
                               fg="#b3261e", roles=("error_message",)))
        snaps.append({
            "schema_version": "ergo-snapshot.v1", "snapshot_id": sid, "run_id": "R-1", "step_index": index,
            "captured_at": "2026-09-28T12:00:00Z",
            "surface": {"kind": "web", "url": "http://127.0.0.1/checkout.html", "title": "checkout", "app_id": None},
            "device": {"id": "galaxy-s24", "viewport_css": [W, H], "dpr": 1.0, "orientation": "portrait"},
            "screenshot": {"path": f"{sid}.png", "sha256": sha, "width_px": W, "height_px": H},
            "elements": elements,
            "focus_point": None if index == 0 else {"x": 55, "y": 272},
            "console_errors": [], "notes": [],
        })
    for snap in snaps:
        (run_dir / f"{snap['snapshot_id']}.json").write_text(json.dumps(snap, ensure_ascii=False), encoding="utf-8")
    run = {
        "schema_version": "ergo-run.v1", "run_id": "R-1", "scenario_id": "SC-checkout", "profile_id": "EP-01",
        "driver": {"name": "test-fixture", "version": "0", "browser": None},
        "device": {"id": "galaxy-s24", "viewport_css": [W, H], "dpr": 1.0, "orientation": "portrait"},
        "mode": "scripted", "started_at": "2026-09-28T12:00:00Z", "ended_at": "2026-09-28T12:00:05Z",
        "status": "completed", "success": True,
        "steps": [{
            "step_index": 1, "action": {"action": "tap", "target": "#pay"}, "target_element_id": "pay",
            "point": {"x": 55, "y": 272}, "before": "S-R-1-000", "after": "S-R-1-001", "t_start_ms": 100,
            "t_end_ms": 180, "feedback_latency_ms": 1500, "result": "ok", "error": None,
        }],
        "timing_windows": [{"id": "toast-1", "selector": "#toast", "kind": "transient_text", "visible_ms": 1500,
                            "text": "쿠폰이 적용되었습니다. 결제 금액과 배송 예정일을 다시 한 번 확인해 주세요."}],
        "persona_notes": [{"step_index": 1, "intent": "결제", "expected": "결제 진행", "observed": "아래에 오류가 떠서 못 봄", "confusion": True}],
    }
    (run_dir / "run.json").write_text(json.dumps(run, ensure_ascii=False), encoding="utf-8")
    return run_dir


class PipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.tmp.name)
        cls.run_dir = make_run(cls.root)
        cls.profiles = sample_profiles(14, 3, ["galaxy-s24"])
        cls.analysis = analyze.analyze_run(cls.run_dir, cls.profiles, None, cross_profile=True)
        cls.findings = swarm.aggregate([cls.analysis], cls.profiles)
        cls.by_check = {}
        for f in cls.findings:
            cls.by_check.setdefault(f["check_id"], []).append(f)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def find(self, check_id, selector):
        return [f for f in self.by_check.get(check_id, []) if f["element_key"].startswith(selector + "|") or selector in f.get("selectors", [])]

    def test_all_profiles_evaluated(self) -> None:
        self.assertEqual(len(self.analysis["profiles_evaluated"]), 14)

    def test_reach_is_right_one_hand_specific(self) -> None:
        found = self.find("RH-01", "#pay")
        self.assertTrue(found)
        self.assertEqual(found[0]["profile_specific"].get("grip"), "one_hand_right")
        self.assertEqual(found[0]["epistemic_status"], "inferred")
        self.assertIn(found[0]["severity"], ("P2", "P3"))

    def test_destructive_neighbour(self) -> None:
        found = self.find("PT-03", "#delete")
        self.assertTrue(found)
        self.assertIn(found[0]["severity"], ("P1", "P2", "P3"))

    def test_small_crowded_icons(self) -> None:
        self.assertTrue(self.find("PT-01", "#close"))
        self.assertEqual(self.find("PT-01", "#close")[0]["epistemic_status"], "observed")

    def test_contrast_and_text_size(self) -> None:
        self.assertTrue(self.find("PC-01", "#hint"))
        size = self.find("PC-04", "#hint")
        self.assertTrue(size)
        # 11 px on a Galaxy S24 at 30 cm is ~23 arcmin: above the 16' floor, below the
        # Hangul critical print size (24.6'), so it is a P3 comfort finding for everyone.
        self.assertEqual(size[0]["severity"], "P3")
        self.assertEqual(size[0]["measurement"]["tier"], "critical_print_size")

    def test_colour_only_is_cvd_specific(self) -> None:
        found = self.by_check.get("PC-03", [])
        self.assertTrue(found)
        for f in found:
            for pid in f["triggered_profiles"]:
                profile = next(p for p in self.profiles if p["profile_id"] == pid)
                self.assertNotEqual(profile["attributes"]["vision"]["cvd"], "none")

    def test_choice_overload_latency_toast_and_note(self) -> None:
        self.assertTrue(self.by_check.get("CG-01"))
        self.assertTrue(self.by_check.get("CG-03"))
        self.assertTrue(self.by_check.get("CG-02"))
        notes = self.by_check.get("PJ-01", [])
        self.assertTrue(notes)
        self.assertEqual(notes[0]["triggered_profiles"], ["EP-01"])
        self.assertEqual(notes[0]["basis"], "judgment")

    def test_feedback_far_from_touch(self) -> None:
        self.assertTrue(self.find("GZ-02", "#error"))

    def test_coverage_label_is_not_prevalence(self) -> None:
        for f in self.findings:
            self.assertIn("coverage, not prevalence", f["coverage_label"])

    def test_bundle_validates(self) -> None:
        doc = bundle.to_evidence_bundle("ergo-test", [self.analysis], self.findings, self.profiles, seed=3)
        self.assertEqual(validate_bundle(doc), [])
        verified = [f for f in doc["records"]["findings"] if f["verification_status"] == "verified"]
        self.assertTrue(verified)
        obs = {o["id"]: o for o in doc["records"]["observations"]}
        for f in verified:
            self.assertTrue(all(obs[o]["basis"] == "measured" for o in f["observation_ids"]))
        inferred = [f for f in doc["records"]["findings"] if f["check_id"] == "RH-01"]
        self.assertTrue(all(f["verification_status"] == "unverified" for f in inferred))

    def test_report_renders_korean(self) -> None:
        text = report.render(self.findings, self.profiles, [self.analysis])
        self.assertIn("커버리지", text)
        self.assertIn("RH-01", text)

    def test_bench_scoring(self) -> None:
        key = {
            "suite": "unit",
            "defects": [
                {"id": "D-1", "scenario_id": "SC-checkout", "category": "reach", "element_selector": "#pay",
                 "profile_condition": {"grip": "one_hand_right"}, "severity_min": "P3"},
                {"id": "D-2", "scenario_id": "SC-checkout", "category": "perception", "element_selector": "#hint", "profile_condition": {}, "severity_min": "P2"},
                {"id": "D-3", "scenario_id": "SC-checkout", "category": "gaze", "element_selector": "#nothing", "profile_condition": {}, "severity_min": "P3"},
            ],
            "decoys": [{"id": "N-1", "scenario_id": "SC-checkout", "category": "pointing", "element_selector": "#title"}],
            "clean_controls": [],
        }
        result = bench.score(key, self.findings, self.profiles)
        self.assertAlmostEqual(result["recall_strict"], 2 / 3, places=3)
        self.assertEqual(result["decoys_flagged"], 0)


class AttachBridgeTests(unittest.TestCase):
    """The persona-qa <-> ergonomics bridge: attach a completed run to a QA bundle."""

    SECOND_PASS = {"reviewer": "self", "task_completed": True, "control_name": "결제하기", "omitted": [],
                   "severity": "agree", "inconclusive": False}

    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.tmp.name)
        cls.run_dir = make_run(cls.root)
        cls.profiles = sample_profiles(3, 7, ["galaxy-s24"])
        qa = json.loads((Path(__file__).parent / "fixtures" / "valid-bundle.json").read_text(encoding="utf-8"))
        # An existing QA graph whose findings carry no P0/P1 (those would need their
        # own fresh receipts and second passes under the same validator).
        qa["records"]["findings"][0]["severity"] = "P2"
        cls.qa_bundle = qa
        cls.receipts = cls.root / "receipts"
        # Owned synthetic fixture metadata is distinct from screenshot bytes.
        for path in [cls.run_dir / "run.json", *cls.run_dir.glob("S-*.json")]:
            doc = json.loads(path.read_text())
            doc.setdefault("surface", {})["build_id"] = "synthetic-checkout-fixture-v1"
            path.write_text(json.dumps(doc))
        cls.reviews = {}
        for cross in (False, True):
            analysis = analyze.analyze_run(cls.run_dir, cls.profiles, cross_profile=cross, gaze_enabled=False)
            cls.reviews[cross] = [dict(cls.SECOND_PASS, finding_id=f"ERGO-{f['id']}@R-1@{pid}")
                                  for f in swarm.aggregate([analysis], cls.profiles)
                                  if f["severity"] in ("P0", "P1") for pid in f["triggered_profiles"]]

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def attach(self, bundle=None, run_dir=None, binding=None, profiles=None, **kwargs):
        from ergoqa.qa_attach import attach_run

        return attach_run(bundle or self.qa_bundle, run_dir or self.run_dir, profiles or self.profiles,
                          binding or {"scenario-1": "EP-01"},
                          receipts_root=kwargs.pop("receipts_root", self.receipts),
                          gaze_enabled=kwargs.pop("gaze_enabled", False),
                          second_pass=kwargs.pop("second_pass", self.reviews[kwargs.get("cross_profile", False)]), **kwargs)

    def test_owner_attach_validates_and_preserves_the_existing_graph(self) -> None:
        before = {p.name: sha256_file(p) for p in sorted(self.run_dir.iterdir())}
        out = self.attach()
        self.assertEqual(validate_bundle(out, artifacts_root=self.receipts), [])
        # Original records, permissions and ids are preserved untouched.
        self.assertEqual(out["permissions"], self.qa_bundle["permissions"])
        for name in ("sources", "evidence", "claims", "personas", "scenarios", "findings", "proposals", "figma"):
            for record in self.qa_bundle["records"][name]:
                self.assertIn(record, out["records"][name], name)
        self.assertEqual(out["records"]["personas"][0]["id"], "persona-1")
        self.assertEqual(out["records"]["scenarios"][0]["id"], "scenario-1")
        # Source run files are unmodified and receipts live outside the run root.
        self.assertEqual({p.name: sha256_file(p) for p in sorted(self.run_dir.iterdir())}, before)
        receipt_files = sorted(p.relative_to(self.receipts).as_posix() for p in self.receipts.rglob("*.png"))
        self.assertTrue(receipt_files)
        self.assertFalse(any((self.run_dir / name).exists() for name in receipt_files))
        # The attached evidence is namespaced, owner-executed and receipt-backed.
        runs = [r for r in out["records"]["runs"] if str(r["id"]).startswith("ERGO-")]
        self.assertEqual([r["cross_profile_evaluation"] for r in runs], [False])
        self.assertEqual(runs[0]["scenario_id"], "scenario-1")
        self.assertEqual(runs[0]["recorded_run_id"], "R-1")
        observations = [o for o in out["records"]["observations"] if str(o["id"]).startswith("ERGO-")]
        self.assertTrue(observations)
        receipts_out = [o["receipt"] for o in observations if o.get("receipt")]
        self.assertTrue(receipts_out)
        for receipt in receipts_out:
            artifact = self.receipts / receipt["artifact_path"]
            self.assertTrue(artifact.is_file(), receipt["artifact_path"])
            self.assertEqual(sha256_file(artifact), receipt["sha256"])
            self.assertFalse(Path(receipt["artifact_path"]).is_absolute())
            self.assertTrue(receipt["quoted_ui_text"])
        findings = [f for f in out["records"]["findings"] if str(f["id"]).startswith("ERGO-")]
        self.assertTrue(findings)
        self.assertTrue(any(f["verification_status"] == "verified" for f in findings))
        self.assertTrue(all("second_pass" in f for f in findings if f["severity"] in ("P0", "P1")))

    def test_cli_round_trip_reaches_the_same_bundle(self) -> None:
        from ergoqa import cli

        profiles_path = self.root / "profiles.json"
        profiles_path.write_text(json.dumps({"profiles": self.profiles}), encoding="utf-8")
        qa_path = self.root / "qa-bundle.json"
        qa_path.write_text(json.dumps(self.qa_bundle, ensure_ascii=False), encoding="utf-8")
        second_path = self.root / "second-pass.json"
        second_path.write_text(json.dumps(self.reviews[False]), encoding="utf-8")
        out_path = self.root / "qa-attached.json"
        args = ["attach", "--bundle", str(qa_path), "--runs", str(self.run_dir), "--profiles", str(profiles_path),
                "--bind", "scenario-1=EP-01", "--receipts-dir", str(self.root / "cli-receipts"),
                "--second-pass", str(second_path), "--no-gaze", "--out", str(out_path)]
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            self.assertEqual(cli.main(args), cli.EXIT_OK, stdout.getvalue())
        attached = json.loads(out_path.read_text(encoding="utf-8"))
        self.assertEqual(validate_bundle(attached, artifacts_root=self.root / "cli-receipts"), [])
        self.assertEqual(attached["bundle_id"], "bundle-demo-001")
        self.assertIn("attached 1 run(s)", stdout.getvalue())

    def test_contract_violations_fail_honestly(self) -> None:
        from ergoqa.qa_attach import AttachError

        def variant_run(name: str, updates: dict | None = None, corrupt_png: bool = False) -> Path:
            target = self.root / name
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(self.run_dir, target)
            run_path = target / "run.json"
            run = json.loads(run_path.read_text(encoding="utf-8"))
            run.update(updates or {})
            run_path.write_text(json.dumps(run, ensure_ascii=False), encoding="utf-8")
            if corrupt_png:
                (target / "S-R-1-000.png").write_bytes(b"not a png")
            return target

        cases = {
            "unknown bundle scenario": ({"scenario-x": "EP-01"}, {}, "bundle has no scenario"),
            "unknown profile": ({"scenario-1": "EP-99"}, {}, "was not supplied"),
            "owner not bound": ({"scenario-1": "EP-02"}, {}, "is not bound"),
            "failed run": ({"scenario-1": "EP-01"}, {"status": "failed", "success": False}, "only completed runs"),
            "incomplete run": ({"scenario-1": "EP-01"}, {"status": "blocked"}, "only completed runs"),
            "no-profile run": ({"scenario-1": "EP-01"}, {"profile_id": "no-profile"}, "no persona executed"),
            "run without persona": ({"scenario-1": "EP-01"}, {"profile_id": "EP-missing"}, "not supplied"),
        }
        for label, (binding, mutate, fragment) in cases.items():
            with self.subTest(label):
                with self.assertRaisesRegex(AttachError, fragment):
                    self.attach(bundle=self.qa_bundle, run_dir=variant_run(label.replace(" ", "-"), mutate), binding=binding)
        with self.subTest("corrupt screenshot"):
            with self.assertRaisesRegex(AttachError, "failed verification"):
                self.attach(run_dir=variant_run("corrupt", corrupt_png=True))
        with self.subTest("stale capture"):
            with self.assertRaisesRegex(AttachError, "predates run start"):
                self.attach(run_dir=variant_run("stale", {"started_at": "2026-09-28T23:00:00Z",
                                                          "ended_at": "2026-09-28T23:00:05Z"}))
        with self.subTest("device mismatch"):
            wrong = copy.deepcopy(self.profiles)
            wrong[0]["attributes"]["device_id"] = "iphone-15"
            with self.assertRaisesRegex(AttachError, "does not match profile"):
                self.attach(profiles=wrong, receipts_root=self.root / "r-dm")
        with self.subTest("orientation mismatch"):
            wrong = copy.deepcopy(self.profiles)
            wrong[0]["attributes"]["orientation"] = "landscape"
            with self.assertRaisesRegex(AttachError, "does not match profile"):
                self.attach(profiles=wrong, receipts_root=self.root / "r-om")
        with self.subTest("identity collision on re-attach"):
            out = self.attach()
            with self.assertRaisesRegex(AttachError, "already exists"):
                self.attach(bundle=out)
        with self.subTest("receipts inside the run root"):
            with self.assertRaisesRegex(AttachError, "outside the run directory"):
                self.attach(receipts_root=self.run_dir / "receipts")
        with self.subTest("missing second pass for P0/P1"):
            with self.assertRaisesRegex(AttachError, "second pass"):
                self.attach(second_pass=None, receipts_root=self.root / "r-sp")

    def test_cross_profile_attach_stays_analytical(self) -> None:
        binding = {"scenario-1": "EP-01", "scenario-1-copy": "EP-02", "scenario-1-copy-2": "EP-03"}
        qa = copy.deepcopy(self.qa_bundle)
        qa["records"]["scenarios"] += [
            {"id": "scenario-1-copy", "persona_id": "persona-1", "task": "ergo 분석 대조"},
            {"id": "scenario-1-copy-2", "persona_id": "persona-1", "task": "ergo 분석 대조"},
        ]
        out = self.attach(bundle=qa, binding=binding, cross_profile=True, receipts_root=self.root / "cp-receipts")
        self.assertEqual(validate_bundle(out, artifacts_root=self.root / "cp-receipts"), [])
        runs = {r["id"]: r for r in out["records"]["runs"] if str(r["id"]).startswith("ERGO-")}
        self.assertEqual(sum(1 for r in runs.values() if not r["cross_profile_evaluation"]), 1)
        analytical = [r for r in runs.values() if r["cross_profile_evaluation"]]
        self.assertEqual(len(analytical), 2)
        findings = [f for f in out["records"]["findings"] if str(f["id"]).startswith("ERGO-")]
        self.assertTrue(any(f["verification_status"] == "verified" for f in findings
                            if f["analysis_kind"] == "owner_execution"))
        self.assertFalse(any(f["verification_status"] == "verified" for f in findings
                             if f["analysis_kind"] == "analytical_cross_profile"))
        unbound = dict(binding)
        unbound.pop("scenario-1-copy-2")
        with self.assertRaisesRegex(ValueError, "not bound"):
            self.attach(bundle=qa, binding=unbound, cross_profile=True, receipts_root=self.root / "cp-unbound")


class AttachIntegrityTests(unittest.TestCase):
    """Negative evidence and filesystem checks use owned synthetic files only."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.run_dir = make_run(self.root)
        self.receipts = self.root / "receipts"
        self.profiles = sample_profiles(3, 7, ["galaxy-s24"])
        self.qa = json.loads((Path(__file__).parent / "fixtures" / "valid-bundle.json").read_text())
        self.qa["records"]["findings"][0]["severity"] = "P2"

    def edit_run(self, **updates):
        path = self.run_dir / "run.json"
        doc = json.loads(path.read_text())
        doc.update(updates)
        path.write_text(json.dumps(doc))

    def edit_snap(self, index=1, **updates):
        path = self.run_dir / f"S-R-1-{index:03d}.json"
        doc = json.loads(path.read_text())
        doc.update(updates)
        path.write_text(json.dumps(doc))

    def attach(self, **kwargs):
        from ergoqa.qa_attach import attach_run
        # This default is intentionally anonymous for the regression that rejects
        # blanket reviews. Positive attachments below supply identity-matched rows.
        kwargs.setdefault("second_pass", AttachBridgeTests.SECOND_PASS)
        return attach_run(self.qa, self.run_dir, kwargs.pop("profiles", self.profiles),
                          {"scenario-1": "EP-01"}, receipts_root=self.receipts,
                          gaze_enabled=False, **kwargs)

    def reviews(self):
        analysis = analyze.analyze_run(self.run_dir, self.profiles, gaze_enabled=False)
        return [dict(AttachBridgeTests.SECOND_PASS, finding_id=f"ERGO-{f['id']}@R-1@EP-01")
                for f in swarm.aggregate([analysis], self.profiles) if f["severity"] in ("P0", "P1")]

    def test_receipt_directory_and_file_symlinks_never_mutate_targets(self) -> None:
        from ergoqa.qa_attach import AttachError
        outside = self.root / "unrelated"
        outside.mkdir()
        sentinel = outside / "S-R-1-000.png"
        sentinel.write_bytes(b"unrelated bytes")
        before = sentinel.read_bytes(), sentinel.stat().st_mode
        self.receipts.mkdir()
        (self.receipts / "R-1").symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(AttachError, "symlink"):
            self.attach()
        self.assertEqual((sentinel.read_bytes(), sentinel.stat().st_mode), before)
        (self.receipts / "R-1").unlink()
        (self.receipts / "R-1").mkdir()
        (self.receipts / "R-1" / sentinel.name).symlink_to(sentinel)
        with self.assertRaisesRegex(AttachError, "symlink"):
            self.attach()
        self.assertEqual((sentinel.read_bytes(), sentinel.stat().st_mode), before)

    def test_conflicting_later_artifact_rejects_before_any_copy(self) -> None:
        from ergoqa.qa_attach import AttachError
        folder = self.receipts / "R-1"
        folder.mkdir(parents=True)
        conflict = folder / "S-R-1-001.png"
        conflict.write_bytes(b"other evidence")
        before = conflict.read_bytes(), conflict.stat().st_mode
        with self.assertRaisesRegex(AttachError, "conflicting"):
            self.attach()
        self.assertEqual((conflict.read_bytes(), conflict.stat().st_mode), before)
        self.assertFalse((folder / "S-R-1-000.png").exists())

    def test_all_device_records_and_completion_intervals_are_checked(self) -> None:
        from ergoqa.qa_attach import AttachError
        original_run = (self.run_dir / "run.json").read_bytes()
        original_snap = (self.run_dir / "S-R-1-001.json").read_bytes()
        device = {"id": "galaxy-s24", "viewport_css": [W, H], "dpr": 1, "orientation": "portrait"}
        cases = [("run device", {"device": dict(device, id="iphone-15")}, {}, "device"),
                 ("later device", {}, {"device": dict(device, id="iphone-15")}, "device"),
                 ("later orientation", {}, {"device": dict(device, orientation="landscape")}, "orientation"),
                 ("null end", {"ended_at": None}, {}, "ended_at"),
                 ("end before start", {"ended_at": "2026-09-28T11:59:59Z"}, {}, "ended_at"),
                 ("capture after end", {}, {"captured_at": "2026-09-28T12:00:06Z"}, "after run end"),
                 ("later stale capture", {}, {"captured_at": "2026-09-28T11:59:59Z"}, "predates run start")]
        for label, run_changes, snap_changes, fragment in cases:
            with self.subTest(label=label):
                (self.run_dir / "run.json").write_bytes(original_run)
                (self.run_dir / "S-R-1-001.json").write_bytes(original_snap)
                self.edit_run(**run_changes)
                self.edit_snap(**snap_changes)
                with self.assertRaisesRegex(AttachError, fragment):
                    self.attach()
                self.assertFalse(self.receipts.exists())

    def test_review_identity_is_required_and_existing_evidence_is_preserved(self) -> None:
        from ergoqa.qa_attach import AttachError
        for review in (AttachBridgeTests.SECOND_PASS,
                       dict(AttachBridgeTests.SECOND_PASS, finding_id="unrelated-finding")):
            with self.subTest(review=review):
                with self.assertRaisesRegex(AttachError, "finding_id|second pass"):
                    self.attach(second_pass=review)
                self.assertFalse(self.receipts.exists())
        reviews = self.reviews()
        self.assertTrue(reviews)
        with self.assertRaisesRegex(AttachError, "second pass"):
            self.attach(second_pass=reviews[:-1])
        self.assertFalse(self.receipts.exists())
        out = self.attach(second_pass=reviews)
        by_id = {r["finding_id"]: r for r in reviews}
        for finding in out["records"]["findings"]:
            if finding["id"] in by_id:
                self.assertEqual(finding["second_pass"], by_id[finding["id"]])
        for group, originals in self.qa["records"].items():
            self.assertTrue(all(row in out["records"][group] for row in originals))

    def test_unknown_builds_stay_unverified_without_image_derived_identity(self) -> None:
        reviews = self.reviews()
        out = self.attach(second_pass=reviews)
        for obs in out["records"]["observations"]:
            if str(obs["id"]).startswith("ERGO-") and obs.get("receipt"):
                self.assertEqual(obs["receipt"]["build_id"], "unknown")
        self.assertFalse(any(f["verification_status"] == "verified" for f in out["records"]["findings"]
                             if str(f["id"]).startswith("ERGO-")))
        # A second run of the same scenario with equally unknown metadata cannot
        # turn the first run into verified evidence of the same build.
        self.edit_run(run_id="R-2")
        for index in (0, 1):
            self.edit_snap(index=index, run_id="R-2")
        from ergoqa.qa_attach import attach_run
        analysis = analyze.analyze_run(self.run_dir, self.profiles, gaze_enabled=False)
        reviews = [dict(AttachBridgeTests.SECOND_PASS, finding_id=f"ERGO-{f['id']}@R-2@EP-01")
                   for f in swarm.aggregate([analysis], self.profiles) if f["severity"] in ("P0", "P1")]
        out = attach_run(out, self.run_dir, self.profiles, {"scenario-1": "EP-01"},
                         receipts_root=self.receipts, gaze_enabled=False, second_pass=reviews)
        self.assertFalse(any(f["verification_status"] == "verified" for f in out["records"]["findings"]
                             if str(f["id"]).startswith("ERGO-")))

    def test_duplicate_profiles_are_rejected_on_attach(self) -> None:
        from ergoqa.qa_attach import AttachError
        conflicting = copy.deepcopy(self.profiles[0])
        conflicting["attributes"]["vision"]["presbyopia"] = True
        with self.assertRaisesRegex(AttachError, "duplicate profile"):
            self.attach(profiles=[*self.profiles, conflicting])
        self.assertFalse(self.receipts.exists())

    def test_known_build_and_probe_context_survive_without_relabeling(self) -> None:
        self.edit_run(surface={"kind": "web", "build_id": "owned-fixture-v2"},
                      reflow=[{"snapshot_id": "S-R-1-001", "width": 320}],
                      focus_walks=[{"snapshot_id": "S-R-1-000", "where": "load"}])
        for index in (0, 1):
            self.edit_snap(index=index, surface={"kind": "web", "url": "http://127.0.0.1/checkout.html",
                                                "title": "checkout", "build_id": "owned-fixture-v2"})
        path = self.run_dir / "S-R-1-001.json"
        snap = json.loads(path.read_text())
        snap["device"].update(viewport_css=[320, 568], dpr=1.0, probe="reflow")
        image = png.new_image(320, 568, 3, (255, 255, 255))
        png.write_png(self.run_dir / snap["screenshot"]["path"], image)
        snap["screenshot"].update(width_px=320, height_px=568,
                                  sha256=sha256_file(self.run_dir / snap["screenshot"]["path"]))
        path.write_text(json.dumps(snap))
        out = self.attach(second_pass=self.reviews())
        attached_run = next(r for r in out["records"]["runs"] if str(r["id"]).startswith("ERGO-"))
        self.assertEqual(attached_run["reflow"], [{"snapshot_id": "S-R-1-001", "width": 320}])
        self.assertEqual(attached_run["focus_walks"], [{"snapshot_id": "S-R-1-000", "where": "load"}])
        captures = {o["snapshot_id"]: o for o in out["records"]["observations"] if o.get("kind") == "capture_coverage"}
        self.assertEqual(captures["S-R-1-001"]["snapshot_device"], snap["device"])
        self.assertIn("320x568", captures["S-R-1-001"]["receipt"]["device"])
        self.assertIn("360x780", captures["S-R-1-000"]["receipt"]["device"])
        self.assertTrue(all(o["receipt"]["build_id"] == "owned-fixture-v2" for o in captures.values()))
        self.assertTrue(any(f["verification_status"] == "verified" for f in out["records"]["findings"]
                            if str(f["id"]).startswith("ERGO-")))
        self.assertEqual(validate_bundle(out, artifacts_root=self.receipts), [])

    def test_existing_priority_receipt_and_review_are_preserved(self) -> None:
        self.receipts.mkdir()
        old_png = self.receipts / "original-qa.png"
        write_png(old_png)
        self.qa["records"]["runs"][0].update(started_at="2026-09-28T11:00:00Z", ended_at="2026-09-28T11:00:05Z")
        self.qa["records"]["observations"][0]["receipt"] = {
            "artifact_path": old_png.name, "sha256": sha256_file(old_png), "captured_at": "2026-09-28T11:00:01Z",
            "surface_url": "https://example.com/product", "build_id": "original-qa-v1", "device": "original-device",
            "quoted_ui_text": "다음 행동"}
        self.qa["records"]["findings"][0].update(severity="P1",
            second_pass=dict(AttachBridgeTests.SECOND_PASS, finding_id="finding-1"))
        original = copy.deepcopy(self.qa)
        old_bytes, old_mode = old_png.read_bytes(), old_png.stat().st_mode
        out = self.attach(second_pass=self.reviews())
        self.assertEqual((old_png.read_bytes(), old_png.stat().st_mode), (old_bytes, old_mode))
        for group, rows in original["records"].items():
            self.assertTrue(all(row in out["records"][group] for row in rows))
        self.assertEqual(validate_bundle(out, artifacts_root=self.receipts), [])

    def test_cli_guards_inputs_source_roots_and_existing_outputs_before_mutation(self) -> None:
        from ergoqa import cli
        qa = self.root / "qa.json"
        qa.write_text(json.dumps(self.qa))
        profiles = self.root / "profiles.json"
        profiles.write_text(json.dumps({"profiles": self.profiles}))
        reviews = self.root / "reviews.json"
        reviews.write_text(json.dumps(AttachBridgeTests.SECOND_PASS))
        existing = self.root / "existing.json"
        existing.write_text("unrelated output")
        before = {p: p.read_bytes() for p in (qa, profiles, reviews, existing, self.run_dir / "run.json")}
        args = ["attach", "--bundle", str(qa), "--runs", str(self.run_dir), "--profiles", str(profiles),
                "--bind", "scenario-1=EP-01", "--receipts-dir", str(self.receipts), "--second-pass", str(reviews)]
        for out in (*before, self.run_dir / "new.json"):
            with self.subTest(out=out), redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                self.assertEqual(cli.main([*args, "--out", str(out)]), cli.EXIT_USAGE)
                self.assertFalse(self.receipts.exists())
                for path, data in before.items():
                    self.assertEqual(path.read_bytes(), data)
        for bind in ("scenario-1=EP-02", "scenario-1=EP-01"):
            with self.subTest(bind=bind), redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()) as err:
                self.assertEqual(cli.main([*args, "--bind", bind, "--out", str(self.root / "new.json")]), cli.EXIT_USAGE)
                self.assertIn("duplicate scenario binding", err.getvalue())
                self.assertFalse(self.receipts.exists())

    def test_clean_runs_keep_owner_coverage_and_capture_receipts(self) -> None:
        self.edit_run(steps=[], timing_windows=[], persona_notes=[])
        for index in (0, 1):
            self.edit_snap(index=index, elements=[el("title", "heading", (16, 70, 200, 28), text="주문 확인", size=20)],
                           focus_point=None)
        analysis = analyze.analyze_run(self.run_dir, self.profiles, gaze_enabled=False)
        self.assertFalse([o for o in analysis["observations"] if not o["passed"]])
        out = self.attach(second_pass=None)
        new_runs = [r for r in out["records"]["runs"] if str(r["id"]).startswith("ERGO-")]
        self.assertEqual(len(new_runs), 1)
        self.assertFalse(new_runs[0]["cross_profile_evaluation"])
        new_observations = [o for o in out["records"]["observations"] if str(o["id"]).startswith("ERGO-")]
        self.assertEqual(len(new_observations), 2)
        self.assertTrue(all(o["kind"] == "capture_coverage" and o.get("receipt") for o in new_observations))
        self.assertEqual(out["records"]["findings"], self.qa["records"]["findings"])
        exported = bundle.to_evidence_bundle("clean", [analysis], [], self.profiles)
        self.assertEqual(len(exported["records"]["runs"]), 1)
        self.assertEqual(validate_bundle(out, artifacts_root=self.receipts), [])


if __name__ == "__main__":
    unittest.main()
