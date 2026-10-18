"""CLI tests for `ergo_qa.py personas`: standalone audiences stay flag-free, research-origin
audiences compose only through the run's fresh gate (--run/--bundle/--gate)."""

from __future__ import annotations

import contextlib
import copy
import io
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
import _paths  # noqa: E402,F401  (puts the skill folder on sys.path)

import engine_release_factory as f  # noqa: E402
from ergoqa.cli import main as ergo_main  # noqa: E402
from uxresearch.canonical import byte_digest, canonical  # noqa: E402
from uxresearch.cli import main as research_main  # noqa: E402
from uxresearch.merge import import_identity  # noqa: E402
from uxresearch.storage import atomic, read_json  # noqa: E402

EXAMPLE = _paths.SKILL / "examples" / "audience" / "transit-card.audience.json"

# Invented offline text for the enriched fixture: the printed numbers (20 users, 60%, 40%,
# 100%) are the literals the age/device value checks quote.
SAMPLE_TEXT = ("Illustrative measurement: business operators completed order lookup in a "
               "diagnostic sample of 20 users. 60% are in their 30s and 40% are in their 40s. "
               "100% used a Galaxy S24. This invented fixture is for offline validation.")
EXCERPT = ("business operators completed order lookup in a diagnostic sample of 20 users. "
           "60% are in their 30s and 40% are in their 40s. 100% used a Galaxy S24.")


def run_ergo(*argv: str) -> tuple[int, str, str]:
    with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()) as err:
        code = ergo_main(list(argv))
    return code, out.getvalue(), err.getvalue()


