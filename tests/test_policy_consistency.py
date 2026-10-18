"""Terms evidence is separate from lift policy; documentation and route data agree."""
from __future__ import annotations

import json
import re
import unittest

import _paths

SKILL = _paths.SKILL


def stale_terms_rules(text):
    """Return obsolete rules, independent of Markdown quoting and soft line breaks."""
    plain = re.sub(r"\s+", " ", text.replace("`", ""))
    patterns = (
        r"\bconfirmed\s+(?:terms\s+)?(?:entry|entries|restriction|restrictions)\s+(?:is|are)\s+never\s+(?:lifted|liftable)",
        r"\bconfirmed\s*[,;:]\s*never\s+lifted",
        r"\bnever\s+(?:offer\s+to\s+)?lift\s+(?:(?:a|an|the|any)\s+)?confirmed\b",
        r"\bonly\s+reported\s+(?:entry|entries|restrictions)\b.{0,60}\blift",
        r"\blift(?:s|ed)?\b.{0,60}\bonly\b.{0,20}\breported\b",
        r"\bwhen\s+the\s+route\s+table\s+marks\s+them\s+reported\b",
        r"confirmed.{0,40}(?:절대|영구).{0,30}(?:해제|풀\s*수)",
    )
    return [m.group(0) for pattern in patterns for m in re.finditer(pattern, plain, re.I)]


def entry_rows(markdown):
    """Parse the entries table in 17.1, ignoring the field definitions and prose."""
    section = markdown.split("### 17.1 Entries", 1)[1].split("### 17.2", 1)[0]
    entries = {}
    for line in section.splitlines():
        if not re.match(r"\|\s*`[a-z0-9-]+`\s*\|", line):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 5:
            continue
        identifier, hosts, status, lift, official = cells
        if status not in {"confirmed", "reported"}:
            continue
        identifier = identifier.strip("`")
        if identifier in entries:
            raise ValueError(f"Duplicate entry {identifier}")
        route = re.match(r"`([^`]+)`", official)
        entries[identifier] = {"hosts": sorted(h.strip().strip("`") for h in hosts.split(",")),
                               "status": status, "lift_requires": lift.strip("`"),
                               "official_route": route.group(1) if route else None}
    return entries


class TermsPolicyConsistencyTests(unittest.TestCase):
    def test_all_skill_documents_use_lift_requires_not_evidence_status(self):
        # READMEs are outside this package's quoted-text scope; the full skill is scanned.
        problems = []
        for path in sorted(SKILL.rglob("*.md")):
            if "node_modules" in path.parts:
                continue
            hits = stale_terms_rules(path.read_text(encoding="utf-8"))
            if hits:
                problems.append(f"{path.relative_to(SKILL)}: {'; '.join(hits)}")
        self.assertEqual(problems, [], "\n".join(problems))

    def test_detector_catches_obsolete_rules_without_banning_never_entries(self):
        for bad in ("A `confirmed` entry is never lifted.",
                    "Never offer to lift a\n`confirmed` entry.",
                    "Only reported entries may be lifted.",
                    "The check lifts only a reported entry.",
                    "Ask when the route table marks them `reported`."):
            self.assertTrue(stale_terms_rules(bad), bad)
        for good in ("Status confirmed records evidence only; lift_requires written_permission governs lifts.",
                     "YouTube: confirmed; lift_requires never prohibits a page lift.",
                     "Every overlapping entry needs a current user check and required written permission."):
            self.assertEqual(stale_terms_rules(good), [], good)

    def test_section_17_1_matches_every_route_entry(self):
        routes = json.loads((SKILL / "uxresearch/data/routes.json").read_text())
        documented = entry_rows((SKILL / "references/research/public-page-access.md").read_text())
        expected = {entry["id"]: {"hosts": sorted(entry["hosts"]), "status": entry["status"],
                                  "lift_requires": entry["lift_requires"],
                                  "official_route": entry.get("official_route")}
                    for entry in routes["terms_restricted"]}
        self.assertEqual(set(documented), set(expected))
        self.assertEqual(documented, expected)

    def test_entries_parser_detects_field_drift(self):
        sample = "### 17.1 Entries\n| `entry` | host.test, m.host.test | confirmed | `terms_check` | `api` (documented) |\n### 17.2 Stop\n"
        row = entry_rows(sample)["entry"]
        self.assertEqual(row, {"hosts": ["host.test", "m.host.test"], "status": "confirmed",
                               "lift_requires": "terms_check", "official_route": "api"})
        changed = entry_rows(sample.replace("terms_check", "never"))["entry"]
        self.assertNotEqual(changed, row)
        with self.assertRaises(ValueError):
            entry_rows(sample.replace("### 17.2 Stop", "| `entry` | host.test | reported | `never` | none |\n### 17.2 Stop"))

    def test_cafe_date_status_and_membership_exception_are_distinct(self):
        text = (SKILL / "references/persona-qa/community-to-test.md").read_text()
        cafe = next(line for line in text.splitlines() if line.startswith("| Naver Cafes"))
        self.assertIn("2026-08-25", cafe)
        self.assertIn("confirmed", cafe)
        self.assertIn("written_permission", cafe)
        self.assertNotIn("2026-08-31", cafe)
        self.assertIn("membership", cafe)


if __name__ == "__main__":
    unittest.main()
