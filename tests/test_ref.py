"""Bounded lookup behavior on real references and adversarial Markdown."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import _paths

SCRIPT = _paths.SKILL / "scripts/ref.py"
spec = importlib.util.spec_from_file_location("skill_ref", SCRIPT)
ref = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = ref
spec.loader.exec_module(ref)


class ReferenceLookupTests(unittest.TestCase):
    def render(self, markdown, section_id=None):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "reference.md"
            path.write_text(markdown, encoding="utf-8")
            return ref.reference_output(path, section_id)

    def test_numbered_section_includes_children_and_heading_path_only(self):
        text = "# Root\n## 17. Policy\nintro\n### 17.1 Entries\nkept\n#### Leaf\nchild\n### 17.2 Stop\nomitted\n"
        result = self.render(text, "17.1")
        self.assertIn("Heading path: Root > 17. Policy > 17.1 Entries", result)
        self.assertIn("kept", result)
        self.assertIn("child", result)
        self.assertNotIn("omitted", result)
        self.assertNotIn("intro", result)

    def test_named_channel_explicit_anchor_and_setext_ids(self):
        text = "Root\n====\n## L16 Terms\na\n### `naver-blog` 네이버\nb\n## Custom {#chosen}\nc\n<a id=\"legacy\"></a>\n## Old\nd\n"
        for identifier, expected in (("L16", "a"), ("naver-blog", "b"), ("chosen", "c"), ("legacy", "d")):
            self.assertIn(expected, self.render(text, identifier))
        ids = [h.section_id for h in ref.parse_headings(text)]
        self.assertEqual(ids, ["root", "L16", "naver-blog", "chosen", "legacy"])

    def test_fences_frontmatter_and_indented_code_do_not_create_headings(self):
        text = "---\nname: sample\n---\n# Real\n````md\n## Fake\n```\n## Also fake\n````\n~~~\n## Hidden\n~~~\n    ## Indented\n    Code title\n----\n## 2. Visible\nbody\n"
        self.assertEqual([h.section_id for h in ref.parse_headings(text)], ["real", "2"])

    def test_table_check_and_standard_ids_keep_context_and_exclude_other_rows(self):
        text = "# Checks\n## Perception\n| ID | Basis | Rule |\n| --- | --- | --- |\n| PC-01 | measured | contrast |\n| PC-02 | model | other |\n## Standards\n| Item | Rule |\n| --- | --- |\n| [6.1.3][standard] Target | size |\n"
        result = self.render(text, "PC-01")
        self.assertIn("Heading path: Checks > Perception", result)
        self.assertIn("| ID | Basis | Rule |", result)
        self.assertIn("contrast", result)
        self.assertNotIn("PC-02", result)
        self.assertIn("size", self.render(text, "6.1.3"))
        self.assertIn("row PC-01", self.render(text))
        hidden = "# Root\n```md\n| ID | Rule |\n| --- | --- |\n| PC-99 | hidden |\n```\n"
        with self.assertRaises(ValueError):
            self.render(hidden, "PC-99")

    def test_real_check_and_standard_row_ids_are_bounded(self):
        for file, identifier in (("references/ergonomics/human-factors-checks.md", "PC-01"),
                                 ("references/persona-qa/kwcag-2.2.md", "6.1.3")):
            output = ref.reference_output(_paths.SKILL / file, identifier)
            self.assertIn(f"ID: {identifier}", output)
            self.assertLessEqual(len(output.encode()), ref.MAX_BYTES)

    def test_utf8_cap_includes_prefix_and_lists_subsections(self):
        text = "# 한글\n## 1. Parent\n" + "문자" * 2000 + "\n### 1.1 Small\nkept\n### 1.2 Other\nother\n"
        result = self.render(text, "1")
        self.assertLessEqual(len(result.encode()), ref.MAX_BYTES)
        self.assertIn("Section exceeds", result)
        self.assertIn("1.1", result)
        self.assertIn("1.2", result)
        self.assertNotIn("문자", result)
        self.assertIn("kept", self.render(text, "1.1"))

    def test_large_leaf_and_long_listing_stay_bounded(self):
        text = "# Root\n## leaf\n" + "한" * 4000
        self.assertIn("No subsections", self.render(text, "leaf"))
        text = "# Root\n" + "".join(f"## {i}. {'한' * 100}\n" for i in range(300))
        listing = self.render(text)
        self.assertLessEqual(len(listing.encode()), ref.MAX_BYTES)
        self.assertIn("299", listing)

    def test_unknown_and_ambiguous_id_never_return_unrelated_section(self):
        with self.assertRaisesRegex(ValueError, "Unknown"):
            self.render("# Root\n## 1. A\n", "missing")
        with self.assertRaisesRegex(ValueError, "Ambiguous"):
            self.render("# Root\n## 1. A\n## 1. B\n", "1")
        self.assertIn("heading", self.render("# heading\na\n# heading\nb\n", "heading-2"))

    def test_file_resolution_refuses_outside_skill_and_symlink_escape(self):
        with self.assertRaises(ValueError):
            ref.resolve_reference("../../RELEASE-CONTRACT.md")
        with self.assertRaises(ValueError):
            ref.resolve_reference("uxresearch/data/routes.json")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "skill"
            root.mkdir()
            outside = Path(directory) / "outside.md"
            outside.write_text("# Private")
            (root / "escape.md").symlink_to(outside)
            with mock.patch.object(ref, "SKILL_ROOT", root):
                with self.assertRaises(ValueError):
                    ref.resolve_reference("escape.md")
        self.assertEqual(ref.resolve_reference("references/research/public-page-access.md"),
                         (_paths.SKILL / "references/research/public-page-access.md").resolve())

    def test_real_document_ids_and_oversized_sections(self):
        for file, identifier in (("references/research/public-page-access.md", "17.1"),
                                 ("references/research/korea/legal-checklist.md", "L16"),
                                 ("references/research/korea/platform-map.md", "naver-blog")):
            with self.subTest(identifier=identifier):
                output = ref.reference_output(_paths.SKILL / file, identifier)
                self.assertLessEqual(len(output.encode()), ref.MAX_BYTES)
                self.assertIn(f"ID: {identifier}", output)

    def test_every_numbered_grading_reference_resolves_within_the_lookup_cap(self):
        grading = _paths.SKILL / "references/research/source-grading.md"
        citation = re.compile(r"`references/research/source-grading\.md`([^`\n]*)")
        checked = 0
        documents = [_paths.SKILL / "SKILL.md", *(_paths.SKILL / "references").rglob("*.md")]
        for path in documents:
            for match in citation.finditer(path.read_text(encoding="utf-8")):
                tail = match.group(1)
                first = re.match(r"(?:의)?\s*(\d+(?:-\d+)?)", tail)
                if first is None:
                    continue
                identifiers = set(re.findall(r"(\d+)절", tail))
                if "-" in first.group(1):
                    start, end = (int(value) for value in first.group(1).split("-"))
                    identifiers.update(str(value) for value in range(start, end + 1))
                else:
                    identifiers.add(first.group(1))
                for identifier in identifiers:
                    with self.subTest(document=path.relative_to(_paths.SKILL), section=identifier):
                        output = ref.reference_output(grading, identifier)
                        self.assertIn(f"ID: {identifier}\n", output)
                        self.assertLessEqual(len(output.encode()), ref.MAX_BYTES)
                        checked += 1
        self.assertGreater(checked, 20, "Numbered research routing must actually be exercised")

    def test_korean_grading_topic_links_return_the_rules_they_name(self):
        grading = _paths.SKILL / "references/research/source-grading.md"
        # Section existence alone does not catch a real but semantically wrong
        # destination such as downgrades being cited as the fit table.
        topics = (("statistics.md", "적합도 표", "| segment_share |"),
                  ("statistics.md", "중립 분모", "never denominators"),
                  ("promotion.md", "하향 조건", "Confirmed promotion/affiliate/seller tie"),
                  ("promotion.md", "독립 단위", "attested thread key"))
        for filename, label, required_rule in topics:
            text = (_paths.SKILL / "references/research/korea" / filename).read_text(encoding="utf-8")
            target = re.search(r"(\d+)절\(" + re.escape(label) + r"\)", text)
            self.assertIsNotNone(target, label)
            output = ref.reference_output(grading, target.group(1))
            self.assertIn(required_rule, output, f"{filename}: {label} routes to the wrong rule")

    def test_promotion_gate_examples_are_executable_cli_contracts(self):
        from uxresearch.cli import build_parser

        text = (_paths.SKILL / "references/research/korea/promotion.md").read_text(encoding="utf-8")
        commands = [shlex.split(line) for line in text.splitlines()
                    if line.startswith("python3 scripts/ux_research.py ")]
        self.assertTrue(commands, "Promotion review must use the implemented gate")
        parser = build_parser()
        for command in commands:
            arguments = parser.parse_args(command[2:])
            self.assertEqual(arguments.command, "gate")
            self.assertEqual(arguments.run, "RUN")
            self.assertEqual(arguments.bundle, Path("RUN/bundle.json"))
        self.assertTrue(any("--write-bundle" in command for command in commands))

    def test_platform_record_joins_every_overlapping_terms_entry(self):
        result = json.loads(ref.platform_output("naver-cafe"))
        entries = {e["id"]: e for e in result["terms_entries"]}
        self.assertEqual(set(entries), {"naver-terms", "naver-cafe-bulk-notice"})
        self.assertTrue(all(e["lift_requires"] == "written_permission" for e in entries.values()))
        self.assertEqual(entries["naver-cafe-bulk-notice"]["effective_from"], "2026-08-25")
        self.assertNotIn("audience", result)
        self.assertLessEqual(len(ref.platform_output("naver-cafe").encode()), ref.MAX_BYTES)

    def test_every_packaged_channel_is_valid_compact_json(self):
        data = json.loads((_paths.SKILL / "uxresearch/data/korea-platforms.json").read_text())
        for channel in data["platforms"]:
            with self.subTest(channel=channel["id"]):
                output = ref.platform_output(channel["id"])
                self.assertEqual(json.loads(output)["id"], channel["id"])
                self.assertLessEqual(len(output.encode()), ref.MAX_BYTES)
        with self.assertRaisesRegex(ValueError, "Unknown channel"):
            ref.platform_output("made-up")

    def test_cli_works_from_unrelated_directory_and_reports_usage_errors(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run([sys.executable, str(SCRIPT), "references/shared/causal-chain.md", "1"],
                                    cwd=directory, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Required chain", result.stdout)
        result = subprocess.run([sys.executable, str(SCRIPT), "platform", "missing"], capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, b"")
        self.assertLessEqual(len(result.stderr), ref.MAX_BYTES)


if __name__ == "__main__":
    unittest.main()
