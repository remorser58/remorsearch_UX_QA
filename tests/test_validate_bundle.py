import copy
import json
import subprocess
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

import _paths  # noqa: F401  (puts the skill folder on sys.path)
from scripts.validate_bundle import validate_bundle


FIXTURES = Path(__file__).parent / "fixtures"
EXAMPLE = _paths.SKILL / "examples" / "bundle" / "minimal.json"


def load_fixture(name: str):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


class ValidateBundleTests(unittest.TestCase):
    def test_valid_bundle_passes(self):
        self.assertEqual(validate_bundle(load_fixture("valid-bundle.json")), [])

    def test_broken_reference_is_rejected(self):
        errors = validate_bundle(load_fixture("invalid-broken-ref.json"))
        self.assertTrue(any("unknown record" in error for error in errors))

    def test_synthetic_persona_cannot_support_real_user_preference(self):
        errors = validate_bundle(load_fixture("invalid-synthetic-claim.json"))
        self.assertTrue(any("synthetic persona" in error for error in errors))

    def test_verified_finding_requires_observation(self):
        errors = validate_bundle(load_fixture("invalid-verified-no-observation.json"))
        self.assertTrue(any("without an observation" in error for error in errors))

    def test_missing_id_is_rejected(self):
        errors = validate_bundle(load_fixture("invalid-missing-id.json"))
        self.assertTrue(any("id is required" in error for error in errors))

    def test_the_example_bundle_that_ships_with_the_skill_passes(self):
        self.assertEqual(validate_bundle(json.loads(EXAMPLE.read_text(encoding="utf-8"))), [])
        result = subprocess.run([sys.executable, str(_paths.SKILL / "scripts" / "validate_bundle.py"), str(EXAMPLE)],
                                capture_output=True, text=True, timeout=60)
        self.assertEqual((result.returncode, result.stdout.strip()), (0, "VALID: bundle-example-minimal"))

    def test_an_item_kept_past_its_retention_date_is_an_error(self):
        now = datetime(2026, 9, 30, 12, tzinfo=timezone.utc)
        bundle = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        source = bundle["records"]["sources"][0]
        source.update(access_basis="official_api", retention_until="2026-09-01T00:00:00Z")
        errors = validate_bundle(bundle, now=now)
        self.assertTrue(any("retention_until 2026-09-01T00:00:00Z has passed" in error for error in errors), errors)
        for still_kept in ("2026-10-30T00:00:00Z", "2026-09-30", "2026-09-30T13:00:00+00:00"):
            source["retention_until"] = still_kept  # a bare date is kept through that day
            self.assertEqual(validate_bundle(bundle, now=now), [], still_kept)
        for value, message in (("2026-09-29", "has passed"), ("soon", "ISO 8601")):
            source["retention_until"] = value
            self.assertTrue(any(message in error for error in validate_bundle(bundle, now=now)), value)
        missing = copy.deepcopy(bundle)
        del missing["records"]["sources"][0]["retention_until"]
        self.assertTrue(any("required for an official_api source" in error
                            for error in validate_bundle(missing, now=now)))


if __name__ == "__main__":
    unittest.main()
