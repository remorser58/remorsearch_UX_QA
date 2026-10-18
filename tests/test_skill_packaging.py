"""Packaging checks for the primary skill, bilingual install docs and bundled toolkit.

Three groups, all offline file checks:

  * SKILL.md must load in the hosts that read it: a plain one-line YAML description within the length limits,
    a valid name, Korean trigger words, and no byte-order marks in the files a host parses.
  * README.md and README.ko.md must say the same things under the same headings. Headings are read outside
    fenced code blocks, because a shell comment such as "# Codex" inside a fence is not a heading.
  * The original search toolkit ships inside the one Remorsearch skill, its source
    and methods retain their hashes, and relocated source installations can read it.
"""
from __future__ import annotations

import hashlib
import json
import os
import posixpath
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
import unittest
from pathlib import Path

import _paths  # noqa: F401  (puts the skill folder on sys.path)

REPO = _paths.REPO
SKILL = _paths.SKILL
README = REPO / "README.md"
README_KO = REPO / "README.ko.md"
SKILL_MD = SKILL / "SKILL.md"
BOM = b"\xef\xbb\xbf"

# The second-level headings of the English README, and the Korean heading each one maps to, in order.
SECTIONS = (
    ("What it does", "하는 일"),
    ("Install", "설치"),
    ("Use", "사용법"),
    ("Evidence rules", "근거 규칙"),
    ("Reading public pages", "공개 페이지 읽기"),
    ("Korean research", "한국어 리서치"),
    ("Repository layout", "저장소 구성"),
    ("Development", "개발"),
    ("Limits", "한계"),
    ("License", "라이선스"),
)
SKIPPED_DIRS = {"node_modules", "__pycache__", ".git", ".ux-loop", ".ux-research"}
# Runtime files belong to other packages; every routing-owned reference is scanned.
UNSCANNED_DIRS = ("drivers/", "ergoqa/")
REPO_PATH = re.compile(r"`((?:docs|tests|benchmarks)/[^`\n]*)`")
REMOVED_VARIABLE = re.compile(r"INSANE_[A-Z0-9_]+")
REMOVED_FIELD = "engine_opt_in"
YAML_INDICATORS = "-?:,[]{}#&*!|>'\"%@`"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def front_matter(text: str) -> dict:
    """The key and value of each line between the two opening '---' lines. Only 'key: value' lines are allowed."""
    lines = text.split("\n")
    if lines[0] != "---" or "---" not in lines[1:]:
        raise ValueError("the file does not start with a front matter block")
    fields = {}
    for line in lines[1:lines.index("---", 1)]:
        match = re.fullmatch(r"([a-z_][a-z0-9_-]*): (.*)", line)
        if not match:
            raise ValueError(f"not a plain 'key: value' line: {line[:60]!r}")
        fields[match.group(1)] = match.group(2)
    return fields


def plain_scalar_problems(value: str) -> list:
    """Reasons a value would not read back as the same plain (unquoted) YAML scalar."""
    problems = []
    if not value or value != value.strip():
        problems.append("empty, or has leading or trailing space")
    if value and value[0] in YAML_INDICATORS:
        problems.append(f"starts with the YAML indicator {value[0]!r}")
    if ": " in value or value.endswith(":"):
        problems.append("contains ': '")
    if " #" in value:
        problems.append("contains ' #'")
    if "<" in value or ">" in value:
        problems.append("contains an angle bracket")
    if any(ord(ch) < 32 for ch in value):
        problems.append("contains a control character")
    if value.lower() in {"true", "false", "null", "yes", "no", "on", "off", "~"} or re.fullmatch(r"[-+]?[\d.]+", value):
        problems.append("would be read as a boolean, null or number")
    return problems


def outside_fences(text: str):
    """(line number, line) for the lines of a Markdown text that are not inside a fenced code block."""
    fenced = False
    for number, line in enumerate(text.split("\n"), 1):
        if line.lstrip().startswith(("```", "~~~")):
            fenced = not fenced
            continue
        if not fenced:
            yield number, line


