"""Opaque captures and the existing loop scratch layout remain usable."""
import json
import subprocess
import sys
import unittest

from _paths import SKILL
from loop_fill_fixture import FillFixture
from uxloop.demo_factory import write_json
from uxloop.io import sha


class FillBoundaryTests(unittest.TestCase):
    def fill(self, fixture: FillFixture) -> subprocess.CompletedProcess[str]:
        write_json(fixture.draft, fixture.packet)
        command = [
            sys.executable, str(SKILL / "scripts/ux_loop.py"), "fill", str(fixture.draft),
            "--evidence-root", str(fixture.evidence), "--workspace", str(fixture.site),
            "--out", str(fixture.out),
        ]
        print("COMMAND:", repr(command), flush=True)
        return subprocess.run(command, capture_output=True, text=True, timeout=30)

    def test_literal_marker_bytes_in_capture_are_not_placeholders(self):
        fixture = FillFixture(self)
        artifact = next(a for a in fixture.packet["artifacts"] if a["kind"] == "screenshot")
        path = fixture.evidence / artifact["path"]
        raw = path.read_bytes() + b"\n<!-- literal @autobot capture annotation -->\n"
        path.write_bytes(raw)
        artifact["sha256"] = "@auto"
        result = self.fill(fixture)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(path.read_bytes(), raw)
        filled = json.loads(fixture.out.read_text())
        captured = next(a for a in filled["artifacts"] if a["id"] == artifact["id"])
        self.assertEqual(captured["sha256"], sha(raw))

    def test_existing_loop_scratch_parent_is_supported(self):
        fixture = FillFixture(self)
        scratch = fixture.root / ".ux-loop" / "scratch"
        scratch.mkdir(parents=True)
        moved = scratch / "evidence"
        fixture.evidence.rename(moved)
        fixture.evidence = moved
        fixture.draft = moved / "draft.json"
        fixture.out = moved / "filled.json"
        result = self.fill(fixture)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(fixture.out.read_bytes(), fixture.draft.read_bytes())


if __name__ == "__main__":
    unittest.main()
