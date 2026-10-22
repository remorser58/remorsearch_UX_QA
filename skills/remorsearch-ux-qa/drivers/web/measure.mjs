#!/usr/bin/env node
// Measure named elements on one page as the layout scan renders it: the same device
// emulation and network policy, read-only. A reviewer checks a suspect from the scan's
// screenshots with one command instead of a one-off browser script.
//
//   node drivers/web/measure.mjs --url URL --selector CSS [--selector CSS ...] --out DIR
//        [--device galaxy-s24] [--allow-origin ORIGIN ...] [--max 12] [--at N]
//
// DIR/measure.json lists, per selector, the matched elements (box in page CSS px, text
// lines, the styles that decide layout, parent box) and, for each pair of neighbouring
// matches in page order, gaps, edge and centre offsets, size differences, the offset of
// their first text lines and any overlap. DIR/measure.png is the screen around the first
// overlap (or match N with --at, or the first shown match) with every match outlined and
// numbered. The same is printed as a short table.
// Exit 0; 2 for usage; 4 when Chromium or the page cannot be used.
import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

import { openBrowser } from './browser_transport.mjs';
import { CATALOG, resolveDevice } from './devices.mjs';
import { loadPlaywright } from './playwright_loader.mjs';
import { DriverFailure, EXIT, UsageError, allowedUrl, writeJsonAtomic } from './util.mjs';

const USAGE = 'usage: measure.mjs --url URL --selector CSS [--selector CSS ...] --out DIR [--device ID] [--allow-origin ORIGIN ...] [--max N] [--at N]';

function parseArgs(argv) {
  const a = { selectors: [], origins: [], device: 'galaxy-s24', max: 12 };
  const keys = { '--url': 'url', '--out': 'out', '--device': 'device', '--max': 'max', '--at': 'at' };
  for (let i = 0; i < argv.length; i += 2) {
    const [k, v] = [argv[i], argv[i + 1]];
    if (v === undefined) throw new UsageError(`${k} needs a value\n${USAGE}`);
    if (k === '--selector') a.selectors.push(v);
    else if (k === '--allow-origin') a.origins.push(v);
    else if (keys[k]) a[keys[k]] = v;
    else throw new UsageError(`unknown argument ${k}\n${USAGE}`);
  }
  if (!a.url || !a.out || !a.selectors.length) throw new UsageError(USAGE);
  if (!/^(https?|file):/i.test(a.url)) {
    if (!fs.existsSync(a.url)) throw new UsageError(`not a URL or an existing file: ${a.url}`);
    a.url = pathToFileURL(path.resolve(a.url)).href;
  }
  if (!CATALOG.has(a.device)) throw new UsageError(`unknown device ${a.device}; known: ${[...CATALOG.keys()].join(', ')}`);
  a.max = Number(a.max);
  if (!Number.isInteger(a.max) || a.max < 1 || a.max > 50) throw new UsageError('--max takes 1 to 50');
  if (a.at !== undefined) {
    a.at = Number(a.at);
    if (!Number.isInteger(a.at) || a.at < 1) throw new UsageError('--at takes the number of a match');
  }
  return a;
}