def headings(text: str) -> list:
    """(level, title) of every heading outside fenced code blocks."""
    found = []
    for _, line in outside_fences(text):
        match = re.match(r"(#{1,6})\s+(.+?)\s*#*\s*$", line)
        if match:
            found.append((len(match.group(1)), match.group(2)))
    return found


def sections(text: str) -> list:
    """(second-level title, start offset, end offset) of each '##' section of a Markdown text.

    Headings are read outside fenced code blocks. A section runs from its heading to the next second-level
    heading or the end of the text, and it includes its own fenced blocks.
    """
    spans, fenced, offset = [], False, 0
    for line in text.split("\n"):
        if line.lstrip().startswith(("```", "~~~")):
            fenced = not fenced
        elif not fenced:
            match = re.match(r"##\s+(.+?)\s*$", line)
            if match:
                if spans:
                    spans[-1][2] = offset
                spans.append([match.group(1), offset, len(text)])
        offset += len(line) + 1
    return [tuple(span) for span in spans]


def shell_commands(text: str) -> list:
    """The command lines (comments and blank lines left out) of every fenced 'sh' block."""
    commands = []
    for block in re.findall(r"^```sh\n(.*?)^```", text, flags=re.S | re.M):
        for line in block.split("\n"):
            if line.strip() and not line.lstrip().startswith("#"):
                commands.append(line.strip())
    return commands


def links(text: str) -> list:
    """The targets of the inline links outside fenced code blocks."""
    body = "\n".join(line for _, line in outside_fences(text))
    return re.findall(r"\]\(([^)\s]+)\)", body)


def paragraphs(text: str) -> list:
    """The paragraphs (blank-line-separated) of a Markdown text, fenced code blocks left out."""
    grouped, current = [], []
    for _, line in outside_fences(text):
        if line.strip():
            current.append(line)
        elif current:
            grouped.append("\n".join(current))
            current = []
    if current:
        grouped.append("\n".join(current))
    return grouped


def leaving_links(relative: str, text: str) -> list:
    """The Markdown links of a file that resolve outside the skill folder (its path is relative to it)."""
    problems = []
    for target in links(text):
        clean = target.split("#")[0]
        if not clean or re.match(r"(?:https?:|mailto:)", clean):
            continue
        resolved = posixpath.normpath(posixpath.join(posixpath.dirname(relative), clean))
        if resolved.startswith("../"):
            problems.append(f"link {target} leaves the skill folder")
    return problems


def bare_repo_paths(text: str) -> list:
    """Backticked docs/, tests/ or benchmarks/ paths whose paragraph does not say, in the same breath, that
    they are repository documents that are not installed."""
    problems = []
    for paragraph in paragraphs(text):
        lowered = paragraph.lower()
        for path in REPO_PATH.findall(paragraph):
            if not (("repositor" in lowered and "not installed" in lowered) or
                    ("저장소" in paragraph and "설치되지" in paragraph)):
                problems.append(f"`{path}` is not marked as a repository document that is not installed")
    return problems


def project_files():
    """The text files of the skill folder and the two READMEs."""
    for path in sorted(SKILL.rglob("*")):
        if path.is_file() and not SKIPPED_DIRS & set(path.relative_to(SKILL).parts):
            yield path
    yield README
    yield README_KO


def text_of(path: Path):
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None  # a binary file: an image, a font


class SkillFrontMatterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = SKILL_MD.read_bytes()
        cls.fields = front_matter(cls.raw.decode("utf-8"))

    def test_the_file_has_no_byte_order_mark(self):
        self.assertFalse(self.raw.startswith(BOM))
        self.assertTrue(self.raw.startswith(b"---\n"))

    def test_only_name_and_description_are_set(self):
        self.assertEqual(set(self.fields), {"name", "description"})

    def test_name_follows_the_naming_rules(self):
        name = self.fields["name"]
        self.assertRegex(name, r"^[a-z0-9-]{1,64}$")
        self.assertFalse(name.startswith("-") or name.endswith("-") or "--" in name)
        self.assertEqual(name, SKILL.name)  # the name is the folder name
        for reserved in ("anthropic", "claude"):
            self.assertNotIn(reserved, name)

    def test_description_is_within_the_length_limits(self):
        description = self.fields["description"]
        self.assertLessEqual(len(description), 1024)
        self.assertLessEqual(len(description.encode("utf-8")), 1024)  # the byte limit bites first for Korean text

    def test_description_is_nfc_and_a_plain_yaml_scalar(self):
        description = self.fields["description"]
        self.assertEqual(unicodedata.normalize("NFC", description), description)
        self.assertEqual(plain_scalar_problems(description), [])

    def test_description_has_korean_trigger_words(self):
        words = set(re.findall(r"[가-힣]{2,}", self.fields["description"]))
        self.assertGreaterEqual(len(words), 3, "the description should carry Korean trigger phrases")

    def test_the_host_metadata_file_has_no_byte_order_mark(self):
        raw = (SKILL / "agents" / "openai.yaml").read_bytes()
        self.assertFalse(raw.startswith(BOM))
        raw.decode("utf-8")

    def test_the_checks_catch_a_bad_front_matter(self):
        self.assertEqual(plain_scalar_problems("Evidence-first UX research (UX 리서치, UX QA)"), [])
        for bad in ("Use it: for research", "Use it #1", "Find <things>", "[list] first", "true",
                    "trailing space ", ""):
            self.assertTrue(plain_scalar_problems(bad), bad)
        for bad in ("name: x\nno colon here", "---\nname: x\n"):
            with self.assertRaises(ValueError):
                front_matter(bad)


class ReadmeParityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.en = read(README)
        cls.ko = read(README_KO)

    def test_fenced_lines_are_not_headings(self):
        sample = "# Title\n\n```sh\n# Claude Code\ncp a b\n# Codex\n```\n\n## Section\n\n~~~\n# also code\n~~~\n"
        self.assertEqual(headings(sample), [(1, "Title"), (2, "Section")])
        self.assertEqual([title for title, _, _ in sections(sample)], ["Section"])

    def test_both_readmes_have_the_same_title(self):
        titles = [[t for level, t in headings(text) if level == 1] for text in (self.en, self.ko)]
        self.assertEqual(titles, [["Remorsearch UX QA"], ["Remorsearch UX QA"]])

    def test_the_second_level_headings_follow_the_map(self):
        for text, column in ((self.en, 0), (self.ko, 1)):
            found = [t for level, t in headings(text) if level == 2]
            self.assertEqual(found, [pair[column] for pair in SECTIONS])

    def test_the_heading_structure_is_the_same(self):
        self.assertEqual([level for level, _ in headings(self.en)], [level for level, _ in headings(self.ko)])

    def test_each_readme_links_to_the_other_under_its_title(self):
        first_en = next(line for line in self.en.split("\n")[1:] if line.strip())
        first_ko = next(line for line in self.ko.split("\n")[1:] if line.strip())
        self.assertEqual(first_en, "English | [한국어](README.ko.md)")
        self.assertEqual(first_ko, "[English](README.md) | 한국어")

    def test_shell_commands_are_the_same_in_both_languages(self):
        self.assertTrue(shell_commands(self.en))
        self.assertEqual(shell_commands(self.en), shell_commands(self.ko))

    def test_the_same_pages_are_linked(self):
        def targets(text):
            return {t.split("#")[0] for t in links(text)}
        english, korean = targets(self.en) - {"README.ko.md"}, targets(self.ko) - {"README.md"}
        self.assertEqual(english, korean)
        self.assertIn("README.md", targets(self.ko))
        self.assertIn("README.ko.md", targets(self.en))

    def test_local_links_resolve(self):
        for path, text in ((README, self.en), (README_KO, self.ko)):
            for target in links(text):
                if re.match(r"(?:https?:|mailto:|#)", target):
                    continue
                self.assertTrue((REPO / target.split("#")[0]).exists(), f"{path.name}: {target}")

    def test_the_project_is_named_by_its_current_repository(self):
        for text in (self.en, self.ko):
            self.assertIn("github.com/remorser58/remorsearch_UX_QA", text)
            self.assertNotIn("ux-research-qa-skills", text)

    def test_the_korean_readme_uses_one_word_for_a_user(self):
        for word in ("유저", "이용자"):
            self.assertNotIn(word, self.ko)


