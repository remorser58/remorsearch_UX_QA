"""Consistency checks for the Korean research pack: its two data files and its Korean references.

The pack is data (uxresearch/data/korea-platforms.json, korea-statistics.json) plus Korean documents
(references/research/korea/*.md, references/persona-qa/kwcag-2.2.md). The reader decides what is read from
uxresearch/data/routes.json, so these tests keep the map and the statistics cards in line with that file and
with the code, and keep the documents in line with the data. They read files only; nothing here touches the
network.
"""
from __future__ import annotations

import json
import re
import unicodedata
import unittest
from datetime import date
from pathlib import Path

import _paths  # noqa: F401  (puts the skill folder on sys.path)
from ergoqa import audience
from uxresearch import scope, verdict

SKILL = _paths.SKILL
REPO = _paths.REPO
DATA = SKILL / "uxresearch" / "data"
KOREA = SKILL / "references" / "research" / "korea"
KWCAG = SKILL / "references" / "persona-qa" / "kwcag-2.2.md"
KOREAN_DOCS = sorted(KOREA.glob("*.md")) + [KWCAG]
PLATFORM_MAP = KOREA / "platform-map.md"

# These channels have no row in the Korean map; their stops still apply through the route table.
ENTRIES_WITHOUT_ROW = {"meta-facebook", "x-terms", "tiktok-terms", "reddit-terms", "hackernews-terms"}
# Member-only or closed communities are never named as audience leads (owner decision S2).
CLOSED_COMMUNITIES = ("여성시대", "subdued20club")
CAFE_PAGE = re.compile(r"cafe\.(?:naver|daum)\.(?:com|net)/"
                       r"(?!(?:robots\.txt|_agreement)(?:[?#\s\"<>]|$))[A-Za-z0-9_-]+")
# A statement read some way other than from the primary text needs a source, unless it is our own rule.
UNSOURCED_OK = {"inference", "skill_rule", "not_found"}
LABEL = re.compile(r"관찰됨|미확인|추론|규칙|미검사")
ISO_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
URL = re.compile(r"https?://[^\s)>\]`]+")
PATH_TOKEN = re.compile(r"`((?:references|uxresearch|schemas|scripts|drivers|ergoqa|uxloop|examples|agents|tests)/"
                        r"[^`\s]+)`")
# An inline link, not a reference link ("[text][label]") that is followed by a parenthesis in the prose.
LINK_TARGET = re.compile(r"(?<!\])\[[^\]\[]*\]\(([^)\s]+)\)")
LINK_DEFINITION = re.compile(r"^\[[^\]]+\]:\s*(\S+)", re.M)


def load(name: str) -> dict:
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def walk(node):
    """Every dict and list inside a JSON value, the value itself first."""
    yield node
    if isinstance(node, dict):
        for value in node.values():
            yield from walk(value)
    elif isinstance(node, list):
        for value in node:
            yield from walk(value)


def strings(node):
    for item in walk(node):
        if isinstance(item, str):
            yield item


def valid_date(value) -> bool:
    try:
        date.fromisoformat(value)
    except (TypeError, ValueError):
        return False
    return True


def outside_fences(text: str):
    """The lines of a Markdown text that are not inside a fenced code block."""
    fenced = False
    for line in text.split("\n"):
        if line.lstrip().startswith(("```", "~~~")):
            fenced = not fenced
            continue
        if not fenced:
            yield line


def headings(text: str) -> list:
    return [line.lstrip("#").strip() for line in outside_fences(text) if re.match(r"#{1,6}\s", line)]


def cells(line: str) -> list:
    inner = line.strip().replace("\\|", "\u0000")
    inner = inner[1:] if inner.startswith("|") else inner
    inner = inner[:-1] if inner.endswith("|") else inner
    return [c.replace("\u0000", "|").strip() for c in inner.split("|")]


