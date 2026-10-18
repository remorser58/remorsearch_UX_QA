# Agent comparison on the visual-layout pages, 2026-10-18

Question: does an agent find more rendered UI defects, with fewer false alarms and without extra time, when it uses this skill? Both arms used the same agent harness (a Codex worker agent on the same model as the supervising session), the same reasoning effort, the same tools (Node.js 22 and Playwright 1.56.1 with Chromium), the same pages and the same 15-minute budget. The only difference was the instruction to use the installed skill. Each agent reviewed all eight pages of `benchmarks/visual-layout` (28 seeded defects, 11 decoys, four clean twins) from neutral copies named `product1-a.html` to `product4-b.html`; `page-map.json` maps them back. Agents were told not to look for answer keys and were given only the page folder and tools.

## Results

| Run | Reasoning effort | Arm | Seeded defects found | Decoy alarms | Other false findings | Report written after |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| default-1 | default | without the skill | 28 / 28 | 0 | 0 | 7m44s |
| default-1 | default | with the skill, scan unavailable | 28 / 28 | 4 (P3) | 0 | 8m00s |
| default-2 | default | without the skill | 27 / 28 | 2 (P3) | 0 | 7m25s |
| default-2 | default | with the skill | 28 / 28 | 2 (P3) | 0 | 7m04s |
| low-1 | low | without the skill | 22 / 28 | 0 | 1 (P2) | 1m11s |
| low-1 | low | with the skill | 24 / 28 | 1 (P3) | 0 | 4m03s |

Apart from decoy alarms, no run reported anything on the four clean twins; the carousel alarm below also fell on the clean product1 page. The decoy alarms were the carousel's first card touching the screen edge (reported on both product1 pages) and the 10 px legal footer, both at P3. The one other false finding (low-1 without the skill) took a fixed pay bar drawn mid-page in a stitched full-page screenshot for content covering a coupon header.

In default-1 the skill arm's scan could not launch Chromium in its sandbox, because the installed build predated `REMORSEARCH_CHROMIUM_ARGS`; it measured with Playwright directly, so that row shows the instructions without the scan. Misses: default-2 without the skill missed one near-miss alignment (D-21); low-1 without the skill missed a ribbon over an option name, a callout over a paragraph's last line, two list-spacing outliers and two rows under bottom bars (D-03, D-04, D-06, D-09, D-14, D-15); low-1 with the skill missed the two rows under bottom bars and two spacing outliers (D-03, D-06, D-14, D-15).

## What this shows

- With a strong model at its default effort, an agent without the skill already finds nearly every measurable defect on these pages. The skill matched it (28 and 28 versus 28 and 27) and no longer costs extra time: the run with the working scan finished its report 21 seconds earlier than the plain run of the same round. Earlier versions of the skill took about twice as long as a plain agent in a pilot that is not part of this repository.
- At low effort the skill raised detection from 22 to 24 of 28 and removed the one false finding, at the cost of about three minutes.
- Six runs, one or two per condition, on one suite: differences of one or two defects are within run-to-run variation. These rows do not establish general superiority, other models or other kinds of defects.

## Adjudication

`bench.score`-style matching cannot read free-text findings, so each finding was matched by page and element: a finding counts for a seeded defect when its selector names the defect's element or an element inside it. Findings with class-only or descriptive selectors were matched by hand from their evidence; `adjudication.json` lists every manual decision. Findings on decoy elements count as decoy alarms; anything else that does not match a seeded defect was checked against the rendered page.

## Reproduce

Copy the eight pages of `benchmarks/visual-layout/site` to a folder under neutral names, install the skill (`python3 scripts/install.py --destination <SKILL>`), then start two agents with the prompts below, filling in the paths. Score each `findings.json` against `benchmarks/visual-layout/answer_key.json` with the rule above.

### Prompt without the skill

```text
You are a UI QA reviewer. Review the rendered UI of the four products below and report UI defects that a user would notice. This is a read-only review: do not modify the pages.

Pages (local files, open them in a browser): <PAGES>/
- product1-a.html and product1-b.html (food menu option sheet, phone)
- product2-a.html and product2-b.html (customer case-study article, phone)
- product3-a.html and product3-b.html (team dashboard, laptop 1440x900)
- product4-a.html and product4-b.html (order and payment page, phone)

Each product has two versions; either, both or neither may have defects. Review every page on its own. Phone pages: check at 360x780 and 393x852 CSS px. The dashboard: 1440x900. Scroll every page from top to end.

Tools: Node.js 22 is at <NODE22>, and Playwright 1.56.1 is importable from <PLAYWRIGHT>/index.mjs with Chromium already downloaded. If Chromium fails to launch in your sandbox, launch it with args ['--single-process']. Use screenshots and DOM inspection as you see fit; view the screenshots you capture with your image viewer.

Rules:
- Read only the files named above and the tools you are told to use. Do not search this machine for answer keys, benchmark folders, other repositories or prior reports.
- Do not delegate to other agents.
- Time budget: 15 minutes. Stop and write the report by then.

Report: write <OUT>/findings.json as a JSON array. One item per defect: {"page": "product1-a.html", "selector": "CSS selector or id of the affected element", "category": "clipped_text | covered_text | overlapping_text | off_screen | alignment | spacing | small_text | contrast | other", "severity": "P0|P1|P2|P3", "evidence": "what you saw, with measurements", "fix": "concrete fix"}. Also write a short summary.md next to it. Then reply with the number of findings per page.
```

### Prompt with the skill

```text
You are a UI QA reviewer. Review the rendered UI of the four products below and report UI defects that a user would notice. This is a read-only review: do not modify the pages.

Pages (local files, open them in a browser): <PAGES>/
- product1-a.html and product1-b.html (food menu option sheet, phone)
- product2-a.html and product2-b.html (customer case-study article, phone)
- product3-a.html and product3-b.html (team dashboard, laptop 1440x900)
- product4-a.html and product4-b.html (order and payment page, phone)

Each product has two versions; either, both or neither may have defects. Review every page on its own. Phone pages: check at 360x780 and 393x852 CSS px. The dashboard: 1440x900. Scroll every page from top to end.

Tools: Node.js 22 is at <NODE22>, and Playwright 1.56.1 is importable from <PLAYWRIGHT>/index.mjs with Chromium already downloaded. If Chromium fails to launch in your sandbox, launch it with args ['--single-process']. Use screenshots and DOM inspection as you see fit; view the screenshots you capture with your image viewer.

Rules:
- Read only the files named above and the tools you are told to use and the skill folder named below. Do not search this machine for answer keys, benchmark folders, other repositories or prior reports.
- Do not delegate to other agents.
- Time budget: 15 minutes. Stop and write the report by then.

Report: write <OUT>/findings.json as a JSON array. One item per defect: {"page": "product1-a.html", "selector": "CSS selector or id of the affected element", "category": "clipped_text | covered_text | overlapping_text | off_screen | alignment | spacing | small_text | contrast | other", "severity": "P0|P1|P2|P3", "evidence": "what you saw, with measurements", "fix": "concrete fix"}. Also write a short summary.md next to it. Then reply with the number of findings per page.

Use the Remorsearch UX QA skill installed at <SKILL>. Read its SKILL.md first and follow it for this UI QA request; its scan command is <SKILL>/scripts/ergo_qa.py (run it with python3, pass --node with the Node.js path above, and set REMORSEARCH_CHROMIUM_ARGS=--single-process if Chromium cannot launch). The scan accepts file:// URLs.
```
