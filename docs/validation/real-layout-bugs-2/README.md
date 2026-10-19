# Real layout bugs, round 2: the fixed skill on new cases

On 4 new layout bugs that open-source maintainers fixed, the skill again did not change what agents found. With the fixed skill (commit 05fe4ba of `codex/v1.0.1`), GPT-6.1 Sol and DeepSeek 4.1 Flash each found 6 of the 8 known defects they were shown, with the skill and without it. Every run found each of the three overlap and cut cases whenever it was shown. No run found the fourth, a carousel arrow 10 px below the centre of its control, and neither did the scan. No run raised an alarm on a fixed page or reported anything the pixels did not support. With the skill, Sol took longer (median 10.2 against 6.6 minutes); Flash used its whole budget either way. Under the rule registered before the runs, the outcome for both models is no demonstrated improvement.

The scan on its own, run the way the agents ran it, matched 2 of the 4 bugs with version 1.0.0 and 2 with the fixed skill. The fixes let the scan load the page's parent-folder stylesheets and run all of its passes, so it now finds the contact cards whose last line hides under the card footer, which 1.0.0 measured without Bootstrap's stylesheet. They also exposed a bug: on the dashboard with six identical count tiles, the text-spacing pass gave two lost elements the same selector, `run.json` validation rejected it, and the scan stopped. All three Sol runs with the skill hit this on that page and worked around it. The bug was fixed after scoring; see [After scoring](#after-scoring).

The protocol was registered before any candidate was screened: [`PROTOCOL.md`](PROTOCOL.md), first committed in 3c5b0cb. Three changes at its end were made before the runs, and a fourth records the fix made after scoring.

## Cases

Screening went through 257 candidate commits in 12 projects, newest first, and accepted 4. The nine registered sources gave 4 cases; three sources added before any run gave none. [`screening.json`](screening.json) lists every candidate with its verdict and reason. Most were rejected because the earlier state shows no fault a reviewer could name, the fault needs a click, hover or another browser, the change is colour or wording, or no build of the fix is committed.

| Item | Source | Fix commit | Page | Viewport | Defect in the broken state |
| --- | --- | --- | --- | --- | --- |
| spectre-4cb36cd7 | picturepan2/spectre | 4cb36cd7 | `docs/components.html` | phone | The page keeps its 960 px desktop layout: the side navigation is drawn over the documentation text, and the content runs 600 px past the right edge |
| gentelella-fc3c0364 | ColorlibHQ/gentelella | fc3c0364 | `production/contacts.html` | phone | In every contact card the grey footer covers the last detail line (10 px at 360 px) |
| gentelella-c0602144 | ColorlibHQ/gentelella | c0602144 | `production/index.html` | phone | Six count tiles sit three to a row and their labels are cut to "Total Conne…", "From l…" |
| bootstrap-d255ba37 | twbs/bootstrap 3 | d255ba37 (#16371), built in 82279a8e | `docs/examples/carousel/index.html` | phone | The previous and next chevrons sit 10 px below the centre of their controls |

Each defect was re-measured on the saved pages over `file://` with the network blocked: present in the broken state, gone in the fixed state. [`answer_key.json`](answer_key.json) has the elements, the rule for counting a finding as found and the measurements.

## Design

As in [round 1](../real-layout-bugs/README.md): each item is one page at its broken and fixed commit, and the seeded shuffle put bootstrap-d255ba37 and gentelella-c0602144 in group A, gentelella-fc3c0364 in B and spectre-4cb36cd7 in C. Run 1 showed A and B broken with C fixed, run 2 A and C broken with B fixed, run 3 B and C broken with A fixed, so the runs held 3, 3 and 2 known defects on four pages with neutral names. Each model ran both arms once per run, in fresh sessions, with the same pages, the round-1 prompt templates byte for byte ([`prompts/`](prompts/)), the same tools (Node.js 22, Playwright 1.56.1 with Chromium), reasoning effort `high` set when each agent started, a 30-minute budget and no network. The skill arm also got the frozen skill, installed with `scripts/install.py --no-prompt` (payload SHA-256 `2a9c9911…fc689`).

A finding counts as found when it is on the right page, points at the defect's element or an element inside or around it, and describes the same visible problem. A finding on a fixed page that calls the item's defect element broken is a fixed-state alarm. Every other finding was judged from the pixels as a valid extra or unsupported.

## Results

| Run | Model | Arm | Shown | Found | Fixed-state alarms | Unsupported | Valid extras | Findings | Minutes |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | Sol | plain | 3 | 2 | 0 | 0 | 1 | 3 | 6.6 |
| 1 | Sol | skill | 3 | 2 | 0 | 0 | 1 | 3 | 10.2 |
| 2 | Sol | plain | 3 | 2 | 0 | 0 | 1 | 5 | 8.2 |
| 2 | Sol | skill | 3 | 2 | 0 | 0 | 1 | 5 | 13.3 |
| 3 | Sol | plain | 2 | 2 | 0 | 0 | 0 | 4 | 6.3 |
| 3 | Sol | skill | 2 | 2 | 0 | 0 | 0 | 3 | 9.6 |
| 1 | Flash | plain | 3 | 2 | 0 | 0 | 1 | 3 | 31.0 |
| 1 | Flash | skill | 3 | 2 | 0 | 0 | 2 | 4 | 37.0 |
| 2 | Flash | plain | 3 | 2 | 0 | 0 | 2 | 5 | 32.1 |
| 2 | Flash | skill | 3 | 2 | 0 | 0 | 1 | 4 | 33.9 |
| 3 | Flash | plain | 2 | 2 | 0 | 0 | 1 | 5 | 29.0 |
| 3 | Flash | skill | 2 | 2 | 0 | 0 | 2 | 6 | 34.1 |

| Model | Found per run, skill vs plain | Alarms and unsupported, skill vs plain | Median time, skill over plain | Outcome |
| --- | --- | --- | ---: | --- |
| GPT-6.1 Sol | 2 vs 2, 2 vs 2, 2 vs 2 | 0 vs 0 | 1.55 | No demonstrated improvement |
| DeepSeek 4.1 Flash | 2 vs 2, 2 vs 2, 2 vs 2 | 0 vs 0 | 1.10 | No demonstrated improvement |

The registered rule counts the skill as better only if its arm finds more known defects in all three paired runs, has no more alarms and unsupported findings in total, and takes at most 1.5 times the plain arm's median time. Every arm found every overlap and cut defect each time it was shown (spectre, both gentelella items: 2 of 2 each) and missed the carousel chevrons each time (0 of 2), so the runs could not separate the arms.

Valid extras: the dashboard's "Top Campaign Performance" heading cut to "Top Campaign Perfor…" at 360 px (in both states), the contacts page's A to Z filter wrapping X, Y and Z onto a second row, and its "…" separator sitting 12 px below the centre of the letter buttons. Sol found 2 valid extras in each arm, Flash 4 without the skill and 5 with it.

What the skill arm did, from its summaries, read after scoring: every Sol run ran the scan on all four pages, and each one hit the dashboard scan stop described above, then reran it phone-only or measured the page directly. Of the Flash runs, one never got a scan to finish and the other two ran it on one or two pages. Agents in both arms reported the cut and covered text with measurements of their own; with the skill, they also listed scan candidates they had dismissed after viewing them, such as scrollable code blocks and collapsed accordion content.

## The scan alone

The scan ran on all 8 states as the agents would run it (`file://` URL, `REMORSEARCH_CHROMIUM_ARGS=--single-process`), once with 1.0.0 and once with the frozen fixed skill. [`scan-alone.json`](scan-alone.json) has the counts and the matching candidates per state.

| Item | 1.0.0 | Fixed skill (05fe4ba) |
| --- | --- | --- |
| spectre-4cb36cd7 | Matched: text cut by the screen edge and nav labels over content text, on the phone | Matched, same candidates |
| gentelella-fc3c0364 | Not matched: Bootstrap's stylesheet in a parent folder was blocked | Matched: "Address:" lines covered by the footer on the phone, none on the fixed page |
| gentelella-c0602144 | Matched: tile labels and captions cut with ellipses | Scan stopped in both states (duplicate selector in `run.json`) |
| bootstrap-d255ba37 | Not matched | Not matched |
| Passes that failed | Reflow, text-spacing, short-window and focus walk, in every state | None |

On spectre's fixed page both versions also listed 6 code blocks as cut by the screen edge and 2 overlaps of labels inside collapsed accordion examples. The code blocks scroll inside their own boxes and the accordion labels are hidden, and the agents who saw these candidates dismissed them. With 1.0.0 the Bootstrap carousel page was also measured without its stylesheet, which produced 37 candidates on each state against 6 with the fixed skill.

## After scoring

The duplicate selector came from the text-spacing pass naming elements by a path of at most five levels; the six identical count tiles share that path. The pass now extends the path until it matches one element and skips a repeated target, and the driver self-test gained a page with three identical cards that fails without the change. These edits came after every run was scored, so none of the numbers above use them. Rerun on the dashboard as a diagnostic (commit 5ca0459, same settings), the patched scan completes on both states with no failed pass. On the broken state it lists the cut tile labels and captions 8 times on the phone; on the fixed state it lists none. With this fix the scan alone would match 3 of the 4 cases, but that figure comes from a change made after seeing these pages and is not part of the registered result.

## Deviations

- Only 4 of the planned 12 cases were found, so the groups hold 2, 1 and 1 items and each run shows 2 or 3 known defects. Changes 1 to 3 in the protocol record the added sources, the replacement of AdminLTE (which round 1 used) and the seal.
- Up to six agents ran at once; each later run started when an earlier one ended, so runs 2 and 3 of Flash overlapped with Sol's and with the scan-alone jobs. Times are wall-clock from start to the findings file.
- Stop messages went out at 33.2 to 33.3 minutes to the Flash runs still working; flash-r2-plain had written its report at 32.1 minutes, before its stop message.
- The findings were scored from a file without arm or model labels after every run had finished. The scorer saw each run's completion message, which gives finding counts per page, as it arrived. Every verdict was set by hand; the ones that needed a fresh measurement carry a note in [`adjudication.json`](adjudication.json).
- One laptop finding on the contacts page was counted as found: at 1440 px the same footer covers the bottom 10 px of each portrait. The run that reported it also reported the phone defect, so the count does not change.

## Limits

- 4 cases, all from Bootstrap-era documentation and admin pages. Three are large and were found every time; one is a 10 px glyph offset that nobody found. Cases between those two levels would be needed to tell the arms apart.
- Chromium only, at 360x780 and 1440x900, from local copies.
- Three paired runs per model; with these cases the arms tie in every run.
- These pages have now been seen. Another retest needs new cases.

## Files

| File | Contents |
| --- | --- |
| [`PROTOCOL.md`](PROTOCOL.md) | Registration, the three changes made before the runs and the fix after scoring |
| [`answer_key.json`](answer_key.json), [`assignment.json`](assignment.json) | Sealed before the runs; their SHA-256 values are in change 3 |
| [`prompts/`](prompts/) | The prompt templates, identical to round 1 |
| `findings/<model>-r<run>-<arm>.json` | Each run's report as written |
| [`adjudication.json`](adjudication.json) | The verdict for every finding |
| [`scores.json`](scores.json) | Per-run scores, the defects found and missed, and times |
| [`scan-alone.json`](scan-alone.json) | The scan on its own per state, with 1.0.0 and the frozen fixed skill |
| [`screening.json`](screening.json) | Every screened candidate with its verdict and reason |

To check the seals, run `shasum -a 256 answer_key.json assignment.json prompts/plain.txt prompts/skill-tail.txt` in this folder and compare with change 3 in the protocol and the template hashes in its registration. The pages are not published here; each case can be rebuilt from the listed page at the parent of the fix commit and at the fix or build commit.
