"""Deterministic privacy boundaries for the research-to-loop projection."""
from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest

import engine_release_factory as f
from uxresearch import merge, minimize
from uxresearch.canonical import canonical, digest
from uxresearch.cli import main
from uxresearch.storage import atomic, read_json
from scripts.validate_bundle import validate_bundle


RUN_ID = "run-20261001T000001Z-abcdef"
IMPORT_ID = "IMP-e0ae6ee3ba38f0c8b382bbd96432cc6a94a64871293612040354f966f1872930"
OTHER_IMPORT_ID = "IMP-" + "a" * 20 + "01012345678" + "b" * 33


def attest(bundle):
    bundle["research"]["summary_attestations"] = [
        dict(record_id=record["id"], field=field, content_sha256=digest(record[field]),
             reviewed_by="self-test", reviewed_at="2026-10-01T00:00:01Z")
        for records in bundle["records"].values()
        for record in records
        for field in ("summary", "statement")
        if field in record
    ]


class MinimizePrivacy(unittest.TestCase):
    def bundle(self):
        source = f.source(1, "measured", summary="An invented aggregate source summary.")
        source["provenance"]["import_id"] = IMPORT_ID
        source["source_ref"] = f"team-import://{RUN_ID}/{IMPORT_ID}"
        evidence = f.evidence(1, source)
        bundle = f.bundle([source], [evidence], f.claim(support=[evidence["id"]]))
        bundle["research"]["run_id"] = RUN_ID
        return bundle

    def project(self, bundle):
        attest(bundle)
        return minimize.minimize(bundle, dict(bundle_input_sha256=digest(bundle),
                                              rules_version="source-grading-2026-10-01.1",
                                              mode="fixture"))

    def assert_identifiers_blocked(self, bundle):
        _, manifest = self.project(bundle)
        self.assertEqual(manifest["exit_code"], 1, manifest)
        self.assertIn("projection_identifiers", {issue["code"] for issue in manifest["issues"]})

    def test_digit_heavy_import_hash_minimizes_after_gate(self):
        # This fixed capture time produces a real import digest with a card-shaped digit run.
        clock = lambda: f.CLOCK + 1
        with tempfile.TemporaryDirectory(prefix="minimize-privacy-") as temporary:
            root = f.fixture.build(Path(temporary).resolve() / "run", clock=clock)

            def command(*args):
                with contextlib.redirect_stdout(io.StringIO()) as output:
                    code = main(list(args), clock=clock)
                return code, json.loads(output.getvalue())

            code, result = command("merge", "--run", str(root), "--manifest", str(root / "axes.json"),
                                   "--search-ledger", str(root / "search-ledger.jsonl"),
                                   "--imports", str(root / "sanitized-imports.json"),
                                   "--returns", str(root / "returns/editors.json"))
            self.assertEqual(code, 0, result)
            bundle = read_json(root / "bundle.json")
            source = bundle["records"]["sources"][0]
            self.assertEqual(source["provenance"]["import_id"], IMPORT_ID)
            self.assertTrue(merge.privacy_scan(source["source_ref"]))
            source["summary"] = "An invented aggregate supplied by the example team."
            attest(bundle)
            atomic(root / "bundle.json", canonical(bundle))
            code, result = command("gate", "--run", str(root), "--bundle", str(root / "bundle.json"),
                                   "--write-bundle")
            self.assertEqual(code, 0, result)
            code, result = command("minimize", "--run", str(root), "--bundle", str(root / "bundle.json"),
                                   "--gate", str(root / "gate.json"))
            self.assertEqual(code, 0, result)
            projected = read_json(root / "bundle.min.json")
            self.assertEqual(projected["records"]["sources"][0]["source_ref"], source["source_ref"])
            self.assertEqual(validate_bundle(projected), [])

    def test_only_exact_provenance_bound_source_reference_is_exempt(self):
        for mutation in ("run", "import", "kind", "missing", "query", "fragment", "external"):
            with self.subTest(mutation=mutation):
                bundle = self.bundle()
                source = bundle["records"]["sources"][0]
                if mutation == "run":
                    bundle["research"]["run_id"] = "run-20261001T000002Z-fedcba"
                elif mutation == "import":
                    source["provenance"]["import_id"] = OTHER_IMPORT_ID
                elif mutation == "kind":
                    source["provenance"]["kind"] = "fetch"
                elif mutation == "missing":
                    source.pop("provenance")
                elif mutation == "query":
                    source["source_ref"] += "?contact=person@example.com"
                elif mutation == "fragment":
                    source["source_ref"] += "#010-1234-5678"
                else:
                    source["source_ref"] = "https://01012345678.example"
                self.assert_identifiers_blocked(bundle)

    def test_authored_and_nested_personal_identifiers_remain_blocked(self):
        cases = ["person@example.com", "010-1234-5678", "4111 1111 1111 1111",
                 "계좌 123-456-78901", "@example-person", "https://example.test/member/person",
                 "118.235.12.34", "IP 118.235", f"team-import://{RUN_ID}/{IMPORT_ID}"]
        for value in cases:
            for group, field in (("sources", "summary"), ("evidence", "summary"), ("claims", "statement")):
                with self.subTest(value=value, group=group):
                    bundle = self.bundle()
                    bundle["records"][group][0][field] = "Contact details: " + value
                    self.assert_identifiers_blocked(bundle)
        bundle = self.bundle()
        bundle["records"]["claims"][0]["scope"]["context_id"] = "person@example.com"
        self.assert_identifiers_blocked(bundle)


if __name__ == "__main__":
    unittest.main()
