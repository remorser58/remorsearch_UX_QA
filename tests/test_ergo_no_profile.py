"""Device-only runs can reuse recorded evidence for matching profile analysis."""

from __future__ import annotations

import copy
import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from _paths import SKILL  # noqa: F401 (makes the skill importable)
from ergoqa import analyze, bundle, cli, swarm
from ergoqa.profiles import sample_profiles
from test_ergo_pipeline import make_run


class OwnerIdentityTests(unittest.TestCase):
    """The recorded owner is explicit; ownership never comes from list order."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.profiles = sample_profiles(4, 7, ["galaxy-s24"])

    def _run(self, profile_id: str) -> Path:
        target = self.root / profile_id
        target.mkdir(parents=True, exist_ok=True)
        run_dir = make_run(target)
        run_path = run_dir / "run.json"
        run = json.loads(run_path.read_text(encoding="utf-8"))
        run["profile_id"] = profile_id
        run_path.write_text(json.dumps(run), encoding="utf-8")
        return run_dir

    def test_analysis_exposes_the_recorded_owner(self) -> None:
        named = analyze.analyze_run(self._run("EP-03"), self.profiles, cross_profile=True, gaze_enabled=False)
        self.assertEqual(named["owner_profile_id"], "EP-03")
        self.assertEqual(named["profiles_evaluated"][0], "EP-03")
        device_only = analyze.analyze_run(self._run("no-profile"), self.profiles, cross_profile=True, gaze_enabled=False)
        self.assertIsNone(device_only["owner_profile_id"])

    def test_ownerless_export_is_always_analytical_and_never_verifies(self) -> None:
        analysis = analyze.analyze_run(self._run("no-profile"), self.profiles, cross_profile=True, gaze_enabled=False)
        findings = swarm.aggregate([analysis], self.profiles)
        doc = bundle.to_evidence_bundle("ergo-ownerless", [analysis], findings, self.profiles)
        runs = {r["id"]: r for r in doc["records"]["runs"]}
        self.assertTrue(runs)
        self.assertTrue(all(r["cross_profile_evaluation"] for r in runs.values()))
        self.assertFalse(any(f["verification_status"] == "verified" for f in doc["records"]["findings"]))

    def test_cross_profile_export_classifies_only_the_owner_as_execution(self) -> None:
        analysis = analyze.analyze_run(self._run("EP-02"), self.profiles, cross_profile=True, gaze_enabled=False)
        findings = swarm.aggregate([analysis], self.profiles)
        # A consumer that reorders profiles_evaluated must not change classification:
        # ownership comes from the recorded owner, never from list order.
        reordered = dict(analysis, profiles_evaluated=list(reversed(analysis["profiles_evaluated"])))
        doc = bundle.to_evidence_bundle("ergo-named", [reordered], findings, self.profiles)
        runs = {r["id"]: r for r in doc["records"]["runs"]}
        owner_runs = [r for r in runs.values() if not r["cross_profile_evaluation"]]
        analytical_runs = [r for r in runs.values() if r["cross_profile_evaluation"]]
        self.assertEqual({r["recorded_run_id"] for r in owner_runs}, {"R-1"})
        self.assertEqual({r["id"].split("@")[1] for r in owner_runs}, {"EP-02"})
        self.assertTrue(analytical_runs)
        self.assertFalse(any("@EP-02" in r["id"] for r in analytical_runs))
        by_id = {f["id"]: f for f in doc["records"]["findings"]}
        owner_findings = [f for f in by_id.values() if f["id"].endswith("@EP-02")]
        analytical_findings = [f for f in by_id.values() if not f["id"].endswith("@EP-02")]
        self.assertTrue(any(f["verification_status"] == "verified" for f in owner_findings))
        self.assertFalse(any(f["verification_status"] == "verified" for f in analytical_findings))

    def test_mixed_owner_runs_cannot_borrow_the_first_pairs_owner(self) -> None:
        first = analyze.analyze_run(self._run("EP-01"), self.profiles, cross_profile=True, gaze_enabled=False)
        for owner in ("EP-02", "no-profile", "missing-owner-evidence"):
            with self.subTest(owner=owner):
                later = copy.deepcopy(first)
                later["run_id"] = "R-2"
                later["owner_profile_id"] = None if owner == "no-profile" else owner
                if owner == "missing-owner-evidence":
                    later.pop("owner_profile_id")
                for o in later["observations"]:
                    o["id"] = o["id"].replace("R-1", "R-2")
                    o["run_id"] = "R-2"
                analyses = [first, later]
                findings = swarm.aggregate(analyses, self.profiles)
                for order in (analyses, list(reversed(analyses))):
                    doc = bundle.to_evidence_bundle("mixed-owners", order, findings, self.profiles)
                    ep1 = [f for f in doc["records"]["findings"] if f["id"].endswith("@EP-01")]
                    self.assertTrue(ep1)
                    self.assertFalse(any(f["verification_status"] == "verified" for f in ep1))

    def test_duplicate_profiles_are_rejected_before_analysis(self) -> None:
        run = self._run("EP-01")
        conflicting = copy.deepcopy(self.profiles[0])
        conflicting["attributes"]["vision"]["presbyopia"] = True
        with self.assertRaisesRegex(ValueError, "duplicate profile"):
            analyze.analyze_run(run, [*self.profiles, conflicting], gaze_enabled=False)


class NoProfileTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.run_dir = make_run(self.root)
        self.run_path = self.run_dir / "run.json"
        self.run = json.loads(self.run_path.read_text(encoding="utf-8"))
        self.run["profile_id"] = "no-profile"
        self.run_path.write_text(json.dumps(self.run), encoding="utf-8")
        self.profiles = sample_profiles(3, 7, ["galaxy-s24"])
        self.other_device = copy.deepcopy(self.profiles[0])
        self.other_device["profile_id"] = "EP-other-device"
        self.other_device["attributes"]["device_id"] = "iphone-15"
        self.other_orientation = copy.deepcopy(self.profiles[0])
        self.other_orientation["profile_id"] = "EP-other-orientation"
        self.other_orientation["attributes"]["orientation"] = "landscape"

    def test_cross_profile_uses_recorded_device_and_orientation(self) -> None:
        original = self.run_path.read_bytes()
        result = analyze.analyze_run(
            self.run_dir, [self.other_device, *self.profiles, self.other_orientation],
            cross_profile=True, gaze_enabled=False,
        )
        self.assertEqual(result["profiles_evaluated"], [p["profile_id"] for p in self.profiles])
        self.assertEqual(result["device_id"], "galaxy-s24")
        self.assertEqual(result["orientation"], "portrait")
        self.assertTrue(result["observations"])
        self.assertEqual(self.run_path.read_bytes(), original)

    def test_operator_judgment_is_not_assigned_to_a_profile(self) -> None:
        result = analyze.analyze_run(self.run_dir, self.profiles, cross_profile=True, gaze_enabled=False)
        self.assertFalse(any(o["check_id"] == "PJ-01" for o in result["observations"]))
        self.assertFalse(any(key.startswith("PJ-01||") for key in result["coverage"]))

    def test_without_cross_profile_names_the_fix(self) -> None:
        with self.assertRaisesRegex(ValueError, r"recorded with --device.*add --cross-profile.*--profiles.*--profile"):
            analyze.analyze_run(self.run_dir, self.profiles, gaze_enabled=False)

    def test_no_matching_device_names_the_recorded_device_and_fix(self) -> None:
        with self.assertRaisesRegex(ValueError, r"no supplied profiles match.*galaxy-s24.*portrait.*--profiles.*--cross-profile"):
            analyze.analyze_run(self.run_dir, [self.other_device], cross_profile=True, gaze_enabled=False)

    def test_no_matching_orientation_and_empty_profiles_fail_clearly(self) -> None:
        for profiles in ([self.other_orientation], []):
            with self.subTest(profiles=profiles):
                with self.assertRaisesRegex(ValueError, r"no supplied profiles match.*orientation 'portrait'"):
                    analyze.analyze_run(self.run_dir, profiles, cross_profile=True, gaze_enabled=False)

    def test_detector_results_match_the_existing_profile_path(self) -> None:
        device_only = analyze.analyze_run(self.run_dir, self.profiles, cross_profile=True, gaze_enabled=False)
        self.run["profile_id"] = self.profiles[0]["profile_id"]
        self.run_path.write_text(json.dumps(self.run), encoding="utf-8")
        named = analyze.analyze_run(self.run_dir, self.profiles, cross_profile=True, gaze_enabled=False)

        def detector_observations(result):
            return [{k: v for k, v in o.items() if k != "id"}
                    for o in result["observations"] if o["check_id"] != "PJ-01"]

        self.assertEqual(detector_observations(device_only), detector_observations(named))
        self.assertEqual(device_only["health"], named["health"])
        self.assertEqual(device_only["profiles_evaluated"], named["profiles_evaluated"])

    def test_missing_named_profile_still_fails(self) -> None:
        self.run["profile_id"] = "EP-missing"
        self.run_path.write_text(json.dumps(self.run), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "profile 'EP-missing'.*not supplied"):
            analyze.analyze_run(self.run_dir, self.profiles, cross_profile=True, gaze_enabled=False)

    def test_cli_round_trip_without_copying_or_rewriting_the_run(self) -> None:
        profiles_path = self.root / "profiles.json"
        profiles_path.write_text(json.dumps({"profiles": self.profiles}), encoding="utf-8")
        output = self.root / "analysis.json"
        args = ["analyze", "--runs", str(self.run_dir), "--profiles", str(profiles_path), "--no-gaze", "--out", str(output)]
        original = self.run_path.read_bytes()
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            self.assertEqual(cli.main(args), cli.EXIT_USAGE)
        self.assertIn("add --cross-profile", stderr.getvalue())
        self.assertFalse(output.exists())
        with redirect_stdout(stdout), redirect_stderr(stderr):
            self.assertEqual(cli.main([*args, "--cross-profile"]), cli.EXIT_OK)
        result = json.loads(output.read_text(encoding="utf-8"))["analyses"][0]
        self.assertEqual(result["profiles_evaluated"], [p["profile_id"] for p in self.profiles])
        self.assertEqual(self.run_path.read_bytes(), original)
        self.assertEqual([p.name for p in self.root.iterdir() if p.is_dir()], ["R-1"])


if __name__ == "__main__":
    unittest.main()