def tables(text: str) -> list:
    """(header cells, data rows) of every pipe table outside fenced code blocks."""
    lines = list(outside_fences(text))
    found, i = [], 0
    while i < len(lines):
        if lines[i].startswith("|") and i + 1 < len(lines) and re.match(r"^\|\s*:?-{3,}", lines[i + 1]):
            head, rows, j = cells(lines[i]), [], i + 2
            while j < len(lines) and lines[j].startswith("|"):
                rows.append(cells(lines[j]))
                j += 1
            found.append((head, rows))
            i = j
        else:
            i += 1
    return found


def section(text: str, start: str, end: str) -> str:
    """The text from the heading that starts with `start` up to the heading that starts with `end`."""
    lines = text.split("\n")
    first = next(i for i, line in enumerate(lines) if line.startswith(start))
    last = next(i for i, line in enumerate(lines) if i > first and line.startswith(end))
    return "\n".join(lines[first:last])


class PlatformDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load("korea-platforms.json")
        cls.rows = cls.data["platforms"]
        cls.vocab = cls.data["vocab"]
        cls.routes = load("routes.json")
        cls.lists = scope.lists_for(None)
        cls.platform_ids = {p["id"] for p in cls.routes["platforms"]}
        cls.reader_hosts = [h for p in cls.routes["platforms"] for h in p["hosts"]]
        cls.private_hosts = [o["host"] for o in cls.routes["out_of_scope"]]
        cls.terms_hosts = [h for t in cls.routes["terms_restricted"] for h in t["hosts"]]

    @staticmethod
    def probe(host: str) -> str:
        return host.replace("*.", "x.")

    def test_file_header_and_no_row_is_marked_verified(self):
        self.assertEqual(self.data["schema_version"], "ux-research-korea-platforms.v1")
        self.assertTrue(valid_date(self.data["checked_at"]))
        self.assertIsNone(self.data["verified_at"])  # only a person's live check sets it
        ids = [row["id"] for row in self.rows]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertGreaterEqual(len(ids), 27)
        for row in self.rows:
            self.assertIsNone(row["verified_at"], row["id"])
            self.assertTrue(valid_date(row["checked_at"]), row["id"])

    def test_vocabulary_agrees_with_the_code(self):
        self.assertEqual(self.vocab["stop_class"], list(verdict.STOP_CLASSES))
        self.assertEqual(self.vocab["terms_restricts"], list(scope.RESTRICTS))
        self.assertLessEqual(set(scope.STATUSES), set(self.vocab["terms_status"]))
        labels = self.data["labels"]
        self.assertEqual(set(labels), set(self.vocab["read_via"]))
        self.assertLessEqual(set(labels.values()), {"관찰됨", "미확인(요약)", "미확인(미러)", "미확인", "추론", "규칙"})

    def test_rows_use_only_the_vocabulary(self):
        vocab = self.vocab
        for row in self.rows:
            where = row["id"]
            self.assertIn(row["family"], vocab["family"], where)
            self.assertIn(row["public_scope"], vocab["public_scope"], where)
            self.assertTrue(row["routes"], where)
            self.assertLessEqual(set(row["routes"]), set(vocab["route"]), where)
            if "none" in row["routes"]:
                self.assertEqual(row["routes"], ["none"], where)  # "none" is the only route or it is not there
            self.assertLessEqual(set(row["expected_stops"]), set(vocab["stop_class"]), where)
            self.assertIn(row["terms"]["status"], vocab["terms_status"], where)
            self.assertLessEqual(set(row["terms"]["restricts"]), set(vocab["terms_restricts"]), where)
            self.assertIn(row["robots"]["expectation"], vocab["robots_expectation"], where)
            self.assertIn(row["audience"]["confidence"], vocab["confidence"], where)
            self.assertRegex(row["id"], r"^[a-z0-9-]+$")

    def test_no_route_is_a_researcher_note(self):
        for name in ("korea-platforms.json", "korea-statistics.json"):
            self.assertNotIn("researcher_note", (DATA / name).read_text(encoding="utf-8"), name)
        for row in self.rows:
            self.assertNotIn("researcher_note", row["routes"], row["id"])

    def test_data_text_is_nfc(self):
        for name in ("korea-platforms.json", "korea-statistics.json"):
            text = (DATA / name).read_text(encoding="utf-8")
            self.assertEqual(unicodedata.normalize("NFC", text), text, name)

    def test_every_host_is_covered_by_the_reader_policy(self):
        for row in self.rows:
            for host in row["hosts"]:
                probe = self.probe(host)
                covered = (verdict.host_matches(probe, self.reader_hosts)
                           or verdict.host_matches(probe, self.private_hosts)
                           or verdict.host_matches(probe, self.terms_hosts))
                self.assertTrue(covered, f"{row['id']}: {host} is in no routes.json platform, out_of_scope or "
                                         f"terms_restricted entry")

    def test_route_ids_exist_in_the_route_table(self):
        for row in self.rows:
            for route_id in row["route_ids"]:
                self.assertIn(route_id, self.platform_ids, f"{row['id']}: {route_id}")

    def test_terms_status_agrees_with_the_route_table(self):
        entries = {e["id"]: e for e in self.routes["terms_restricted"]}
        pointed_at = set()
        for row in self.rows:
            where = row["id"]
            found = set()
            for host in row["hosts"]:
                entry = scope.terms_entry(self.probe(host), self.lists)
                found.add(entry["id"] if entry else None)
            self.assertLessEqual(len(found), 1, f"{where}: hosts fall under different terms entries {found}")
            entry_id = next(iter(found)) if found else None
            terms, status = row["terms"], row["terms"]["status"]
            if entry_id is None:
                self.assertNotIn(status, scope.STATUSES, f"{where}: {status} but no routes.json entry covers it")
                self.assertIsNone(terms.get("routes_entry"), where)
                self.assertNotIn("terms_restricted", row["expected_stops"], where)
                continue
            pointed_at.add(entry_id)
            self.assertEqual(status, entries[entry_id]["status"], where)
            self.assertEqual(terms["routes_entry"], entry_id, where)
            self.assertEqual(terms["restricts"], entries[entry_id]["restricts"], where)
            if "lift_requires" in terms:
                self.assertEqual(terms["lift_requires"], entries[entry_id]["lift_requires"], where)
            self.assertIn("terms_restricted", row["expected_stops"], where)
            if status == "confirmed":  # only a clause that was read makes an entry confirmed
                self.assertTrue(terms["terms_url"].startswith("https://") and terms["clause"], where)
        self.assertEqual(set(entries) - pointed_at, ENTRIES_WITHOUT_ROW & set(entries))
        for entry in entries.values():  # the route table says how an entry was read in the map's own words
            self.assertIn(entry["read_via"], self.vocab["read_via"], entry["id"])

    def test_new_stops_and_own_app_exports_are_consistent(self):
        rows = {row["id"]: row for row in self.rows}
        for name, requirement, routes in (("daangn", "written_permission", ["reader_public_page"]),
                                           ("clien", "never", ["none"]),
                                           ("app-store-kr", "never", ["team_export"])):
            self.assertEqual(rows[name]["terms"]["lift_requires"], requirement)
            self.assertEqual(rows[name]["routes"], routes)
            self.assertIn("terms_restricted", rows[name]["expected_stops"])
            self.assertEqual(rows[name]["checked_at"], "2026-09-30")
        self.assertEqual(rows["app-store-kr"]["hosts"], ["apps.apple.com", "itunes.apple.com"])
        self.assertEqual(next(p for p in self.routes["platforms"] if p["id"] == "app-store")["official"], [])

    def test_every_statement_carries_its_provenance(self):
        for holder in (self.rows, self.data["corpus_norms"]):
            for node in walk(holder):
                if not isinstance(node, dict) or "read_via" not in node:
                    continue
                label = node.get("id") or node.get("text") or node.get("what") or node.get("status")
                self.assertIn(node["read_via"], self.vocab["read_via"], label)
                sources = node.get("sources") or []
                self.assertTrue(all(s.startswith(("https://", "http://")) for s in sources), label)
                if node["read_via"] not in UNSOURCED_OK:
                    self.assertTrue(sources, f"read via {node['read_via']} but no source: {str(label)[:60]}")

    def test_rule_references_resolve(self):
        for node in walk(self.data):
            if isinstance(node, dict):
                for key in ("rule_ref", "legal_ref"):
                    if isinstance(node.get(key), str):
                        target = node[key].split()[0]  # "references/x.md L10": a path, then a row id
                        self.assertTrue((SKILL / target).exists(), f"{key} {node[key]}")

    def test_leads_never_name_a_closed_community(self):
        text = (DATA / "korea-platforms.json").read_text(encoding="utf-8")
        for name in CLOSED_COMMUNITIES:
            self.assertNotIn(name, text)
        self.assertEqual(CAFE_PAGE.findall(text), [])  # no single cafe is named as a lead
        whole_channel_stops = [entry["host"] for entry in self.routes["out_of_scope"]
                               if not entry.get("path_prefix")]
        coverage = section(read(PLATFORM_MAP), "## 5.", "## 6.")
        for row in self.rows:
            closed = (row["public_scope"] in {"private", "member_only", "member-only", "out_of_scope"}
                      or "out_of_scope" in row["routes"]
                      or any(verdict.host_matches(self.probe(host), whole_channel_stops)
                             for host in row["hosts"]))
            if not closed:
                continue
            with self.subTest(channel=row["id"]):
                lead = row["audience"]
                self.assertRegex(lead["text"],
                                 r"\A싣지 않음\. (?:회원 전용 채널|멤버 전용 서비스|참여해야 보이는 채팅방)[은는] "
                                 r"사용자 단서로 삼지 않음\(1절\)\."
                                 r"(?: (?:학생 사용자|이 채널의 사용자)는 설문·인터뷰로 조사함\.)?\Z")
                self.assertEqual(lead["confidence"], "low")
                self.assertEqual(lead["read_via"], "skill_rule")
                self.assertEqual(lead["sources"], [])
                for name in [row["name_ko"], row["name_ko"].split()[-1], row["id"], *row["hosts"]]:
                    self.assertNotIn(name, coverage)


class PlatformMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load("korea-platforms.json")
        cls.rows = cls.data["platforms"]
        cls.text = read(PLATFORM_MAP)

    def test_channel_sections_follow_the_data_order(self):
        ids = re.findall(r"^### `([a-z0-9-]+)` ", self.text, flags=re.M)
        self.assertEqual(ids, [row["id"] for row in self.rows])

    def test_summary_table_matches_the_data(self):
        (head, table), = tables(section(self.text, "## 2.", "## 3."))
        column = {name: head.index(name) for name in ("id", "정당한 경로", "예상 중단", "약관", "단서 신뢰도")}
        rows = {cell[column["id"]].strip("`"): cell for cell in table}
        self.assertEqual(list(rows), [row["id"] for row in self.rows])
        for row in self.rows:
            cell = rows[row["id"]]
            self.assertEqual(re.findall(r"`([a-z_]+)`", cell[column["정당한 경로"]]), row["routes"], row["id"])
            self.assertEqual(re.findall(r"`([a-z_]+)`", cell[column["예상 중단"]]), row["expected_stops"], row["id"])
            self.assertEqual(cell[column["약관"]].strip("`"), row["terms"]["status"], row["id"])
            self.assertEqual(cell[column["단서 신뢰도"]], row["audience"]["confidence"], row["id"])

    def test_route_and_audience_text_matches_the_data(self):
        channels = dict(re.findall(r"^### `([a-z0-9-]+)`[^\n]*\n(.*?)(?=^### |^## 4\.)",
                                   self.text, flags=re.M | re.S))
        for row in self.rows:
            channel = channels[row["id"]]
            for note in row["route_notes"]:
                self.assertIn(note["text"], channel, row["id"])
            self.assertIn(f"- 사용자 단서(신뢰도 `{row['audience']['confidence']}`): "
                          f"{row['audience']['text']}", channel, row["id"])

    def test_source_list_is_the_urls_of_the_data(self):
        in_data = {s for s in strings(self.data) if re.match(r"https?://", s)}
        in_text = {u.rstrip(".,;") for u in URL.findall(self.text)}
        self.assertEqual(sorted(in_data ^ in_text), [])

    def test_no_url_appears_before_the_source_list(self):
        self.assertEqual(URL.findall(self.text.split("\n## 11.")[0]), [])

    def test_corpus_norms_are_in_the_document(self):
        norms = section(self.text, "## 4.", "## 5.")
        self.assertEqual(len(re.findall(r"^- ", norms, flags=re.M)), len(self.data["corpus_norms"]))


class StatisticsDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load("korea-statistics.json")
        cls.vocab = cls.data["vocab"]
        cls.sources = cls.data["sources"]
        cls.routes = {r["id"]: r for r in cls.data["routes"]}

    def test_file_header(self):
        self.assertEqual(self.data["schema_version"], "ux-research-korea-statistics.v1")
        self.assertTrue(valid_date(self.data["checked_at"]))
        self.assertIsNone(self.data["verified_at"])
        ids = [s["id"] for s in self.sources]
        self.assertEqual(len(ids), len(set(ids)))

    def test_source_types_are_audience_source_types(self):
        self.assertLessEqual(set(self.vocab["source_type"]), set(audience.SOURCE_TYPES))
        for source in self.sources:
            self.assertIn(source["source_type"], audience.SOURCE_TYPES, source["id"])
            self.assertEqual(self.vocab["family"][source["source_type"]], source["family"], source["id"])

    def test_every_source_states_its_frame_and_provenance(self):
        frame_keys = {"population", "unit", "n", "method", "reference_period", "published_at", "weights_and_error"}
        for source in self.sources:
            where = source["id"]
            self.assertLessEqual(frame_keys, set(source["frame"]), where)
            self.assertIn(source["frame"]["unit"], self.vocab["unit"], where)
            self.assertIn(source["frame"]["age_frame"], self.data["age_frames"], where)
            if not source["values"]:  # a row that carries no figure says why it carries none
                self.assertTrue(source.get("unverified") or source.get("notes"), where)
            for value in source["values"]:
                self.assertTrue(value["label"] and value["as_printed"], where)
            self.assertTrue(source["sources"], where)
            self.assertTrue(all(u.startswith("https://") for u in source["sources"]), where)
            self.assertIn(source["read_via"], self.vocab["read_via"], where)
            self.assertIn(source["confidence"], self.vocab["confidence"], where)
            self.assertTrue(valid_date(source["checked_at"]), where)
            self.assertIn(source["route"]["route_id"], self.routes, where)
            for key in ("approval_no", "table_id", "licence", "use"):
                self.assertIn(key, source, where)

    def test_count_only_rows_never_answer_a_size_question(self):
        rule = self.data["count_only_rule"]
        kinds = self.data["question_ids"]
        counted = {s["id"] for s in self.sources if s["count_only"]}
        self.assertEqual(set(rule["rows"]), counted)
        for source in self.sources:
            if not source["count_only"]:
                continue
            claimed = {k for answer in source["answers"] for k in kinds[answer]["claim_kinds"]}
            self.assertEqual(claimed & set(rule["never_supports"]), set(), source["id"])
            self.assertLessEqual(claimed - {"workaround"}, set(rule["may_support"]), source["id"])

    def test_kosis_is_a_route_and_never_a_publisher(self):
        for source in self.sources:
            for field in ("id", "publisher", "org"):
                self.assertNotRegex(source[field].lower(), r"kosis|국가통계포털", f"{source['id']} {field}")
        self.assertEqual(self.routes["kosis-openapi"]["kind"], "api_user_key")
        self.assertEqual(self.routes["kosis-openapi"]["env"], "REMORSEARCH_KOSIS_API_KEY")
        self.assertIs(self.routes["kosis-openapi"]["enabled"], False)  # no adapter in this version
        self.assertIn(self.routes["kosis-portal-download"]["kind"], self.vocab["route_kind"])
        domains = {d["domain"] for d in self.data["portal_domains"]}
        self.assertIn("kosis.kr", domains)
        for record in self.data["org_aliases"]:
            self.assertNotIn("kosis.kr", record.get("domains", []), record["canonical"])  # a portal names no agency

    def test_routes_are_switched_off_with_a_reason_and_keys_are_namespaced(self):
        for route in self.routes.values():
            self.assertIn(route["kind"], self.vocab["route_kind"], route["id"])
            if route.get("env"):
                self.assertRegex(route["env"], r"^REMORSEARCH_[A-Z0-9_]+$", route["id"])
            if route.get("enabled") is False:
                self.assertTrue(route["reason"], route["id"])
        naver = load("routes.json")["discovery"]
        off = next(p for p in naver if p["id"] == "naver-datalab")
        self.assertEqual(self.routes["naver-datalab"]["reason"], off["reason"])

    def test_agency_aliases_are_unique(self):
        owner = {}
        for record in self.data["org_aliases"]:
            names = [record["canonical"], record.get("canonical_en", "")]
            names += record.get("aliases", []) + record.get("aliases_unverified", [])
            for body in record.get("related_bodies", []):
                names += [body["name"]] + body.get("aliases", [])
            for name in filter(None, names):
                key = unicodedata.normalize("NFKC", name).casefold()
                self.assertEqual(owner.setdefault(key, record["canonical"]), record["canonical"], name)

    def test_age_frames_are_named_the_same_way(self):
        for age_frame in self.data["age_frames"]:
            self.assertRegex(age_frame, r"^age_[a-z0-9_]+$|^not_applicable$")

    def test_the_statistics_document_names_only_ids_the_data_has(self):
        text = read(KOREA / "statistics.md")
        known = {s["id"] for s in self.sources} | set(self.routes) | set(self.data["age_frames"])
        named = set(re.findall(r"`([a-z0-9]+(?:-[a-z0-9]+)+)`", text))
        self.assertEqual(named - known, set())
        self.assertTrue({s["id"] for s in self.sources} & named)  # the document really names the data's rows