class SkillFolderTests(unittest.TestCase):
    def test_each_mode_workflow_keeps_its_first_line(self):
        modes = {"research": "research", "persona-qa": "persona-qa", "ergonomics": "ergonomics", "loop": "loop"}
        for folder, mode in modes.items():
            first = read(SKILL / "references" / folder / "workflow.md").split("\n")[0]
            self.assertRegex(first, rf"^<!-- Mode: {mode}\b.*Entry point: `SKILL\.md`\. -->$", folder)

    def test_the_two_copies_of_the_bundle_contract_are_identical(self):
        research = SKILL / "references" / "research" / "evidence-bundle-contract.md"
        persona_qa = SKILL / "references" / "persona-qa" / "evidence-bundle-contract.md"
        self.assertEqual(research.read_bytes(), persona_qa.read_bytes())

    def test_causal_cards_are_merged_and_callers_use_the_shared_path(self):
        shared = SKILL / "references/shared/causal-chain.md"
        self.assertTrue(shared.is_file())
        for mode in ("research", "persona-qa"):
            self.assertFalse((SKILL / f"references/{mode}/causal-ux-analysis.md").exists())
            self.assertIn("references/shared/causal-chain.md", read(SKILL / f"references/{mode}/workflow.md"))
        for path in [SKILL_MD, *sorted((SKILL / "references").rglob("*.md"))]:
            self.assertNotIn("causal-ux-analysis.md", read(path), path.relative_to(SKILL))

    def test_new_cards_lookup_and_manifest_ship_in_the_skill(self):
        for file in ("references/shared/access-card.md", "references/shared/evidence-card.md",
                     "references/shared/causal-chain.md", "references/persona-qa/kwcag-card.md",
                     "references/reading.json", "scripts/ref.py"):
            self.assertTrue((SKILL / file).is_file(), file)

    def test_router_has_no_mode_relative_path_or_old_name_mapping(self):
        text = read(SKILL_MD)
        self.assertNotIn("references/<mode>", text)
        for name in ("aside-community-ux-research", "persona-driven-ux-qa",
                     "ergonomic-persona-swarm-qa", "ux-improvement-loop"):
            self.assertNotIn(name, text)

    def test_no_file_names_the_old_repository(self):
        for path in project_files():
            text = text_of(path)
            if text is not None:
                self.assertNotIn("ux-research-qa-skills", text, path.relative_to(REPO))

    def test_every_mode_named_in_the_router_has_a_workflow(self):
        paths = re.findall(r"`(references/[a-z-]+/workflow\.md)`", read(SKILL_MD))
        self.assertEqual(len(set(paths)), 4)  # research, persona-qa, ergonomics and loop
        for path in paths:
            self.assertTrue((SKILL / path).is_file(), path)


