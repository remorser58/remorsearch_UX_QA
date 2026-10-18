# Research reader fixtures

Authored test inputs for `tests/test_ux_read.py`. Nothing here was captured from
a real site; every page is invented, and every host name uses the reserved
`.test` name, so no fixture can be mistaken for real community evidence.

The tests serve these files from a threaded `http.server` bound to 127.0.0.1.
Two in-process hooks, `net._TEST_ALLOW_LOOPBACK` and `net._TEST_RESOLVE`, map the
`.test` names to that address for the reader. No environment variable, flag or
file can set them, so a separate process (the CLI shim test) and every real run
keep the private-address guard; test names never reach real DNS or a proxy.

| Path | What it exercises |
| --- | --- |
| `pages/post-normal.html` | an ordinary community post (read) |
| `pages/post-header-login.html` | a login box in the header and a full post below (read, not auth_gate) |
| `pages/post-captcha-discussion.html` | a post that talks about captchas without a widget (read, not human_check) |
| `pages/post-header-login-short.html`, `post-header-login-medium.html` | the same header login box over posts of about 60 and 150 characters (read, not auth_gate) |
| `pages/post-form-wrapped.html` | a whole page wrapped in one form, as older sites do, with a header login box (read; the post counts as main content) |
| `pages/post-short.html` | a two-sentence post whose navigation links to a members-only board (read, not auth_gate) |
| `pages/post-comment-captcha.html` | a short post with a reCAPTCHA widget in its comment form (read, not human_check) |
| `pages/login-wall.html`, `age-gate.html`, `member-only.html` | password form plus login word on thin content; age and membership walls (auth_gate) |
| `pages/paywall-jsonld.html` | JSON-LD `isAccessibleForFree: false` (paywall, metadata only) |
| `pages/deleted-post.html` | a removed post served with status 200 (gone) |
| `pages/noai-meta.html`, `tdm-meta.html` | robots `noai` and `tdm-reservation` meta tags (opted_out) |
| `pages/captcha-recaptcha.html`, `captcha-turnstile.html`, `captcha-ko.html` | interactive human checks, including a Korean 보안문자 form (human_check, host stop) |
| `pages/js-check.html` | a self-clearing "checking your browser" interstitial (js_check: an opted_out stop for the whole site, never rendered past; served for robots.txt it makes robots.txt `unavailable_bot_filtered`) |
| `pages/js-shell-*.html`, `mobile-post.html` | JS shells with a same-site alternate, an other-site alternate, or none; the mobile twin |
| `pages/jsonld-shell.html` | a JS shell whose JSON-LD review body is longer than the visible text |
| `pages/blocked-403.html` | a plain block page (bot_filter: an opted_out stop for the whole site, never escalated) |
| `pages/euckr-page.utf8.html` | stored as UTF-8; the tests serve it as CP949 under EUC-KR, ks_c_5601-1987 and x-windows-949 labels |
| `pages/injection-post.html` | injection phrases (en and ko) and a forged envelope END line |
| `pages/feed.xml` | an RSS feed for the R0 route-table test |
| `pages/pii-post.html` | a post and metadata carrying invented phone, e-mail, account, card, resident-registration and partial-IP identifiers (scrubbed before `read` or `ingest` prints or saves anything) |
| `captures/` | render captures for `ingest`: HTML, text, a ux-page-read.v1 document, and a signed-in view that must be refused |
| `robots/*.txt` | RFC 9309 precedence, product-token groups, wildcards, percent-encoding, Crawl-delay |
| `robots/ai-agent-group.txt` | groups naming other AI agents with fixture tokens: a fetch-for-a-user agent (honoured as our own, disallows only) and a training crawler (a recorded signal) |
| `agent-tokens.test.json` | the fixture tokens, handed to `start --agent-tokens` |
| `promotion-ko.json` | labelled synthetic cases for the Korean promotion, incentive and virtual-person markers: disclosures by position, and negated disclaimers, questions, quotes and complaints that must not be flagged |
| `routes.test.json` | a route table with `.test` hosts only, including terms_restricted entries (reported, confirmed, one whose lift needs written permission, and a parent and a child entry that each need their own check; a run table's own entries never name an official route, so the official-only tests add their routes to a copy of the packaged table), search pages and a switched-off discovery endpoint. The official-only route reads REMORSEARCH_FIXTURE_TUBE_KEY or its alias REMORSEARCH_FIXTURE_TUBE_OLD_KEY; the listed alias FIXTURE_TUBE_KEY is never read (keys come only from REMORSEARCH_* variables) |
| `brief.json` | a ux-research-brief.v1 example |

`tests/test_ux_youtube.py` needs no files here: its fake Data API (videos and commentThreads answers, error bodies and robots.txt) is built in memory and served on 127.0.0.1, and its route tables are the packaged one or a copy of it with fixture hosts.

The 10 MB page and the gzip bomb are generated inside the tests instead of being
stored here.
