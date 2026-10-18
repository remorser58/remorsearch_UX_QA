# Real layout bugs: agent QA with and without the skill

On 12 layout bugs that open-source maintainers reported and fixed, Remorsearch UX QA 1.0.0 did not make agent QA better. Over three runs each, GPT-6.1 Sol found 18 of the 34 known defects it was shown without the skill and 13 with it, and DeepSeek 4.1 Flash found 14 without and 15 with it. Neither model met the rule registered before the runs. No run raised an alarm on a fixed page. Every arm found the four cases in which a phone page scrolls sideways each time they were shown, and no arm found the five subtler cases.

In this setup the skill's own scan mostly measured pages that had lost their stylesheets, so it could not point the agents to any of the known bugs. The pages were local files, which the skill's documentation allows, and on a `file://` page the scan loads only files in the page's own folder. On 8 of the 12 items it blocked the page's own theme stylesheet, which sits in a parent folder, and measured the page without it; `scan.md` said that styles might be missing. In every scan the skill-arm agents ran, the reflow, text-spacing and short-window passes failed, as they do when Chromium runs with `REMORSEARCH_CHROMIUM_ARGS=--single-process`, a setting the prompt and the documentation allow when Chromium cannot launch in a sandbox. `scan.md` does not report the failure. Served over http with a normal Chromium launch, the scan alone matched 2 of the 12 bugs and the shared header overflow on every page where it shows; as the agents ran it, the scan matched none.

The protocol was registered before any candidate was screened: [`PROTOCOL.md`](PROTOCOL.md), first committed in f117811, with four changes listed at its end, all made before the runs.

## Cases