class BundledToolkitTests(unittest.TestCase):
    def test_primary_skill_is_the_only_discoverable_entrypoint(self):
        self.assertEqual(sorted(SKILL.rglob("SKILL.md")), [SKILL_MD])

    def test_original_source_and_method_bytes_match_recorded_provenance(self):
        toolkit = SKILL / "references/insane-search"
        provenance = json.loads((toolkit / "PROVENANCE.json").read_text())
        expected = set()
        for relative, receipt in provenance["files"].items():
            shipped = "SOURCE.md" if relative == "SKILL.md" else relative
            expected.add(shipped)
            raw = (toolkit / shipped).read_bytes()
            self.assertEqual(len(raw), receipt["bytes"], shipped)
            self.assertEqual(hashlib.sha256(raw).hexdigest(), receipt["sha256"], shipped)
        actual = {path.relative_to(toolkit).as_posix()
                  for path in toolkit.rglob("*") if path.is_file()}
        self.assertEqual(actual - {"PROVENANCE.json", "upstream-LICENSE"}, expected)
        license_raw = (toolkit / "upstream-LICENSE").read_bytes()
        self.assertEqual(hashlib.sha256(license_raw).hexdigest(),
                         provenance["upstream_license"]["sha256"])
        self.assertEqual(license_raw, (REPO / "integrations/insane-search/upstream-LICENSE").read_bytes())

    def test_original_local_reference_links_resolve_inside_the_toolkit(self):
        toolkit = SKILL / "references/insane-search"
        count = 0
        for path in toolkit.rglob("*.md"):
            for target in links(read(path)):
                clean = target.split("#")[0]
                if not clean or re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*:", clean):
                    continue
                resolved = (path.parent / clean).resolve()
                self.assertTrue(resolved.is_relative_to(toolkit.resolve()), (path, target))
                self.assertTrue(resolved.is_file(), (path, target))
                count += 1
        self.assertGreater(count, 0)

    def test_relocated_source_folder_loads_a_linked_platform_method_body(self):
        with tempfile.TemporaryDirectory() as folder:
            installed = Path(folder) / "installed" / "remorsearch-ux-qa"
            shutil.copytree(SKILL, installed, ignore=shutil.ignore_patterns(*SKIPPED_DIRS))
            caller = Path(folder) / "another-project"
            caller.mkdir()
            command = [sys.executable, str(installed / "scripts/ref.py")]
            env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
            source = subprocess.run([*command, "references/insane-search/SOURCE.md",
                "phase-0-특수-엔드포인트-인덱스"], cwd=caller, env=env, text=True, capture_output=True)
            self.assertEqual(source.returncode, 0, source.stderr)
            self.assertIn("references/public-api.md", source.stdout)
            method = subprocess.run([*command, "references/insane-search/references/public-api.md",
                "stack-exchange-v23"], cwd=caller, env=env, text=True, capture_output=True)
            self.assertEqual(method.returncode, 0, method.stderr)
            self.assertIn("curl", method.stdout)
            self.assertIn("https://api.stackexchange.com/", method.stdout)
            self.assertNotIn("Section IDs:", method.stdout)
            self.assertEqual(list(caller.iterdir()), [])

    def test_the_removed_runtime_variables_and_field_do_not_come_back(self):
        for path in project_files():
            text = text_of(path)
            if text is None:
                continue
            relative = path.relative_to(REPO)
            self.assertEqual(REMOVED_VARIABLE.findall(text), [], relative)
            self.assertNotIn(REMOVED_FIELD, text, relative)


class InstalledFolderPathTests(unittest.TestCase):
    """D-09: inside the installed skill folder, a Markdown link must not leave the folder, and a backticked
    `docs/`, `tests/` or `benchmarks/` path must sit in a paragraph that says it is a repository document
    that is not installed. Paths in operational references are written from the skill root."""

    def test_no_link_or_backticked_path_points_out_of_the_installed_folder(self):
        for path in sorted(SKILL.rglob("*.md")):
            relative = path.relative_to(SKILL).as_posix()
            if relative.startswith(UNSCANNED_DIRS):
                continue
            text = read(path)
            for problem in leaving_links(relative, text) + bare_repo_paths(text):
                self.fail(f"{relative}: {problem}")

    def test_the_checks_catch_a_leaving_link_and_an_unmarked_repo_path(self):
        relative = "references/loop/cli.md"
        bad = "See [architecture](../../../../docs/architecture.md) and run `tests/loop_factory.py` first.\n"
        self.assertEqual(leaving_links(relative, bad), ["link ../../../../docs/architecture.md leaves the skill folder"])
        self.assertEqual(bare_repo_paths(bad), ["`tests/loop_factory.py` is not marked as a repository document "
                                                "that is not installed"])
        good = ("See the repository document `docs/architecture.md` and `docs/release.md` "
                "(not installed with the skill), and [provider contract](provider-contract.md).\n")
        self.assertEqual(leaving_links(relative, good), [])
        self.assertEqual(bare_repo_paths(good), [])


if __name__ == "__main__":
    unittest.main()
