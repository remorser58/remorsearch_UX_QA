"""Tests for ergo-audience.v1 validation and audience-based persona composition."""

from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import _paths  # noqa: E402,F401  (puts the skill folder on sys.path)

from ergoqa import audience, bundle, report, swarm  # noqa: E402
from ergoqa.profiles import validate_profile  # noqa: E402
from validate_bundle import validate_bundle  # noqa: E402

EXAMPLE = _paths.SKILL / "examples" / "audience" / "transit-card.audience.json"


def load() -> dict:
    return json.loads(EXAMPLE.read_text(encoding="utf-8"))


class ValidateAudience(unittest.TestCase):
    def test_example_is_valid(self) -> None:
        self.assertEqual(audience.validate_audience(load()), [])

    def test_segment_needs_evidence_and_known_sources(self) -> None:
        doc = load()
        doc["segments"][0]["evidence"] = []
        doc["segments"][1]["conditions"][0]["source_ids"] = ["SRC-missing"]
        errors = audience.validate_audience(doc)
        self.assertTrue(any("evidence must be a non-empty array" in e for e in errors))
        self.assertTrue(any("unknown source_id 'SRC-missing'" in e for e in errors))

    def test_tasks_need_concrete_data(self) -> None:
        doc = load()
        doc["segments"][0]["tasks"][0]["concrete_data"] = {}
        errors = audience.validate_audience(doc)
        self.assertTrue(any("concrete_data" in e for e in errors))

    def test_unknown_device_and_share_rules(self) -> None:
        doc = load()
        doc["segments"][0]["devices"] = {"nokia-3310": 1.0}
        doc["segments"][2]["share"] = {"value": 0.1, "basis": "unknown"}
        errors = audience.validate_audience(doc)
        self.assertTrue(any("unknown device id 'nokia-3310'" in e for e in errors))
        self.assertTrue(any("share.value must be null when basis is unknown" in e for e in errors))