// Runs in the page (serialized by Playwright): self-contained, reads only.
export function measureElements({ selectors, max }) {
  const r1 = (n) => Math.round(n * 10) / 10;
  const sx = window.scrollX;
  const sy = window.scrollY;
  const step = (el) => {
    if (el.id) return '#' + CSS.escape(el.id);
    const same = el.parentElement ? [...el.parentElement.children].filter((c) => c.localName === el.localName) : [];
    return same.length > 1 ? `${el.localName}:nth-of-type(${same.indexOf(el) + 1})` : el.localName;
  };
  const pathOf = (el) => {
    const parts = [];
    for (let n = el; n && n.nodeType === 1 && n.localName !== 'html' && parts.length < 4; n = n.parentElement) {
      parts.unshift(step(n));
      if (n.id) break;
    }
    return parts.join(' > ');
  };
  const boxOf = (el) => {
    const b = el.getBoundingClientRect();
    return { x: r1(b.left + sx), y: r1(b.top + sy), w: r1(b.width), h: r1(b.height) };
  };
  // Text line boxes: the client rects of the element's text, merged per line.
  const lineBoxes = (el) => {
    const rects = [];
    const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    for (let t = walker.nextNode(); t && rects.length < 600; t = walker.nextNode()) {
      if (!t.textContent.trim()) continue;
      const range = document.createRange();
      range.selectNodeContents(t);
      for (const b of range.getClientRects()) if (b.width > 0.5 && b.height > 0.5) rects.push(b);
    }
    rects.sort((a, b) => a.top - b.top || a.left - b.left);
    const rows = [];
    for (const b of rects) {
      const mid = (b.top + b.bottom) / 2;
      const row = rows.find((r) => mid > r.top && mid < r.bottom);
      if (row) Object.assign(row, { left: Math.min(row.left, b.left), right: Math.max(row.right, b.right), top: Math.min(row.top, b.top), bottom: Math.max(row.bottom, b.bottom) });
      else rows.push({ left: b.left, right: b.right, top: b.top, bottom: b.bottom });
    }
    return rows.map((r) => ({ x: r1(r.left + sx), y: r1(r.top + sy), w: r1(r.right - r.left), h: r1(r.bottom - r.top) }));
  };
  const STYLES = ['display', 'position', 'float', 'clear', 'box-sizing', 'width', 'height', 'margin', 'padding', 'border-width',
    'font-family', 'font-size', 'font-weight', 'line-height', 'text-align', 'vertical-align', 'white-space', 'overflow-x', 'overflow-y',
    'z-index', 'gap', 'flex-wrap', 'align-items', 'justify-content', 'grid-template-columns', 'transform'];
  const matches = [];
  const all = [];
  for (const selector of selectors) {
    let nodes;
    try {
      nodes = [...document.querySelectorAll(selector)];
    } catch {
      matches.push({ selector, error: 'invalid selector' });
      continue;
    }
    const items = [];
    for (const el of nodes.slice(0, max)) {
      const cs = getComputedStyle(el);
      const style = {};
      for (const p of STYLES) style[p] = p === 'font-family' ? cs.getPropertyValue(p).split(',')[0].trim() : cs.getPropertyValue(p);
      const lines = lineBoxes(el);
      const label = el.innerText || el.value || el.getAttribute('alt') || el.getAttribute('aria-label') || '';
      const item = {
        n: 0, path: pathOf(el), tag: el.localName, text: String(label).slice(0, 400).replace(/\s+/g, ' ').trim().slice(0, 80),
        box: boxOf(el), shown: el.getClientRects().length > 0 && cs.visibility === 'visible' && cs.display !== 'none' && Number(cs.opacity) > 0,
        lines: { count: lines.length, first: lines[0] || null, last: lines.length > 1 ? lines[lines.length - 1] : null },
        style, parent: el.parentElement ? { path: pathOf(el.parentElement), box: boxOf(el.parentElement) } : null,
      };
      items.push(item);
      all.push({ el, item });
    }
    matches.push({ selector, count: nodes.length, items });
  }
  // One number per element in page order; an element two selectors match keeps one number.
  const unique = [];
  for (const x of all) if (!unique.some((u) => u.el === x.el)) unique.push(x);
  unique.sort((a, b) => (a.el.compareDocumentPosition(b.el) & Node.DOCUMENT_POSITION_FOLLOWING ? -1 : 1));
  unique.forEach((u, i) => { u.n = i + 1; });
  for (const x of all) x.item.n = unique.find((u) => u.el === x.el).n;
  const pairs = [];
  for (let i = 1; i < unique.length; i++) {
    const [a, b] = [unique[i - 1], unique[i]];
    const [A, B] = [a.item.box, b.item.box];
    const ox = Math.min(A.x + A.w, B.x + B.w) - Math.max(A.x, B.x);
    const oy = Math.min(A.y + A.h, B.y + B.h) - Math.max(A.y, B.y);
    const [fa, fb] = [a.item.lines.first, b.item.lines.first];
    pairs.push({
      a: a.n, b: b.n, nested: a.el.contains(b.el) || b.el.contains(a.el),
      gap_x: r1(B.x - (A.x + A.w)), gap_y: r1(B.y - (A.y + A.h)),
      left: r1(B.x - A.x), right: r1(B.x + B.w - (A.x + A.w)), top: r1(B.y - A.y), bottom: r1(B.y + B.h - (A.y + A.h)),
      centre_x: r1(B.x + B.w / 2 - (A.x + A.w / 2)), centre_y: r1(B.y + B.h / 2 - (A.y + A.h / 2)),
      width: r1(B.w - A.w), height: r1(B.h - A.h),
      first_line_bottom: fa && fb ? r1(fb.y + fb.h - (fa.y + fa.h)) : null,
      overlap: ox > 0.5 && oy > 0.5 ? { w: r1(ox), h: r1(oy) } : null,
    });
  }
  const doc = document.documentElement;
  const body = document.body;
  return {
    viewport: { w: innerWidth, h: innerHeight },
    page: { w: Math.max(doc.scrollWidth, body ? body.scrollWidth : 0), h: Math.max(doc.scrollHeight, body ? body.scrollHeight : 0) },
    matches, pairs,
  };
}

