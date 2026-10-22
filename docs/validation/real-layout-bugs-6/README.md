# Real layout bugs, round 6

Eight layout bugs from six projects no earlier round used, with the skill frozen at commit e72a71c before any run ([`PROTOCOL.md`](PROTOCOL.md)). After round 5 the scan gained sheets of every screen, `ergo_qa.py measure` for named elements, LY-14 (text over an image it does not belong to), LY-15 (grid rows that touch) and a fix for the end of wide phone pages, and the fast path was rewritten around them. Those changes were built while looking at rounds 1 to 5, so this round is their held-out check. Only GPT-6.1 Sol ran, at effort `high`, three runs per arm.

## Result

| Case | What is broken | Found, with skill | Found, without |
| --- | --- | ---: | ---: |
| one-page-wonder ec94d15b | On a phone each section keeps two half-width columns, so its text box is 69 px wide and breaks one or two words per line | 2 of 2 runs | 2 of 2 |
| coming-soon f2f16308 | The social icons drop below the full-height hero to the left edge of an empty second screen | 2 of 2 | 2 of 2 |
| 98.css 68d7366d | On a phone two code blocks make the page 407 px wide | 2 of 2 | 2 of 2 |
| 98.css ecfc9758 | On a phone the documentation keeps its desktop layout, 1068 px wide | 2 of 2 | 2 of 2 |
| holiday.css 1eba36ad | The table-of-contents links are 18 px tall and 18 px apart, under the 24 px target size | 0 of 2 | 0 of 2 |
| holiday.css e27aca20 | Headings and text start at the left edge of the screen (no side margin) | 0 of 2 | 0 of 2 |
| spcss 93b12537 | On a phone headings and text start at the left edge of the screen | 0 of 2 | 0 of 2 |
| wtf-forms 5dcd2aa1 | Without a viewport tag a phone lays the page out 980 px wide and shrinks it to a third | 0 of 2 | 0 of 2 |

| Model | Known found, with skill | Without | Alarms and unsupported, with | Without | Median minutes, with | Without |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| GPT-6.1 Sol | 8 of 16 | 8 of 16 | 0 | 0 | 7.15 | 6.23 |

By the registered rule the result is no demonstrated improvement: each run found the same number with and without the skill (3 and 3, 3 and 3, 2 and 2). The skill arm took 1.15 times as long, down from 1.30 in round 5, so the secondary target, a skill arm faster than the plain arm, was missed again. Times run from each session's start to its written findings file.

Both arms found the four bugs that are large and visible and missed the other four. Those four are kinds the review prompt does not list: it asks for content that is cut off, covered, overlapping or off the screen, components in the wrong rows, misalignment with siblings or the container, size mismatches and off-centre icons. Text flush against the screen edge, a page shrunk to fit a phone and links too close to tap are none of these, and no run reported them. Item 3 of the registered inclusion rule names the same kinds as the prompt, so these four should not have been accepted; the screening error is a limit of this round.

The skill runs started the scan about 30 s into the session, and it finished about 70 s later; each run then spent five to five and a half minutes on review. One run spent about a minute and a half checking how the scan emulates a phone after seeing the shrunk wtf-forms page, and wrote one script of its own to capture the end of a long laptop page that the scan had reported as not captured. The plain runs wrote four to six scripts and finished in about six minutes.

The scan alone matched 2 of the 8 bugs ([`scan-alone.json`](scan-alone.json)), the two 98.css pages wider than the phone (LY-08); the version frozen for round 5 produced the same layout rows. It had no row for text against the screen edge, for the shrunk page or for the icons, and LY-10 missed the squeezed columns because their 69 px text boxes sit inside 165 px columns, above its four-em rule. PT-01 (WCAG 2.5.8 target size) listed the 18 px links, as it did on both e27aca20 pages, which predate that fix; agents treat target size as outside a layout review. On an otherwise idle machine the scan recorded the 16 states in 94 s against 122 s for the round 5 version. Three states that fit one screen still took 42 screens each, about 25 to 36 s, because the scan kept scrolling a page that could not scroll, and the two 1eba36ad laptop pages took 42 screens and left a slice of 150 to 170 px near their end uncaptured.

Judging followed rounds 3 to 5. One finding was a valid extra: on holiday.css the label of the disabled checkbox wraps its last word onto the next row beside the colour inputs, in both states. The e27aca20 pages also carry the table-of-contents links that 1eba36ad later spaced out; a report of them would have been a valid extra, and none was made.

Each run's findings and summary are in [`findings/`](findings/), the verdicts in [`adjudication.json`](adjudication.json), the scores in [`scores.json`](scores.json) and the times in [`timing.json`](timing.json).

## After the round

Commit 1de6620 adds LY-16 (three or more texts within 1.5 px of the screen edge), LY-17 (a phone page laid out 30 % wider than the screen without a device-width viewport) and a words-per-line rule to LY-10, and fixes the scan's scrolling: a step that the wheel spends on a frame or an inner box moves the page the rest of the way, and the scan stops once a step moves nothing. These were built from this round's pages, so the numbers below are development numbers ([`after-round-6.json`](after-round-6.json)).

On the 16 states the scan now names 6 of the 8 bugs (LY-10 the squeezed columns, LY-16 both pages without a side margin, LY-17 the shrunk page) with no new row on a fixed page, and records them in 58 s instead of 94 s; one-screen pages take 2 screens instead of 42. On the 76 states of rounds 1 to 5 it took 385 s against 484 s, and its layout rows are those of e72a71c except for a few covered-text rows on two AdminLTE pages that come and go between runs in both states.

The six sessions ran again on the same pages with the same prompts and this skill, scored by the round's conventions but not blind. Both arms found 8 of 16 again, with no alarm or unsupported finding; every skill run also reported the wrapped checkbox label. The skill arm's median time was lower for the first time, 6.45 against 6.94 minutes (6.45, 8.64 and 5.87 against 6.94, 6.43 and 7.60), and its scan took about 45 s. The skill runs saw the new rows and left them out, saying flush-left text matches its container and a page scaled to fit is not one of the requested defect kinds.

## Limits

Eight cases from six projects out of 529 screened candidates in 60 sources, four short of the registered twelve. The two holiday.css cases are one page at two commits, and so are the two 98.css cases. Four cases are kinds the review prompt does not list, so the agents' results on them measure the prompt as much as the skill. Only Sol ran, three runs per arm; a difference of one find per run says little on its own. The rerun after the round is on the pages its changes were built from and was scored without blinding.
