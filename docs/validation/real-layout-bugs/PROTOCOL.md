# Real layout bugs: preregistered protocol

Written 2026-10-19 before any candidate was screened, any page was built or any
agent was run. Changes after this point are listed at the end with their reason.

## Question

On real, reported and fixed layout bugs in real open-source web pages, does an
agent find more of them, without more false alarms and within the same time
budget, when it uses the Remorsearch UX QA skill? Separately, what does the
skill's scan find on its own?

## Frozen skill

Public release v1.0.0 of remorser58/remorsearch_UX_QA (tag v1.0.0, commit
0dc74293787eed60a369a369280e93a1ce849479, skill payload SHA-256
4fcfbb1a0acd9a86aeed5c906b68e04d6b5a1d1d03362a57fa113b7dca9a60f0), installed once
with scripts/install.py into an isolated folder. No skill or detector file
changes until every run is scored.

## Sources

Fixed in advance for a practical reason only: their history holds ready-to-open
HTML pages with the built CSS and JavaScript committed, so a historical commit
renders without a build.

- ColorlibHQ/AdminLTE (version 3 line: pages/, dist/, plugins/)
- StartBootstrap/startbootstrap-sb-admin-2 (root pages, css/, vendor/)
- picocss/pico (version 1 line: docs/ and css/)

## Candidate rule

Every commit reachable from the repository's tags and default branch whose
message, or the title of the pull request or issue it references, matches
(case-insensitive) overflow, overlap, cut off, cut-off, clip, truncat, hidden,
behind, cover, misalign, align, z-index, wrap, responsive, mobile, small screen,
width, height, spacing, margin, padding, gap, position, sticky, fixed, layout,
and that changes a CSS, SCSS or HTML file. Candidates are screened newest first.

## Inclusion

A candidate becomes a case when all of these hold:

1. The defect is visible without interaction (on load and after scrolling) on an
   HTML page shipped in the repository at the parent commit, at 360x780 or
   393x852 (phone, touch, DPR 3) or 1440x900 (laptop), in Chromium 141
   (Playwright 1.56.1).
2. At the fix commit, or the first later commit whose committed built CSS
   contains the fix, the defect is gone on the same page and viewport.
3. A user would notice it: content or text cut, covered, overlapping, outside the
   screen, or an element misplaced, misaligned or mis-sized by at least 2 CSS px.

Excluded: defects that need hover, click, focus or keyboard; other browsers only;
print; colour or contrast only; wording only; script errors without a visible
layout effect. Screening stops for a repository after 8 accepted cases or 60
screened candidates. Every screened candidate is listed with its verdict.

## Page items and versions

A page item is one HTML page at one commit with one or more accepted defects,
plus its fixed state. Items are split into three groups A, B and C. Run k shows
every item once: run 1 shows A and B broken and C fixed, run 2 shows A and C
broken and B fixed, run 3 shows B and C broken and A fixed. Agents see neutral
names only and are never told which pages are broken. Pages load from local
files with every asset vendored; nothing loads from the network.

## Arms and runs

Two models, chosen before screening: GPT-6.1 Sol at its default effort (strong)
and DeepSeek 4.1 Flash at its default effort (cheap). Each model runs both arms
(without the skill, with the skill) three times, one per run index, all fresh
sessions with no shared history. Both arms get the same pages, prompt, tools
(Node.js 22, Playwright 1.56.1 with Chromium) and a 30-minute budget; the skill
arm is also told to use the installed skill. No network, no answer keys, no
other repositories, no delegation.

## Scoring

- Found: a finding on the right page that points at the defect's element (or an
  element inside or containing it) and describes the same visible problem.
  Severity and category wording do not matter.
- Fixed-state alarm: a finding on a fixed page that points at a known defect's
  element and calls it broken.
- Every other finding is judged from the pixels at the stated viewport as a
  valid extra or unsupported.
- Adjudication is blind to arm and model.

Primary: known defects found per run, over the defects shown in that run.
Secondary: fixed-state alarms, unsupported findings, valid extras, time to the
written report.

## Decision rule

For each model, the skill counts as better only if its arm finds more known
defects in all three paired runs, has no more fixed-state alarms plus unsupported
findings in total, and its median time is at most 1.5 times the plain arm's.
Otherwise the result is reported as no demonstrated improvement. The scan alone
is scored on the broken pages with the same matching rule.

## Changes after registration

All made before any agent run.

1. 2026-10-19, during screening: how inclusion criterion 3 is applied. A
   difference between the two states counts as a defect only when the broken
   state shows a fault a reviewer could name without seeing the fix: content cut,
   covered or overlapping, content outside the screen, a component that breaks
   into the wrong rows, an element misaligned with the siblings or container it
   belongs to, an element mis-sized against an attached element (a field shorter
   than its button), or a glyph off the centre of its control. Spacing, shadow or
   style refinements that leave the broken state looking intended are excluded.
2. 2026-10-19, after screening the three registered sources: they gave 4
   cases (AdminLTE 3: 3 of 60 screened; SB Admin 2: 1 of 5; Pico 1: 0 of 30),
   too few to compare two arms. Added source: ColorlibHQ/AdminLTE version 4 line
   (origin/master minus the version 3 line; built pages under dist/), with the
   same candidate rule, inclusion rule and limits (8 accepted or 60 screened).
   Pages that load fonts, icons or libraries from a CDN get those files vendored
   locally; every case is re-checked on the vendored pages before it is used.
3. 2026-10-19, before the runs: screening closed with 12 cases (AdminLTE 4: 8 of
   60 screened; AdminLTE 3: 3 of 60; SB Admin 2: 1 of 5; Pico 1: 0 of 30). The
   header overflow that afa7215e fixed also shows, by 4 or 52 px, on four other
   AdminLTE 4 states; it is keyed as a known defect wherever it shows. Agents
   check every page at 360x780 and 1440x900, the two sizes where all 12 cases
   show. Sealed SHA-256 before any run: answer key
   915ad36c4dabf53a42e871b503ede552517edefe4135fe0a9c512bb05928435f, page
   assignment 404d26af11b76ccd0b09b3635be439eb23926cc06007f4c378f07ed90215726f,
   prompts 52c837ad508ff60a8db69799814aa411d5cbe43d1b505112b34ee81f9e83466f
   (both arms) and 5dbb8f30f50c72cee709a684a54554e1afdd2f9765ebfd0fad5b43b3366c8cf1
   (skill arm addition), run pages
   85a44faca52d92e52c3df95ee65a0128cc80696fff2aba785990e76ab23335bd.