// Runs in the page: numbered outlines in page coordinates, drawn for the screenshot only.
function outlineBoxes({ boxes }) {
  const host = document.createElement('div');
  host.style.cssText = 'position:absolute;left:0;top:0;width:0;height:0;z-index:2147483647;pointer-events:none';
  for (const { n, x, y, w, h } of boxes) {
    const frame = document.createElement('div');
    frame.style.cssText = `position:absolute;left:${x}px;top:${y}px;width:${Math.max(1, w)}px;height:${Math.max(1, h)}px;outline:2px solid rgb(230,30,30)`;
    const tag = document.createElement('div');
    tag.textContent = String(n);
    tag.style.cssText = `position:absolute;left:${x}px;top:${Math.max(0, y - 16)}px;font:bold 12px/16px sans-serif;color:#fff;background:rgb(230,30,30);padding:0 4px`;
    host.append(frame, tag);
  }
  document.documentElement.append(host);
}

const signed = (v) => (v > 0 ? '+' : '') + v;

function render(doc, shot) {
  const out = [`measure: ${doc.url} on ${doc.device} (${doc.viewport.w}x${doc.viewport.h}), page ${doc.page.w}x${doc.page.h} CSS px`];
  if (doc.blocked_requests) out.push(`  blocked ${doc.blocked_requests} requests; a missing font or style changes the layout`);
  for (const m of doc.matches) {
    if (m.error) {
      out.push(`${m.selector}: ${m.error}`);
      continue;
    }
    out.push(`${m.selector}: ${m.count} match${m.count === 1 ? '' : 'es'}${m.count > m.items.length ? ` (first ${m.items.length})` : ''}`);
    for (const it of m.items) {
      const s = it.style;
      const f = it.lines.first;
      out.push(`  ${it.n} ${it.path}${it.text ? ` "${it.text.slice(0, 40)}"` : ''}${it.shown ? '' : ' (hidden)'}`
        + ` box ${it.box.x},${it.box.y} ${it.box.w}x${it.box.h}`
        + (it.lines.count ? ` lines ${it.lines.count} (first ${f.x},${f.y} ${f.w}x${f.h})` : '')
        + ` font ${s['font-size']}/${s['line-height']} ${s['font-weight']} ${s['text-align']}`
        + ` ${s.display}${s.position !== 'static' ? ` ${s.position}` : ''}${s.float !== 'none' ? ` float ${s.float}` : ''}`
        + ` margin ${s.margin} padding ${s.padding}`);
    }
  }
  if (doc.pairs.length) out.push('neighbours in page order (second minus first, CSS px):');
  for (const p of doc.pairs) {
    const parts = [`gap x ${p.gap_x} y ${p.gap_y}`, `left ${signed(p.left)} right ${signed(p.right)} top ${signed(p.top)} bottom ${signed(p.bottom)}`,
      `centre x ${signed(p.centre_x)} y ${signed(p.centre_y)}`, `size ${signed(p.width)} x ${signed(p.height)}`];
    if (p.first_line_bottom !== null) parts.push(`first line ${signed(p.first_line_bottom)}`);
    if (p.overlap) parts.push(`OVERLAP ${p.overlap.w}x${p.overlap.h}`);
    out.push(`  ${p.a}-${p.b}${p.nested ? ' (nested)' : ''}: ${parts.join('; ')}`);
  }
  out.push(`screenshot: ${shot} (scrolled to ${doc.screenshot.scroll.x},${doc.screenshot.scroll.y})`);
  return out.join('\n') + '\n';
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const pageUrl = new URL(args.url);
  const origins = new Set(['http:', 'https:'].includes(pageUrl.protocol) ? [pageUrl.origin] : []);
  for (const o of args.origins) {
    try {
      origins.add(new URL(o).origin);
    } catch {
      throw new UsageError(`--allow-origin is not a URL: ${o}`);
    }
  }
  const { pw, info } = loadPlaywright();
  const transport = await openBrowser(pw, info, { timeout: 60000 });
  let context = null;
  try {
    const dev = resolveDevice({ id: args.device, pwDevices: pw.devices, chromeMajor: parseInt(transport.browserVersion, 10) });
    context = await transport.browser.newContext({ ...dev.contextOptions, colorScheme: 'light', reducedMotion: 'no-preference', serviceWorkers: 'block', acceptDownloads: false });
    let blocked = 0;
    await context.route('**/*', (route) => {
      const req = route.request();
      if (allowedUrl(pageUrl, origins, req.url(), req.resourceType())) return route.continue().catch(() => {});
      blocked++;
      return route.abort('blockedbyclient').catch(() => {});
    });
    await context.routeWebSocket(/.*/, (ws) => ws.close({ code: 1008, reason: 'blocked by ergoqa network policy' }).catch(() => {}));
    const page = await context.newPage();
    let response;
    try {
      response = await page.goto(args.url, { waitUntil: 'load', timeout: 30000 });
    } catch (err) {
      throw new DriverFailure(`cannot load ${args.url}: ${String(err.message).split('\n')[0]}`);
    }
    if (response && response.status() >= 400) throw new DriverFailure(`${args.url} returned HTTP ${response.status()}`);
    await page.evaluate(() => Promise.race([document.fonts.ready, new Promise((r) => setTimeout(r, 3000))])).catch(() => {});
    await page.waitForTimeout(300);
    const result = await page.evaluate(measureElements, { selectors: args.selectors, max: args.max });
    const items = result.matches.flatMap((m) => m.items || []);
    const byN = new Map(items.map((it) => [it.n, it]));
    const overlap = result.pairs.find((p) => p.overlap && !p.nested);
    const focus = args.at !== undefined ? byN.get(args.at)
      : overlap ? byN.get(overlap.b) : items.filter((it) => it.shown).sort((a, b) => a.n - b.n)[0];
    if (args.at !== undefined && !focus) throw new UsageError(`--at ${args.at}: no match with that number`);
    if (focus) {
      const top = overlap && args.at === undefined ? Math.min(byN.get(overlap.a).box.y + byN.get(overlap.a).box.h, focus.box.y) - result.viewport.h / 2 : focus.box.y - 80;
      await page.evaluate(({ x, y, vw }) => window.scrollTo(x + 40 > vw ? Math.max(0, x - 20) : 0, Math.max(0, y - 80)),
        { x: focus.box.x, y: top + 80, vw: result.viewport.w });
      await page.waitForTimeout(250);
    }
    const boxes = new Map();
    for (const it of items) boxes.set(it.n, { n: it.n, ...it.box });
    await page.evaluate(outlineBoxes, { boxes: [...boxes.values()] });
    fs.mkdirSync(args.out, { recursive: true });
    const shot = path.join(args.out, 'measure.png');
    await page.screenshot({ path: shot, scale: 'css', animations: 'disabled' });
    const scroll = await page.evaluate(() => ({ x: Math.round(scrollX), y: Math.round(scrollY) }));
    const doc = {
      schema_version: 'ergo-measure.v1', url: args.url, device: args.device, viewport: result.viewport, page: result.page,
      blocked_requests: blocked, screenshot: { path: 'measure.png', scroll }, matches: result.matches, pairs: result.pairs,
    };
    writeJsonAtomic(path.join(args.out, 'measure.json'), doc);
    process.stdout.write(render(doc, shot));
  } finally {
    await transport.close([context]);
  }
}

main().then(() => process.exit(EXIT.OK), (err) => {
  if (err instanceof UsageError) {
    process.stderr.write(`measure: ${err.message}\n`);
    process.exit(EXIT.USAGE);
  }
  process.stderr.write(`measure: ${err instanceof DriverFailure ? '' : 'unexpected error: '}${err && err.message ? String(err.message).split('\n')[0] : err}\n`);
  process.exit(EXIT.DRIVER);
});