| ID | Source | Fix commit | Page | Viewport | Defect in the broken state |
| --- | --- | --- | --- | --- | --- |
| S1 | SB Admin 2 | 60d24312 | `index.html` | laptop | Topbar search field 34.4 px tall next to its 38 px button |
| A1 | AdminLTE 3 | 9cc4ce39 (#4042), built in bd4d9c72 | `index.html` | laptop | World-map zoom glyphs 2 px below the centre of their buttons |
| A2 | AdminLTE 3 | 6f396ae1 | `iframe.html` | phone | Iframe tab toolbar wraps into two rows |
| A3 | AdminLTE 3 | 6934469b | `pages/tables/data.html` | phone | DataTables table 549 px wide on a 360 px screen |
| B1 | AdminLTE 4 | 083d844f (#6114), built in 12b4b06f | `dist/layout/collapsed-sidebar.html` | laptop | Mini-sidebar logo 4 px left of centre |
| B2 | AdminLTE 4 | 60fabdb3 | `dist/docs/javascript/plugins-overview.html` | phone | Reference tables make the page 942 px wide |
| B3 | AdminLTE 4 | afa7215e | `dist/index.html` | phone | Header row 412 px wide, user menu off screen |
| B4 | AdminLTE 4 | 3f9716ad (#6104) | `dist/layout/fixed-sidebar.html` | laptop | Layout 948 px tall in a 900 px window, so it scrolls 48 px |
| B5 | AdminLTE 4 | d635f939 | `dist/UI/ribbons.html` | both | Corner ribbons leave a bare triangle in the card corner |
| B6 | AdminLTE 4 | 155e8698 (#6044) | `dist/mailbox/inbox.html` | phone | Inbox rows do not truncate, page 940 px wide |
| B7 | AdminLTE 4 | e1892ef3 (#6020), built in f0c024de | `dist/layout/fixed-header.html` | laptop | Sidebar not sticky under a fixed header, page 1699 px tall |
| B8 | AdminLTE 4 | dc7d4bd4, built in aae8438e | `dist/UI/general.html` | phone | Sidebar open on load, covering the content |
| H | AdminLTE 4 | afa7215e | B4, B5 and B6 in both states, B7 fixed | phone | Header user menu past the right edge by 4 or 52 px |

H is the header overflow that afa7215e fixed, where it also shows on other AdminLTE 4 states. As registered, it counts once per page where it shows, which makes it 10 of the 34 known defects shown to each arm.

Screening went through 155 candidate commits newest first (AdminLTE 4: 60, AdminLTE 3: 60, SB Admin 2: 5, Pico 1: 30) and accepted 12. [`screening.json`](screening.json) lists each candidate with its verdict.

## Design

Each item is one page at its broken and its fixed commit. The items were split into three groups: A (B3, A3, A1, B2), B (B8, B7, A2, B6) and C (B5, S1, B1, B4). Run 1 showed A and B broken with C fixed, run 2 showed A and C broken with B fixed, and run 3 showed B and C broken with A fixed. Each run therefore held 12 pages with neutral names (p01 to p12) and 11 or 12 known defects; [`assignment.json`](assignment.json) maps the names to items.

Each model ran both arms once per run, in fresh sessions, with the same pages, prompt, tools (Node.js 22, Playwright 1.56.1 with Chromium), a 30-minute budget and no network. The skill arm also got the frozen skill, installed once from tag v1.0.0 (payload SHA-256 `4fcfbb1a…a60f0`), and an instruction to follow it. The prompt templates are in [`prompts/`](prompts/).

A finding counts as found when it is on the right page, points at the defect's element or an element inside or around it, and describes the same visible problem. A finding on a fixed page that calls a known defect's element broken is a fixed-state alarm. Every other finding was judged from the pixels as a valid extra (a real defect outside the key) or unsupported.

## Results

| Run | Model | Arm | Shown | Found | Fixed-state alarms | Unsupported | Valid extras | Findings | Minutes |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | Sol | plain | 11 | 6 | 0 | 0 | 4 | 10 | 6.3 |
| 1 | Sol | skill | 11 | 6 | 0 | 0 | 5 | 11 | 12.5 |
| 2 | Sol | plain | 12 | 8 | 0 | 0 | 9 | 17 | 11.9 |
| 2 | Sol | skill | 12 | 4 | 0 | 0 | 6 | 10 | 9.3 |
| 3 | Sol | plain | 11 | 4 | 0 | 0 | 5 | 9 | 10.0 |
| 3 | Sol | skill | 11 | 3 | 0 | 0 | 9 | 12 | 15.5 |
| 1 | Flash | plain | 11 | 6 | 0 | 0 | 3 | 10 | 33.3 |
| 1 | Flash | skill | 11 | 6 | 0 | 0 | 3 | 9 | 34.0 |
| 2 | Flash | plain | 12 | 4 | 0 | 0 | 1 | 5 | 31.5 |
| 2 | Flash | skill | 12 | 5 | 0 | 1 | 3 | 10 | 33.9 |
| 3 | Flash | plain | 11 | 4 | 0 | 2 | 3 | 9 | 34.4 |
| 3 | Flash | skill | 11 | 4 | 0 | 0 | 3 | 8 | 34.1 |

| Model | Arm | Found | Found without H | Alarms | Unsupported | Valid extras | Median minutes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Sol | plain | 18 of 34 | 11 of 24 | 0 | 0 | 18 | 10.0 |
| Sol | skill | 13 of 34 | 10 of 24 | 0 | 0 | 20 | 12.5 |
| Flash | plain | 14 of 34 | 10 of 24 | 0 | 2 | 7 | 33.3 |
| Flash | skill | 15 of 34 | 9 of 24 | 0 | 1 | 9 | 34.0 |

The registered rule counts the skill as better only if its arm finds more known defects in all three paired runs, has no more alarms and unsupported findings in total, and takes at most 1.5 times the plain arm's median time.

| Model | Found per run, skill vs plain | Alarms and unsupported, skill vs plain | Median time, skill over plain | Outcome |
| --- | --- | --- | ---: | --- |
| GPT-6.1 Sol | 6 vs 6, 4 vs 8, 3 vs 4 | 0 vs 0 | 1.25 | No demonstrated improvement |
| DeepSeek 4.1 Flash | 6 vs 6, 5 vs 4, 4 vs 4 | 1 vs 2 | 1.02 | No demonstrated improvement |

### Per defect

Found over shown, across the three runs of each arm.

| Defect | Sol plain | Sol skill | Flash plain | Flash skill |
| --- | ---: | ---: | ---: | ---: |
| S1 | 0/2 | 0/2 | 0/2 | 0/2 |
| A1 | 0/2 | 0/2 | 0/2 | 0/2 |
| A2 | 2/2 | 2/2 | 0/2 | 0/2 |
| A3 | 2/2 | 2/2 | 2/2 | 2/2 |
| B1 | 0/2 | 0/2 | 0/2 | 0/2 |
| B2 | 2/2 | 2/2 | 2/2 | 2/2 |
| B3 | 2/2 | 2/2 | 2/2 | 2/2 |
| B4 | 1/2 | 0/2 | 0/2 | 0/2 |
| B5 | 0/2 | 0/2 | 0/2 | 0/2 |
| B6 | 2/2 | 2/2 | 2/2 | 2/2 |
| B7 | 0/2 | 0/2 | 0/2 | 0/2 |
| B8 | 0/2 | 0/2 | 2/2 | 1/2 |
| H | 7/10 | 3/10 | 4/10 | 6/10 |

The four cases in which a phone page scrolls sideways (A3, B2, B3, B6) were found every time they were shown; the same header overflow on other pages (H) was found 3 to 7 times out of 10. S1, A1, B1, B5 and B7 were found in none of their 40 showings: a search field 3.6 px shorter than its button, zoom glyphs 2 px below centre, a logo 4 px off centre, a ribbon that leaves a bare corner, and a sidebar that scrolls away under a fixed header. Most of the gap between Sol's arms is H, which its plain arm reported on 7 of 10 pages and its skill arm on 3.

Valid extras came from every arm: a cut avatar, a split legend and a scroll button over the footer on S1; a pagination button past the left edge on A3; a to-do label that drops below its checkbox on A1; a header search block on its own row and an empty-state heading flush against the left edge on A2; a 26 px navbar input on B8; a ribbon over paragraph text on B5; a search group overlapping the Inbox title on B6; and a truncated sidebar label on two AdminLTE 4 pages. Some come from built CSS that lagged the HTML at that commit.

## The scan alone

The registered scan-alone result is the scan as the skill-arm agents ran it. Two more configurations were added after the agent runs to find out why it missed.

| Configuration | Cases matched (of 12) | H matched (broken pages) | What went wrong |
| --- | ---: | ---: | --- |
| `file://` with `--single-process` (as the agents ran it) | 0 | 0 of 3 | Theme stylesheet in a parent folder blocked on 8 of 12 items; reflow, text-spacing and short-window passes failed in all 24 states, the focus walk in half of the device runs |
| `file://`, normal launch | 0 | 0 of 3 | Same blocked stylesheets; the 320 px copies rendered without any of the page's styles |
| http, normal launch | 2 (B3, B6) | 3 of 3 | Nothing failed |

Over http, RF-01 named the header row on B3 (412 px wide at 320 px), the inbox rows on B6, and the header overflow on every state where the key lists it, including the four fixed states, and did not flag the header on B3's fixed state. On B6's fixed state it listed the newly truncated inbox text as cut (eight P3 truncation notes and one RF-01 at 320 px), which an agent has to dismiss after viewing. RF-01 measures at 320 CSS px (400 % zoom), one step narrower than the phone. A3 and B2 scroll sideways because of tables, which RF-01 exempts as WCAG 1.4.10 does. The scan caught none of the misalignment bugs. Most candidates in every configuration were about target size, contrast, accessible names and icon-only controls, and in the `file://` runs 8 of the 12 items gave the same candidate list in both states. [`scan-alone.json`](scan-alone.json) has the counts, blocked requests, pass failures and layout candidates per state.

## Deviations

- Reasoning effort was not set when the agents started, so each inherited the supervising session's setting, which may differ from the model's default. The effort actually applied was not recorded.
- Every Flash run reached the budget. Stop messages went out at about 33 minutes, and flash-r2-plain ended at 29.95 minutes without a report and was asked once to write it. Flash times measure the budget.
- Each run's prompt fills the template placeholders (page list, output folder, skill folder) and adds a short paragraph that names the run's working folder and rules out reading other benchmark folders.
- Up to six runs shared one machine, with the first scan-alone job running at the same time. Times are wall-clock from start to the findings file.
- The findings were scored from a file without arm or model labels, but the scorer had seen some raw outputs while watching the runs. A keyword rule proposed a verdict for each of the 120 findings, every verdict was reviewed by hand, and 14 were set by hand; [`adjudication.json`](adjudication.json) marks them and gives the measurements behind the overrides.
- Rejection reasons were not written down for each screened candidate. [`screening.json`](screening.json) gives every verdict with the measured pixel difference and a reason category reconstructed afterwards.
- The scan alone was registered as one run. The http run and the `file://` run with a normal launch were added after the agent runs.

## Limits

- 12 cases, 11 of them from AdminLTE; all are Bootstrap admin pages.
- Chromium only, at 360x780 and 1440x900, from local copies with CDN files vendored. The photos S1 loads from source.unsplash.com are missing in both states.
- Three paired runs per model. Sol's plain arm alone ranged from 4 to 8 found per run, so a difference of a few defects is within run-to-run variation; the rule asks for a consistent direction for that reason.
- These pages have now been seen. A corrected skill needs new cases for a fair retest.

## Files

| File | Contents |
| --- | --- |
| [`PROTOCOL.md`](PROTOCOL.md) | Registration and the four changes made before the runs |
| [`answer_key.json`](answer_key.json), [`assignment.json`](assignment.json) | Sealed before the runs; their SHA-256 values are in the protocol |
| [`prompts/`](prompts/) | The sealed prompt templates for both arms and the skill arm's addition |
| `findings/<model>-r<run>-<arm>.json` | Each run's report as written |
| [`adjudication.json`](adjudication.json) | The verdict for every finding |
| [`scores.json`](scores.json) | Per-run scores, the defects found and missed, and times |
| [`scan-alone.json`](scan-alone.json) | The scan on its own, per state, in the three configurations |
| [`screening.json`](screening.json) | Every screened candidate with its verdict |

To check the seals, run `shasum -a 256 answer_key.json assignment.json prompts/plain.txt prompts/skill-tail.txt` in this folder and compare with changes 3 and 4 in the protocol. The pages themselves are not published here. Each case can be rebuilt by opening the listed page at the parent of the fix commit and at the fix or build commit, with its CDN files saved locally.