class ResearchRuns(unittest.TestCase):
    """Builds gated offline research runs (invented data, never real research)."""

    def write(self, run: Path, name: str, value) -> None:
        atomic(run / name, value if isinstance(value, bytes) else canonical(value))

    def command(self, name: str, run: Path, *extra: str, returns: list[Path] | None = None) -> int:
        args = [name, "--run", str(run)]
        if name == "merge":
            args += ["--manifest", str(run / "axes.json"), "--search-ledger", str(run / "search-ledger.jsonl"),
                     "--imports", str(run / "sanitized-imports.json"),
                     "--returns", *[str(p) for p in (returns or [run / "returns/editors.json"])]]
        else:
            args += ["--bundle", str(run / "bundle.json")]
        if name == "export-audience":
            args += ["--gate", str(run / "gate.json"), "--audience-id", "AU-diagnostic-operators"]
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return research_main(args + list(extra), clock=lambda: f.CLOCK)

    def plain_gated_run(self, root: Path) -> Path:
        run = f.fixture.build(root / "run", clock=lambda: f.CLOCK)
        self.assertEqual(self.command("merge", run), 0)
        self.assertEqual(self.command("gate", run), 0)
        return run

    def enriched_run(self, root: Path) -> Path:
        """Fixture run whose gate also exports age bands, a device mix and task fields."""
        run = f.fixture.build(root / "run", clock=lambda: f.CLOCK)
        returned = read_json(run / "returns/editors.json")
        imports = read_json(run / "sanitized-imports.json")
        manifest = read_json(run / "axes.json")
        (run / "sample.txt").write_bytes(SAMPLE_TEXT.encode())
        imp = imports["imports"][0]
        imp["content_sha256"] = byte_digest(SAMPLE_TEXT.encode())
        imp["import_id"] = import_identity(imp)
        returned["sources"][0]["provenance"].update(import_id=imp["import_id"], content_sha256=imp["content_sha256"])
        excerpt = returned["excerpts"][0]
        excerpt.update(capture_ref=imp["import_id"], excerpt=EXCERPT)
        day = returned["sources"][0]["published_at"]
        den = dict(population="business operators", period_start="2026-09-01", period_end=day,
                   product_relation="product_users", sampling_frame="neutral census", n=20, method="census",
                   unit="percent", value_as_printed="20 users", interpretation="product_measure")
        excerpt["denominator"] = den
        excerpt["scope"].update(population="business operators", period_start="2026-09-01", period_end=day,
                                product_relation="product_users")
        # Weight values (age_bands, devices) make their claims counter-search required: declare a
        # counter assignment, log its call in the ledger and return an empty completed part for it.
        manifest["axes"][0]["assignments"].append(dict(assignment_id="counter-1", reader_id="reader-1",
                                                       round=0, purpose="counter_search"))
        call = copy.deepcopy(returned["queries_run"][0])
        call.update(call_id="Q-0000000000000002", phase="counter_search", assignment_id="counter-1", results_n=0,
                    queries=[dict(q="diagnostic operator age mix contrary evidence", lang="en")])
        counter_return = dict(schema_version="ux-reader-return.v1", run_id=returned["run_id"], return_id="return-counter",
                              axis=dict(axis_id="product", assignment_id="counter-1", reader_id="reader-1", round=0,
                                        part_index=1, part_count=1, completion="complete",
                                        audience_questions=["segments"]),
                              queries_run=[call], search_count=1, sources=[], excerpts=[], candidate_claims=[],
                              expand_leads=[], dead_ends=[],
                              tail_reason="The counter search completed with no contrary diagnostic result.",
                              gaps=[], budget_used=dict(searches=1, document_requests=0, policy_requests=0,
                                                        request_fetch_ids=[]))
        counter = dict(call_ids=["Q-0000000000000002"], read_source_ids=[], counter_evidence_ids=[],
                       outcome="none_found", summary="No contrary diagnostic result found.", resolution_id=None)
        subject = dict(segment_id="operators", task_id=None, condition_id=None, context_id=None, pain_point_id=None)
        base = dict(counter_excerpt_ids=[], context_excerpt_ids=[], observation_ids=[], scope=excerpt["scope"],
                    about_current_version=False, stakes="normal", scenario_priorities=[])
        returned["candidate_claims"] += [
            dict(base, local_id="claim-age", claim_kind="segment_share",
                 statement="Diagnostic analytics record the operators age mix.", excerpt_ids=["excerpt"],
                 subject=subject, counter_search=counter,
                 audience_values=[dict(join=dict(segment_id="operators", entity_kind="segment", entity_id="operators",
                                                 field="age_bands"),
                                       value={"30s": 0.6, "40s": 0.4}, denominator_evidence_ids=["excerpt"],
                                       value_checks=[dict(pointer="/30s", evidence_id="excerpt", value_as_printed="60%",
                                                          conversion="percent_to_fraction", numerator_as_printed=None,
                                                          denominator_as_printed=None),
                                                     dict(pointer="/40s", evidence_id="excerpt", value_as_printed="40%",
                                                          conversion="percent_to_fraction", numerator_as_printed=None,
                                                          denominator_as_printed=None)])]),
            dict(base, local_id="claim-devices", claim_kind="device_mix",
                 statement="Diagnostic analytics record the operators device mix.", excerpt_ids=["excerpt"],
                 subject=subject, counter_search=copy.deepcopy(counter),
                 audience_values=[dict(join=dict(segment_id="operators", entity_kind="segment", entity_id="operators",
                                                 field="devices"),
                                       value={"galaxy-s24": 1.0}, denominator_evidence_ids=["excerpt"],
                                       value_checks=[dict(pointer="/galaxy-s24", evidence_id="excerpt",
                                                          value_as_printed="100%", conversion="percent_to_fraction",
                                                          numerator_as_printed=None, denominator_as_printed=None)])]),
            dict(base, local_id="claim-task", claim_kind="task",
                 statement="Diagnostic analytics record the operators lookup task.", excerpt_ids=["excerpt"],
                 subject=dict(subject, task_id="lookup"), counter_search=None,
                 audience_values=[dict(join=dict(segment_id="operators", entity_kind="task", entity_id="lookup",
                                                 field="goal_ko"), value="주문 조회", denominator_evidence_ids=[],
                                       value_checks=[]),
                                  dict(join=dict(segment_id="operators", entity_kind="task", entity_id="lookup",
                                                 field="frequency"), value="daily",
                                       denominator_evidence_ids=["excerpt"], value_checks=[])]),
        ]
        self.write(run, "sanitized-imports.json", imports)
        self.write(run, "axes.json", manifest)
        self.write(run, "returns/editors.json", returned)
        self.write(run, "returns/counter.json", counter_return)
        self.write(run, "search-ledger.jsonl",
                   canonical(returned["queries_run"][0]) + b"\n" + canonical(call) + b"\n")
        self.assertEqual(self.command("merge", run, returns=[run / "returns/editors.json",
                                                             run / "returns/counter.json"]), 0)
        self.assertEqual(self.command("gate", run), 0)
        self.assertEqual(self.command("export-audience", run), 0)
        return run

    def completed_audience(self, run: Path, root: Path) -> Path:
        """Author the completed ergo-audience.v1 from the exported draft's exact provenance."""
        draft = read_json(run / "audience.draft.json")
        bundle = read_json(run / "bundle.json")
        gate = read_json(run / "gate.json")
        proofs = draft["value_provenance"]

        def value_of(join: dict) -> dict:
            return next(p for p in proofs if p["join"] == join)

        seg = draft["segments"][0]
        rows = {row["claim_id"]: row for row in gate["claims"]}
        confidence = min((rows[cid]["confidence"] for cid in seg["existence_claim_ids"]),
                         key=lambda c: {"medium": 0, "high": 1}[c])
        exists = next(c for c in bundle["records"]["claims"] if c["claim_kind"] == "segment_exists")
        ev = next(e for e in bundle["records"]["evidence"] if e["id"] == exists["evidence_ids"][0])
        owner = [dict(join=dict(segment_id="operators", entity_kind="task", entity_id="lookup", field="concrete_data"),
                      value={"order": "R-124"}, basis="owner_decision", bundle_id=bundle["bundle_id"], claim_ids=[],
                      evidence_ids=[], source_ids=[], observation_ids=[], input_sha256s={},
                      decision_ref="owner-diagnostic", reason="Owner chose the diagnostic test values."),
                 dict(join=dict(segment_id="operators", entity_kind="task", entity_id="lookup", field="criticality"),
                      value="access", basis="owner_decision", bundle_id=bundle["bundle_id"], claim_ids=[],
                      evidence_ids=[], source_ids=[], observation_ids=[], input_sha256s={},
                      decision_ref="owner-diagnostic", reason="Owner chose the diagnostic criticality.")]
        doc = {
            "schema_version": "ergo-audience.v1",
            "audience_id": draft["audience_id"],
            "product": {"name": draft["product"]["name"]},
            "sources": draft["sources"],
            "segments": [{
                "segment_id": "operators",
                "name_ko": value_of(dict(segment_id="operators", entity_kind="segment", entity_id="operators",
                                         field="name_ko"))["value"],
                "priority": value_of(dict(segment_id="operators", entity_kind="segment", entity_id="operators",
                                          field="priority"))["value"],
                "confidence": confidence,
                "share": {"value": None, "basis": "unknown", "source_ids": []},
                "evidence": [{"source_id": draft["sources"][0]["source_id"], "claim": exists["statement"],
                              "kind": "statistic", "quote": ev["excerpt"], "quote_basis": "document"}],
                "age_bands": value_of(dict(segment_id="operators", entity_kind="segment", entity_id="operators",
                                           field="age_bands"))["value"],
                "devices": value_of(dict(segment_id="operators", entity_kind="segment", entity_id="operators",
                                         field="devices"))["value"],
                "tasks": [{"task_id": "lookup",
                           "goal_ko": value_of(dict(segment_id="operators", entity_kind="task", entity_id="lookup",
                                                    field="goal_ko"))["value"],
                           "frequency": value_of(dict(segment_id="operators", entity_kind="task", entity_id="lookup",
                                                      field="frequency"))["value"],
                           "concrete_data": owner[0]["value"], "criticality": owner[1]["value"],
                           "source_ids": [draft["sources"][0]["source_id"]]}],
            }],
            "value_provenance": list(proofs) + owner,
        }
        path = root / "audience.completed.json"
        path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return path


