# Real layout bugs, round 3: preregistered protocol

Written 2026-10-20, before any candidate in the sources below was rendered or judged and before any agent ran on these sources. Changes after this point are listed at the end with their reason.

## Question

After rounds 1 and 2, the scan gained measurements for the misses those rounds exposed: an icon or glyph off the centre of its control, a field whose attached button has different edges, a page wider than the screen, and a full-height layout that scrolls a few pixels. The scan also records both devices at once and reports one row per cause. Those changes were made while looking at the round 1 and 2 pages, so the pages are no longer a fair test. On new real layout bugs from projects neither round used, does an agent with the skill find more of them than the same agent without it, without more false alarms and within the time budget?

## Skill under test

Commit 1fc4581 of branch `codex/v1.0.1`, installed once with `scripts/install.py --no-prompt` into an isolated folder (payload SHA-256 `e9685a9f141d7504add39d39cb67d2efce0c3c588433fa183ead905462e9278b`). No skill or detector file changes until every round 3 run is scored. The same frozen skill is also run on the round 1 and 2 pages; those results are development numbers and are reported apart from this round.

## Sources

Chosen for one practical reason: their history holds ready-to-open HTML pages with the built CSS committed, so a historical commit renders without a build. None was used in round 1 or 2. Screened in this order:

1. StartBootstrap/startbootstrap-agency
2. StartBootstrap/startbootstrap-creative
3. StartBootstrap/startbootstrap-freelancer
4. StartBootstrap/startbootstrap-grayscale
5. StartBootstrap/startbootstrap-new-age
6. StartBootstrap/startbootstrap-landing-page
7. StartBootstrap/startbootstrap-clean-blog
8. StartBootstrap/startbootstrap-resume
9. designmodo/Flat-UI
10. mdbootstrap/bootstrap-material-design
11. BootstrapDash/PurpleAdmin-Free-Admin-Template
12. creativetimofficial/light-bootstrap-dashboard
13. creativetimofficial/paper-dashboard
14. creativetimofficial/now-ui-dashboard
15. creativetimofficial/black-dashboard
16. Kamona-WD/kwd-dashboard
17. thomaspark/bootswatch: each theme's preview page (`docs/<theme>/index.html`), commits on the version 4 and 5 lines from 2017-08 that change one to three themes' built CSS.

Sources 1 to 16 were picked by repository metadata only (size, stars, whether HTML and built CSS are committed). They hold 59 candidates in all, too few for twelve cases at the yield of rounds 1 and 2, so Bootswatch was added. Its commit subjects were listed before this protocol was written, and several name defect kinds the new measurements look for (input and button heights). It can contribute at most three cases, like every source. Two other repositories, themesberg/volt-bootstrap-5-dashboard and zuramai/mazer, were cloned and dropped before screening because their histories do not commit the built CSS next to the pages.

## Candidate rule

As in round 2: every commit on the default branch or a tag that changes a CSS, SCSS, LESS or HTML file and whose subject matches (case-insensitive) overflow, overlap, cut off, cut-off, clip, truncat, hidden, behind, cover, misalign, align, z-index, wrap, responsive, mobile, small screen, width, height, spacing, margin, padding, gap, position, sticky, fixed, layout. Candidates are screened newest first.

## Inclusion

Unchanged from rounds 1 and 2:

1. The defect is visible without interaction (on load and after scrolling) on an HTML page shipped in the repository at the parent commit, at 360x780 or 393x852 (phone, touch) or 1440x900 (laptop), in Chromium 141 (Playwright 1.56.1).
2. At the fix commit, or the first later commit whose committed built CSS contains the fix, the defect is gone on the same page and viewport.
3. A reviewer could name the fault without seeing the fix: content cut, covered or overlapping, content outside the screen, a component that breaks into the wrong rows, an element misaligned with the siblings or container it belongs to, an element mis-sized against an attached element, or a glyph off the centre of its control, by at least 2 CSS px where it is a geometry fault.

Excluded: defects that need hover, click, focus or keyboard; other browsers only; print; colour or contrast only; wording only; script errors without a visible layout effect; spacing or style refinements that leave the broken state looking intended. Every screened candidate is listed with its verdict and reason.

At most 3 cases are accepted from one source; screening of a source stops at 3 accepted or 40 screened. Screening stops when 12 cases are accepted. If the sources run out first, the comparison runs with the cases found, and the shortfall is reported.

## Page items, arms, runs, scoring and decision

As registered for round 2, unchanged: page items with broken and fixed states, the seeded split into groups A, B and C and the three-run rotation, neutral page names, local files with the network blocked; GPT-6.1 Sol and DeepSeek 4.1 Flash (InferHub combo route) at reasoning effort `high`, each running both arms once per run index in fresh sessions; the round 1 prompt templates byte for byte; a 30-minute budget; at most six agents at once; found, fixed-state alarm, valid extra and unsupported judged from a file without arm or model labels. The skill counts as better for a model only if its arm finds more known defects in all three paired runs, has no more fixed-state alarms plus unsupported findings in total, and its median time is at most 1.5 times the plain arm's.

## Scan alone

The frozen scan runs on every page state as the agents would run it (`file://` URL, `REMORSEARCH_CHROMIUM_ARGS=--single-process`). Broken pages are scored with the matching rule; candidates on fixed pages are counted.

## Changes after registration