class Compose(unittest.TestCase):
    def test_export_separates_composition_from_explicit_or_malformed_research_refs(self) -> None:
        profiles = audience.compose(load(), 2, floors=[])["profiles"]
        composition = copy.deepcopy(profiles[0]["audience_ref"])
        cases = [
            ("standalone", composition, True),
            ("empty-claims", {**composition, "claim_ids": []}, False),
            ("linked-claims", {**composition, "claim_ids": ["CLM-existing"]}, False),
            ("null-claims", {**composition, "claim_ids": None}, False),
            ("invalid-claims", {**composition, "claim_ids": "CLM-existing"}, False),
            ("invalid-segment", {**composition, "segment_id": None}, False),
            ("empty-ref", {}, False),
            ("null-ref", None, False),
            ("invalid-ref", [], False),
        ]
        for name, ref, standalone in cases:
            with self.subTest(case=name):
                profiles[0]["audience_ref"] = copy.deepcopy(ref)
                original = copy.deepcopy(profiles)
                exported = bundle.to_evidence_bundle("audience-export", [], [], profiles)
                for index, (profile, persona) in enumerate(zip(profiles, exported["records"]["personas"])):
                    if standalone or index == 1:
                        self.assertNotIn("audience_ref", persona)
                        self.assertEqual(persona["scenario_assumptions"]["audience_composition"], profile["audience_ref"])
                    else:
                        self.assertEqual(persona["audience_ref"], ref)
                        self.assertNotIn("audience_composition", persona["scenario_assumptions"])
                    self.assertEqual(persona["basis"], "synthetic")
                self.assertEqual(profiles, original)
                errors = validate_bundle(exported)
                if standalone:
                    self.assertEqual(errors, [])
                elif name == "empty-claims":
                    self.assertIn("audience_ref references unknown research segment", errors)
                elif name == "linked-claims":
                    self.assertIn("audience_ref.claim_ids[0] references an unknown record", errors)
                    self.assertIn("audience_ref references unknown research segment", errors)
                else:
                    self.assertTrue(any("audience_ref" in e for e in errors), errors)

    def test_budget_respected_and_profiles_valid(self) -> None:
        doc = load()
        for budget in (1, 2, 3, 5, 8, 12, 16):
            plan = audience.compose(doc, budget)
            self.assertLessEqual(len(plan["profiles"]), budget)
            for p in plan["profiles"]:
                self.assertEqual(validate_profile(p), [], p["profile_id"])
                self.assertEqual(p["origin"], "audience_composed")
                self.assertTrue(p["audience_ref"]["reasons"])

    def test_every_segment_first_then_priority_when_budget_is_small(self) -> None:
        doc = load()
        plan = audience.compose(doc, 3)
        self.assertEqual({p["audience_ref"]["segment_id"] for p in plan["profiles"]}, {"SEG-commuter", "SEG-senior", "SEG-lowvision"})
        plan = audience.compose(doc, 2)
        self.assertEqual({p["audience_ref"]["segment_id"] for p in plan["profiles"]}, {"SEG-commuter", "SEG-senior"})
        self.assertTrue(any(u["facet"] == "segment" for u in plan["untested"]))

    def test_heavier_segment_gets_more_profiles(self) -> None:
        plan = audience.compose(load(), 12)
        counts = plan["segments"]
        self.assertGreater(counts["SEG-commuter"]["profiles"], counts["SEG-senior"]["profiles"])
        self.assertGreaterEqual(counts["SEG-senior"]["profiles"], counts["SEG-lowvision"]["profiles"])

    def test_typical_member_carries_majority_conditions_and_modal_context(self) -> None:
        plan = audience.compose(load(), 3)
        by_seg = {p["audience_ref"]["segment_id"]: p for p in plan["profiles"]}
        self.assertTrue(by_seg["SEG-senior"]["attributes"]["vision"]["presbyopia"])
        self.assertEqual(by_seg["SEG-lowvision"]["attributes"]["vision"]["acuity"], "low")
        self.assertEqual(by_seg["SEG-commuter"]["attributes"]["context"]["mobility"], "walking")
        self.assertEqual(by_seg["SEG-commuter"]["audience_ref"]["facet"], "typical")

    def test_facets_vary_one_thing(self) -> None:
        plan = audience.compose(load(), 12)
        typical = next(p for p in plan["profiles"] if p["audience_ref"]["segment_id"] == "SEG-commuter" and p["audience_ref"]["facet"] == "typical")
        for p in plan["profiles"]:
            ref = p["audience_ref"]
            if ref["segment_id"] != "SEG-commuter" or ref["facet"] == "typical" or ref["floor"]:
                continue
            a, t = p["attributes"], typical["attributes"]
            diffs = [k for k in ("age_band", "device_id") if a[k] != t[k]]
            diffs += ["grip"] if a["grip"] != t["grip"] else []
            diffs += [k for k in ("cvd", "presbyopia", "acuity") if a["vision"][k] != t["vision"][k]]
            diffs += [k for k in ("mobility", "lighting") if a["context"][k] != t["context"][k]]
            diffs += ["tremor"] if a["motor"]["tremor"] != t["motor"]["tremor"] else []
            diffs += ["familiarity"] if a["cognition"]["familiarity"] != t["cognition"]["familiarity"] else []
            if ref["facet"] == "context":
                self.assertTrue(set(diffs) <= {"mobility", "lighting"}, (p["profile_id"], diffs))
            else:
                self.assertLessEqual(len(diffs), 1, (p["profile_id"], diffs))

    def test_left_hand_and_deutan_floors_are_met_without_duplicates(self) -> None:
        plan = audience.compose(load(), 8)
        grips = [p["attributes"]["grip"] for p in plan["profiles"]]
        self.assertIn("one_hand_left", grips)
        self.assertTrue(any(p["attributes"]["vision"]["cvd"] == "deutan" for p in plan["profiles"]))
        keys = [json.dumps(p["attributes"], sort_keys=True) for p in plan["profiles"]]
        self.assertEqual(len(keys), len(set(keys)), "duplicate profiles")

    def test_no_floors_when_disabled(self) -> None:
        doc = load()
        doc["segments"][0]["conditions"] = []
        plan = audience.compose(doc, 4, floors=[])
        self.assertFalse(any(p["audience_ref"]["floor"] for p in plan["profiles"]))
        self.assertFalse(any(p["attributes"]["vision"]["cvd"] == "deutan" for p in plan["profiles"]))

    def test_deterministic(self) -> None:
        a = audience.compose(load(), 10)
        b = audience.compose(load(), 10)
        self.assertEqual(json.dumps(a, sort_keys=True), json.dumps(b, sort_keys=True))

    def test_unknown_share_gets_priority_default_inside_unclaimed_mass(self) -> None:
        weights = audience.segment_weights(load()["segments"])
        self.assertAlmostEqual(weights["SEG-commuter"], 0.55)
        self.assertAlmostEqual(weights["SEG-lowvision"], 0.15)

    def test_invalid_audience_raises(self) -> None:
        doc = copy.deepcopy(load())
        doc["segments"] = []
        with self.assertRaises(audience.AudienceError):
            audience.compose(doc, 4)