class StandalonePersonasCLI(unittest.TestCase):
    def test_standalone_audience_composes_without_research_refs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "profiles.json"
            code, stdout, stderr = run_ergo("personas", "--audience", str(EXAMPLE), "--budget", "4", "--out", str(out))
            self.assertEqual(code, 0, stderr)
            plan = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(plan["strategy"], "audience_composed")
            self.assertEqual(len(plan["profiles"]), 4)
            self.assertIn("AP-01", stdout)


class ResearchPersonasCLI(ResearchRuns):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="ergo-personas-cli-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.run = self.enriched_run(self.root)
        self.audience = self.completed_audience(self.run, self.root)
        self.refs = ["--run", str(self.run), "--bundle", str(self.run / "bundle.json"),
                     "--gate", str(self.run / "gate.json")]

    def personas(self, *extra: str) -> tuple[int, str, str]:
        out = self.root / "out" / "profiles.json"
        code, stdout, stderr = run_ergo("personas", "--audience", extra[0], "--budget", "4", "--out", str(out),
                                        *extra[1:])
        return code, stdout, stderr

    def test_completed_research_audience_composes_through_the_fresh_gate(self) -> None:
        code, stdout, stderr = self.personas(str(self.audience), *self.refs)
        self.assertEqual(code, 0, stderr)
        plan = json.loads((self.root / "out" / "profiles.json").read_text(encoding="utf-8"))
        self.assertEqual(plan["audience_id"], "AU-diagnostic-operators")
        self.assertTrue(plan["profiles"])
        self.assertEqual({p["audience_ref"]["segment_id"] for p in plan["profiles"]}, {"operators"})
        self.assertTrue(all(p["attributes"]["device_id"] == "galaxy-s24" for p in plan["profiles"]))
        self.assertIn("AP-01", stdout)

    def test_research_audience_without_refs_is_rejected(self) -> None:
        code, stdout, stderr = self.personas(str(self.audience))
        self.assertEqual(code, 2, stdout)
        self.assertIn("requires a fresh gate and completed value check", stderr)
        self.assertFalse((self.root / "out" / "profiles.json").exists())

    def test_partial_refs_are_rejected(self) -> None:
        code, stdout, stderr = self.personas(str(self.audience), "--run", str(self.run))
        self.assertEqual(code, 2, stdout)
        self.assertIn("--run, --bundle and --gate are required together", stderr)
        code, _, stderr = self.personas(str(self.audience), "--gate", str(self.run / "gate.json"))
        self.assertEqual(code, 2)
        self.assertIn("--run, --bundle and --gate are required together", stderr)

    def test_incomplete_draft_is_rejected_even_with_refs(self) -> None:
        code, stdout, stderr = self.personas(str(self.run / "audience.draft.json"), *self.refs)
        self.assertEqual(code, 2, stdout)
        self.assertIn("Research audience is incomplete or stale for composition", stderr)

    def test_stale_gate_is_rejected(self) -> None:
        run = self.plain_gated_run(self.root / "stale")
        bundle = read_json(run / "bundle.json")
        bundle["research"]["gaps"].append(dict(code="coverage_note", note="A new uncertainty after the gate"))
        self.write(run, "bundle.json", bundle)
        audience = self.audience  # research-origin file; the run's gate never saw it, but staleness fires first
        code, stdout, stderr = self.personas(str(audience), "--run", str(run), "--bundle", str(run / "bundle.json"),
                                             "--gate", str(run / "gate.json"))
        self.assertEqual(code, 2, stdout)
        self.assertIn("changed after the committed gate", stderr)

    def test_mismatched_bundle_is_rejected(self) -> None:
        other = self.plain_gated_run(self.root / "other")
        code, stdout, stderr = self.personas(str(self.audience), "--run", str(self.run),
                                             "--bundle", str(other / "bundle.json"), "--gate", str(self.run / "gate.json"))
        self.assertEqual(code, 2, stdout)
        self.assertIn("changed after the committed gate", stderr)

    def test_missing_gate_is_rejected(self) -> None:
        run = f.fixture.build(self.root / "ungated" / "run", clock=lambda: f.CLOCK)
        self.assertEqual(self.command("merge", run), 0)
        code, stdout, stderr = self.personas(str(self.audience), "--run", str(run),
                                             "--bundle", str(run / "bundle.json"), "--gate", str(run / "gate.json"))
        self.assertEqual(code, 2, stdout)
        self.assertIn("A required committed engine artifact is absent", stderr)

    def test_gate_path_outside_the_run_is_rejected(self) -> None:
        code, stdout, stderr = self.personas(str(self.audience), "--run", str(self.run),
                                             "--bundle", str(self.run / "bundle.json"),
                                             "--gate", str(self.root / "gate.json"))
        self.assertEqual(code, 2, stdout)
        self.assertIn("fixed committed gate.json", stderr)


if __name__ == "__main__":
    unittest.main()
