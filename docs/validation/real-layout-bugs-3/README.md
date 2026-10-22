# Real layout bugs, round 3

Four layout bugs from projects rounds 1 and 2 did not use, with the skill frozen before any run ([`PROTOCOL.md`](PROTOCOL.md)). The same frozen skill was also rerun on the round 1 and 2 pages; that rerun is a development check, reported in its own section below.

## Result

The skill did not help on the held-out cases. Every run of both arms found the dashboard whose sidebar squeezes the content on a phone, and no run found the other three:

| Case | What is broken | Found, with skill | Found, without |
| --- | --- | ---: | ---: |
| light-bootstrap-dashboard a5032470 | On a phone the 260 px sidebar stays open and leaves the content a 100 px column | 4 of 4 runs | 4 of 4 runs |
| Bootswatch Lux 0cbc74c6 | The navbar search field is 45 px tall beside a 42.4 px button, 8 px apart | 0 of 4 | 0 of 4 |
| Bootswatch Materia f02c7f9f | Switch toggles sit 4.6 px above the centre of their labels | 0 of 4 | 0 of 4 |
| startbootstrap-grayscale 4eaba19f | On a phone the menu toggle sits 3 px below the brand beside it | 0 of 4 | 0 of 4 |

| Model | Known found, with skill | Without | Alarms and unsupported, with | Without | Median minutes, with | Without |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| GPT-6.1 Sol | 2 of 8 | 2 of 8 | 5 | 1 | 15.2 | 11.2 |
| DeepSeek 4.1 Flash | 2 of 8 | 2 of 8 | 3 | 2 | 35.1 | 35.1 |

By the registered rule the result is no demonstrated improvement for either model. The skill arms reported more unsupported findings, mostly a documentation button that appears only on hover and a chart drawn past its frame. Flash used the whole budget in both arms. Sol took 1.36 times as long with the skill, down from about twice as long on the round 1 pages before one scan command could take every page.

The scan alone matched none of the four ([`scan-alone.json`](scan-alone.json)). Its measurements cover an icon off the centre of its own control, a field and a button joined to it, and a page wider than the screen. The three misses are offsets between elements of different kinds that sit side by side: a field and a separate button, a switch and its label, a toggle and the brand in one bar. The squeezed dashboard scrolls inside its own panel, and no check measured how narrow the panel had become.

Each run's findings and summary are in [`findings/`](findings/), the blind verdicts in [`adjudication.json`](adjudication.json) and the scores in [`scores.json`](scores.json).

## Development check on the round 1 and 2 pages

The new measurements were written after looking at what rounds 1 and 2 missed, so these numbers show the fixes working on the pages they were built from. The skill arm was rerun with commit 1fc4581 on the same pages, prompts and models, and compared with the plain arms recorded in those rounds:

| Pages | Model | Known found, plain arm of the round | 1.0.0 or 1.0.1 skill | Development skill |
| --- | --- | ---: | ---: | ---: |
| Round 1 (12 cases, 34 known) | GPT-6.1 Sol | 18 | 13 | 25 |
| Round 1 | DeepSeek 4.1 Flash | 14 | 15 | 18 |
| Round 2 (4 cases, 8 known) | GPT-6.1 Sol | 6 | 6 | 7 |
| Round 2 | DeepSeek 4.1 Flash | 6 | 6 | 8 |

Sol found more than its plain arm in all three paired runs on the round 1 pages, with no alarm or unsupported finding, but its median time was 20.5 minutes against 10.0. Defects no earlier run had found were now reported: zoom glyphs 2.2 px below centre, a collapsed-sidebar logo 4 px off centre, a search field whose bottom edge is 3.6 px above its button's, a layout that scrolls 48 px too far, and a carousel arrow 10 px below centre, which both models found in every run that showed it. Scores, verdicts and findings are in [`development/`](development/).

The scan alone now matches 12 of the 16 round 1 and 2 defects, against 5 for version 1.0.1, and records a page in a median 37 s instead of 117 s (worst page 46 s instead of 535 s), because it records both devices at once and decodes each screenshot once ([`development/scan-alone.json`](development/scan-alone.json)).

## Limits

Four held-out cases, two of them from one project, and 74 screened candidates. The cases cover few defect kinds, so the result says little about how often the scan's measured kinds occur in real projects.
