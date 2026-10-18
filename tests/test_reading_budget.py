"""Initial reading closure, conditional switches, and the research command interface."""
from __future__ import annotations

import itertools
import json
import re
import subprocess
import sys
import unittest

import _paths

SKILL = _paths.SKILL
MANIFEST = SKILL / "references/reading.json"
COMMANDS = {"start", "read", "ingest", "robots", "author-key", "merge", "gate",
            "report-check", "export-audience", "minimize", "close", "plan",
            "persona-starter", "export-personas", "persona-intake"}


def documents():
    yield SKILL / "SKILL.md"
    yield from sorted((SKILL / "references").rglob("*.md"))


def research_commands(text):
    # Only actual CLI mentions, not generic words such as a discovery phase.
    return set(re.findall(r"\bux_research\.py[ \t\r\n]+([a-z][a-z0-9-]*)(?![a-z0-9-])", text))


def whole_lookup_reads(text, lookup_only):
    """Find imperative whole-file loads; explicit bounded section/ID lookup is valid."""
    problems = []
    # Join soft wraps, preserve paragraphs; code examples are checked for cat-style whole reads too.
    for paragraph in re.split(r"\n\s*\n", text):
        joined = re.sub(r"\s+", " ", paragraph)
        for file in lookup_only:
            if file not in joined:
                continue
            at = joined.index(file)
            before, after = joined[max(0, at - 100):at], joined[at:at + len(file) + 130]
            if re.search(r"\b(?:cat|read_text|read_bytes)\b[^.;]*$", before, re.I):
                problems.append(file)
                continue
            directive = re.search(r"\b(?:read|load|open|consult|follow|use)\b[^.;|]*$", before, re.I)
            if not directive:
                continue
            context = before[directive.start():] + after
            if re.search(r"\b(?:whole|entire|in full|every line)\b", context, re.I):
                problems.append(file)
            elif not re.search(r"(?:\b(?:section|sections|lookup|look up|by ID|by item|fields|options)\b|\b\d+(?:\.\d+)*\b)", context, re.I):
                problems.append(file)
    return sorted(set(problems))


def closure(manifest, mode, enabled=(), external=False):
    files = set(manifest["modes"][mode]["before_first_action"])
    if external:
        files.update(manifest["modes"][mode]["before_external_page"])
    for switch in enabled:
        rule = manifest["korean_switches"][switch]
        if mode in rule["modes"]:
            files.update(rule["files"])
    return files


class ReadingBudgetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_manifest_covers_all_modes_and_real_unique_files(self):
        self.assertEqual(set(self.manifest["modes"]), {"research", "persona-qa", "ergonomics", "loop"})
        for mode, rule in self.manifest["modes"].items():
            self.assertIn("SKILL.md", rule["before_first_action"])
            self.assertIn(f"references/{mode}/workflow.md", rule["before_first_action"])
            for key in ("before_first_action", "before_external_page", "lookup_only"):
                self.assertEqual(len(rule[key]), len(set(rule[key])), (mode, key))
                for file in rule[key]:
                    self.assertTrue((SKILL / file).is_file(), file)
            self.assertFalse(set(rule["before_first_action"]) & set(rule["lookup_only"]), mode)

    def test_skill_and_small_card_sizes(self):
        limits = self.manifest["limits"]
        size = (SKILL / "SKILL.md").stat().st_size
        self.assertLessEqual(size, limits["skill_ceiling"])
        self.assertGreaterEqual(size, limits["skill_target_min"])
        self.assertLessEqual(size, limits["skill_target_max"])
        for file, cap in self.manifest["card_limits"].items():
            with self.subTest(file=file):
                self.assertLessEqual((SKILL / file).stat().st_size, cap)

    def test_all_initial_closures_with_switches_and_earliest_external_page(self):
        switches = list(self.manifest["korean_switches"])
        for mode in self.manifest["modes"]:
            for n in range(len(switches) + 1):
                for enabled in itertools.combinations(switches, n):
                    for external in (False, True):
                        files = closure(self.manifest, mode, enabled, external)
                        total = sum((SKILL / file).stat().st_size for file in files)
                        substantive_ko = set(enabled) - {"report_language"}
                        cap = self.manifest["limits"]["korean" if substantive_ko else "base"]
                        with self.subTest(mode=mode, switches=enabled, external=external, bytes=total):
                            self.assertLessEqual(total, cap, " + ".join(sorted(files)))

    def test_loop_first_provider_closures_fit_before_search_or_browser(self):
        switches = list(self.manifest["korean_switches"])
        for provider, variant in self.manifest["modes"]["loop"]["first_provider_variants"].items():
            for n in range(len(switches) + 1):
                for enabled in itertools.combinations(switches, n):
                    active = set(enabled) - set(variant["defer_switches"])
                    for external in (False, True):
                        files = closure(self.manifest, "loop", active, external) | set(variant["files"])
                        total = sum((SKILL / file).stat().st_size for file in files)
                        cap = self.manifest["limits"]["korean" if active - {"report_language"} else "base"]
                        with self.subTest(provider=provider, switches=enabled, external=external, bytes=total):
                            self.assertLessEqual(total, cap, " + ".join(sorted(files)))

    def test_product_improvement_is_a_conditional_qa_entry(self):
        guide = "references/loop/product-improvement.md"
        rule = self.manifest["modes"]["loop"]
        variant = rule["first_provider_variants"]["product-improvement"]
        self.assertEqual(set(variant["files"]),
                         {guide, "references/persona-qa/workflow.md"})
        self.assertIn("research_channels_or_users", variant["defer_switches"])
        self.assertIn(guide, self.manifest["card_limits"])
        for component in self.manifest["modes"].values():
            self.assertNotIn(guide, component["before_first_action"])
        self.assertEqual(whole_lookup_reads((SKILL / guide).read_text(),
                                            rule["lookup_only"]), [])

    def test_language_switch_adds_no_channel_or_qa_reading(self):
        for mode in self.manifest["modes"]:
            self.assertEqual(closure(self.manifest, mode), closure(self.manifest, mode, ["report_language"]))
        self.assertEqual(self.manifest["korean_switches"]["product_under_qa"]["files"],
                         ["references/persona-qa/kwcag-card.md"])

    def test_research_access_and_evidence_are_unconditional(self):
        rule = self.manifest["modes"]["research"]
        for card in ("references/shared/access-card.md", "references/shared/evidence-card.md"):
            self.assertIn(card, rule["before_first_action"])
        for mode in ("persona-qa", "ergonomics", "loop"):
            self.assertIn("references/shared/access-card.md", self.manifest["modes"][mode]["before_external_page"])

    def test_router_and_mode_cards_do_not_load_lookup_only_files_whole(self):
        for mode, rule in self.manifest["modes"].items():
            for file in ("SKILL.md", f"references/{mode}/workflow.md"):
                with self.subTest(file=file):
                    self.assertEqual(whole_lookup_reads((SKILL / file).read_text(), rule["lookup_only"]), [])

    def test_phase_zero_references_are_manifested_or_bounded_lookups(self):
        for mode, rule in self.manifest["modes"].items():
            permitted = closure(self.manifest, mode, self.manifest["korean_switches"], external=True)
            permitted.update(rule["lookup_only"])
            permitted.update(rule["later_conditions"]["grading_community_evidence"])
            router_files = {f for switch in self.manifest["korean_switches"].values() for f in switch["files"]}
            for file in ("SKILL.md", f"references/{mode}/workflow.md"):
                text = (SKILL / file).read_text()
                phase = re.split(r"^## Phase 0[^\n]*\n", text, maxsplit=1, flags=re.M)[1]
                phase = re.split(r"^## ", phase, maxsplit=1, flags=re.M)[0]
                named = set(re.findall(r"`([^`\n]+\.md)`", phase))
                allowed = permitted | router_files if file == "SKILL.md" else permitted
                self.assertFalse(named - allowed, (file, sorted(named - allowed)))

    def test_lookup_instruction_detector_catches_regressions(self):
        file = "references/research/source-grading.md"
        for bad in (f"Read `{file}` before searching.", f"Load [{file}]({file}) in full.",
                    f"Read\n`{file}` first.", f"cat {file}"):
            self.assertEqual(whole_lookup_reads(bad, [file]), [file], bad)
        for good in (f"Look up `{file}` section 4.", f"Read `{file}` by section.",
                     f"Use `{file}` by ID.", f"| Grade? | `{file}` 7 |"):
            self.assertEqual(whole_lookup_reads(good, [file]), [], good)

    def test_documents_name_only_contract_research_commands(self):
        self.assertEqual(set(self.manifest["research_commands"]), COMMANDS)
        problems = []
        for file in documents():
            unknown = research_commands(file.read_text()) - COMMANDS
            if unknown:
                problems.append(f"{file.relative_to(SKILL)}: {', '.join(sorted(unknown))}")
        self.assertEqual(problems, [], "\n".join(problems))

    def test_command_scan_ignores_flags_and_detects_unknown_names(self):
        self.assertEqual(research_commands("ux_research.py --help; ux_research.py <command> --help"), set())
        self.assertEqual(research_commands("python3 scripts/ux_research.py gate --write-bundle"), {"gate"})
        self.assertEqual(research_commands("`ux_research.py\n discover`"), {"discover"})

    def test_contract_engine_commands_are_available(self):
        result = subprocess.run([sys.executable, str(SKILL / "scripts/ux_research.py"), "--help"],
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        choices = re.search(r"\{([a-z0-9,-]+)\}", result.stdout)
        self.assertIsNotNone(choices)
        missing = COMMANDS - set(choices.group(1).split(","))
        self.assertEqual(missing, set(), "Engine package still needs: " + ", ".join(sorted(missing)))


if __name__ == "__main__":
    unittest.main()