class KoreanDocsTests(unittest.TestCase):
    def test_the_pack_has_the_documents_the_overview_lists(self):
        overview = read(KOREA / "overview.md")
        listed = set(re.findall(r"^\| `([^`]+)` \|", overview.split("\n## 8.")[1], flags=re.M))
        in_folder = {f"references/research/korea/{p.name}" for p in KOREA.glob("*.md")}
        self.assertEqual({p for p in listed if p.startswith("references/research/korea/")}, in_folder)
        for path in ("references/persona-qa/kwcag-2.2.md", "uxresearch/data/korea-platforms.json",
                     "uxresearch/data/korea-statistics.json"):
            self.assertIn(path, listed)
        for path in listed:
            self.assertTrue((SKILL / path).is_file(), path)

    def test_each_document_has_done_when_and_failure_modes(self):
        for path in KOREAN_DOCS:
            found = headings(read(path))
            if path.name == "report-template.md":
                # The skeleton's headings are the report's own; the writer's self-check closes it.
                self.assertTrue(any("완료 점검" in h for h in found), f"{path.name}: no '완료 점검' heading")
                continue
            self.assertTrue(any("Done when" in h for h in found), f"{path.name}: no 'Done when' heading")
            self.assertTrue(any("Failure modes" in h for h in found), f"{path.name}: no 'Failure modes' heading")

    def test_text_is_nfc_and_has_no_tabs(self):
        for path in KOREAN_DOCS:
            text = read(path)
            self.assertEqual(unicodedata.normalize("NFC", text), text, path.name)
            self.assertNotIn("\t", text, path.name)

    def test_backticked_paths_resolve(self):
        for path in KOREAN_DOCS:
            for token in set(PATH_TOKEN.findall(read(path))):
                target = token.rstrip(".,;:)").split("#")[0]
                if re.search(r"[<>{}*…]", target):
                    continue  # a pattern or a placeholder, not a path
                base = REPO if target.startswith("tests/") else SKILL
                self.assertTrue((base / target).exists(), f"{path.name}: {token} does not resolve")

    def test_markdown_links_resolve(self):
        for path in KOREAN_DOCS:
            text = read(path)
            for target in LINK_TARGET.findall(text) + LINK_DEFINITION.findall(text):
                if re.match(r"(?:https?:|mailto:|#)", target):
                    continue
                target = target.split("#")[0]
                self.assertTrue((path.parent / target).exists() or (SKILL / target).exists(),
                                f"{path.name}: link {target} does not resolve")

    def test_reference_style_links_have_definitions(self):
        for path in KOREAN_DOCS:
            text = read(path)
            defined = {m.lower() for m in re.findall(r"^\[([^\]]+)\]:", text, flags=re.M)}
            used = {m.lower() for m in re.findall(r"\]\[([^\]]+)\]", text)}
            self.assertEqual(used - defined, set(), path.name)

    def test_stop_classes_in_the_report_template_are_the_codes_stop_classes(self):
        text = read(KOREA / "report-template.md")
        table = section(text, "### 1.4", "### 1.5")
        codes = re.findall(r"^\| `([a-z_]+)` \|", table, flags=re.M)
        self.assertEqual(set(codes) - {"read", "deferred", "unread", "stopped"}, set(verdict.STOP_CLASSES))

    def test_tables_with_a_check_column_label_every_row(self):
        checked = 0
        for path in KOREAN_DOCS:
            for head, rows in tables(read(path)):
                for index, name in enumerate(head):
                    if not name.startswith("확인"):
                        continue
                    for row in rows:
                        cell = row[index] if index < len(row) else ""
                        if name.startswith("확인일"):
                            self.assertRegex(cell, ISO_DATE.pattern, f"{path.name}: {row[0][:40]}")
                        else:
                            self.assertRegex(cell, LABEL.pattern, f"{path.name}: {row[0][:40]}")
                        checked += 1
        self.assertGreater(checked, 50)  # the statistics, promotion and KWCAG tables really were checked

    def test_every_document_dates_and_labels_its_claims(self):
        for path in KOREAN_DOCS:
            text = read(path)
            self.assertRegex(text, ISO_DATE.pattern, f"{path.name}: no check date")
            self.assertRegex(text, LABEL.pattern, f"{path.name}: no evidence label")

    def test_documents_that_cite_statutes_say_they_are_not_legal_advice(self):
        for path in KOREAN_DOCS:
            text = read(path)
            if re.search(r"제\d+조", text):
                self.assertIn("법률 자문", text, path.name)

    def test_no_closed_community_is_named(self):
        for path in KOREAN_DOCS:
            text = read(path)
            for name in CLOSED_COMMUNITIES:
                self.assertNotIn(name, text, path.name)
            self.assertEqual(CAFE_PAGE.findall(text), [], f"{path.name} names a single cafe")

    def test_no_document_offers_researcher_notes(self):
        for path in KOREAN_DOCS:
            text = read(path)
            for phrase in ("researcher_note", "researcher note", "연구자 메모"):
                self.assertNotIn(phrase, text, path.name)


if __name__ == "__main__":
    unittest.main()