class NoOpFacets(unittest.TestCase):
    def test_a_facet_equal_to_the_typical_member_is_not_composed_or_listed(self) -> None:
        # A two-thumb segment with no one-handed context: its "two_thumbs grip" facet
        # would copy the typical member (reported by a Stage-0 agent, 2026-09-29).
        doc = load()
        seg = doc["segments"][0]
        seg["grips"] = {"two_thumbs": 1.0}
        seg["contexts"] = [c for c in seg.get("contexts") or [] if not c.get("one_handed")]
        if not seg["contexts"]:
            del seg["contexts"]
        plan = audience.compose(doc, 12)
        keys = [json.dumps(p["attributes"], sort_keys=True) for p in plan["profiles"]]
        self.assertEqual(len(keys), len(set(keys)))
        self.assertFalse([u for u in plan["untested"] if u["facet"] == "grip" and u["segment_id"] == seg["segment_id"]])


class ResearchRules(unittest.TestCase):
    def test_statistic_evidence_needs_a_quoted_number(self) -> None:
        doc = load()
        doc["segments"][1]["evidence"][0]["quote"] = "많다"
        self.assertTrue(any("quote the source's number" in e for e in audience.validate_audience(doc)))

    def test_not_simulated_conditions_and_non_operators_are_listed_untested(self) -> None:
        doc = load()
        doc["segments"].append({**copy.deepcopy(doc["segments"][1]), "segment_id": "SEG-payer", "name_ko": "보호자(결제만)", "role": "customer"})
        plan = audience.compose(doc, 8)
        self.assertFalse(any(p["audience_ref"]["segment_id"] == "SEG-payer" for p in plan["profiles"]))
        reasons = " ".join(u["reason"] for u in plan["untested"])
        self.assertIn("screen_reader", reasons)
        self.assertIn("role customer", reasons)
        self.assertIn("TalkBack", reasons)

    def test_community_sources_support_existence_not_size(self) -> None:
        doc = load()
        doc["sources"].append({"source_id": "SRC-forum", "type": "community", "title": "커뮤니티 글", "bundle_ref": "SRC-B-7"})
        doc["segments"][0]["share"] = {"value": 0.3, "basis": "estimated", "source_ids": ["SRC-forum"]}
        doc["segments"][1]["evidence"][0]["source_id"] = "SRC-forum"
        errors = audience.validate_audience(doc)
        self.assertTrue(any("support existence, not size" in e for e in errors))
        self.assertTrue(any("record it as firsthand" in e for e in errors))
        doc["sources"][-1]["bundle_ref"] = ""
        self.assertTrue(any("bundle_ref must be a non-empty string" in e for e in audience.validate_audience(doc)))

    def test_walking_floor_only_on_handheld_devices(self) -> None:
        doc = load()
        for seg in doc["segments"]:
            seg["devices"] = {"galaxy-tab-s9": 1.0}
            for c in seg.get("contexts") or []:
                c["mobility"] = "standing"
        plan = audience.compose(doc, 8)
        self.assertFalse(any(p["attributes"]["context"]["mobility"] == "walking" for p in plan["profiles"]))
        self.assertFalse(any(f["floor"] == "walking" for f in plan["floors_used"]))
        doc["segments"][2]["devices"] = {"galaxy-tab-s9": 0.5, "galaxy-s24": 0.5}
        plan = audience.compose(doc, 16)
        walkers = [p for p in plan["profiles"] if p["attributes"]["context"]["mobility"] == "walking"]
        self.assertTrue(walkers)
        self.assertTrue(all(p["attributes"]["device_id"] == "galaxy-s24" for p in walkers))

    def test_stubs_only_for_operators_and_quote_basis(self) -> None:
        doc = load()
        payer = {**copy.deepcopy(doc["segments"][1]), "segment_id": "SEG-payer", "name_ko": "보호자(결제만)", "role": "customer"}
        payer["tasks"] = [{**copy.deepcopy(doc["segments"][1]["tasks"][0]), "task_id": "T-pay-only"}]
        doc["segments"].append(payer)
        self.assertNotIn("SC-T-pay-only", {s["scenario_id"] for s in audience.scenario_stubs(doc)})
        doc["segments"][0]["evidence"][0]["quote_basis"] = ""
        self.assertTrue(any("quote_basis must be a non-empty string" in e for e in audience.validate_audience(doc)))
        self.assertEqual(audience.quote_basis_kind("search tool's extract of the page (may paraphrase)"), "snippet")
        self.assertEqual(audience.quote_basis_kind("document (read in full)"), "document")
        self.assertEqual(audience.quote_basis_kind("page"), "page")
        doc["segments"][0]["evidence"][0]["quote_basis"] = "snippet"
        self.assertEqual(audience.validate_audience(doc), [])
        text = audience.plan_markdown(audience.compose(doc, 4), doc)
        self.assertIn("quote_basis=snippet", text)

    def test_age_facet_does_not_switch_presbyopia(self) -> None:
        plan = audience.compose(load(), 16)
        base = next(p for p in plan["profiles"] if p["audience_ref"]["segment_id"] == "SEG-commuter" and p["audience_ref"]["facet"] == "typical")
        for p in plan["profiles"]:
            if p["audience_ref"]["segment_id"] == "SEG-commuter" and p["audience_ref"]["facet"] == "age":
                self.assertEqual(p["attributes"]["vision"]["presbyopia"], base["attributes"]["vision"]["presbyopia"])

    def test_an_age_band_alone_never_sets_presbyopia(self) -> None:
        # SEG-lowvision's modal age is 50s but it does not declare presbyopia; the
        # demographic alone must not imply the sensory condition (spec: age is
        # context, conditions are explicit inputs or declared assumptions).
        doc = load()
        senior = copy.deepcopy(doc["segments"][1])
        senior.update(segment_id="SEG-quiet-60s", name_ko="조용한 60대", conditions=[], evidence=[copy.deepcopy(doc["segments"][0]["evidence"][0])])
        doc["segments"].append(senior)
        plan = audience.compose(doc, 16)
        for p in plan["profiles"]:
            if p["audience_ref"]["segment_id"] in ("SEG-lowvision", "SEG-quiet-60s"):
                self.assertFalse(p["attributes"]["vision"]["presbyopia"], p["profile_id"])

    def test_declared_presbyopia_condition_still_applies(self) -> None:
        plan = audience.compose(load(), 6)
        seniors = [p for p in plan["profiles"] if p["audience_ref"]["segment_id"] == "SEG-senior"]
        self.assertTrue(seniors)
        self.assertTrue(all(p["attributes"]["vision"]["presbyopia"] for p in seniors))


