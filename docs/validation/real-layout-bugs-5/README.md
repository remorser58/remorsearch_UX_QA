# Real layout bugs, round 5

Ten layout bugs from six projects no earlier round used, with the skill frozen at commit ac1a187 before any run ([`PROTOCOL.md`](PROTOCOL.md)). After round 4 the scan gained LY-11 (stacked fields of different widths), LY-12 (labels of adjacent links or buttons that touch) and LY-13 (an item of a header bar hanging past its edge), and it records a page in about a third of the time. Those changes were built while looking at the round 4 pages, so this round is their held-out check.

## Result

| Case | What is broken | Found, with skill | Found, without |
| --- | --- | ---: | ---: |
| tufte-css c6e436bb | On the laptop every side note and margin note sits 6 to 7 px above the baseline of the line it belongs to | 0 of 4 runs | 0 of 4 runs |
| tufte-css 6c2f3e8e | On the laptop a figure's margin caption runs 49 px down over the title of the full-width figure below it | 2 of 4 | 3 of 4 |
| tufte-css 69255155 | On a phone a code sample makes the page 455 px wide | 4 of 4 | 4 of 4 |
| lit 481f5cc3 | On a phone the form's text field and textarea run 17 px past the screen | 4 of 4 | 4 of 4 |
| lit fce9ac96 | On a 360 px phone the Components button covers the bottom 18 px of the Utilities button | 4 of 4 | 4 of 4 |
| lit ce470806 | On the laptop the six rows of the grid demo touch, so the grey cells run together | 0 of 4 | 0 of 4 |
| writ e0b84596 | On a phone an image makes the page 586 px wide | 4 of 4 | 4 of 4 |
| almond.css 44f880c2 | Radio buttons and checkboxes sit 6 px below the middle of their labels | 3 of 4 | 1 of 4 |
| flexboxgrid 7b71b69e | On a phone the hero description under the centred title is left-aligned | 0 of 4 | 0 of 4 |
| bahunya 0aa2c063 | The brand link in the top bar sits 4 px higher than the links beside it | 2 of 4 | 1 of 4 |

| Model | Known found, with skill | Without | Alarms and unsupported, with | Without | Median minutes, with | Without |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| GPT-6.1 Sol | 13 of 20 | 12 of 20 | 0 | 1 | 16.95 | 13.03 |
| DeepSeek 4.1 Flash | 10 of 20 | 9 of 20 | 5 | 7 | 34.2 | 34.2 |

By the registered rule the result is no demonstrated improvement for either model. Sol found more with the skill in run 1 (4 against 3) and the same in runs 2 and 3 (5 and 5, 4 and 4), and took 1.30 times as long (1.64 in round 4). Flash found more in run 1 (5 against 3), fewer in run 2 (3 against 4) and the same in run 3 (2 and 2). The secondary target, a skill arm faster than the plain arm, was missed for Sol. Both Flash arms ran into the 30-minute budget, so their times are equal by construction.

The skill's extra finds were the two small offsets the scan measures: the checkboxes and radios below their labels (3 of 4 runs with the skill, 1 without) and the brand link above the other links (2 against 1). One Sol run with the skill saw the scan's row for the brand link and dismissed it because the brand and the links have different roles.

Every skill run had the scan of all ten pages before it wrote its report; the scan took 107 to 218 s with six agent sessions sharing the machine. In round 4 two of the three Flash skill runs wrote their report before the scan finished. The time Sol added with the skill went into its own process around the scan. In all three runs it spent about a minute reading the skill and the scan's options before starting the scan, wrote its own script to combine the scan's screenshots into sheets, and wrote four to seven scripts of its own in total, most of them to measure elements it had seen in the screenshots. Two runs checked the finished report against the pages again, and one wrote the receipt and coverage files the skill's evidence rules ask for. Without the skill Sol wrote its capture and sheet scripts in about two and a half minutes and six to eight scripts in total. Both arms viewed a similar number of screenshots.

The scan alone matched 6 of the 10 bugs ([`scan-alone.json`](scan-alone.json)): the 586 px and 455 px pages (LY-08), the fields past the screen (LY-08 names them), the covered Utilities button (LY-02), the checkboxes and radios (LY-09) and the brand link (LY-09 and LY-04). The version frozen for round 4 produced the same layout rows. Neither found the side-note baseline, the caption over the figure, the touching grid rows or the hero copy alignment. None of the ten bugs is a field width, a link gap or a hanging bar item, so LY-11 to LY-13 had nothing to find here; they produced no row on any of the 20 states. On an otherwise idle machine the frozen scan recorded the 20 states in 82 s with 189 CPU-seconds, a median 11 s per page, against 222 s, 310 CPU-seconds and 29 s for the round 4 version. With six agents running it took 145 s against 232 s.

Judging followed rounds 3 and 4. Tables, code blocks, lists and selects that scroll inside their own box were judged unsupported, which covers bahunya's navigation list on a phone and a report of the tufte-css table caption cut by its scrolling table. Valid extras, present in both states: flexboxgrid's menu label 'listview' spills out of its box because the saved page lacks its icon font, bahunya's checkboxes sit 14 px above their labels, the tufte-css table columns collide on a phone, the lit alert's close button drops to its own row and 'Full Page Landing' splits across two lines, and the tufte-css code blocks still make the page 2 px wider after the fix.

Each run's findings and summary are in [`findings/`](findings/), the verdicts in [`adjudication.json`](adjudication.json), the scores in [`scores.json`](scores.json) and the times in [`timing.json`](timing.json).

## Limits

Ten cases from six projects, three each from tufte-css and lit, out of 238 screened candidates: two short of the registered twelve. The three tufte-css cases are one page at three commits. The Flash times measure the budget. Three runs per arm is a small sample, so a difference of one find per run says little on its own.
