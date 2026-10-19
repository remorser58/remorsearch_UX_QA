# Real layout bugs, round 2: preregistered protocol

Written 2026-10-19, before any candidate in the sources below was screened, before the fixed skill was frozen and before any agent run. Changes after this point are listed at the end with their reason.

## Question

The question of [round 1](../real-layout-bugs/PROTOCOL.md), on new cases and with the skill fixed for the two faults round 1 exposed: on a `file://` page the scan blocked stylesheets in parent folders, and under `REMORSEARCH_CHROMIUM_ARGS=--single-process` its reflow, text-spacing and short-window passes failed. On real layout bugs that open-source maintainers fixed, does an agent find more of them, without more false alarms and within the same time budget, when it uses the skill? What does the scan find on its own before and after the fixes?

## Skill under test

The fixed skill is frozen at a commit of branch `codex/v1.0.1` in this repository. Its commit SHA and skill payload SHA-256 are recorded in the changes below before any agent run, and it is installed once with `scripts/install.py --no-prompt` into an isolated folder. No skill or detector file changes until every run is scored. The v1.0.0 payload of round 1 is used only for the scan-alone comparison.

## Sources

Chosen for one practical reason: their history holds ready-to-open HTML pages with the built CSS committed, so a historical commit renders without a build. None was used in round 1. Screened in this order:

1. creativetimofficial/soft-ui-dashboard
2. creativetimofficial/argon-dashboard
3. themeselection/sneat-html-admin-template-free
4. StartBootstrap/startbootstrap-sb-admin
5. picturepan2/spectre
6. estevanmaito/windmill-dashboard
7. ColorlibHQ/gentelella
8. creativetimofficial/material-dashboard
9. twbs/bootstrap, version 3 line (`docs/examples/`)

## Candidate rule

Every commit reachable from the repository's tags and default branch that changes a CSS, SCSS, LESS or HTML file, and whose message, the title of the pull request or issue it references, or the changelog lines it adds match (case-insensitive) overflow, overlap, cut off, cut-off, clip, truncat, hidden, behind, cover, misalign, align, z-index, wrap, responsive, mobile, small screen, width, height, spacing, margin, padding, gap, position, sticky, fixed, layout. Candidates are screened newest first.

## Inclusion

Round 1's inclusion rule, including its change 1, applies unchanged:

1. The defect is visible without interaction (on load and after scrolling) on an HTML page shipped in the repository at the parent commit, at 360x780 or 393x852 (phone, touch, DPR 3) or 1440x900 (laptop), in Chromium 141 (Playwright 1.56.1).
2. At the fix commit, or the first later commit whose committed built CSS contains the fix, the defect is gone on the same page and viewport.
3. A reviewer could name the fault without seeing the fix: content cut, covered or overlapping, content outside the screen, a component that breaks into the wrong rows, an element misaligned with the siblings or container it belongs to, an element mis-sized against an attached element, or a glyph off the centre of its control, by at least 2 CSS px where it is a geometry fault.

Excluded: defects that need hover, click, focus or keyboard; other browsers only; print; colour or contrast only; wording only; script errors without a visible layout effect; spacing or style refinements that leave the broken state looking intended. Every screened candidate is listed with its verdict and reason.

At most 3 cases are accepted from one source, and screening of a source stops at 3 accepted or 40 screened. Screening stops when 12 cases are accepted. If the sources run out first, the comparison runs with the cases found, and the shortfall is reported.

## Page items and versions

As in round 1: a page item is one HTML page at one commit with its accepted defect, plus its fixed state. The items are split into three groups A, B and C of four by a seeded shuffle that keeps at most two items of one source in a group; the seed is recorded with the sealed key. Run 1 shows A and B broken and C fixed, run 2 A and C broken and B fixed, run 3 B and C broken and A fixed. Agents see neutral names only and are never told which pages are broken. Pages load from local files with every asset saved locally; nothing loads from the network.

## Arms and runs

Two models, as in round 1: GPT-6.1 Sol (strong) and DeepSeek 4.1 Flash through the InferHub combo route (cheap), both at reasoning effort `high`, set explicitly when each agent starts. Each model runs both arms (without the skill, with the skill) once per run index, three times in all, in fresh sessions with no shared history. Both arms get the same pages, the round 1 prompt templates unchanged (`prompts/plain.txt` SHA-256 52c837ad508ff60a8db69799814aa411d5cbe43d1b505112b34ee81f9e83466f, `prompts/skill-tail.txt` 5dbb8f30f50c72cee709a684a54554e1afdd2f9765ebfd0fad5b43b3366c8cf1), the same tools (Node.js 22, Playwright 1.56.1 with Chromium) and a 30-minute budget. No network, no answer keys, no other repositories, no delegation. At most six agents run at once.

## Scoring

- Known defects are each item's own accepted defect on its broken page. A defect that also shows on another item counts as a valid extra there.
- Found: a finding on the right page that points at the defect's element (or an element inside or containing it) and describes the same visible problem. Severity and category wording do not matter.
- Fixed-state alarm: a finding on a fixed page that points at that item's defect element and calls it broken.
- Every other finding is judged from the pixels at the stated viewport as a valid extra or unsupported.
- Adjudication works from a file without arm or model labels. The adjudicator does not read agent outputs before every run has finished.

Primary: known defects found per run, over the defects shown in that run. Secondary: fixed-state alarms, unsupported findings, valid extras, time to the written report.

## Decision rule

For each model, the skill counts as better only if its arm finds more known defects in all three paired runs, has no more fixed-state alarms plus unsupported findings in total, and its median time is at most 1.5 times the plain arm's. Otherwise the result is reported as no demonstrated improvement.

## Scan alone

The scan runs on every page state (24) as the agents would run it (`file://` URL, `REMORSEARCH_CHROMIUM_ARGS=--single-process`), once with v1.0.0 and once with the frozen fixed skill. Broken pages are scored with the matching rule above; candidates on fixed pages are counted and reported.

## Changes after registration

1. Sources added, 2026-10-19, before any agent run and before any candidate in the added sources was screened. The nine sources above, screened under the unchanged rules, gave 4 cases: 1 from spectre, 2 from gentelella and 1 from Bootstrap 3. Four cases are too few to separate the arms, so three sources are added. They were chosen for the same reason as the nine (HTML pages with the built CSS committed in their history) and are screened after them, in this order, under the same candidate rule, inclusion rule, per-source limits and stop rule:
    10. ColorlibHQ/AdminLTE: pages at the root and in `pages/` (versions 2 and 3) and in `dist/` (version 4).
    11. tabler/tabler, limited to its commits from 2018-02-14 to 2019-03-12, when the built demo pages in `dist/` were committed.
    12. Semantic-Org/Semantic-UI: `examples/`.

    If fewer than 12 cases are found, the seeded shuffle splits them into groups A, B and C as evenly as possible (sizes differ by at most one, with at most two items of one source in a group where the count allows). The run design, arms, scoring and decision rule stay as registered.
2. AdminLTE replaced, 2026-10-19, before any of its candidates was screened. Round 1 used AdminLTE's version 3 and 4 lines, and this round asks about projects round 1 did not use, so AdminLTE is dropped. Tabler and Semantic UI move up to places 10 and 11, and a third source takes place 12:
    12. Dogfalo/materialize, limited to its commits up to 2017-04-21, when the documentation pages at the root and their built stylesheet `css/ghpages-materialize.css` were committed.