class StubsAndReport(unittest.TestCase):
    def test_scenario_stubs_embed_concrete_data(self) -> None:
        stubs = audience.scenario_stubs(load())
        ids = {s["scenario_id"] for s in stubs}
        self.assertEqual(ids, {"SC-T-topup", "SC-T-balance"})
        topup = next(s for s in stubs if s["scenario_id"] == "SC-T-topup")
        self.assertIn("20,000원", topup["task_goal_ko"])
        self.assertEqual(sorted(topup["audience_ref"]["segment_ids"]), ["SEG-commuter", "SEG-senior"])
        # The emitted role contract (targets.irreversible) must satisfy the
        # scenario validator's role set (stubs leave url/success as TODO).
        from ergoqa.snapshot import validate_scenario
        self.assertIn("irreversible", topup["targets"])
        topup["surface"]["url"] = "http://127.0.0.1:9477/topup"
        topup["success"] = {"selector_visible": "#done"}
        self.assertEqual(validate_scenario(topup), [], json.dumps(validate_scenario(topup), ensure_ascii=False))

    def test_segments_affected_and_report(self) -> None:
        doc = load()
        plan = audience.compose(doc, 6)
        profiles = plan["profiles"]
        target = next(p for p in profiles if p["audience_ref"]["segment_id"] == "SEG-senior")
        others = [p for p in profiles if p["attributes"]["device_id"] == target["attributes"]["device_id"] and p is not target]
        obs = [{"id": "OB-1", "check_id": "PC-04", "element_key": "#amount|p", "profile_id": target["profile_id"], "passed": False,
                "severity": "P2", "run_id": "R-1", "measurement": {"name": "arcmin", "value": 14, "unit": "arcmin", "threshold": 16, "comparator": ">="},
                "message_ko": "작음", "model": None, "selectors": ["#amount"], "context_selectors": []}]
        obs += [{"id": f"OB-{i + 2}", "check_id": "PC-04", "element_key": "#amount|p", "profile_id": p["profile_id"], "passed": True, "run_id": "R-1"}
                for i, p in enumerate(others)]
        findings = swarm.aggregate([{"scenario_id": "SC-T-topup", "observations": obs}], profiles)
        self.assertEqual(findings[0]["segments_affected"], ["SEG-senior"])
        text = report.render(findings, profiles, [], audience=doc, plan=plan)
        self.assertIn("세그먼트별 발견", text)
        self.assertIn("지하철 이용 고령층", text)


if __name__ == "__main__":
    unittest.main()
