# Real layout bugs, round 4

Eight layout bugs from projects no earlier round used, with the skill frozen at commit 51240ed before any run ([`PROTOCOL.md`](PROTOCOL.md)). After round 3 the scan gained LY-09 (a control against its label, a field against a separate button, the items of a header bar), LY-10 (a content column squeezed on a phone) and an LY-08 that names the widening element anywhere on the page. Those were built while looking at the round 1 to 3 pages, so this round is their held-out check.

## Result

| Case | What is broken | Found, with skill | Found, without |
| --- | --- | ---: | ---: |
| simple.css c6af6463 | On a phone the aside floats beside the text as a 77 px column and breaks its words letter by letter | 3 of 4 runs | 3 of 4 runs |
| simple.css 36144b34 | The header links have no space between them, so their labels run together | 2 of 4 | 3 of 4 |
| mvp 66ec5a39 | The sign-up textarea is 31 px narrower than the fields above it | 0 of 4 | 0 of 4 |
| mvp 11722ccc | On a phone the textarea runs 42 px past its card and off the screen | 4 of 4 | 2 of 4 |
| picnic 8ae635b1 | On a phone the page is 610 px wide and the menu button sits off the screen | 4 of 4 | 4 of 4 |
| picnic 8bb0d652 | On a phone the top bar's links wrap onto a second row and hang 20 px below the fixed bar | 4 of 4 | 3 of 4 |
| picnic ec6a3d0d | On a phone the table of contents stays as a 65 px column, its title runs into the page title and the page is 413 px wide | 4 of 4 | 4 of 4 |
| mini.css 0ed75ca8 | A card is 2280 px wide and the page scrolls sideways | 4 of 4 | 4 of 4 |

| Model | Known found, with skill | Without | Alarms and unsupported, with | Without | Median minutes, with | Without |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| GPT-6.1 Sol | 13 of 16 | 14 of 16 | 0 | 0 | 17.0 | 10.4 |
| DeepSeek 4.1 Flash | 12 of 16 | 9 of 16 | 4 | 5 | 34.6 | 34.4 |

By the registered rule the result is no demonstrated improvement for either model. Flash found more with the skill in runs 1 and 3 (5 against 3, 4 against 3) and the same in run 2 (3 and 3); the rule asks for more in all three runs. Its extra finds were the textarea past its card, found in both skill runs that showed it and in neither plain run, and the menu links below the fixed bar once. Sol found 14 of 16 without the skill, missed the touching header links once with it, and took 1.64 times as long, above the registered 1.5.

The gain for Flash cannot be traced to the scan. In two of the three Flash runs with the skill, the scan of all eight pages did not finish: it left results for one page in one run and three in the other. Six agent sessions shared the machine, and under that load the scan took about 3.7 times as long as on an idle machine.

The scan alone matched 5 of the 8 bugs ([`scan-alone.json`](scan-alone.json)): the squeezed aside (LY-10), the textarea past its card (LY-08 lists it among the elements outside the screen only on the broken page), the 610 px page, the table of contents running into the page title (LY-03) and the 2280 px card. The version frozen for round 3 matched 3, the last three of these. No LY-06, LY-07 or LY-09 row appeared on any of the 16 states, and LY-10 fired only on the three states that have the squeezed aside. On an idle machine the scan recorded a page in a median 45 s (worst 57 s) and produced the same layout rows.

No run and no scan found the textarea 31 px narrower than the fields above it. No check compares the widths of sibling form controls, and none measures the gap between adjacent links or menu items hanging below a fixed bar.

Judging followed round 3. Tables and code blocks that scroll inside their own box were judged unsupported, and a table running past the page was valid. Every run credited with the table-of-contents case also reported the title overlap, so crediting reports that name only the 413 px page width changes no count. The one alarm was a report of the 610 px width on the fixed state of picnic 8ae635b1, which is 360 px wide.

Each run's findings and summary are in [`findings/`](findings/), the verdicts in [`adjudication.json`](adjudication.json), the scores in [`scores.json`](scores.json) and the times in [`timing.json`](timing.json).

## Limits

Eight cases from four projects, three of them from picnic, out of 226 screened candidates: four short of the registered twelve. Two pairs of cases share a page. The first launch of the Flash sessions was lost to an interruption and restarted without reading its output (change 4 in the protocol). Three runs per arm and model is a small sample, so a difference of one or two finds per run says little on its own.
