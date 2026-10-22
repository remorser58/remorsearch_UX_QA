// Functions that run inside the page under test. They are serialized by
// Playwright (addInitScript / evaluate), so each must be self-contained: no
// closures over module scope. None of them evaluates strings or request data;
// they only read the DOM and computed styles, and keep a small driver state
// object under a non-enumerable Symbol.for(key) property of `window`.

export const STATE_KEY = 'ergoqa.driver.v1';
export const TW_BINDING = '__ergoqaDriverTimingWindow';

/**
 * Installed with addInitScript before any page script runs (main frame only):
 * - MutationObserver ring buffer of callback timestamps (epoch ms) for
 *   feedback-latency measurement (input events count too: a field's value change);
 * - optional timing-window poller (every cfg.pollMs, default 16 ms) that reports
 *   visibility transitions of CSS selectors through an exposed binding.
 */
export function pageInit(cfg) {
  try {
    if (window.top !== window) return;
  } catch (e) {
    return;
  }
  const KEY = Symbol.for(cfg.key);
  if (window[KEY]) return;
  const now = () => performance.timeOrigin + performance.now();
  const N = 8192;
  const times = new Float64Array(N);
  let head = 0;
  let count = 0;
  const scan = (t0, t1, visit) => {
    for (let i = 1; i <= count; i++) {
      const v = times[(head - i + N) % N];
      if (v < t0) break;
      if (v <= t1) visit(v);
    }
  };
  const state = {
    ids: new WeakMap(),
    mutations: 0,
    now,
    firstMutationAfter(t0, t1) {
      let best = null;
      scan(t0, t1, (v) => { best = v; });
      return best;
    },
    countMutations(t0, t1) {
      let c = 0;
      scan(t0, t1, () => { c++; });
      return c;
    },
  };
  Object.defineProperty(window, KEY, { value: state, enumerable: false, configurable: false, writable: false });
  const record = () => {
    times[head] = now();
    head = (head + 1) % N;
    if (count < N) count++;
    state.mutations++;
  };
  // Only real changes count: a script that writes an attribute or text node with the
  // value it already has (a style re-set) changes nothing on screen. Attributes of <html>
  // and <body> are page-state markers (input modality, scroll lock, theme): what they
  // change on screen, if anything, is seen by the visual comparison.
  const changed = (m) => {
    if (m.type === 'childList') return m.addedNodes.length > 0 || m.removedNodes.length > 0;
    if (m.type === 'attributes') {
      if (m.target === document.documentElement || m.target === document.body) return false;
      return m.oldValue !== m.target.getAttribute(m.attributeName);
    }
    return m.oldValue !== m.target.data;
  };
  try {
    new MutationObserver((list) => {
      if (list.some(changed)) record();
    }).observe(document, {
      subtree: true, childList: true, attributes: true, characterData: true, attributeOldValue: true, characterDataOldValue: true,
    });
  } catch (e) { /* no document yet: nothing to observe */ }
  // A field's value changing (typed or deleted characters) is feedback too, and it is
  // not a DOM mutation. The driver masks the focused field in visual comparisons (the
  // caret blinks), so this is how typing echo is seen.
  // Checkbox, radio, range, colour, file and select changes show nothing by themselves.
  const NO_ECHO = ['checkbox', 'radio', 'range', 'color', 'file'];
  try {
    window.addEventListener('input', (e) => {
      const t = e.target;
      if (t && (t.tagName === 'SELECT' || (t.tagName === 'INPUT' && NO_ECHO.includes((t.type || '').toLowerCase())))) return;
      record();
    }, true);
  } catch (e) { /* ignore */ }

  // A script that changes a field's value (an amount chip filling the amount field)
  // changes what is on screen without a DOM mutation or an input event.
  for (const C of [window.HTMLInputElement, window.HTMLTextAreaElement]) {
    try {
      const d = C && Object.getOwnPropertyDescriptor(C.prototype, 'value');
      if (!d || !d.get || !d.set || !d.configurable) continue;
      Object.defineProperty(C.prototype, 'value', {
        configurable: true,
        enumerable: d.enumerable,
        get() { return d.get.call(this); },
        set(v) {
          const before = d.get.call(this);
          d.set.call(this, v);
          if (this.isConnected && d.get.call(this) !== before && !NO_ECHO.includes((this.type || '').toLowerCase())) record();
        },
      });
    } catch (e) { /* leave the property as it is */ }
  }

  const windows = Array.isArray(cfg.windows) ? cfg.windows : [];
  if (!windows.length || !cfg.binding) return;
  // Rendered, whether or not it is inside the viewport: a message that appears
  // off-screen is itself a finding (it cannot be read), so it must be recorded.
  const shown = (el) => {
    const r = el.getBoundingClientRect();
    if (r.width <= 0 || r.height <= 0) return false;
    if (typeof el.checkVisibility === 'function') {
      return el.checkVisibility({ opacityProperty: true, visibilityProperty: true });
    }
    const cs = getComputedStyle(el);
    return cs.display !== 'none' && cs.visibility === 'visible' && parseFloat(cs.opacity) > 0;
  };
  const last = new Map();
  const tick = () => {
    const fn = window[cfg.binding];
    if (typeof fn !== 'function') return;
    const t = now();
    for (const w of windows) {
      let v = false;
      let text = null;
      let box = null;
      let bg = null;
      let off = null;
      try {
        for (const el of document.querySelectorAll(w.selector)) {
          if (shown(el)) {
            v = true;
            if (last.get(w.id) !== true) {
              text = (el.innerText || el.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 500);
              // Geometry and own fill at appearance: elements that flash between
              // snapshots are never captured by them.
              const r = el.getBoundingClientRect();
              box = { x: r.left, y: r.top, w: r.width, h: r.height };
              bg = getComputedStyle(el).backgroundColor || null;
              off = r.bottom <= 0 || r.right <= 0 || r.top >= window.innerHeight || r.left >= window.innerWidth;
            }
            break;
          }
        }
      } catch (e) {
        v = null; // not a CSS selector: the driver falls back to Playwright polling
      }
      if (!last.has(w.id) || last.get(w.id) !== v) {
        last.set(w.id, v);
        try {
          Promise.resolve(fn({ id: w.id, v, t, text, box, bg, off })).catch(() => {});
        } catch (e) { /* binding gone during unload */ }
      }
    }
  };
  setInterval(tick, cfg.pollMs || 16);
}

/**
 * Element extraction for one snapshot (spec section 10). `args`:
 *   key, cap, groups: [{role, handles: [ElementHandle]}], hotspots (scenario),
 *   hotspotRoles: {hotspotId: [role]}, knownRoles: [role]
 * Returns {elements, candidates, truncated, viewport, scroll, active, pageHotspotError, unknownRoles}.
 */
export function extractSnapshot(args) {
  const KEY = Symbol.for(args.key);
  let state = window[KEY];
  if (!state) {
    state = { ids: new WeakMap() };
    try {
      Object.defineProperty(window, KEY, { value: state, enumerable: false });
    } catch (e) { /* ignore */ }
  }
  // The screen shows the visual viewport. At scale 1 it can be smaller than the layout
  // viewport (content wider than the screen widens the layout viewport) and panned
  // inside it. Geometry is computed in layout coordinates (elementFromPoint) against
  // the screen's bounds [VX0, VX1) x [VY0, VY1), and reported relative to the screen, so
  // boxes line up with the screenshot and with input coordinates.
  const vvp = window.visualViewport;
  const panned = !!vvp && Math.abs(vvp.scale - 1) < 0.01
    && (vvp.offsetLeft > 0.5 || vvp.offsetTop > 0.5 || vvp.width < window.innerWidth - 1 || vvp.height < window.innerHeight - 1);
  const VX0 = panned ? vvp.offsetLeft : 0;
  const VY0 = panned ? vvp.offsetTop : 0;
  const vw = panned ? vvp.width : window.innerWidth;
  const vh = panned ? vvp.height : window.innerHeight;
  const VX1 = VX0 + vw;
  const VY1 = VY0 + vh;
  const known = new Set(args.knownRoles || []);
  const unknownRoles = new Set();
  const round2 = (n) => Math.round(n * 100) / 100;

  // ---------- colours
  let probe = null;
  const colorCache = new Map();
  const parseColor = (str) => {
    if (!str) return null;
    if (colorCache.has(str)) return colorCache.get(str);
    let out = null;
    const m = /^rgba?\(\s*([\d.]+)[\s,]+([\d.]+)[\s,]+([\d.]+)(?:\s*[,/]\s*([\d.]+)(%?))?\s*\)$/.exec(str);
    if (m) {
      let a = m[4] === undefined ? 1 : parseFloat(m[4]);
      if (m[5] === '%') a /= 100;
      out = { r: +m[1], g: +m[2], b: +m[3], a: Math.max(0, Math.min(1, a)) };
    } else if (str === 'transparent') {
      out = { r: 0, g: 0, b: 0, a: 0 };
    } else {
      try {
        if (!probe) {
          const c = typeof OffscreenCanvas === 'function' ? new OffscreenCanvas(1, 1) : document.createElement('canvas');
          probe = c.getContext('2d', { willReadFrequently: true });
        }
        probe.clearRect(0, 0, 1, 1);
        probe.fillStyle = '#000';
        probe.fillStyle = str;
        probe.fillRect(0, 0, 1, 1);
        const d = probe.getImageData(0, 0, 1, 1).data;
        out = { r: d[0], g: d[1], b: d[2], a: d[3] / 255 };
      } catch (e) {
        out = null;
      }
    }
    colorCache.set(str, out);
    return out;
  };
  const over = (top, bottom) => ({
    r: top.r * top.a + bottom.r * (1 - top.a),
    g: top.g * top.a + bottom.g * (1 - top.a),
    b: top.b * top.a + bottom.b * (1 - top.a),
  });
  const mix = (a, b, t) => ({ r: a.r + (b.r - a.r) * t, g: a.g + (b.g - a.g) * t, b: a.b + (b.b - a.b) * t });
  const hex = (c) => {
    if (!c) return null;
    const h = (v) => Math.max(0, Math.min(255, Math.round(v))).toString(16).padStart(2, '0');
    return `#${h(c.r)}${h(c.g)}${h(c.b)}`;
  };

  const styleCache = new Map();
  const style = (el) => {
    let cs = styleCache.get(el);
    if (!cs) {
      cs = getComputedStyle(el);
      styleCache.set(el, cs);
    }
    return cs;
  };
  const parentOf = (n) => n.parentElement || (n.getRootNode && n.getRootNode() !== document ? n.getRootNode().host : null) || null;
  const MEDIA = new Set(['img', 'video', 'canvas', 'svg', 'iframe', 'picture', 'object', 'embed']);

  let canvasBase = null;
  const baseColor = () => {
    if (canvasBase) return canvasBase;
    let c = { r: 255, g: 255, b: 255 };
    const root = document.documentElement;
    const body = document.body;
    const rootBg = root ? parseColor(style(root).backgroundColor) : null;
    if (rootBg && rootBg.a > 0) c = over(rootBg, c);
    else if (body) {
      const bodyBg = parseColor(style(body).backgroundColor);
      if (bodyBg && bodyBg.a > 0) c = over(bodyBg, c);
    }
    canvasBase = c;
    return c;
  };

  // Layers from `el` downward in paint order (el first).
  const layersBelow = (el, rect) => {
    const ancestors = [];
    for (let n = el; n; n = parentOf(n)) ancestors.push(n);
    const ix0 = Math.max(VX0, rect.left);
    const ix1 = Math.min(VX1, rect.right);
    const iy0 = Math.max(VY0, rect.top);
    const iy1 = Math.min(VY1, rect.bottom);
    if (ix1 - ix0 >= 1 && iy1 - iy0 >= 1) {
      let stack = [];
      try {
        stack = document.elementsFromPoint((ix0 + ix1) / 2, (iy0 + iy1) / 2);
      } catch (e) {
        stack = [];
      }
      let idx = stack.indexOf(el);
      if (idx >= 0) return { chain: stack.slice(idx), ancestors };
      idx = stack.findIndex((n) => n !== el && n.contains && n.contains(el));
      if (idx >= 0) {
        const container = stack[idx];
        const head = [];
        for (const n of ancestors) {
          if (n === container) break;
          head.push(n);
        }
        return { chain: head.concat(stack.slice(idx)), ancestors };
      }
    }
    return { chain: ancestors, ancestors };
  };

  // Effective opaque colours with group opacity for ancestors (spec: walk ancestors,
  // composite rgba over white; null when an image/gradient/canvas is underneath).
  const colorsFor = (el, rect, cs, svgPaint = false) => {
    const unknownMedia = (n) => MEDIA.has(n.tagName?.toLowerCase()) && !(svgPaint && n.tagName?.toLowerCase() === 'svg');
    // SVG shapes/groups do not paint CSS box backgrounds. The outer <svg> does.
    const svgGraphic = (n) => svgPaint && n instanceof SVGElement && n.tagName.toLowerCase() !== 'svg';
    const background = (n, ncs) => svgGraphic(n) ? null : parseColor(ncs.backgroundColor);
    const imageBackground = (n, ncs) => !svgGraphic(n) && ncs.backgroundImage && ncs.backgroundImage !== 'none';
    const { chain, ancestors } = layersBelow(el, rect);
    const anc = new Set(ancestors);
    let color = baseColor();
    const groups = [];
    let outer = null;
    // Start at the topmost fully opaque solid layer at or below the element when no
    // translucent group sits above it: whatever is under an opaque fill (canvas,
    // image, gradient) cannot show through, so it must not null the colour.
    let start = chain.length - 1;
    for (let i = 0; i < chain.length; i++) {
      const n = chain[i];
      const tag = n.tagName ? n.tagName.toLowerCase() : '';
      const ncs = style(n);
      if (unknownMedia(n) || imageBackground(n, ncs)) break;
      if ((parseFloat(ncs.opacity) || 0) < 1) break;
      const bg = background(n, ncs);
      if (bg && bg.a >= 0.999) {
        start = i;
        break;
      }
    }
    for (let i = start; i >= 0; i--) {
      const n = chain[i];
      const tag = n.tagName ? n.tagName.toLowerCase() : '';
      if (unknownMedia(n)) return null;
      // A different SVG shape behind this one is not a uniform CSS backdrop.
      if (svgPaint && n instanceof SVGElement && n !== el && !n.contains(el) && n.tagName.toLowerCase() !== 'svg') return null;
      const ncs = style(n);
      if (imageBackground(n, ncs)) return null;
      const op = parseFloat(ncs.opacity);
      const bg = background(n, ncs);
      if (n === el) outer = { color, groups: groups.slice() };
      if (anc.has(n)) {
        if (op < 1) groups.push({ backdrop: color, alpha: op });
        if (bg && bg.a > 0) color = over(bg, color);
      } else if (bg && bg.a > 0) {
        let cum = 1;
        for (let p = n; p; p = parentOf(p)) cum *= parseFloat(style(p).opacity) || 0;
        color = over({ ...bg, a: bg.a * cum }, color);
      }
    }
    const fgRaw = parseColor(cs.color) || { r: 0, g: 0, b: 0, a: 1 };
    let bgC = color;
    let fgC = over(fgRaw, color);
    for (let i = groups.length - 1; i >= 0; i--) {
      bgC = mix(groups[i].backdrop, bgC, groups[i].alpha);
      fgC = mix(groups[i].backdrop, fgC, groups[i].alpha);
    }
    let containerC = null;
    if (outer) {
      containerC = outer.color;
      for (let i = outer.groups.length - 1; i >= 0; i--) {
        containerC = mix(outer.groups[i].backdrop, containerC, outer.groups[i].alpha);
      }
    }
    if (start === 0 && chain.length > 1) {
      // The element's own fill is opaque, so the loop above started at the element and
      // `outer` fell back to the page base colour. Composite the layers below it instead.
      let below = chain.length - 1;
      let blocked = false;
      for (let i = 1; i < chain.length; i++) {
        const n = chain[i];
        const tag = n.tagName ? n.tagName.toLowerCase() : '';
        const ncs = style(n);
        if (unknownMedia(n) || imageBackground(n, ncs)) { blocked = true; break; }
        const bg = background(n, ncs);
        if (bg && bg.a >= 0.999) { below = i; break; }
      }
      if (blocked) containerC = null;
      else {
        let c = baseColor();
        for (let i = below; i >= 1; i--) {
          const bg = background(chain[i], style(chain[i]));
          if (bg && bg.a > 0) c = over(bg, c);
        }
        containerC = c;
      }
    }
    const composite = (raw, backdrop = color) => {
      let c = over(raw, backdrop);
      for (let i = groups.length - 1; i >= 0; i--) c = mix(groups[i].backdrop, c, groups[i].alpha);
      return c;
    };
    return { fg: fgC, bg: bgC, container: containerC, composite, rawBg: color };
  };

  const borderFor = (cs, bg) => {
    let best = null;
    for (const side of ['Top', 'Right', 'Bottom', 'Left']) {
      const w = parseFloat(cs[`border${side}Width`]) || 0;
      const st = cs[`border${side}Style`];
      if (w <= 0 || st === 'none' || st === 'hidden') continue;
      if (!best || w > best.w) best = { w, c: parseColor(cs[`border${side}Color`]) };
    }
    if (!best || !best.c || best.c.a <= 0) return { color: null, width: 0, raw: null };
    return { color: bg ? hex(over(best.c, bg)) : hex(best.c), width: round2(best.w), raw: best.c };
  };

  // ---------- semantics
  const text = (n) => (n ? (n.innerText ?? n.textContent ?? '').replace(/\s+/g, ' ').trim() : '');
  const implicitRole = (el) => {
    const tag = el.tagName.toLowerCase();
    switch (tag) {
      case 'a': return el.hasAttribute('href') ? 'link' : 'generic';
      case 'button': case 'summary': return 'button';
      case 'select': return el.multiple || el.size > 1 ? 'listbox' : 'combobox';
      case 'textarea': return 'textbox';
      case 'h1': case 'h2': case 'h3': case 'h4': case 'h5': case 'h6': return 'heading';
      case 'p': return 'paragraph';
      case 'li': return 'listitem';
      case 'img': return 'img';
      case 'nav': return 'navigation';
      case 'dialog': return 'dialog';
      case 'option': return 'option';
      case 'td': return 'cell';
      case 'th': return 'columnheader';
      case 'output': return 'status';
      case 'input': {
        const t = (el.getAttribute('type') || 'text').toLowerCase();
        if (['submit', 'button', 'reset', 'image'].includes(t)) return 'button';
        if (t === 'checkbox') return 'checkbox';
        if (t === 'radio') return 'radio';
        if (t === 'range') return 'slider';
        if (t === 'number') return 'spinbutton';
        if (t === 'search') return 'searchbox';
        return 'textbox';
      }
      default: return 'generic';
    }
  };
  const roleOf = (el) => {
    const explicit = (el.getAttribute('role') || '').trim().split(/\s+/)[0];
    return explicit || implicitRole(el);
  };
  // Accessible name and where it came from (accname 1.2 order, simplified): the
  // source lets checks tell a label-in-name mismatch (aria-label overriding the
  // visible text) from a placeholder-only field or an unnamed icon button.
  // Ids resolve in the element's own tree (document or shadow root).
  const byId = (el, id) => {
    const root = el.getRootNode();
    return (root && typeof root.getElementById === 'function' ? root.getElementById(id) : null) || document.getElementById(id);
  };
  // SVG has no innerText; its textContent includes <style> and <script>. Its name comes
  // from a <title> child only.
  const svgTitle = (el) => {
    const t = [...el.children].find((c) => c.tagName && c.tagName.toLowerCase() === 'title');
    return t ? t.textContent.replace(/\s+/g, ' ').trim() : '';
  };
  // Roles whose name comes from the author only, never from their content (ARIA 1.2
  // "Name From: author"): a role=textbox div's text is its value, not its name.
  const AUTHOR_ONLY = new Set(['textbox', 'searchbox', 'combobox', 'listbox', 'spinbutton', 'slider', 'progressbar', 'meter', 'scrollbar',
    'tree', 'treegrid', 'grid', 'table', 'menu', 'menubar', 'radiogroup', 'tablist', 'toolbar', 'dialog', 'alertdialog', 'img', 'group']);
  const accNameSrc = (el) => {
    const lb = el.getAttribute('aria-labelledby');
    if (lb) {
      const t = lb.split(/\s+/).map((id) => byId(el, id)).filter(Boolean).map(text).join(' ').trim();
      if (t) return [t, 'aria-labelledby'];
    }
    const al = (el.getAttribute('aria-label') || '').trim();
    if (al) return [al, 'aria-label'];
    const tag = el.tagName.toLowerCase();
    const type = (el.getAttribute('type') || '').toLowerCase();
    if (tag === 'img' || (tag === 'input' && type === 'image')) {
      const alt = (el.getAttribute('alt') || '').trim();
      if (alt) return [alt, 'alt'];
    }
    if (tag === 'input' && ['submit', 'button', 'reset'].includes(type)) {
      const v = (el.value || (type === 'submit' ? 'Submit' : type === 'reset' ? 'Reset' : '')).trim();
      if (v) return [v, 'value'];
    } else if (['input', 'select', 'textarea'].includes(tag)) {
      if (el.labels && el.labels.length) {
        const t = [...el.labels].map(text).join(' ').trim();
        if (t) return [t, 'label'];
      }
      // HTML-AAM order: title before placeholder.
      const ti = (el.getAttribute('title') || '').trim();
      if (ti) return [ti, 'title'];
      const ph = (el.getAttribute('placeholder') || '').trim();
      if (ph) return [ph, 'placeholder'];
    } else if (typeof SVGElement !== 'undefined' && el instanceof SVGElement) {
      const t = svgTitle(el);
      if (t) return [t, 'content'];
    } else if (!AUTHOR_ONLY.has((el.getAttribute('role') || '').trim().split(/\s+/)[0])) {
      const t = nameFromContent(el) || text(el);
      if (t) return [t.slice(0, 300), 'content'];
      const img = el.querySelector && el.querySelector('img[alt]');
      if (img && img.alt.trim()) return [img.alt.trim(), 'content'];
      const svgTitle = el.querySelector && el.querySelector('svg title');
      if (svgTitle && svgTitle.textContent.trim()) return [svgTitle.textContent.trim(), 'content'];
    }
    const title = (el.getAttribute('title') || '').trim();
    return title ? [title, 'title'] : ['', 'none'];
  };
  const accName = (el) => accNameSrc(el)[0];
  // Visually hidden (the "visually-hidden" pattern, display:none, visibility:hidden).
  const visuallyHidden = (n) => {
    const cs = style(n);
    if (cs.display === 'none' || cs.visibility === 'hidden' || cs.visibility === 'collapse') return true;
    if (/inset\(\s*50%/.test(cs.clipPath || '') || /rect\(\s*0(px)?,?\s*0(px)?,?\s*0(px)?,?\s*0(px)?\s*\)/.test(cs.clip || '')) return true;
    const r = n.getBoundingClientRect();
    return r.width <= 1 && r.height <= 1 && (cs.overflow === 'hidden' || cs.overflow === 'clip');
  };
  // ACT "visible inner text": text a sighted user sees inside the element.
  const visibleInnerText = (el) => {
    const out = [];
    let budget = 400;
    const walk = (n) => {
      for (const c of n.childNodes) {
        if (budget-- <= 0) return;
        if (c.nodeType === 3) out.push(c.nodeValue);
        else if (c.nodeType === 1 && !visuallyHidden(c) && c.tagName.toLowerCase() !== 'style' && c.tagName.toLowerCase() !== 'script') {
          // Inline boxes join their text ("A", "C", "T" reads "ACT"); block boxes and
          // <br> break words, as innerText does.
          const block = c.tagName.toLowerCase() === 'br' || !/^inline/.test(style(c).display || 'inline');
          if (block) out.push(' ');
          walk(c);
          if (block) out.push(' ');
        }
      }
    };
    walk(el);
    return out.join('').replace(/\s+/g, ' ').trim().slice(0, 300);
  };
  // Name from content (accname 1.2 step 2F, simplified): text, plus the names of
  // descendant images and labelled elements; hidden descendants contribute nothing.
  const nameFromContent = (el) => {
    const out = [];
    let budget = 400;
    const walk = (n) => {
      for (const c of n.childNodes) {
        if (budget-- <= 0) return;
        if (c.nodeType === 3) {
          out.push(c.nodeValue);
          continue;
        }
        if (c.nodeType !== 1) continue;
        const tag = c.tagName.toLowerCase();
        if (tag === 'style' || tag === 'script') continue;
        const cs = style(c);
        if (cs.display === 'none' || cs.visibility === 'hidden' || c.getAttribute('aria-hidden') === 'true') continue;
        const lb = c.getAttribute('aria-labelledby');
        const lbText = lb ? lb.split(/\s+/).map((id) => byId(c, id)).filter(Boolean).map(text).join(' ').trim() : '';
        const al = (c.getAttribute('aria-label') || '').trim();
        if (lbText) out.push(lbText);
        else if (al) out.push(al);
        else if (tag === 'img' || (tag === 'input' && (c.getAttribute('type') || '').toLowerCase() === 'image')) {
          out.push((c.getAttribute('alt') || '').trim() || (c.getAttribute('title') || '').trim());
        } else if (typeof SVGElement !== 'undefined' && c instanceof SVGElement) out.push(svgTitle(c) || (c.getAttribute('title') || ''));
        else {
          const before = out.length;
          walk(c);
          if (out.slice(before).join('').trim() === '' && c.getAttribute('title')) out.push(c.getAttribute('title').trim());
        }
      }
    };
    walk(el);
    return out.join(' ').replace(/\s+/g, ' ').trim();
  };
  const NATIVE_FOCUSABLE = new Set(['a', 'button', 'input', 'select', 'textarea', 'summary']);
  // Programmatic state a check can read without a screen reader (WCAG 4.1.2, 3.3.1).
  const a11yOf = (el) => {
    const tag = el.tagName.toLowerCase();
    const ids = (attr) => (el.getAttribute(attr) || '').split(/\s+/).filter((id) => id && byId(el, id));
    const tabAttr = el.getAttribute('tabindex');
    const native = NATIVE_FOCUSABLE.has(tag) && !(tag === 'a' && !el.hasAttribute('href'));
    let disabled = false;
    try {
      disabled = el.matches(':disabled');
    } catch (e) {
      disabled = false;
    }
    return {
      name_source: accNameSrc(el)[1],
      invalid: el.getAttribute('aria-invalid') === 'true',
      user_invalid: (() => {
        try {
          return el.matches(':user-invalid');
        } catch (e) {
          return false;
        }
      })(),
      described_by: ids('aria-describedby').slice(0, 8),
      // A visible label is the primary affordance. Icon-only controls also need a
      // discoverable hover/focus explanation; record native title or an associated
      // role=tooltip when it is present in the captured state.
      tooltip: (() => {
        const title = (el.getAttribute('title') || '').trim();
        if (title) return title.slice(0, 200);
        return ids('aria-describedby').map((id) => byId(el, id)).filter((node) => node && node.getAttribute('role') === 'tooltip')
          .map((node) => text(node)).filter(Boolean).join(' ').slice(0, 200);
      })(),
      visible_label: tag === 'textarea' ? '' : visibleInnerText(el),
      // Hidden from assistive technology (aria-hidden or inert on it or an ancestor).
      hidden: !!(el.closest && (el.closest('[aria-hidden="true"]') || el.closest('[inert]'))),
      // Rendered (not display:none, not visibility:hidden), even with a zero-size box: such
      // an element is still in the accessibility tree (AUT-20). Opacity does not count.
      rendered: (() => {
        if (typeof el.checkVisibility === 'function') return el.checkVisibility({ visibilityProperty: true });
        const cs = style(el);
        return cs.display !== 'none' && cs.visibility === 'visible' && el.getClientRects().length > 0;
      })(),
      // Visible text drawn by an icon font (ligatures such as "menu"): not a text label.
      icon_font: (() => {
        const nodes = [el, ...el.querySelectorAll('span, i, em')].slice(0, 6);
        return nodes.some((n) => n.textContent && n.textContent.trim() && iconFont(style(n).fontFamily));
      })(),
      error_message: ids('aria-errormessage')[0] || null,
      required: el.required === true || el.getAttribute('aria-required') === 'true',
      focusable: !disabled && (tabAttr !== null ? parseInt(tabAttr, 10) >= 0 : native || el.isContentEditable),
      tabindex: tabAttr !== null && Number.isFinite(parseInt(tabAttr, 10)) ? parseInt(tabAttr, 10) : null,
    };
  };
  // Text cut off by its own box (XCTest textClipped; WCAG 1.4.4/1.4.12 symptoms).
  // Glyph boxes of the text an element owns. A block's box and its text differ: a
  // nowrap line can run past the edge of a block that itself stays inside its column.
  const ownTextRects = (el) => {
    const rects = [];
    for (const node of el.childNodes) {
      if (node.nodeType !== 3 || !node.nodeValue.trim()) continue;
      const range = document.createRange();
      range.selectNodeContents(node);
      rects.push(...[...range.getClientRects()].filter((r) => r.width > 0 && r.height > 0));
    }
    return rects;
  };
  const unionRect = (rects) => rects.reduce((u, r) => ({ left: Math.min(u.left, r.left), top: Math.min(u.top, r.top),
    right: Math.max(u.right, r.right), bottom: Math.max(u.bottom, r.bottom) }),
  { left: Infinity, top: Infinity, right: -Infinity, bottom: -Infinity });
  // Boxes that clip on purpose: carousels, sliders and scroll-snap rows show part of the
  // next item, and a disclosure (named by a control's aria-controls) shows a preview.
  const DESIGNED_TRACK = /carousel|swiper|slick|splide|flickity|glide|embla|marquee|ticker|slider/i;
  const designedClip = (n) => {
    const rd = (n.getAttribute('aria-roledescription') || '').toLowerCase();
    if (rd.includes('carousel') || rd.includes('slide')) return true;
    const snap = style(n).scrollSnapType;
    if (snap && snap !== 'none') return true;
    if (n.id) {
      try {
        if (n.getRootNode().querySelector(`[aria-controls~="${CSS.escape(n.id)}"]`)) return true;
      } catch (e) { /* an unusual id never hides a cut */ }
    }
    return DESIGNED_TRACK.test(`${n.id || ''} ${typeof n.className === 'string' ? n.className : ''}`);
  };
  // Text that paints nothing (a transparent fill with no stroke, shadow or background
  // clipped to the glyphs, such as a sizing mirror behind a field, or text hidden by
  // visibility or a zero opacity, such as a width-reserving copy of a bold label) cannot
  // be cut, covered or drawn over another text.
  const ICON_FONT = /icon|material|awesome|symbol|glyph|fontello|ionicon|bootstrap-icons/i;
  // An icon font leads its stack; a symbol font later in a system stack (Bootstrap's
  // "Segoe UI Symbol") only backs up ordinary text.
  const iconFont = (family) => ICON_FONT.test(String(family || '').split(',')[0].replace(/["']/g, ''));
  const inkCache = new Map();
  const paintsInk = (el) => {
    if (inkCache.has(el)) return inkCache.get(el);
    const cs = style(el);
    const fill = parseColor(cs.webkitTextFillColor || cs.color);
    const stroke = parseColor(cs.webkitTextStrokeColor);
    let ink = !fill || fill.a > 0 || (!!cs.textShadow && cs.textShadow !== 'none')
      || ((parseFloat(cs.webkitTextStrokeWidth) || 0) > 0 && (!stroke || stroke.a > 0));
    for (let n = el; !ink && n && n.nodeType === 1; n = parentOf(n)) {
      const ncs = style(n);
      if (ncs.backgroundClip === 'text' || ncs.webkitBackgroundClip === 'text') ink = true;
    }
    // display: contents has no box of its own, so the nearest box above it is tested.
    let probe = el;
    while (probe && probe.nodeType === 1 && style(probe).display === 'contents') probe = parentOf(probe);
    if (ink && cs.visibility !== 'visible') ink = false;
    if (ink && probe && probe.nodeType === 1 && typeof probe.checkVisibility === 'function'
      && !probe.checkVisibility({ opacityProperty: true, visibilityProperty: true })) ink = false;
    inkCache.set(el, ink);
    return ink;
  };
  // Rectangles and glyph boxes are on screen while client sizes are in the element's own
  // units; their ratio is the scale on screen. Under rotation, skew or a 3D transform a
  // rectangle is only a bounding box, so such text is left unmeasured (null).
  const screenScale = (el) => {
    for (let p = el; p && p.nodeType === 1; p = p.assignedSlot || parentOf(p)) {
      const pcs = style(p);
      if (pcs.rotate && pcs.rotate !== 'none') return null;
      if (pcs.transform && pcs.transform !== 'none') {
        let m = null;
        try {
          m = new DOMMatrixReadOnly(pcs.transform);
        } catch (e) {
          return null;
        }
        if (!m.is2D || Math.abs(m.b) > 1e-6 || Math.abs(m.c) > 1e-6) return null;
      }
    }
    const r = el.getBoundingClientRect();
    return { sx: el.offsetWidth ? r.width / el.offsetWidth : 1, sy: el.offsetHeight ? r.height / el.offsetHeight : 1 };
  };
  // The padding box on screen, where overflow clips.
  const paddingBoxOf = (n, r, sc) => ({ left: r.left + n.clientLeft * sc.sx, top: r.top + n.clientTop * sc.sy,
    right: r.left + (n.clientLeft + n.clientWidth) * sc.sx, bottom: r.top + (n.clientTop + n.clientHeight) * sc.sy });
  // owner: the element reported for the text (a control whose label sits in spans); a cut
  // by its own box reads as its own (by: null).
  const clippedOf = (el, cs, directLabel = false, owner = el) => {
    const hide = (v) => v === 'hidden' || v === 'clip';
    if (!paintsInk(el)) return null;
    const sc = screenScale(el);
    if (!sc) return null;
    // A control's scroll size includes decoration and nested labels. Measure only
    // the text this candidate owns; tagged descendants are captured separately.
    const rects = ownTextRects(el);
    if (directLabel && !rects.length) return null;
    const cuts = (a, axis) => rects.some((r) => axis === 'x'
      ? r.right > a.right + 1 || r.left < a.left - 1
      : r.bottom > a.bottom + 1 || r.top < a.top - 1);
    // Overflow does not apply to an inline box.
    const clipsSelf = cs.display !== 'inline' && cs.display !== 'contents';
    const inner = paddingBoxOf(el, el.getBoundingClientRect(), sc);
    let x = clipsSelf && hide(cs.overflowX) && (directLabel ? cuts(inner, 'x') : el.scrollWidth > el.clientWidth + 1);
    let y = clipsSelf && hide(cs.overflowY) && (directLabel ? cuts(inner, 'y') : el.scrollHeight > el.clientHeight + 1);
    let by = null;
    let viewportCut = false;
    let ellipsis = cs.textOverflow === 'ellipsis';
    if (!x && !y) {
      // ACT 59br37: text cut by an ancestor that clips (a fixed-width chip or label, a
      // card, a page column). Measured on the glyph boxes the element owns, so a nowrap
      // line that runs out of its block is found at any depth. The text must be partly
      // visible: a slide wholly outside its carousel is not cut text. A scroll container
      // is reachable, a designed clip is intended, and a box under 4 px holds visually
      // hidden text.
      const r = rects.length ? unionRect(rects) : el.getBoundingClientRect();
      const box = el.getBoundingClientRect();
      const past = (a, axis) => (rects.length ? cuts(a, axis) : axis === 'x'
        ? r.right > a.right + 1 || r.left < a.left - 1 : r.bottom > a.bottom + 1 || r.top < a.top - 1);
      // Partly on screen: the text or the box holding it (a cell whose text has
      // already run past the edge still shows its first pixels).
      const shownX = (a) => (r.left < a.right && r.right > a.left) || (box.left < a.right && box.right > a.left);
      const shownY = (a) => (r.top < a.bottom && r.bottom > a.top) || (box.top < a.bottom && box.bottom > a.top);
      const scrolls = (v) => v === 'auto' || v === 'scroll';
      for (let n = parentOf(el); n && n.nodeType === 1 && n !== document.body && n !== document.documentElement; n = parentOf(n)) {
        if (designedClip(n)) return null;
        const ncs = style(n);
        const ax = ncs.overflowX;
        const ay = ncs.overflowY;
        if (!hide(ax) && !hide(ay) && !scrolls(ax) && !scrolls(ay)) continue;
        const nb = n.getBoundingClientRect();
        if (nb.width < 4 || nb.height < 4) return null;
        const a = n.offsetWidth && n.offsetHeight
          ? paddingBoxOf(n, nb, { sx: nb.width / n.offsetWidth, sy: nb.height / n.offsetHeight }) : nb;
        // Judge each axis on its own: overflow-x hidden makes overflow-y compute to auto,
        // which scrolls only text that runs out vertically.
        const overX = past(a, 'x');
        const overY = past(a, 'y');
        if ((scrolls(ax) && overX) || (scrolls(ay) && overY)) return null; // reachable by scrolling this box
        const cutX = hide(ax) && overX && shownX(a);
        const cutY = hide(ay) && overY && shownY(a);
        if (cutX || cutY) {
          x = cutX;
          y = cutY;
          by = n;
          ellipsis = ellipsis || ncs.textOverflow === 'ellipsis';
          break;
        }
      }
      if (!x && !y && rects.length) {
        // The screen edge cuts sideways when the page hides horizontal overflow: text past
        // it can never be scrolled into view.
        const rootHides = [document.documentElement, document.body].some((n) => n && hide(style(n).overflowX));
        const screen = { left: VX0, right: VX1, top: VY0, bottom: VY1 };
        if (rootHides && cuts(screen, 'x') && shownX(screen)) {
          x = true;
          by = document.documentElement;
          viewportCut = true;
        }
      }
      if (!x && !y) return null;
    }
    const clamp = cs.webkitLineClamp && cs.webkitLineClamp !== 'none';
    // ACT 59br37's exceptions, on the clipping box: sideways, one line that does not
    // wrap and ends in a marker (white-space nowrap, text-overflow other than clip);
    // vertically, a box one line high (used line-height >= its height, content box for
    // overflow-y clip) whose glyphs fit in it. Clipped this way the text is cut cleanly.
    const cb = by || el;
    const bcs = by ? style(by) : cs;
    // text-overflow draws its marker only in a block container (not a flex or grid box).
    const markerShown = bcs.textOverflow !== 'clip' && ['block', 'inline-block', 'list-item', 'flow-root', 'table-cell', 'table-caption'].includes(bcs.display);
    const exemptX = !x || (/^nowrap/.test(bcs.whiteSpace) && markerShown);
    const fontPx = parseFloat(cs.fontSize) || 16;
    // A "normal" line height depends on the font (about 1.45 em for Korean fonts): take
    // the height of the text's first line box instead of assuming 1.2 em.
    let lineH = parseFloat(bcs.lineHeight);
    if (!(lineH > 0)) {
      lineH = 1.2 * fontPx;
      try {
        const rg = document.createRange();
        rg.selectNodeContents(el);
        const first = rg.getClientRects()[0];
        if (first && first.height > 0) lineH = first.height / sc.sy;
      } catch (e) { /* keep the estimate */ }
    }
    // In the box's own units, like the line height and font size.
    const boxH = bcs.overflowY === 'clip'
      ? cb.clientHeight - (parseFloat(bcs.paddingTop) || 0) - (parseFloat(bcs.paddingBottom) || 0)
      : cb.offsetHeight || cb.getBoundingClientRect().height / sc.sy;
    const exemptY = !y || (lineH >= boxH - 0.5 && fontPx <= boxH + 0.5);
    if (by && !markerShown) ellipsis = false; // declared but not drawn
    // Tickers and marquees clip by design: text that moves (CSS animation on the element
    // or a close ancestor, or <marquee>) is recorded as animated.
    let animated = false;
    for (let n = el, i = 0; n && n.nodeType === 1 && i < 4; n = n.parentElement, i++) {
      const ncs = style(n);
      if (n.tagName.toLowerCase() === 'marquee' || (ncs.animationName && ncs.animationName !== 'none')
        || (typeof n.getAnimations === 'function' && n.getAnimations().length)) {
        animated = true;
        break;
      }
    }
    return { x, y, ellipsis: ellipsis || !!clamp, line_clamp: !!clamp, animated,
      by: viewportCut ? 'viewport' : by && by !== owner ? (by.getAttribute('id') ? `#${by.getAttribute('id')}` : by.tagName.toLowerCase()) : null,
      act: exemptX && exemptY ? 'passed' : 'failed' };
  };
  // The control that reports for a text holder: its nearest interactive ancestor.
  const ownerControl = (n) => {
    for (let p = n.parentElement; p; p = p.parentElement) if (isInteractive(p)) return p;
    return null;
  };
  // A holder that is a candidate of its own (tagged, interactive, an alert, or text that
  // no control contains) reports for itself.
  const ownCandidate = (n) => {
    if (roleMap.has(n) || isInteractive(n)) return true;
    const role = (n.getAttribute('role') || '').trim();
    if (role === 'alert' || role === 'status') return true;
    const tag = n.tagName.toLowerCase();
    return (ALWAYS_TEXT.has(tag) || DIRECT_TEXT.has(tag)) && !(n.parentElement && n.parentElement.closest(INTERACTIVE));
  };
  // The elements that draw a control's words when they sit in spans: each owns a text
  // node, reports through this control (not a nested one, not a candidate of its own),
  // is not visually hidden, draws no icon-font glyphs and paints ink (LY-01..03).
  const labelHolders = (el) => {
    const out = [];
    const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    for (let node = walker.nextNode(); node && out.length < 12; node = walker.nextNode()) {
      const holder = node.parentElement;
      if (!node.nodeValue.trim() || !holder || holder === el || out.includes(holder)) continue;
      if (ownCandidate(holder) || ownerControl(holder) !== el) continue;
      let hidden = false;
      for (let p = holder; p && p !== el; p = p.parentElement) if (visuallyHidden(p)) { hidden = true; break; }
      if (hidden || iconFont(style(holder).fontFamily) || !paintsInk(holder)) continue;
      out.push(holder);
    }
    return out;
  };
  const labelClip = (el) => {
    for (const holder of labelHolders(el)) {
      const clip = clippedOf(holder, style(holder), true, el);
      if (clip) return { ...clip, label: uniqueSelector(holder) };
    }
    return null;
  };
  // Whether an element's text paints anything: its own text or, for a control whose
  // words sit in spans, any of them (null when it has no text).
  const textInk = (el, interactive) => {
    if (hasDirectText(el)) return paintsInk(el);
    if (!interactive) return null;
    let seen = false;
    const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    for (let node = walker.nextNode(); node; node = walker.nextNode()) {
      if (!node.nodeValue.trim() || !node.parentElement) continue;
      seen = true;
      if (paintsInk(node.parentElement)) return true;
    }
    return seen ? false : null;
  };
  const visibleText = (el) => {
    const tag = el.tagName.toLowerCase();
    if (tag === 'input') {
      const type = (el.getAttribute('type') || '').toLowerCase();
      return ['submit', 'button', 'reset'].includes(type) ? (el.value || '').trim() : '';
    }
    if (tag === 'textarea') return '';
    if (tag === 'select') {
      const opt = el.selectedOptions && el.selectedOptions[0];
      return opt ? text(opt) : '';
    }
    return text(el).slice(0, 300);
  };
  const hasDirectText = (el) => {
    for (const n of el.childNodes) {
      if (n.nodeType === 3 && n.nodeValue.trim()) return true;
    }
    return false;
  };

  // Canvas bounds describe glyphs in a matching CSS font, not DOM raster pixels
  // or line layout. Keep actual displayed text separate from fixed font probes.
  let fontContext = null;
  const fontProbeCache = new Map();
  // FontFaceSet.check() costs about a millisecond a call, once per text element. It can only
  // answer false when a face of one of the font's families is not loaded, so a family list
  // whose faces are all loaded (or that has none, a system font) needs no call.
  const familiesReady = new Map();
  const fontLoadedFor = (cs, font, textValue) => {
    let ready = familiesReady.get(cs.fontFamily);
    if (ready === undefined) {
      const unquote = (s) => s.trim().replace(/^['"]|['"]$/g, '').toLowerCase();
      const names = new Set(cs.fontFamily.split(',').map(unquote));
      ready = true;
      for (const face of document.fonts) {
        if (face.status !== 'loaded' && names.has(unquote(face.family))) {
          ready = false;
          break;
        }
      }
      familiesReady.set(cs.fontFamily, ready);
    }
    return ready || document.fonts.check(font, textValue);
  };
  const privateFontNodes = new Set();
  const fontProperties = ['fontFamily', 'fontSize', 'fontWeight', 'fontStyle', 'fontStretch',
    'fontVariant', 'fontFeatureSettings', 'fontVariationSettings', 'fontOpticalSizing',
    'fontKerning', 'letterSpacing', 'wordSpacing', 'textTransform', 'direction', 'writingMode'];
  const fontMetricsFor = (el, displayedText) => {
    const gaps = new Set(['dom_ink_unmeasured', 'font_fallback_unverified']);
    const result = { method: 'canvas-textmetrics-v1', unit: 'css_px', status: 'unavailable',
      body_height_px: null, probes: null, limitations: [] };
    const finish = () => ({ ...result, limitations: [...gaps].sort() });
    const privateControl = (n) => ['input', 'textarea', 'select'].includes(n.tagName?.toLowerCase()) || n.isContentEditable
      || ['textbox', 'searchbox', 'combobox', 'listbox', 'spinbutton'].includes(n.getAttribute('role'))
      || n.hasAttribute('data-sensitive') || n.hasAttribute('data-private') || privateFontNodes.has(n);
    if ((args.privateValues || []).some((value) => typeof value === 'string' && value && displayedText.includes(value))) {
      gaps.add('private_control'); return finish();
    }
    for (let n = el, count = 0; n; n = parentOf(n)) {
      if (++count > 64) { gaps.add('node_cap'); return finish(); }
      if (privateControl(n)) { gaps.add('private_control'); return finish(); }
      const cs = style(n);
      if ((cs.transform && cs.transform !== 'none') || ['scale', 'rotate', 'translate'].some((k) => cs[k] && cs[k] !== 'none')
        || (cs.zoom && Number(cs.zoom) !== 1)) { gaps.add('transform_or_zoom'); return finish(); }
    }
    if (vvp && Math.abs(vvp.scale - 1) > 0.001) { gaps.add('transform_or_zoom'); return finish(); }
    const cs = style(el);
    if (cs.writingMode !== 'horizontal-tb') { gaps.add('vertical_text'); return finish(); }
    const font = `${cs.fontStyle} ${cs.fontWeight} ${cs.fontSize} ${cs.fontFamily}`;
    const signature = fontProperties.map((k) => cs[k]).join('|');
    const chunks = [];
    let visited = 0;
    let characters = 0;
    const walk = (n) => {
      if (++visited > 64) { gaps.add('node_cap'); return; }
      if (n.nodeType === 3) {
        const value = n.nodeValue || '';
        characters += value.length;
        if (characters > 300) { gaps.add('text_cap'); return; }
        chunks.push(value);
        return;
      }
      if (n.nodeType !== 1) return;
      const tag = n.tagName.toLowerCase();
      if (privateControl(n)) { gaps.add('private_control'); return; }
      if (['script', 'style', 'template', 'noscript'].includes(tag) || visuallyHidden(n)) return;
      if (!(n instanceof HTMLElement) || n.shadowRoot) { gaps.add('unsupported_text'); return; }
      const ns = style(n);
      if (fontProperties.map((k) => ns[k]).join('|') !== signature) { gaps.add('mixed_font_or_style'); return; }
      if (ns.textTransform !== 'none' || !['normal', '0px'].includes(ns.letterSpacing) || !['normal', '0px'].includes(ns.wordSpacing)
        || ns.fontVariant !== 'normal' || ns.fontFeatureSettings !== 'normal' || ns.fontVariationSettings !== 'normal'
        || !['normal', '100%'].includes(ns.fontStretch) || (ns.fontSizeAdjust && ns.fontSizeAdjust !== 'none')
        || (ns.textShadow && ns.textShadow !== 'none') || parseFloat(ns.webkitTextStrokeWidth) > 0
        || ns.transform !== 'none' || ['scale', 'rotate', 'translate'].some((k) => ns[k] && ns[k] !== 'none')
        || (ns.zoom && Number(ns.zoom) !== 1)) gaps.add('unsupported_text');
      for (const pseudo of ['::before', '::after']) {
        const content = getComputedStyle(n, pseudo).content;
        if (content && !['none', 'normal', '""'].includes(content)) gaps.add('pseudo_text');
      }
      if (tag === 'br' || (n !== el && !/^inline/.test(ns.display))) chunks.push(' ');
      for (const child of n.childNodes) {
        if (visited >= 64 || characters > 300) { gaps.add(visited >= 64 ? 'node_cap' : 'text_cap'); break; }
        walk(child);
      }
      if (n !== el && !/^inline/.test(ns.display)) chunks.push(' ');
    };
    walk(el);
    const measuredText = chunks.join('').replace(/\s+/g, ' ').trim();
    if (!measuredText || measuredText !== displayedText) gaps.add('text_mismatch');
    if (gaps.size > 2) return finish();
    try {
      if (!document.fonts || document.fonts.status !== 'loaded' || !fontLoadedFor(cs, font, measuredText)) {
        gaps.add('font_not_loaded'); return finish();
      }
      if (!fontContext) fontContext = document.createElement('canvas').getContext('2d');
      if (!fontContext || !CSS.supports('font', font)) { gaps.add('canvas_unavailable'); return finish(); }
      fontContext.font = font;
      fontContext.textBaseline = 'alphabetic';
      fontContext.direction = cs.direction;
      fontContext.fontKerning = cs.fontKerning;
      const height = (value) => {
        const m = fontContext.measureText(value);
        const h = m.actualBoundingBoxAscent + m.actualBoundingBoxDescent;
        if (!Number.isFinite(h) || h <= 0 || h > 10000) throw new Error('unsupported text bounds');
        return h;
      };
      let probes = fontProbeCache.get(signature);
      if (!probes) {
        probes = { cap_H_px: height('H'), x_height_px: height('x'), body_Hg_px: height('Hg'), hangul_px: height('한') };
        fontProbeCache.set(signature, probes);
      }
      result.body_height_px = height(measuredText);
      result.probes = probes;
      result.status = 'matched_font';
    } catch (e) { gaps.add('canvas_unavailable'); }
    return finish();
  };

  // ---------- selectors
  const cssStr = (v) => String(v).replace(/\\/g, '\\\\').replace(/"/g, '\\"');
  // Each selector test queries the whole document, and one capture asks for most elements'
  // selectors twice; the DOM does not change during a capture, so each is computed once.
  const selectorCache = new Map();
  const uniqueSelector = (el) => {
    let s = selectorCache.get(el);
    if (s === undefined) {
      s = selectorOf(el);
      selectorCache.set(el, s);
    }
    return s;
  };
  const selectorOf = (el) => {
    const root = el.getRootNode();
    const q = (s) => {
      try {
        return root.querySelectorAll(s);
      } catch (e) {
        return [];
      }
    };
    const only = (s) => {
      const r = q(s);
      return r.length === 1 && r[0] === el;
    };
    const tag = el.tagName.toLowerCase();
    if (el.id) {
      const s = `#${CSS.escape(el.id)}`;
      if (only(s)) return s;
    }
    for (const attr of ['data-testid', 'data-test', 'data-qa', 'data-ergo-id', 'name', 'aria-label']) {
      const v = el.getAttribute(attr);
      if (v && v.length <= 80) {
        const s = `${tag}[${attr}="${cssStr(v)}"]`;
        if (only(s)) return s;
      }
    }
    const parts = [];
    let cur = el;
    while (cur && cur.nodeType === 1) {
      if (cur !== el && cur.id && q(`#${CSS.escape(cur.id)}`).length === 1) {
        parts.unshift(`#${CSS.escape(cur.id)}`);
        if (only(parts.join(' > '))) break;
        parts.shift();
      }
      let part = cur.tagName.toLowerCase();
      const parent = cur.parentElement;
      if (parent) {
        const same = [...parent.children].filter((c) => c.tagName === cur.tagName);
        if (same.length > 1) part += `:nth-of-type(${same.indexOf(cur) + 1})`;
      }
      parts.unshift(part);
      const s = parts.join(' > ');
      if (only(s)) return s;
      cur = parent;
    }
    return parts.join(' > ');
  };

  // ---------- candidates
  const INTERACTIVE = 'a, button, input:not([type="hidden"]), select, textarea, summary, canvas, '
    + '[role="button"], [role="link"], [role="tab"], [role="checkbox"], [role="radio"], [role="switch"], '
    + '[role="menuitem"], [role="slider"], [role="textbox"], [role="searchbox"], [role="combobox"], [role="listbox"], '
    + '[role="spinbutton"], [role="option"], [role="menuitemcheckbox"], [role="menuitemradio"], [role="treeitem"], '
    + '[role="gridcell"][tabindex], [onclick], [contenteditable=""], [contenteditable="true"]';
  const isInteractive = (el) => {
    try {
      if (el.matches(INTERACTIVE)) return true;
    } catch (e) {
      return false;
    }
    return el.hasAttribute('tabindex') && el.tabIndex >= 0;
  };
  const isDisabled = (el) => {
    try {
      return el.matches(':disabled') || el.getAttribute('aria-disabled') === 'true' || !!el.closest('[inert]');
    } catch (e) {
      return false;
    }
  };
  const ALWAYS_TEXT = new Set(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'label', 'legend', 'figcaption', 'caption']);
  const DIRECT_TEXT = new Set(['span', 'div', 'small', 'strong', 'em', 'b', 'i', 'td', 'th', 'dt', 'dd', 'blockquote', 'output', 'pre', 'code', 'section', 'article', 'header', 'footer', 'main', 'aside']);

  const all = [];
  const walk = (root) => {
    for (const el of root.querySelectorAll('*')) {
      all.push(el);
      if (el.shadowRoot) walk(el.shadowRoot);
    }
  };
  walk(document);
  for (const root of [document, ...all.map((n) => n.shadowRoot).filter(Boolean)]) {
    for (const selector of args.redactSelectors || []) {
      try { for (const node of root.querySelectorAll(selector)) privateFontNodes.add(node); } catch (e) { /* no valid selector */ }
    }
  }
  const order = new Map(all.map((el, i) => [el, i]));

  const roleMap = new Map();
  const addRole = (el, role) => {
    if (!known.has(role)) {
      unknownRoles.add(role);
      return;
    }
    if (!roleMap.has(el)) roleMap.set(el, new Set());
    roleMap.get(el).add(role);
  };
  for (const g of args.groups || []) {
    for (const h of g.handles || []) if (h && h.nodeType === 1) addRole(h, g.role);
  }
  for (const el of all) {
    const v = el.getAttribute('data-ergo-role');
    if (v) for (const r of v.split(/[\s,]+/).filter(Boolean)) addRole(el, r);
  }

  const geometry = new Map();
  const geo = (el) => {
    let g = geometry.get(el);
    if (g) return g;
    const r = el.getBoundingClientRect();
    let vis = r.width > 0 && r.height > 0;
    if (vis) {
      if (typeof el.checkVisibility === 'function') {
        vis = el.checkVisibility({ opacityProperty: true, visibilityProperty: true });
      } else {
        const cs = style(el);
        vis = cs.display !== 'none' && cs.visibility === 'visible' && parseFloat(cs.opacity) > 0;
      }
    }
    const inVp = r.width > 0 && r.height > 0 && r.right > VX0 && r.bottom > VY0 && r.left < VX1 && r.top < VY1;
    g = { r, vis, inVp };
    geometry.set(el, g);
    return g;
  };

  // Gaze uses the viewport/overflow intersection, while target-size and reach
  // retain the authored bounding box. Non-rectangular clipping stays unknown.
  const visibleBoxOf = (el) => {
    const r = geo(el).r;
    let x0 = Math.max(VX0, r.left), y0 = Math.max(VY0, r.top);
    let x1 = Math.min(VX1, r.right), y1 = Math.min(VY1, r.bottom);
    let clipped = false;
    for (let p = el; p; p = p.assignedSlot || parentOf(p)) {
      const cs = style(p);
      if ((cs.clipPath && cs.clipPath !== 'none') || (cs.clip && cs.clip !== 'auto')
        || (cs.maskImage && cs.maskImage !== 'none')
        // Individual rotate (including axis/3D forms) is separate from transform.
        || (cs.rotate && cs.rotate !== 'none')) return { visible_box: null, visible_geometry: 'unsupported' };
      if (cs.transform && cs.transform !== 'none') {
        const m = new DOMMatrixReadOnly(cs.transform);
        if (!m.is2D || Math.abs(m.b) > 1e-6 || Math.abs(m.c) > 1e-6) return { visible_box: null, visible_geometry: 'unsupported' };
      }
      if (p === el) continue; // an element's own overflow clips its children
      const clipX = ['hidden', 'clip', 'auto', 'scroll'].includes(cs.overflowX);
      const clipY = ['hidden', 'clip', 'auto', 'scroll'].includes(cs.overflowY);
      if (!clipX && !clipY) continue;
      const pr = geo(p).r;
      if (!p.offsetWidth || !p.offsetHeight) return { visible_box: null, visible_geometry: 'unsupported' };
      const sx = pr.width / p.offsetWidth, sy = pr.height / p.offsetHeight;
      const left = pr.left + p.clientLeft * sx, top = pr.top + p.clientTop * sy;
      const right = left + p.clientWidth * sx, bottom = top + p.clientHeight * sy;
      const old = [x0, y0, x1, y1];
      if (clipX) { x0 = Math.max(x0, left); x1 = Math.min(x1, right); }
      if (clipY) { y0 = Math.max(y0, top); y1 = Math.min(y1, bottom); }
      if (old.some((v, i) => v !== [x0, y0, x1, y1][i])) clipped = true;
    }
    if (x1 <= x0 || y1 <= y0) return { visible_box: null, visible_geometry: 'empty' };
    return { visible_box: { x: round2(x0), y: round2(y0), w: round2(x1 - x0), h: round2(y1 - y0) },
      visible_geometry: clipped ? 'ancestor_clipped' : 'measured' };
  };

  // Open modal layers: <dialog> opened with showModal() or a visible [aria-modal="true"].
  const modals = all.filter((el) => {
    try {
      if (el.matches(':modal')) return true;
    } catch (e) { /* :modal unsupported */ }
    if (el.getAttribute('aria-modal') !== 'true') return false;
    const g = geo(el);
    return g.vis && g.inVp;
  });
  const inertByModal = (el) => modals.length > 0 && !modals.some((m) => m === el || m.contains(el) || el.contains(m));
  // Count rendered, enabled controls by direct-child subtree, including below-fold
  // controls. The boundary describes DOM structure, not semantic alternatives.
  const siblingBranches = new WeakMap();
  for (const el of all) {
    if (!isInteractive(el) || !geo(el).vis || isDisabled(el) || inertByModal(el)) continue;
    for (let child = el, parent = el.parentElement; parent && parent !== document.body && parent !== document.documentElement; child = parent, parent = parent.parentElement) {
      if (!siblingBranches.has(parent)) siblingBranches.set(parent, new Set());
      siblingBranches.get(parent).add(child);
    }
  }
  const siblingScopes = new WeakMap();
  const siblingScope = (el) => {
    if (siblingScopes.has(el)) return siblingScopes.get(el);
    let result = { sibling_scope_id: null, sibling_scope_status: 'none' };
    for (let parent = el.parentElement; parent && parent !== document.body && parent !== document.documentElement; parent = parent.parentElement) {
      if ((siblingBranches.get(parent)?.size || 0) >= 2) {
        const selector = uniqueSelector(parent);
        result = selector && selector.length <= 256
          ? { sibling_scope_id: selector, sibling_scope_status: 'measured' }
          : { sibling_scope_id: null, sibling_scope_status: 'unavailable' };
        break;
      }
    }
    siblingScopes.set(el, result);
    return result;
  };
  // Fraction of sample points inside the visible box where another element is on top
  // (not the element, a descendant or an ancestor): a sheet, scrim or overlay.
  const occlusion = (el, r) => {
    // Hit testing cannot see elements that ignore pointer events (HUD and subtitle
    // overlays): elementFromPoint returns what lies BELOW them, so their occlusion is unknown.
    if (style(el).pointerEvents === 'none') return { fraction: null, by: null };
    const x0 = Math.max(VX0, r.left), x1 = Math.min(VX1, r.right), y0 = Math.max(VY0, r.top), y1 = Math.min(VY1, r.bottom);
    if (x1 - x0 < 1 || y1 - y0 < 1) return { fraction: null, by: null };
    const pts = [[0.5, 0.5], [0.25, 0.25], [0.75, 0.25], [0.25, 0.75], [0.75, 0.75]];
    let covered = 0;
    let by = null;
    for (const [fx, fy] of pts) {
      let top = null;
      try {
        top = document.elementFromPoint(x0 + (x1 - x0) * fx, y0 + (y1 - y0) * fy);
      } catch (e) {
        top = null;
      }
      if (!top || top === el || el.contains(top) || top.contains(el)) continue;
      // Hit testing also returns transparent layers (stretched-link ::after, click
      // catchers, input layers). Only a layer that paints, or a modal, hides the element.
      if (!paintsOver(top, el)) continue;
      covered += 1;
      if (!by) by = top;
    }
    return { fraction: covered / pts.length, by };
  };
  const paintsOver = (top, el) => {
    for (let n = top; n && !n.contains(el); n = parentOf(n)) {
      if (n.nodeType !== 1) continue;
      const tag = n.tagName.toLowerCase();
      const cs = style(n);
      if ((parseFloat(cs.opacity) || 0) <= 0.01 || cs.visibility !== 'visible') continue;
      if (tag === 'dialog' || n.getAttribute('aria-modal') === 'true') return true;
      if (MEDIA.has(tag)) return true;
      // A background clipped to the text paints the glyphs, not a box.
      if (cs.backgroundClip === 'text' || cs.webkitBackgroundClip === 'text') continue;
      if (cs.backgroundImage && cs.backgroundImage !== 'none') return true;
      const bg = parseColor(cs.backgroundColor);
      if (bg && bg.a > 0.05) return true;
    }
    return false;
  };

  // Bounded solid-paint evidence, not a general rendering model. CSS `color` is
  // What covers an element: the nearest fixed or sticky layer (scrolling moves content
  // under it) or a box in the normal layout (nothing moves it away), and whether it is
  // a dialog, popup or large overlay that covers content on purpose.
  const OVERLAY_ROLES = new Set(['dialog', 'alertdialog', 'tooltip', 'menu', 'listbox', 'status', 'alert']);
  const occluderOf = (top, el) => {
    let layer = top;
    let position = 'flow';
    let overlay = false;
    for (let n = top; n && n.nodeType === 1 && !n.contains(el); n = parentOf(n)) {
      const tag = n.tagName.toLowerCase();
      if (tag === 'dialog' || n.getAttribute('aria-modal') === 'true' || OVERLAY_ROLES.has((n.getAttribute('role') || '').trim())) overlay = true;
      const p = style(n).position;
      if (position === 'flow' && (p === 'fixed' || p === 'sticky')) {
        position = p;
        layer = n;
      }
    }
    const b = layer.getBoundingClientRect();
    if (b.width * b.height >= 0.4 * vw * vh) overlay = true;
    // Scrolling can move the covered text out from under a fixed or sticky bar only in
    // the box that scrolls it: an inner scroll container, or else the page.
    let scroller = null;
    for (let n = parentOf(el); n && n.nodeType === 1 && n !== document.body && n !== document.documentElement; n = parentOf(n)) {
      const oy = style(n).overflowY;
      if ((oy === 'auto' || oy === 'scroll') && n.scrollHeight > n.clientHeight + 1) {
        scroller = { top: round2(n.scrollTop), max: round2(n.scrollHeight - n.clientHeight), inner: true };
        break;
      }
    }
    if (!scroller) {
      const se = document.scrollingElement || document.documentElement;
      scroller = { top: round2(window.scrollY), max: round2(Math.max(0, se.scrollHeight - window.innerHeight)), inner: false };
    }
    return { position, overlay, selector: uniqueSelector(layer), scroller,
      box: { x: round2(b.left), y: round2(b.top), w: round2(b.width), h: round2(b.height) } };
  };

  // included only when a text node actually occupies a rendered glyph box.
  const paintFor = (el) => {
    const parts = [];
    const gaps = new Set();
    if (!geo(el).vis) return { source: 'dom-solid-v1', parts, gaps: [], decorative: false };
    const graphic = ['switch', 'slider', 'checkbox', 'radio', 'status', 'alert'].includes(roleOf(el))
      || [...(roleMap.get(el) || [])].some((r) => ['status', 'error_message', 'critical_message'].includes(r));
    if (!isInteractive(el) && el.closest('[aria-hidden="true"], [role="presentation"], [role="none"]')) {
      return { source: 'dom-solid-v1', parts, gaps: [], decorative: true };
    }
    const symbolOnly = /^[\s×✕✗✓✔+−\-→←↑↓⋯…☰]*$/.test(visibleText(el));
    const scanChildren = graphic || (isInteractive(el) && (!visibleText(el) || symbolOnly || a11yOf(el).icon_font));
    let visited = 0;
    const add = (node, key, kind, color, background, shape = null) => {
      if (parts.length >= 16) { gaps.add('part_cap'); return; }
      const r = geo(node).r;
      if (!color || !background) { gaps.add('unknown_background'); return; }
      parts.push({ key, kind, color: hex(color), background: hex(background), shape,
        box: { x: round2(r.left), y: round2(r.top), w: round2(r.width), h: round2(r.height) } });
    };
    const walkPaint = (node, key) => {
      if (++visited > 64) { gaps.add('node_cap'); return; }
      if (node !== el && isInteractive(node)) return; // another control owns its paint
      if (!geo(node).vis) return;
      const cs = style(node);
      const tag = node.tagName.toLowerCase();
      if (['style', 'script', 'title', 'desc', 'defs'].includes(tag)) return;
      const r = geo(node).r;
      for (let p = parentOf(node); p; p = parentOf(p)) {
        const ps = style(p), pr = geo(p).r;
        const clipX = ['hidden', 'clip'].includes(ps.overflowX), clipY = ['hidden', 'clip'].includes(ps.overflowY);
        if ((clipX && (r.right <= pr.left || r.left >= pr.right)) || (clipY && (r.bottom <= pr.top || r.top >= pr.bottom))) return;
        if ((clipX && (r.left < pr.left || r.right > pr.right)) || (clipY && (r.top < pr.top || r.bottom > pr.bottom))) {
          gaps.add('clipped_paint'); return;
        }
      }
      const cover = geo(node).inVp ? occlusion(node, r).fraction : null;
      if (cover === 1) return;
      if (cover > 0) { gaps.add('occluded_paint'); return; }
      if (node.shadowRoot) gaps.add('shadow_paint');
      for (const pseudo of ['::before', '::after']) {
        const ps = getComputedStyle(node, pseudo);
        if (ps.display !== 'none' && ps.visibility === 'visible' && ps.content && !['none', 'normal'].includes(ps.content)) gaps.add('pseudo_paint');
      }
      for (let p = node; p; p = parentOf(p)) {
        const ps = style(p);
        if ((ps.filter && ps.filter !== 'none') || (ps.mixBlendMode && ps.mixBlendMode !== 'normal')
          || (ps.maskImage && ps.maskImage !== 'none') || (ps.clipPath && ps.clipPath !== 'none')) {
          gaps.add('unsupported_effect'); return;
        }
      }
      if (node === el && ['input', 'select'].includes(tag) && cs.appearance !== 'none'
        && (tag === 'select' || ['checkbox', 'radio', 'range', 'color', 'file'].includes(node.type))) {
        gaps.add('native_appearance'); return;
      }
      const svgShape = node instanceof SVGElement && ['rect', 'circle', 'ellipse', 'path', 'polygon', 'polyline', 'line'].includes(tag);
      const colors = colorsFor(node, geo(node).r, cs, node instanceof SVGElement);
      if (svgShape) {
        const attributes = { rect: ['x', 'y', 'width', 'height', 'rx', 'ry'], circle: ['cx', 'cy', 'r'],
          ellipse: ['cx', 'cy', 'rx', 'ry'], line: ['x1', 'y1', 'x2', 'y2'], path: ['d'], polygon: ['points'], polyline: ['points'] }[tag];
        const geometry = [];
        let validGeometry = true;
        for (const attr of attributes) {
          const value = (node.getAttribute(attr) || '').trim();
          if (attr === 'd' || attr === 'points') {
            const allowed = attr === 'd' ? /^[MmLlHhVvCcSsQqTtAaZzEe\d+.,\s-]+$/ : /^[Ee\d+.,\s-]+$/;
            if (!value || value.length > 400 || !allowed.test(value)) { validGeometry = false; break; }
            const numbers = value.match(/[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?/g) || [];
            if (!numbers.length || numbers.some((v) => !Number.isFinite(Number(v)) || Math.abs(Number(v)) > 1e6)) { validGeometry = false; break; }
            if (attr === 'points' && (numbers.length % 2 || numbers.length < (tag === 'polygon' ? 6 : 4))) { validGeometry = false; break; }
            if (attr === 'd') {
              const tokens = value.match(/[MmLlHhVvCcSsQqTtAaZz]|[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?/g) || [];
              const arity = { m: 2, l: 2, h: 1, v: 1, c: 6, s: 4, q: 4, t: 2, a: 7, z: 0 };
              let command = null, count = 0;
              validGeometry = /^[Mm]/.test(tokens[0] || '') && value.replace(/[MmLlHhVvCcSsQqTtAaZz]|[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?/g, '').replace(/[\s,]/g, '') === '';
              for (const token of tokens) {
                if (token.toLowerCase() in arity) {
                  if (command && arity[command] && (!count || count % arity[command])) validGeometry = false;
                  command = token.toLowerCase(); count = 0;
                } else {
                  if (!command || !arity[command] || (command === 'a' && [3, 4].includes(count % 7) && ![0, 1].includes(Number(token)))) validGeometry = false;
                  count++;
                }
              }
              if (command && arity[command] && (!count || count % arity[command])) validGeometry = false;
              if (!validGeometry) break;
            }
            geometry.push(value.replace(/[\s,]+/g, ' '));
          } else {
            const numeric = value ? Number(value) : 0;
            if ((value && !/^[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?$/.test(value)) || !Number.isFinite(numeric) || Math.abs(numeric) > 1e6
              || (['width', 'height', 'r', 'rx', 'ry'].includes(attr) && numeric < 0)) { validGeometry = false; break; }
            geometry.push(String(numeric));
          }
        }
        const signature = [tag, ...geometry].join('|');
        if (!validGeometry || signature.length > 512 || node.closest('svg')?.querySelector('use, image, foreignObject')) {
          gaps.add('unsupported_svg'); return;
        }
        for (const channel of ['fill', 'stroke']) {
          if (cs[channel] === 'none' || (channel === 'stroke' && !(parseFloat(cs.strokeWidth) > 0))) continue;
          if (!cs[channel] || /url\(/.test(cs[channel])) { gaps.add('unsupported_svg'); continue; }
          const parsed = parseColor(cs[channel]);
          if (!parsed || parsed.a <= 0) continue;
          const raw = { ...parsed };
          raw.a *= parseFloat(cs[channel === 'fill' ? 'fillOpacity' : 'strokeOpacity']);
          if (raw.a > 0) add(node, `${key}:${channel}`, 'graphic', colors?.composite(raw), colors?.bg, signature);
        }
      } else if (!(node instanceof SVGElement)) {
        const rawBg = parseColor(cs.backgroundColor);
        const hasText = hasDirectText(node);
        if (cs.backgroundImage && cs.backgroundImage !== 'none') gaps.add('unknown_background');
        // Label wrappers are not state-indicator parts. Their own text is extracted
        // separately; textless track/thumb boxes supply the graphical channels.
        if (node === el || !hasText) {
          if (rawBg && rawBg.a > 0) add(node, `${key}:fill`, 'boundary', colors?.bg, colors?.container);
          const border = borderFor(cs, null);
          if (border.raw) add(node, `${key}:border`, 'boundary', colors?.composite(border.raw), colors?.container);
        }
        if (hasText && parseFloat(cs.fontSize) > 0 && (parseColor(cs.color)?.a || 0) > 0) {
          let glyph = false;
          for (const child of node.childNodes) {
            if (child.nodeType !== 3 || !child.nodeValue.trim()) continue;
            const range = document.createRange(); range.selectNodeContents(child);
            if ([...range.getClientRects()].some((r) => r.width > 0 && r.height > 0)) { glyph = true; break; }
          }
          if (glyph) add(node, `${key}:text`, 'text', colors?.fg, colors?.bg);
        }
      } else if (tag !== 'svg' && !svgShape) gaps.add('unsupported_svg');
      if (!scanChildren) return;
      let i = 0;
      for (const child of node.children) {
        if (visited >= 64) { gaps.add('node_cap'); break; }
        walkPaint(child, `${key}/${i++}`);
      }
    };
    walkPaint(el, 'self');
    if (graphic && !parts.some((p) => p.kind !== 'text') && !gaps.size) gaps.add('no_graphic_paint');
    return { source: 'dom-solid-v1', parts, gaps: [...gaps].sort(), decorative: false };
  };

  const candidates = [];
  for (const el of all) {
    const tag = el.tagName.toLowerCase();
    if (['script', 'style', 'template', 'noscript', 'head', 'meta', 'link', 'title', 'html', 'body', 'br', 'option'].includes(tag)) continue;
    const tagged = roleMap.has(el);
    const interactive = isInteractive(el);
    const explicitRole = (el.getAttribute('role') || '').trim();
    const alertStatus = explicitRole === 'alert' || explicitRole === 'status';
    let group = -1;
    if (tagged) group = 0;
    else if (interactive) group = 1;
    else if (alertStatus) group = 2;
    else if ((ALWAYS_TEXT.has(tag) || DIRECT_TEXT.has(tag)) && hasDirectText(el)) {
      // Only elements that own a text node: a <li> whose text sits in a child button
      // would otherwise report the child's text with its own (inherited) font size.
      const host = el.parentElement ? el.parentElement.closest(INTERACTIVE) : null;
      if (host) continue; // text inside a control is reported through the control
      group = 3;
    }
    if (group < 0) continue;
    const g = geo(el);
    if (group === 3 && (!g.vis || !text(el))) continue;
    const visRank = g.vis && g.inVp ? 0 : (g.vis ? 1 : 2);
    candidates.push({ el, group, visRank, interactive, order: order.get(el) });
  }

  // Hotspots: page-provided (live) boxes win over scenario-declared ones.
  let pageHotspotError = null;
  const spots = new Map();
  const addSpot = (h, source) => {
    if (!h || typeof h !== 'object' || typeof h.id !== 'string' || !h.id || h.id.length > 128) return false;
    const b = h.box;
    if (!b || ![b.x, b.y, b.w, b.h].every((n) => typeof n === 'number' && Number.isFinite(n)) || b.w < 0 || b.h < 0) return false;
    const prev = spots.get(h.id);
    const roles = new Set(prev ? prev.roles : []);
    for (const r of Array.isArray(h.roles) ? h.roles : []) {
      if (typeof r === 'string') {
        if (known.has(r)) roles.add(r);
        else unknownRoles.add(r);
      }
    }
    spots.set(h.id, {
      id: h.id,
      name: typeof h.name === 'string' ? h.name.slice(0, 200) : (prev ? prev.name : h.id),
      box: { x: b.x, y: b.y, w: b.w, h: b.h },
      roles,
      visible: h.visible === false ? false : true,
      enabled: h.enabled === false ? false : true,
      origin: source,
    });
    return true;
  };
  for (const h of args.hotspots || []) addSpot(h, 'scenario');
  try {
    const api = window.__ergoqa__;
    if (api && typeof api.hotspots === 'function') {
      const list = api.hotspots();
      if (Array.isArray(list)) {
        const live = new Set();
        for (const h of list.slice(0, 200)) {
          if (!addSpot(h, 'page')) pageHotspotError = 'some page hotspots were malformed and skipped';
          else live.add(h.id);
        }
        // The page reports its live hotspots; a scenario fallback it does not list is not
        // on screen in this state (e.g. attack/jump on a menu screen).
        for (const s of spots.values()) if (s.origin === 'scenario' && !live.has(s.id)) s.visible = false;
      } else {
        pageHotspotError = 'window.__ergoqa__.hotspots() did not return an array';
      }
    }
  } catch (e) {
    pageHotspotError = `window.__ergoqa__.hotspots() threw: ${String(e && e.message || e).slice(0, 200)}`;
  }
  for (const [id, roles] of Object.entries(args.hotspotRoles || {})) {
    const s = spots.get(id);
    if (s) for (const r of roles) if (known.has(r)) s.roles.add(r);
  }

  // What is on screen comes first: a long page's off-screen controls must not crowd
  // visible text out of the cap (truncation is reported with the snapshot).
  candidates.sort((a, b) => a.visRank - b.visRank || a.group - b.group || a.order - b.order);
  const cap = Math.max(0, (args.cap || 400) - spots.size);
  const kept = candidates.slice(0, cap).sort((a, b) => a.order - b.order);

  const ids = new WeakMap();
  const elements = [];
  const recordOf = new Map();
  let n = 0;
  for (const c of kept) {
    const el = c.el;
    const id = `el-${++n}`;
    ids.set(el, id);
    const g = geo(el);
    const cs = style(el);
    const tag = el.tagName.toLowerCase();
    const colors = colorsFor(el, g.r, cs);
    const fgRaw = parseColor(cs.color);
    const isControl = ['input', 'select', 'textarea', 'button'].includes(tag)
      || ['button', 'textbox', 'combobox', 'checkbox', 'radio', 'switch', 'searchbox', 'slider'].includes(roleOf(el));
    const border = isControl ? borderFor(cs, colors ? colors.container || colors.bg : null) : { color: null, width: 0 };
    let cumOpacity = 1;
    for (let p = el; p; p = parentOf(p)) cumOpacity *= parseFloat(style(p).opacity);
    const disabled = isDisabled(el);
    const fw = parseInt(cs.fontWeight, 10);
    const fs = parseFloat(cs.fontSize);
    const displayedText = visibleText(el);
    elements.push({
      id,
      role: roleOf(el),
      name: accName(el).slice(0, 300),
      text: displayedText,
      tag,
      selector: uniqueSelector(el),
      dom_id: el.id ? String(el.id).slice(0, 120) : null,
      box: { x: round2(g.r.left), y: round2(g.r.top), w: round2(g.r.width), h: round2(g.r.height) },
      ...visibleBoxOf(el),
      interactive: c.interactive,
      visible: g.vis,
      enabled: !disabled,
      in_viewport: g.inVp,
      font_size_px: Number.isFinite(fs) ? round2(fs) : null,
      font_weight: Number.isFinite(fw) ? Math.max(1, Math.min(1000, fw)) : null,
      font_metrics: fontMetricsFor(el, displayedText),
      color_fg: colors ? hex(colors.fg) : hex(fgRaw),
      color_bg: colors ? hex(colors.bg) : null,
      container_bg: colors && colors.container ? hex(colors.container) : null,
      border_color: border.color,
      border_width_px: border.width,
      opacity: Math.round(cumOpacity * 1000) / 1000,
      paint: paintFor(el),
      // Associated <label> boxes accept the same click (HTML activation behaviour),
      // so they are part of the control's target (WCAG 2.5.8 "target").
      ...(() => {
        if (!el.labels || !el.labels.length) return {};
        const boxes = [];
        for (const lab of el.labels) {
          const lr = lab.getBoundingClientRect();
          if (lr.width > 0 && lr.height > 0) boxes.push({ x: round2(lr.left), y: round2(lr.top), w: round2(lr.width), h: round2(lr.height) });
        }
        return boxes.length ? { hit_boxes: boxes.slice(0, 4) } : {};
      })(),
      ...(() => {
        const o = g.vis && g.inVp ? occlusion(el, g.r) : { fraction: null, by: null };
        return {
          occluded_fraction: o.fraction,
          occluded_by: o.by ? uniqueSelector(o.by) : null,
          ...(o.by && o.fraction > 0 ? { occluder: occluderOf(o.by, el) } : {}),
          inert_by_modal: inertByModal(el),
        };
      })(),
      ...(c.interactive || ['input', 'select', 'textarea'].includes(tag) ? { a11y: a11yOf(el) } : {}),
      ...(() => {
        const direct = hasDirectText(el);
        const clip = (direct ? clippedOf(el, cs, c.interactive) : null) || (c.interactive ? labelClip(el) : null);
        // Text that paints nothing is marked so box-sampled covering skips it (LY-02).
        return { ...(clip ? { clipped: clip } : {}), ...(textInk(el, c.interactive) === false ? { ink: false } : {}) };
      })(),
      roles: roleMap.has(el) ? [...roleMap.get(el)].sort() : [],
      // Ids of the nearest ancestors (grouping context such as a toolbar or chip row).
      ancestor_ids: (() => {
        const ids = [];
        for (let p = el.parentElement; p && ids.length < 3; p = p.parentElement) {
          if (p.id && p !== document.body && p !== document.documentElement) ids.push(p.id);
        }
        return ids;
      })(),
      ...siblingScope(el),
      source: 'dom',
    });
    recordOf.set(el, elements[elements.length - 1]);
  }
  for (const s of spots.values()) {
    const b = s.box;
    const inVp = b.w > 0 && b.h > 0 && b.x + b.w > 0 && b.y + b.h > 0 && b.x < vw && b.y < vh;
    elements.push({
      id: `hs-${s.id.replace(/[^A-Za-z0-9._-]/g, '_')}`,
      role: 'hotspot',
      name: s.name || s.id,
      text: '',
      tag: 'hotspot',
      selector: `hotspot:${s.id}`,
      box: { x: round2(b.x), y: round2(b.y), w: round2(b.w), h: round2(b.h) },
      interactive: true,
      visible: s.visible,
      enabled: s.enabled,
      in_viewport: inVp,
      font_size_px: null,
      font_weight: null,
      color_fg: null,
      color_bg: null,
      border_color: null,
      roles: [...s.roles].sort(),
      source: 'manual',
      hotspot_origin: s.origin,
    });
  }
  // ---------- rendered layout: overlapping text, near-miss alignment, uneven spacing
  // Text drawn over other text: lines of one element whose glyph bands cross (a line
  // height far below the font size) or two elements whose glyph bands cross (a negative
  // margin, an absolutely placed label). The band is the middle 0.8 em of each line box,
  // so ordinary tight headings do not count. Pairs in different fixed or sticky layers
  // are left to the covered-text record, which knows whether scrolling moves them apart.
  const fixedHost = (el) => {
    for (let n = el; n && n.nodeType === 1; n = parentOf(n)) {
      const p = style(n).position;
      if (p === 'fixed' || p === 'sticky') return n;
    }
    return null;
  };
  const bandsOf = (el, rects) => {
    const fs = parseFloat(style(el).fontSize) || 16;
    return rects.map((r) => {
      const h = Math.min(r.height, 0.8 * fs);
      const top = r.top + (r.height - h) / 2;
      return { left: r.left, right: r.right, top, bottom: top + h };
    });
  };
  const crossing = (a, b) => {
    const ix = Math.min(a.right, b.right) - Math.max(a.left, b.left);
    const iy = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
    return ix >= 6 && iy >= 1 ? iy : 0;
  };
  const texts = [];
  for (const c of kept) {
    const el = c.el;
    const g = geo(el);
    if (!g.vis || !g.inVp) continue;
    // The text an element owns; a control also owns the words its spans draw
    // (labelHolders), which are reported through the control. Each glyph box keeps the
    // element that paints it.
    const owned = [];
    if (hasDirectText(el)) {
      for (const q of ownTextRects(el)) owned.push({ rect: q, holder: el });
    }
    if (c.interactive) {
      for (const holder of labelHolders(el)) {
        for (const q of ownTextRects(holder)) if (owned.length < 24) owned.push({ rect: q, holder });
      }
    }
    const shown = owned.filter(({ rect, holder }) => rect.width >= 2 && rect.height >= 4
      && rect.bottom > VY0 && rect.top < VY1 && rect.right > VX0 && rect.left < VX1 && paintsInk(holder));
    if (!shown.length) continue;
    const rects = shown.map((o) => o.rect);
    // Each line's band follows the font size of the element that draws it.
    texts.push({ el, rects, holders: shown.map((o) => o.holder), bands: shown.map((o) => bandsOf(o.holder, [o.rect])[0]),
      host: fixedHost(el), direct: hasDirectText(el) });
  }
  const overlapOf = new Map();
  for (const t of texts) {
    if (!t.direct) continue;
    const lines = t.bands.map((b, i) => ({ b, top: t.rects[i].top })).sort((p, q) => p.top - q.top);
    for (let i = 1; i < lines.length; i++) {
      if (Math.abs(lines[i].top - lines[i - 1].top) < 1) continue; // same line
      const amount = crossing(lines[i - 1].b, lines[i].b);
      if (amount) {
        overlapOf.set(t.el, { kind: 'lines', with: null, overlap_px: round2(amount) });
        break;
      }
    }
  }
  // Two texts collide only when both stay visible: where the upper one sits on a painted
  // box (a sheet, toast, keypad or card background), the lower text is covered instead,
  // which the covered-text record judges with its reach and overlay rules.
  for (let i = 0; i < texts.length; i++) {
    for (let j = i + 1; j < texts.length; j++) {
      const a = texts[i];
      const b = texts[j];
      // A control's label spans count as its text (they are not candidates of their own).
      if (a.host !== b.host || a.el.contains(b.el) || b.el.contains(a.el)) continue;
      let amount = 0;
      let spot = null;
      for (const p of a.bands) {
        for (const q of b.bands) {
          const v = crossing(p, q);
          if (v > amount) {
            amount = v;
            spot = { x: (Math.max(p.left, q.left) + Math.min(p.right, q.right)) / 2, y: (Math.max(p.top, q.top) + Math.min(p.bottom, q.bottom)) / 2 };
          }
        }
      }
      if (!amount || spot.x < VX0 || spot.y < VY0 || spot.x >= VX1 || spot.y >= VY1) continue;
      let top = null;
      try {
        top = document.elementFromPoint(spot.x, spot.y);
      } catch (e) {
        top = null;
      }
      const upper = top && (a.el === top || a.el.contains(top)) ? a : top && (b.el === top || b.el.contains(top)) ? b : null;
      if (!upper) continue; // a third layer is on top: covered, not colliding
      const lower = upper === a ? b : a;
      if (paintsOver(top, lower.el)) continue;
      const later = a.el.compareDocumentPosition(b.el) & Node.DOCUMENT_POSITION_FOLLOWING ? b : a;
      const other = later === a ? b : a;
      if (!overlapOf.has(later.el)) overlapOf.set(later.el, { kind: 'element', with: uniqueSelector(other.el), overlap_px: round2(amount) });
    }
  }
  for (const [el, v] of overlapOf) {
    const rec = recordOf.get(el);
    if (rec) rec.text_overlap = v;
  }

  // Glyphs under a painted box: five points across the middle of every visible line.
  // The element box sampling above misses a ribbon over one word or a callout pulled
  // over a paragraph's last line; a line counts as covered when two of its five points
  // (about 40 % of it) are under a painted box that neither contains nor sits inside
  // the text.
  for (const t of texts) {
    let points = 0;
    let hidden = 0;
    let lines = 0;
    let cover = null;
    t.bands.forEach((band, i) => {
      const holder = t.holders[i];
      const y = (band.top + band.bottom) / 2;
      let onLine = 0;
      for (const fx of [0.1, 0.3, 0.5, 0.7, 0.9]) {
        const x = band.left + (band.right - band.left) * fx;
        if (x < VX0 || y < VY0 || x >= VX1 || y >= VY1) continue;
        points += 1;
        let top = null;
        try {
          top = document.elementFromPoint(x, y);
        } catch (e) {
          top = null;
        }
        if (!top || top === holder || holder.contains(top) || top.contains(holder) || !paintsOver(top, holder)) continue;
        hidden += 1;
        onLine += 1;
        if (!cover) cover = occluderOf(top, holder);
      }
      if (onLine >= 2) lines += 1;
    });
    if (cover && lines) {
      const rec = recordOf.get(t.el);
      if (rec) rec.glyph_cover = { fraction: round2(hidden / Math.max(1, points)), lines_covered: lines, lines: t.bands.length, ...cover };
    }
  }

  // Siblings meant to line up: three or more same-kind blocks stacked in a column (where
  // their text starts) or set side by side in a row (their top edges). One block 1.5-8
  // px off while the rest agree is a near-miss; in a column of four or more, one gap
  // that differs from the others by at least 4 px and 25 % is uneven rhythm. Recorded
  // as candidates with the outlier's selector; the analyser rates them P3.
  const layoutOutliers = [];
  const firstGlyphLeft = (el) => {
    const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    for (let node = walker.nextNode(); node; node = walker.nextNode()) {
      if (!node.nodeValue.trim()) continue;
      const host = node.parentElement;
      if (!host || !geo(host).vis) continue;
      if (['center', 'right', 'end', 'justify'].includes(style(host).textAlign)) return null;
      const range = document.createRange();
      range.selectNodeContents(node);
      const r = [...range.getClientRects()].find((q) => q.width > 0 && q.height > 0);
      return r ? r.left : null;
    }
    return null;
  };
  const contentLeft = (el) => {
    const glyph = firstGlyphLeft(el);
    if (glyph !== null) return glyph;
    const cs = style(el);
    return el.getBoundingClientRect().left + (parseFloat(cs.borderLeftWidth) || 0) + (parseFloat(cs.paddingLeft) || 0);
  };
  // Same component: list items and table rows by tag; other blocks by a shared class,
  // or by classes that differ only in modifiers (`card` and `card--new`).
  const LIST_ITEMS = new Set(['LI', 'TR', 'DT', 'DD']);
  const sameKind = (a, b) => {
    if (a.tagName !== b.tagName) return false;
    if (LIST_ITEMS.has(a.tagName)) return true;
    const base = (el) => new Set([...el.classList].filter((c) => !/--|^is-|^has-/.test(c)));
    const ca = base(a);
    const cb = base(b);
    return (!ca.size && !cb.size) || [...ca].some((c) => cb.has(c));
  };
  const modeOf = (values, tolerance) => {
    let best = null;
    for (const v of values) {
      const agree = values.filter((w) => Math.abs(w - v) <= tolerance).length;
      if (!best || agree > best.agree) best = { value: v, agree };
    }
    return best;
  };
  const textOf = (el) => (el.innerText || el.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 60);
  const boxOf = (el) => {
    const b = el.getBoundingClientRect();
    return { x: round2(b.left), y: round2(b.top), w: round2(b.width), h: round2(b.height) };
  };
  const containers = new Set();
  for (const c of kept) {
    for (let n = parentOf(c.el), i = 0; n && n.nodeType === 1 && i < 4; n = parentOf(n), i++) containers.add(n);
  }
  for (const box of containers) {
    const kids = [...box.children].filter((k) => {
      if (['script', 'style', 'template', 'br', 'hr'].includes(k.tagName.toLowerCase())) return false;
      const cs = style(k);
      if (!['static', 'relative'].includes(cs.position) || cs.display === 'contents' || cs.float !== 'none') return false;
      // Off-screen members still set the rule (a long list never fits one screen);
      // an outlier is reported only from a screen that shows it.
      const g = geo(k);
      return g.vis && g.r.height > 2 && g.r.width > 2;
    });
    if (kids.length < 3) continue;
    const groups = [];
    for (const k of kids) {
      const g = groups.find((list) => sameKind(list[0], k));
      if (g) g.push(k); else groups.push([k]);
    }
    for (const group of groups) {
      if (group.length < 3) continue;
      const rs = group.map((k) => geo(k).r);
      const column = rs.every((r, i) => i === 0 || r.top >= rs[i - 1].bottom - 1);
      const row = !column && rs.every((r, i) => i === 0 || (r.left >= rs[i - 1].right - 1 && r.top < rs[i - 1].bottom && r.bottom > rs[i - 1].top));
      if (!column && !row) continue;
      // A row lines up on the edge its container aligns: centres for align-items
      // center, bottoms for end; baseline rows depend on text and are skipped.
      const align = style(box).alignItems;
      if (row && align === 'baseline') continue;
      const values = column ? group.map(contentLeft) : rs.map((r) => (align === 'center' ? (r.top + r.bottom) / 2
        : ['flex-end', 'end'].includes(align) ? r.bottom : r.top));
      const mode = modeOf(values, 0.75);
      if (mode && mode.agree >= group.length - 1 && mode.agree >= 2) {
        const off = group.map((k, i) => ({ k, d: values[i] - mode.value })).filter((o) => Math.abs(o.d) > 0.75);
        if (off.length === 1 && Math.abs(off[0].d) >= 1.5 && Math.abs(off[0].d) <= 8 && geo(off[0].k).inVp) {
          layoutOutliers.push({ kind: 'alignment', axis: column ? 'x' : 'y', selectors: [uniqueSelector(off[0].k)],
            container: uniqueSelector(box), offset_px: round2(off[0].d), group_size: group.length,
            text: textOf(off[0].k), box: boxOf(off[0].k) });
        }
      }
      if (column && group.length >= 4) {
        const gaps = rs.slice(1).map((r, i) => r.top - rs[i].bottom);
        const typical = modeOf(gaps, 1);
        if (typical && typical.agree >= gaps.length - 1 && typical.agree >= 2) {
          const odd = gaps.map((v, i) => ({ v, i })).filter((o) => Math.abs(o.v - typical.value) > 1);
          // Only a squeezed gap: a wider one often separates groups on purpose (a divider
          // between sections of a menu or form), which needs the design rule to judge.
          const off = odd.length === 1 ? odd[0].v - typical.value : 0;
          const uneven = off < 0 && -off >= 4 && -off >= 0.25 * typical.value;
          if (odd.length === 1 && uneven) {
            const before = group[odd[0].i];
            const after = group[odd[0].i + 1];
            if (geo(before).inVp && geo(after).inVp) layoutOutliers.push({ kind: 'spacing', axis: 'y', selectors: [uniqueSelector(before), uniqueSelector(after)],
              container: uniqueSelector(box), gap_px: round2(odd[0].v), typical_px: round2(typical.value), group_size: group.length,
              text: textOf(after), box: boxOf(after) });
          }
        }
      }
    }
  }

  // Smaller misplacements that eyes skip. An icon, image or symbol that is the only visible
  // content of a control and sits 2 px or more off the control's centre while the box leaves
  // room to centre it (icon_offset, LY-06); content flush against one side of a much wider
  // box is a designed alignment and is skipped. A field and the painted button or addon
  // attached to it (gap of at most 1.5 px) whose top or bottom edges differ by 2 px or more
  // (attached_mismatch, LY-07). A page that runs past the screen (LY-08): content wider than
  // the screen (page_overflow), or a full-height layout that scrolls 1 to 80 px
  // (scroll_slack).
  {
    const LETTER = /[\p{L}\p{N}]/u;
    const inView = (r) => r.right > VX0 && r.bottom > VY0 && r.left < VX1 && r.top < VY1;
    const helperText = (e) => {
      const r = geo(e).r;
      const cs = style(e);
      return (r.width <= 2 && r.height <= 2) || (cs.clip && cs.clip !== 'auto') || /inset\(50%/.test(cs.clipPath || '');
    };
    const shownContent = (v) => !!v && v !== 'none' && v !== 'normal' && v !== '""' && v !== "''";
    // A glyph's ink, from the canvas text metrics of its font: the text box of "+" or "×" is
    // the font's full height, often taller than a small button, while the ink is what the
    // eye centres. Null when the run wraps or the metrics are missing (the text box stands in).
    let inkCtx = null;
    const glyphInk = (t, host) => {
      const v = t.nodeValue;
      const i0 = v.search(/\S/);
      const i1 = v.replace(/\s+$/, '').length;
      if (i0 < 0) return null;
      const range = document.createRange();
      range.setStart(t, i0);
      range.setEnd(t, i1);
      const qs = [...range.getClientRects()].filter((q) => q.width > 0 && q.height > 0);
      if (qs.length !== 1) return qs.length ? { boxes: qs, ink: false } : null;
      const q = qs[0];
      try {
        inkCtx = inkCtx || document.createElement('canvas').getContext('2d');
        const cs = style(host);
        inkCtx.font = cs.fontStyle + ' ' + cs.fontWeight + ' ' + cs.fontSize + ' ' + cs.fontFamily;
        const m = inkCtx.measureText(v.slice(i0, i1));
        const fa = m.fontBoundingBoxAscent;
        const fd = m.fontBoundingBoxDescent;
        if (!(fa + fd > 0) || !(m.width > 0) || !Number.isFinite(m.actualBoundingBoxAscent)) return { boxes: qs, ink: false };
        const ky = q.height / (fa + fd);
        const kx = q.width / m.width;
        const base = q.top + fa * ky;
        const ink = { left: q.left - m.actualBoundingBoxLeft * kx, right: q.left + m.actualBoundingBoxRight * kx,
          top: base - m.actualBoundingBoxAscent * ky, bottom: base + m.actualBoundingBoxDescent * ky };
        if (!(ink.right - ink.left > 0.5) || !(ink.bottom - ink.top > 0.5)) return { boxes: qs, ink: false };
        return { boxes: [ink], ink: true };
      } catch (e) {
        return { boxes: qs, ink: false };
      }
    };
    // The content of an icon-only control: letterless glyphs (by their ink), images, SVG,
    // icon-font marks drawn by ::before or ::after, and empty boxes painted with a
    // background image (a chevron or close sprite). Null for a labelled control or a group.
    const iconBoxes = (ctl) => {
      const found = [];
      let inked = true;
      let inkedX = true;
      const walker = document.createTreeWalker(ctl, NodeFilter.SHOW_TEXT);
      for (let t = walker.nextNode(); t; t = walker.nextNode()) {
        const s = t.nodeValue.trim();
        if (!s) continue;
        const host = t.parentElement;
        if (!host || !geo(host).vis || helperText(host)) continue;
        if (LETTER.test(s)) return null; // a label: the control is not icon-only
        const glyph = glyphInk(t, host);
        if (!glyph) continue;
        found.push(...glyph.boxes);
        inked = inked && glyph.ink;
      }
      for (const e of ctl.querySelectorAll('*')) {
        if (!geo(e).vis || helperText(e)) continue;
        if (isInteractive(e)) return null; // a group of controls
        if (MEDIA.has(e.localName)) {
          found.push(geo(e).r);
          inked = false;
          inkedX = false;
          continue;
        }
        if (e.textContent.trim()) continue;
        const cs = style(e);
        const er = geo(e).r;
        const bordered = !e.children.length && er.width <= 24 && er.height <= 24
          && ['Top', 'Right', 'Bottom', 'Left'].some((side) => (parseFloat(cs['border' + side + 'Width']) || 0) > 0 && cs['border' + side + 'Style'] !== 'none');
        if (shownContent(getComputedStyle(e, '::before').content) || shownContent(getComputedStyle(e, '::after').content)
          || (cs.backgroundImage && cs.backgroundImage !== 'none' && !e.children.length) || bordered) {
          found.push(er); // an icon-font glyph, a drawn mark (a border caret) or a sprite
          inkedX = false;
          inked = false;
        }
      }
      return found.length ? { boxes: found, inked, inkedX: inked && inkedX } : null;
    };
    const unionOf = (rs) => ({ l: Math.min(...rs.map((q) => q.left)), t: Math.min(...rs.map((q) => q.top)),
      r: Math.max(...rs.map((q) => q.right)), b: Math.max(...rs.map((q) => q.bottom)) });
    const paddingOf = (el) => {
      const r = geo(el).r;
      const cs = style(el);
      return { l: r.left + (parseFloat(cs.borderLeftWidth) || 0), t: r.top + (parseFloat(cs.borderTopWidth) || 0),
        r: r.right - (parseFloat(cs.borderRightWidth) || 0), b: r.bottom - (parseFloat(cs.borderBottomWidth) || 0) };
    };
    for (const el of all) {
      const g = geo(el);
      if (!g.vis || !inView(g.r) || g.r.width < 8 || g.r.height < 8 || g.r.width > 400 || g.r.height > 700) continue;
      if (['input', 'select', 'textarea', 'canvas', 'iframe'].includes(el.localName) || MEDIA.has(el.localName)) continue;
      const host = parentOf(el);
      if (!isInteractive(el) && !(style(el).cursor === 'pointer' && !(host && host.nodeType === 1 && style(host).cursor === 'pointer'))) continue;
      const icon = iconBoxes(el);
      if (!icon) continue;
      // A mark the control draws itself (a dropdown caret on ::after) takes room next to
      // the icon but has no box to measure; the icon is then centred with it, not alone.
      if (['::before', '::after'].some((ps) => {
        const pc = getComputedStyle(el, ps);
        return pc.content !== 'none' && pc.content !== 'normal' && pc.display !== 'none' && pc.position !== 'absolute' && pc.position !== 'fixed';
      })) continue;
      const u = unionOf(icon.boxes);
      if (u.r - u.l > 80 || u.b - u.t > 80) continue;
      const p = paddingOf(el);
      for (const [axis, lo, hi, a, b] of [['x', p.l, p.r, u.l, u.r], ['y', p.t, p.b, u.t, u.b]]) {
        const inkedAxis = axis === 'x' ? icon.inkedX : icon.inked;
        const free = (hi - lo - (b - a)) / 2;
        const off = (a + b) / 2 - (lo + hi) / 2;
        if (free < 1 || Math.abs(off) < 2 || Math.abs(off) > free + 0.5) continue;
        if (Math.abs(off) > 0.6 * free && free > 12) continue; // flush against one side of a wide box
        // Measured glyph ink is exact, so 2 px counts; an image or icon box may carry its own
        // transparent margin, so it needs 3 px or most of the free room.
        if (!inkedAxis && Math.abs(off) < 3.5 && Math.abs(off) < 0.75 * free) continue;
        if (inkedAxis && Math.abs(off) < 0.1 * Math.min(hi - lo, 64)) continue; // 2 px reads as centred in a large box
        layoutOutliers.push({ kind: 'icon_offset', axis, selectors: [uniqueSelector(el)], container: null, offset_px: round2(off),
          free_px: round2(free), size_px: round2(hi - lo), content_px: round2(b - a), ink: inkedAxis, text: (accName(el) || '').replace(/\s+/g, ' ').trim().slice(0, 60),
          box: boxOf(el) });
      }
    }
    const FIELD = 'input:not([type=checkbox]):not([type=radio]):not([type=hidden]):not([type=range]):not([type=color]):not([type=file])'
      + ':not([type=submit]):not([type=button]):not([type=reset]):not([type=image]), select';
    const paintedBox = (e) => {
      const cs = style(e);
      const bg = parseColor(cs.backgroundColor);
      return (bg && bg.a > 0.05) || (cs.backgroundImage && cs.backgroundImage !== 'none')
        || (parseFloat(cs.borderTopWidth) || 0) > 0 || (parseFloat(cs.borderBottomWidth) || 0) > 0;
    };
    for (const f of all) {
      try {
        if (!f.matches(FIELD)) continue;
      } catch (e) {
        continue;
      }
      const fg = geo(f);
      if (!fg.vis || !inView(fg.r) || fg.r.width < 20 || fg.r.height < 10) continue;
      const fr = fg.r;
      // The field's group: its grandparent (a wrapper holding the addon), or its parent when
      // the grandparent is the page itself.
      const top = (n) => !n || n.nodeType !== 1 || n === document.body || n === document.documentElement;
      const up = parentOf(f);
      if (top(up)) continue;
      const scope = top(parentOf(up)) ? up : parentOf(up);
      let best = null;
      for (const b of scope.querySelectorAll('*')) {
        if (b === f || b.contains(f) || f.contains(b) || !geo(b).vis || !paintedBox(b)) continue;
        const br = geo(b).r;
        if (br.height < 10 || br.width < 8 || !(br.left >= fr.right - 1.5 || br.right <= fr.left + 1.5)) continue;
        const gap = Math.min(Math.abs(br.left - fr.right), Math.abs(fr.left - br.right));
        const overlap = Math.min(fr.bottom, br.bottom) - Math.max(fr.top, br.top);
        if (gap > 1.5 || overlap < 0.5 * Math.min(fr.height, br.height)) continue;
        if (!best || br.width * br.height < best.area) best = { el: b, area: br.width * br.height, r: br };
      }
      if (!best) continue;
      const dt = best.r.top - fr.top;
      const db = best.r.bottom - fr.bottom;
      if (Math.max(Math.abs(dt), Math.abs(db)) < 2) continue;
      layoutOutliers.push({ kind: 'attached_mismatch', axis: 'y', selectors: [uniqueSelector(f), uniqueSelector(best.el)], container: uniqueSelector(scope),
        offset_px: round2(Math.abs(dt) >= Math.abs(db) ? dt : db), top_px: round2(dt), bottom_px: round2(db), field_px: round2(fr.height),
        other_px: round2(best.r.height), text: (accName(f) || f.getAttribute('placeholder') || '').replace(/\s+/g, ' ').trim().slice(0, 60), box: boxOf(f) });
    }
    // Side by side, different kinds (LY-09): a checkbox, radio or switch whose centre is
    // 3 px or more off the first line of its label; a field and a separate button in one
    // row (gap up to 16 px) whose heights differ by 2 px or more; and in a bar (a header,
    // navigation or toolbar row), a control whose content centre is 3 px or more off the
    // others'. Content centres use the first text line or the icon, so a taller box with
    // centred content does not count.
    const firstLine = (el, skip) => {
      const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
      for (let t = walker.nextNode(); t; t = walker.nextNode()) {
        if ((skip && skip.contains(t)) || !t.nodeValue.trim()) continue;
        const host = t.parentElement;
        if (!host || !geo(host).vis || helperText(host)) continue;
        const range = document.createRange();
        range.selectNodeContents(t);
        const q = [...range.getClientRects()].find((x) => x.width > 0 && x.height > 0);
        if (q) return q;
      }
      return null;
    };
    const CHOICE = 'input[type=checkbox], input[type=radio], [role=switch], [role=checkbox], [role=radio]';
    for (const c of all) {
      try {
        if (!c.matches(CHOICE)) continue;
      } catch (e) {
        continue;
      }
      const g = geo(c);
      if (!g.vis || !inView(g.r) || g.r.width < 8 || g.r.height < 8 || g.r.height > 48 || helperText(c)) continue;
      if (parseFloat(style(c).opacity) === 0 || style(c).pointerEvents === 'none') continue;
      let label = (c.labels && c.labels[0]) || c.closest('label');
      if (!label && c.nextElementSibling && textOf(c.nextElementSibling)) label = c.nextElementSibling;
      if (!label || !geo(label).vis) continue;
      const line = firstLine(label, c);
      if (!line) continue;
      const overlap = Math.min(line.bottom, g.r.bottom) - Math.max(line.top, g.r.top);
      if (!(line.left >= g.r.right - 2 || line.right <= g.r.left + 2) || overlap <= 0) continue;
      const off = (g.r.top + g.r.bottom) / 2 - (line.top + line.bottom) / 2;
      if (Math.abs(off) < 3) continue;
      layoutOutliers.push({ kind: 'label_offset', axis: 'y', selectors: [uniqueSelector(c)], container: uniqueSelector(label), offset_px: round2(off),
        line_px: round2(line.height), control_px: round2(g.r.height), text: textOf(label), box: boxOf(c) });
    }
    const BUTTONISH = 'button, input[type=submit], input[type=button], input[type=reset], a.btn, [role=button]';
    for (const f of all) {
      try {
        if (!f.matches(FIELD)) continue;
      } catch (e) {
        continue;
      }
      const fg = geo(f);
      if (!fg.vis || !inView(fg.r) || fg.r.width < 40 || fg.r.height < 16 || fg.r.height > 72) continue;
      const fr = fg.r;
      const scope = f.closest('form, .input-group, [role=search]') || parentOf(parentOf(f) || f);
      if (!scope || scope.nodeType !== 1 || scope === document.body || scope === document.documentElement) continue;
      let next = null;
      for (const b of scope.querySelectorAll(BUTTONISH)) {
        if (b.contains(f) || !geo(b).vis) continue;
        const br = geo(b).r;
        const gap = br.left >= fr.right - 1 ? br.left - fr.right : (br.right <= fr.left + 1 ? fr.left - br.right : -1);
        const overlap = Math.min(fr.bottom, br.bottom) - Math.max(fr.top, br.top);
        if (gap <= 1.5 || gap > 16 || overlap < 0.5 * Math.min(fr.height, br.height) || br.height < 0.6 * fr.height) continue;
        if (!next || gap < next.gap) next = { el: b, gap, r: br };
      }
      if (!next || !paintedBox(next.el)) continue;
      const dh = next.r.height - fr.height;
      if (Math.abs(dh) < 2) continue;
      layoutOutliers.push({ kind: 'pair_mismatch', axis: 'y', selectors: [uniqueSelector(f), uniqueSelector(next.el)], container: uniqueSelector(scope),
        offset_px: round2(dh), gap_px: round2(next.gap), top_px: round2(next.r.top - fr.top), field_px: round2(fr.height), other_px: round2(next.r.height),
        text: (accName(f) || f.getAttribute('placeholder') || '').replace(/\s+/g, ' ').trim().slice(0, 60), box: boxOf(f) });
    }
    const vw = VX1 - VX0;
    const BAR_ITEM = 'a, button, [role=button]';
    const placedOut = (n, el) => {
      for (let a = n; a && a !== el; a = parentOf(a)) if (a.nodeType === 1 && ['absolute', 'fixed'].includes(style(a).position)) return true;
      return false;
    };
    const contentCentre = (el) => {
      const rects = [];
      const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
      for (let t = walker.nextNode(); t; t = walker.nextNode()) {
        const host = t.parentElement;
        if (!t.nodeValue.trim() || !host || !geo(host).vis || helperText(host) || placedOut(host, el)) continue;
        const range = document.createRange();
        range.selectNodeContents(t);
        const q = [...range.getClientRects()].find((x) => x.width > 0 && x.height > 0);
        if (q) { rects.push(q); break; }
      }
      for (const e of el.querySelectorAll('*')) {
        if (!geo(e).vis || placedOut(e, el) || e.textContent.trim()) continue;
        if (MEDIA.has(e.localName)) rects.push(geo(e).r);
        else if (!e.children.length && (shownContent(getComputedStyle(e, '::before').content) || shownContent(getComputedStyle(e, '::after').content))) rects.push(geo(e).r);
      }
      if (!rects.length) return null;
      const u = unionOf(rects);
      return { c: (u.t + u.b) / 2, h: u.b - u.t };
    };
    const bars = all.filter((b) => {
      const g = geo(b);
      if (!g.vis || !inView(g.r) || g.r.height < 24 || g.r.height > 120 || g.r.width < 0.6 * vw) return false;
      const role = b.getAttribute('role');
      return ['nav', 'header'].includes(b.localName) || role === 'navigation' || role === 'banner' || role === 'toolbar'
        || /(^|[-_ ])(navbar|topbar|toolbar|appbar|header)([-_ ]|$)/i.test(b.className && b.className.baseVal === undefined ? b.className : '');
    });
    for (const bar of bars.filter((b) => !bars.some((o) => o !== b && o.contains(b)))) {
      const br = geo(bar).r;
      const items = [...bar.querySelectorAll(BAR_ITEM)].filter((e) => {
        const g = geo(e);
        return g.vis && inView(g.r) && g.r.height <= 72 && g.r.top >= br.top - 1 && g.r.bottom <= br.bottom + 1;
      });
      const outer = items.filter((e) => !items.some((o) => o !== e && o.contains(e)));
      const placed = [];
      for (const e of outer) {
        const cs = style(e);
        if (cs.display === 'inline' && (parentOf(e) && style(parentOf(e)).display === 'inline')) continue;
        const cc = contentCentre(e);
        if (cc && cc.h <= 48) placed.push({ e, c: cc.c, h: cc.h, r: geo(e).r });
      }
      if (placed.length < 2) continue;
      // One row only: the items whose boxes overlap the row of the first item.
      const sameRow = placed.filter((it) => Math.min(it.r.bottom, placed[0].r.bottom) - Math.max(it.r.top, placed[0].r.top) > 0.5 * Math.min(it.r.height, placed[0].r.height));
      // Items of similar content height only: an avatar with a name beside a row of icons is
      // centred on purpose with its own height.
      const hs = sameRow.map((it) => it.h).sort((a, b) => a - b);
      const hm = hs[Math.floor(hs.length / 2)];
      const row = sameRow.filter((it) => it.h <= 1.8 * hm && it.h >= hm / 1.8);
      if (row.length < 2) continue;
      const centres = row.map((it) => it.c).sort((a, b) => a - b);
      const mid = centres[Math.floor(centres.length / 2)];
      let worst = null;
      for (const it of row) {
        const d = it.c - mid;
        const others = row.filter((o) => o !== it);
        const agree = others.every((o) => Math.abs(o.c - mid) <= 1.5);
        if (Math.abs(d) >= 3 && agree && (!worst || Math.abs(d) > Math.abs(worst.d))) worst = { it, d, ref: others[0] };
      }
      if (!worst) continue;
      layoutOutliers.push({ kind: 'bar_offset', axis: 'y', selectors: [uniqueSelector(worst.it.e), uniqueSelector(worst.ref.e)], container: uniqueSelector(bar),
        offset_px: round2(worst.d), items: row.length, text: (accName(worst.it.e) || textOf(worst.it.e)).slice(0, 60), box: boxOf(worst.it.e) });
    }
    // A squeezed column (LY-10): on a phone-width screen, two or more texts of two or more
    // words in boxes narrower than four em that wrap to three or more lines, or of six or
    // more words that break every one or two words. Reported once, through the outermost
    // ancestor still narrower than 40 % of the screen.
    if (vw <= 520) {
      const squeezed = [];
      for (const e of all) {
        if (squeezed.length > 30) break;
        const g = geo(e);
        if (!g.vis || !inView(g.r) || ![...e.childNodes].some((n) => n.nodeType === 3 && n.nodeValue.trim())) continue;
        const words = textOf(e).split(' ').filter(Boolean);
        if (words.length < 2 || textOf(e).length < 8) continue;
        const cs = style(e);
        const fs = parseFloat(cs.fontSize) || 16;
        const lh = parseFloat(cs.lineHeight) || fs * 1.2;
        // Or a longer text in a box under 40 % of the screen that breaks every one or two words
        // (table cells and nested list items wrap by design and are left out).
        const lines = Math.round(g.r.height / lh);
        if ((g.r.width < 4 * fs && g.r.height >= 2.5 * lh) || (g.r.width < 3 * fs && g.r.height >= 1.6 * lh)
          || (words.length >= 6 && lines >= 3 && lines >= words.length / 2 && g.r.width < 0.4 * vw && !e.closest('table, li li'))) squeezed.push(e);
      }
      if (squeezed.length >= 2) {
        let col = squeezed[0];
        for (let a = parentOf(col); a && a.nodeType === 1 && a !== document.body && a !== document.documentElement; a = parentOf(a)) {
          if (geo(a).r.width < 0.4 * vw) col = a; else break;
        }
        layoutOutliers.push({ kind: 'narrow_column', axis: 'x', selectors: [uniqueSelector(col)], container: null, offset_px: round2(geo(col).r.width),
          screen_px: round2(vw), count: squeezed.length, text: textOf(squeezed[0]), box: boxOf(col) });
      }
    }
    // Uneven fields and crowded neighbours (LY-11..13). Two text fields stacked in one form
    // column (same left edge, nothing beside their right edge) whose widths differ by 4 px
    // or more and by less than a quarter; a deliberately short field differs by more
    // (field_width). Two links or buttons next to each other on one line, at one size and
    // baseline, whose labels touch: under 0.1 em from the end of one label's text to the
    // start of the next, so they read as one phrase (run_together). A link or button of a
    // painted header bar (fixed, sticky, or a header or navigation bar 24 to 160 px tall)
    // whose text starts inside the bar and hangs past its bottom edge by 4 px and 30 % of
    // its line or more; a bar at the bottom of the screen is checked upwards (hanging_item).
    const trimmedRects = (t) => {
      const v = t.nodeValue;
      const i0 = v.search(/\S/);
      if (i0 < 0) return [];
      const range = document.createRange();
      range.setStart(t, i0);
      range.setEnd(t, v.replace(/\s+$/, '').length);
      return [...range.getClientRects()].filter((q) => q.width > 0 && q.height > 0);
    };
    const TEXT_FIELD = 'textarea, input:not([type]), input[type=text], input[type=email], input[type=password], input[type=search], input[type=tel], input[type=url]';
    const textFields = [];
    for (const f of all) {
      try {
        if (!f.matches(TEXT_FIELD)) continue;
      } catch (e) {
        continue;
      }
      const g = geo(f);
      if (g.vis && g.r.width >= 40 && g.r.height >= 12 && !helperText(f)) textFields.push(f);
    }
    const fieldScopes = new Map();
    for (const f of textFields) {
      let scope = f.closest('form, fieldset');
      for (let a = parentOf(f), i = 0; !scope && a && a.nodeType === 1 && a !== document.body && i < 4; a = parentOf(a), i++) {
        if (textFields.some((o) => o !== f && a.contains(o))) scope = a;
      }
      if (!scope) continue;
      if (!fieldScopes.has(scope)) fieldScopes.set(scope, []);
      fieldScopes.get(scope).push(f);
    }
    for (const [scope, list] of fieldScopes) {
      if (list.length < 2) continue;
      const near = [...scope.querySelectorAll('*')].slice(0, 800).filter((e) => !list.includes(e) && geo(e).vis);
      // Something beside a field's right edge (an addon, a button, another field, a hint)
      // takes part of its row: that field is narrower on purpose.
      const free = list.filter((f) => {
        const r = geo(f).r;
        return !near.some((e) => {
          if (e.contains(f) || f.contains(e)) return false;
          const q = geo(e).r;
          const ov = Math.min(r.bottom, q.bottom) - Math.max(r.top, q.top);
          return q.width >= 4 && ov > 0.5 * Math.min(r.height, q.height) && q.left >= r.right - 1.5 && q.left < r.right + 48;
        });
      }).sort((a, b) => geo(a).r.top - geo(b).r.top);
      const shares = (f, skip) => free.some((o) => !skip.includes(o) && Math.abs(geo(o).r.left - geo(f).r.left) <= 1.5 && Math.abs(geo(o).r.width - geo(f).r.width) <= 1);
      const reported = new Set();
      for (let i = 1; i < free.length; i++) {
        const a = geo(free[i - 1]).r;
        const b = geo(free[i]).r;
        const gap = b.top - a.bottom;
        if (Math.abs(a.left - b.left) > 1.5 || gap < 0 || gap > 120) continue;
        const ratio = b.width / a.width;
        if (Math.abs(b.width - a.width) < 4 || ratio < 0.75 || ratio > 1.34) continue;
        // The odd field is the one whose width no other field of the column shares.
        const pair = [free[i - 1], free[i]];
        const odd = shares(pair[0], pair) && !shares(pair[1], pair) ? pair[1] : (shares(pair[1], pair) && !shares(pair[0], pair) ? pair[0] : pair[1]);
        const other = odd === pair[0] ? pair[1] : pair[0];
        if (reported.has(odd) || !inView(geo(odd).r)) continue;
        reported.add(odd);
        layoutOutliers.push({ kind: 'field_width', axis: 'x', selectors: [uniqueSelector(odd), uniqueSelector(other)], container: uniqueSelector(scope),
          offset_px: round2(geo(odd).r.width - geo(other).r.width), field_px: round2(geo(odd).r.width), other_px: round2(geo(other).r.width),
          text: (accName(odd) || odd.getAttribute('placeholder') || '').replace(/\s+/g, ' ').trim().slice(0, 60), box: boxOf(odd) });
      }
    }
    const ITEM = 'a[href], button, [role=button], [role=link], [role=tab], [role=menuitem]';
    const labelEnds = (el) => {
      let first = null;
      let last = null;
      let letters = false;
      const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
      for (let t = walker.nextNode(); t; t = walker.nextNode()) {
        const host = t.parentElement;
        if (!t.nodeValue.trim() || !host || !geo(host).vis || helperText(host) || placedOut(host, el)) continue;
        const qs = trimmedRects(t);
        if (!qs.length) continue;
        const fs = parseFloat(style(host).fontSize) || 16;
        if (!first) first = { q: qs[0], fs };
        last = { q: qs[qs.length - 1], fs };
        letters = letters || LETTER.test(t.nodeValue);
      }
      return first ? { first, last, letters } : null;
    };
    const runs = new Map();
    let prevItem = null;
    for (const e of all) {
      try {
        if (!e.matches(ITEM)) continue;
      } catch (err) {
        continue;
      }
      if (prevItem && prevItem.e.contains(e)) continue;
      const g = geo(e);
      if (!g.vis || !inView(g.r) || helperText(e)) continue;
      const ends = labelEnds(e);
      if (!ends) continue;
      if (!ends.letters) {
        prevItem = null; // a caret or symbol between two labels separates them
        continue;
      }
      const item = { e, ...ends };
      if (prevItem) {
        const a = prevItem.last.q;
        const b = item.first.q;
        const fs = Math.min(prevItem.last.fs, item.first.fs);
        const ov = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
        const gap = b.left - a.right;
        if (ov > 0.5 * Math.min(a.height, b.height) && b.left > a.left + 1 && gap < 0.1 * fs && gap > -0.3 * fs
          && Math.max(prevItem.last.fs, item.first.fs) <= 1.25 * fs && Math.abs(a.bottom - b.bottom) <= 0.25 * fs) {
          let common = parentOf(prevItem.e);
          while (common && common.nodeType === 1 && !common.contains(e)) common = parentOf(common);
          const key = common && common.nodeType === 1 ? common : document.body;
          if (!runs.has(key)) runs.set(key, []);
          runs.get(key).push({ a: prevItem.e, b: e, gap });
        }
      }
      prevItem = item;
    }
    for (const [box, pairs] of runs) {
      const p = pairs[0];
      layoutOutliers.push({ kind: 'run_together', axis: 'x', selectors: [uniqueSelector(p.b), uniqueSelector(p.a)], container: uniqueSelector(box),
        offset_px: round2(p.gap), pairs: pairs.length, text: (textOf(p.a) + ' | ' + textOf(p.b)).slice(0, 80), box: boxOf(p.b) });
    }
    const BAR_NAME = /(^|[-_ ])(navbar|topbar|toolbar|appbar|header|nav)([-_ ]|$)/i;
    const hangBars = all.filter((b) => {
      const g = geo(b);
      if (!g.vis || !inView(g.r) || g.r.height < 24 || g.r.height > 160 || g.r.width < 0.6 * vw) return false;
      const cs = style(b);
      const pinned = cs.position === 'fixed' || cs.position === 'sticky';
      const named = ['nav', 'header'].includes(b.localName) || ['navigation', 'banner', 'toolbar'].includes(b.getAttribute('role'))
        || BAR_NAME.test(typeof b.className === 'string' ? b.className : '');
      return (pinned || named) && paintedBox(b) && cs.overflowY === 'visible';
    });
    for (const bar of hangBars.filter((b) => !hangBars.some((o) => o !== b && o.contains(b)))) {
      const br = geo(bar).r;
      const atBottom = br.bottom >= VY1 - 1 && br.top > VY0 + (VY1 - VY0) / 2;
      let worst = null;
      let count = 0;
      for (const it of bar.querySelectorAll(ITEM)) {
        const g = geo(it);
        if (!g.vis || g.r.right <= VX0 + 1 || g.r.left >= VX1 - 1 || helperText(it) || placedOut(it, bar)) continue;
        const rects = [];
        const walker = document.createTreeWalker(it, NodeFilter.SHOW_TEXT);
        for (let t = walker.nextNode(); t; t = walker.nextNode()) {
          const host = t.parentElement;
          if (t.nodeValue.trim() && host && geo(host).vis && !helperText(host)) rects.push(...trimmedRects(t));
        }
        if (!rects.length) continue;
        const line = Math.min(...rects.map((q) => q.height));
        if (paintedBox(it)) rects.push(g.r);
        const u = unionOf(rects);
        const hang = atBottom ? br.top - u.t : u.b - br.bottom;
        const starts = atBottom ? u.b <= br.bottom + 1 && u.b > br.top + 2 : u.t >= br.top - 1 && u.t < br.bottom - 2;
        if (!starts || hang < 4 || hang < 0.3 * line) continue;
        count++;
        if (!worst || hang > worst.hang) worst = { it, hang };
      }
      if (worst) {
        layoutOutliers.push({ kind: 'hanging_item', axis: 'y', selectors: [uniqueSelector(worst.it)], container: uniqueSelector(bar), offset_px: round2(worst.hang),
          items: count, bar_px: round2(br.height), pinned: ['fixed', 'sticky'].includes(style(bar).position), edge: atBottom ? 'top' : 'bottom',
          text: textOf(worst.it), box: boxOf(worst.it) });
      }
    }
    // Text over an image (LY-14): the glyphs of a text overlap an image it does not belong to
    // by 8 px across and 4 px down or more while its block runs past the image's edge, as when
    // a float or a negative margin carries a caption into the next figure. Deliberate overlays
    // stay out: a text block wholly inside the image, anything placed out of flow (absolute,
    // fixed, sticky) or transformed between either one and their common ancestor, both in one
    // grid, and text on a painted panel of its own. A transparent image drawn over the text
    // counts too: the text shows through it (text_over_image).
    const pictures = [];
    for (const e of all) {
      if (!['img', 'svg', 'video', 'canvas', 'object', 'embed'].includes(e.localName) || (e.localName === 'svg' && parentOf(e) && parentOf(e).closest && parentOf(e).closest('svg'))) continue;
      const g = geo(e);
      if (g.vis && inView(g.r) && g.r.width >= 40 && g.r.height >= 24 && parseFloat(style(e).opacity) >= 0.5) pictures.push(e);
      if (pictures.length >= 80) break;
    }
    const offFlow = (from, top) => {
      for (let a = from; a && a !== top; a = parentOf(a)) {
        if (a.nodeType !== 1) continue;
        const cs = style(a);
        if (['absolute', 'fixed', 'sticky'].includes(cs.position) || (cs.transform && cs.transform !== 'none')) return true;
      }
      return false;
    };
    const panelAt = (from, top, x, y) => {
      for (let a = from; a && a !== top; a = parentOf(a)) {
        if (a.nodeType !== 1) continue;
        const cs = style(a);
        const bg = parseColor(cs.backgroundColor);
        const r = geo(a).r;
        if (((bg && bg.a >= 0.5) || (cs.backgroundImage && cs.backgroundImage !== 'none')) && x >= r.left && x <= r.right && y >= r.top && y <= r.bottom) return true;
      }
      return false;
    };
    if (pictures.length) {
      const over = new Map();
      const walker = document.createTreeWalker(document.body || document.documentElement, NodeFilter.SHOW_TEXT);
      for (let t = walker.nextNode(); t; t = walker.nextNode()) {
        const host = t.parentElement;
        if (!host || !LETTER.test(t.nodeValue)) continue;
        const hg = geo(host);
        if (!hg.vis || !inView(hg.r) || helperText(host)) continue;
        const near = pictures.filter((p) => {
          const q = geo(p).r;
          return !p.contains(host) && hg.r.left < q.right && hg.r.right > q.left && hg.r.top < q.bottom && hg.r.bottom > q.top;
        });
        if (!near.length) continue;
        let block = host;
        while (block && block.nodeType === 1 && ['inline', 'contents'].includes(style(block).display) && parentOf(block)) block = parentOf(block);
        const bb = geo(block).r;
        for (const q of trimmedRects(t)) {
          for (const p of near) {
            const r = geo(p).r;
            if (bb.left >= r.left - 1 && bb.right <= r.right + 1 && bb.top >= r.top - 1 && bb.bottom <= r.bottom + 1) continue;
            const ox = Math.min(q.right, r.right) - Math.max(q.left, r.left);
            const oy = Math.min(q.bottom, r.bottom) - Math.max(q.top, r.top);
            if (ox < 8 || oy < 4 || oy < 0.3 * q.height) continue;
            const x = (Math.max(q.left, r.left) + Math.min(q.right, r.right)) / 2;
            const y = (Math.max(q.top, r.top) + Math.min(q.bottom, r.bottom)) / 2;
            if (x < VX0 || x > VX1 || y < VY0 || y > VY1) continue;
            let common = parentOf(host);
            while (common && common.nodeType === 1 && !common.contains(p)) common = parentOf(common);
            if (!common || common.nodeType !== 1 || ['grid', 'inline-grid'].includes(style(common).display)) continue;
            if (offFlow(host, common) || offFlow(p, common) || panelAt(host, common, x, y)) continue;
            const hit = document.elementFromPoint(x, y);
            const under = !!hit && (hit === p || p.contains(hit));
            const seen = over.get(p);
            if (!seen) over.set(p, { p, host, oy, ox, under, lines: 1 });
            else {
              seen.lines++;
              if (oy > seen.oy) Object.assign(seen, { host, oy, ox, under });
            }
          }
        }
      }
      for (const { p, host, oy, ox, under, lines } of over.values()) {
        layoutOutliers.push({ kind: 'text_over_image', axis: 'y', selectors: [uniqueSelector(host), uniqueSelector(p)], offset_px: round2(oy),
          overlap_w: round2(ox), image_on_top: under, lines, text: textOf(host), box: boxOf(host) });
      }
    }
    // Rows that touch while columns keep a gap (LY-15): painted cells in rows and columns
    // whose neighbour on the same row keeps 4 to 64 px from them while the cell below touches
    // them (within 1 px), so the rows run together into one block. Tables, controls and inline
    // boxes (a wrapped row of buttons or tabs), the items of one card beside another card's,
    // and stacks side by side (the cell below in the same parent, the neighbour in another)
    // stay out (touching_rows).
    const cellBoxes = [];
    const CONTROL = 'a, button, input, select, textarea, label, summary, [role=button], [role=tab], [role=link], [role=menuitem]';
    for (const e of all) {
      const g = geo(e);
      if (!g.vis || !inView(g.r) || g.r.width < 16 || g.r.height < 12 || g.r.width > 0.95 * vw) continue;
      const cs = style(e);
      if (cs.display.startsWith('inline') || cs.display.startsWith('table') || ['absolute', 'fixed'].includes(cs.position)) continue;
      try {
        if (e.matches(CONTROL)) continue;
      } catch (err) {
        continue;
      }
      const bg = parseColor(cs.backgroundColor);
      const ring = ['Top', 'Right', 'Bottom', 'Left'].every((s) => (parseFloat(cs['border' + s + 'Width']) || 0) > 0);
      if ((bg && bg.a > 0.05) || (cs.backgroundImage && cs.backgroundImage !== 'none') || ring) cellBoxes.push({ c: e, r: g.r });
      if (cellBoxes.length >= 400) break;
    }
    const apart = (a, b) => a !== b && !a.c.contains(b.c) && !b.c.contains(a.c);
    const sameRow = (a, b) => Math.abs(a.r.top - b.r.top) <= 1 && Math.abs(a.r.bottom - b.r.bottom) <= 2;
    const gapRight = (a, b) => b.r.left - a.r.right;
    for (const a of cellBoxes) {
      a.right = null;
      a.spaced = false;
      for (const o of cellBoxes) {
        if (!apart(a, o) || !sameRow(a, o)) continue;
        const g1 = gapRight(a, o);
        const g2 = gapRight(o, a);
        if ((g1 >= 4 && g1 <= 64) || (g2 >= 4 && g2 <= 64)) a.spaced = true;
        if (g1 >= 4 && g1 <= 64 && (!a.right || o.r.left < a.right.r.left)) a.right = o;
      }
    }
    const touching = new Map();
    for (const a of cellBoxes) {
      if (!a.right) continue;
      const c = a.right;
      for (const b of cellBoxes) {
        if (b === c || !b.spaced || !apart(a, b) || !apart(b, c)) continue;
        const gy = b.r.top - a.r.bottom;
        const ox = Math.min(a.r.right, b.r.right) - Math.max(a.r.left, b.r.left);
        if (gy < -1 || gy > 1 || ox < 0.5 * Math.min(a.r.width, b.r.width)) continue;
        if (parentOf(a.c) === parentOf(b.c) && parentOf(c.c) !== parentOf(a.c)) continue;
        let panel = parentOf(a.c);
        while (panel && panel.nodeType === 1 && !paintedBox(panel)) panel = parentOf(panel);
        if (panel && panel.nodeType === 1 && !panel.contains(c.c)) continue;
        let common = parentOf(a.c);
        while (common && common.nodeType === 1 && !(common.contains(b.c) && common.contains(c.c))) common = parentOf(common);
        const key = common && common.nodeType === 1 ? common : document.body;
        if (!touching.has(key)) touching.set(key, { a, b, gy, gx: gapRight(a, c), pairs: 0 });
        touching.get(key).pairs++;
      }
    }
    for (const [box, t] of touching) {
      layoutOutliers.push({ kind: 'touching_rows', axis: 'y', selectors: [uniqueSelector(t.b.c), uniqueSelector(t.a.c)], container: uniqueSelector(box),
        offset_px: round2(t.gy), gap_px: round2(t.gx), pairs: t.pairs, text: (textOf(t.a.c) + ' / ' + textOf(t.b.c)).slice(0, 80), box: boxOf(t.b.c) });
    }
    // Text against the screen edge (LY-16): three or more texts whose glyphs start or end
    // within 1.5 px of the left or right edge of the screen leave the page no side margin.
    // Text in a code block or in a box whose content runs past it sideways (a scroller, a
    // carousel) is cut by that box and is left out. Reported once per side, through the first three texts.
    {
      const sides = { left: [], right: [] };
      const inSideBox = (e) => {
        for (let a = e; a && a.nodeType === 1 && a !== document.body && a !== document.documentElement; a = parentOf(a)) {
          if (a.tagName === 'PRE' || (style(a).overflowX !== 'visible' && a.scrollWidth > a.clientWidth + 1)) return true;
        }
        return false;
      };
      for (const e of all) {
        if (sides.left.length > 8 && sides.right.length > 8) break;
        if (!e.childNodes || ![...e.childNodes].some((n) => n.nodeType === 3 && n.nodeValue.trim())) continue;
        const g = geo(e);
        if (!g.vis || !inView(g.r) || inSideBox(e)) continue;
        let left = Infinity;
        let right = -Infinity;
        for (const n of e.childNodes) {
          if (n.nodeType !== 3 || !n.nodeValue.trim()) continue;
          const range = document.createRange();
          range.selectNodeContents(n);
          for (const q of range.getClientRects()) {
            if (q.width < 1 || q.height < 1 || q.bottom <= VY0 || q.top >= VY1) continue;
            left = Math.min(left, q.left);
            right = Math.max(right, q.right);
          }
        }
        if (left !== Infinity && left >= VX0 - 0.5 && left - VX0 <= 1.5) sides.left.push({ e, d: Math.max(0, left - VX0) });
        if (right !== -Infinity && right <= VX1 + 0.5 && VX1 - right <= 1.5) sides.right.push({ e, d: Math.max(0, VX1 - right) });
      }
      for (const side of ['left', 'right']) {
        const hits = sides[side];
        if (hits.length < 3) continue;
        layoutOutliers.push({ kind: 'edge_text', axis: 'x', side, selectors: hits.slice(0, 3).map((h) => uniqueSelector(h.e)), container: null,
          offset_px: round2(Math.max(...hits.map((h) => h.d))), count: hits.length, screen_px: round2(vw), text: textOf(hits[0].e), box: boxOf(hits[0].e) });
      }
    }
    // A desktop layout on a phone (LY-17): a touch screen of phone width whose page is laid
    // out at least 30 % wider than the screen without a device-width viewport, so the
    // browser shrinks the whole page to fit and its text renders a few pixels tall.
    {
      const sw = (window.screen && window.screen.width) || 0;
      const meta = document.querySelector('meta[name="viewport" i]');
      const deviceWidth = !!meta && /width\s*=\s*device-width/i.test(meta.getAttribute('content') || '');
      if (navigator.maxTouchPoints > 0 && sw > 0 && sw <= 520 && window.innerWidth >= 1.3 * sw && !deviceWidth) {
        const scale = vvp && vvp.scale > 0 ? vvp.scale : sw / window.innerWidth;
        const fs = document.body ? parseFloat(style(document.body).fontSize) || 16 : 16;
        layoutOutliers.push({ kind: 'desktop_layout', axis: 'x', selectors: ['html'], container: null, offset_px: round2(window.innerWidth),
          screen_px: sw, scale: round2(scale), text_px: round2(fs * scale), meta: meta ? (meta.getAttribute('content') || '') : null,
          text: '', box: { x: 0, y: 0, w: round2(Math.min(vw, 600)), h: 160 } });
      }
    }
    const scroller = document.scrollingElement || document.documentElement;
    if (scroller) {
      const sx = window.scrollX || 0;
      const cw = scroller.clientWidth;
      const ch = scroller.clientHeight;
      if (scroller.scrollWidth > cw + 1) {
        const rootHides = [document.documentElement, document.body].some((n) => n && ['hidden', 'clip'].includes(style(n).overflowX));
        const offenders = [];
        for (const e of all) {
          const g = geo(e);
          if (!g.vis || g.r.width < 1 || g.r.right + sx <= cw + 1) continue;
          const p = parentOf(e);
          if (p && p.nodeType === 1 && p !== document.body && p !== document.documentElement && geo(p).r.right + sx > cw + 1) continue;
          let clippedAway = false;
          for (let a = p; a && a.nodeType === 1 && a !== document.body && a !== document.documentElement; a = parentOf(a)) {
            if (style(a).overflowX !== 'visible') { clippedAway = true; break; }
          }
          if (clippedAway || ['fixed'].includes(style(e).position)) continue;
          offenders.push(e);
        }
        // The cut a user sees: an element that starts on the screen and runs past its edge.
        offenders.sort((a, b) => (geo(a).r.left + sx < cw) - (geo(b).r.left + sx < cw) || geo(b).r.right - geo(a).r.right).reverse();
        const shown = offenders.filter((e) => geo(e).r.left + sx < cw && geo(e).r.bottom > VY0 && geo(e).r.top < VY1);
        if (shown.length) {
          shown.sort((a, b) => geo(b).r.right - geo(a).r.right);
          layoutOutliers.push({ kind: 'page_overflow', axis: 'x', selectors: shown.slice(0, 3).map(uniqueSelector), container: null,
            offset_px: round2(scroller.scrollWidth - cw), page_px: scroller.scrollWidth, screen_px: cw, hides: rootHides,
            text: textOf(shown[0]), box: boxOf(shown[0]) });
        } else {
          // The page is wider on every screen even when the element that widens it lies
          // further down: name it, and outline the screen's right edge.
          const elsewhere = offenders.filter((e) => geo(e).r.left + sx < cw).sort((a, b) => geo(b).r.right - geo(a).r.right);
          if (elsewhere.length) {
            layoutOutliers.push({ kind: 'page_overflow', axis: 'x', selectors: elsewhere.slice(0, 3).map(uniqueSelector), container: null,
              offset_px: round2(scroller.scrollWidth - cw), page_px: scroller.scrollWidth, screen_px: cw, hides: rootHides, offscreen: true,
              offender_y: round2(geo(elsewhere[0]).r.top + (window.scrollY || 0)), text: textOf(elsewhere[0]),
              box: { x: round2(VX1 - 40), y: round2(VY0), w: 40, h: round2(VY1 - VY0) } });
          }
        }
      }
      const slack = scroller.scrollHeight - ch;
      if (slack >= 1 && slack <= 80) {
        const full = all.find((e) => {
          if (e === document.body || e === document.documentElement || !geo(e).vis) return false;
          return Math.abs(geo(e).r.height - ch) <= 1 || (parseFloat(style(e).minHeight) || 0) >= ch - 1;
        });
        if (full) {
          layoutOutliers.push({ kind: 'scroll_slack', axis: 'y', selectors: [uniqueSelector(full)], container: null, offset_px: round2(slack),
            page_px: scroller.scrollHeight, screen_px: ch, text: '', box: boxOf(full) });
        }
      }
    }
  }

  state.ids = ids;
  state.hotspots = [...spots.values()].map((s) => ({ id: s.id, box: s.box, elementId: `hs-${s.id.replace(/[^A-Za-z0-9._-]/g, '_')}` }));

  let active = null;
  const ae = document.activeElement;
  if (ae && ae !== document.body && ae !== document.documentElement && ae.getBoundingClientRect) {
    const r = ae.getBoundingClientRect();
    if (r.width > 0 && r.height > 0) active = { x: round2(r.left + r.width / 2), y: round2(r.top + r.height / 2) };
  }
  // Layers that take over the screen (FM-02): declared dialogs, and fixed or absolute
  // painted boxes covering at least 40 % of the viewport. Records whether keyboard
  // focus is inside each one; values are never read.
  let deep = document.activeElement;
  while (deep && deep.shadowRoot && deep.shadowRoot.activeElement) deep = deep.shadowRoot.activeElement;
  const focusOnBody = !deep || deep === document.body || deep === document.documentElement;
  const layers = [];
  const vpArea = Math.max(1, vw * vh);
  const painted = (n) => {
    const cs = style(n);
    const bg = cs.backgroundColor || '';
    const a = /rgba\(.*,\s*([\d.]+)\)/.exec(bg);
    return (bg && bg !== 'transparent' && !(a && parseFloat(a[1]) === 0)) || (cs.backgroundImage && cs.backgroundImage !== 'none');
  };
  for (const n of all) {
    if (layers.length >= 8) break;
    if (n === document.body || n === document.documentElement) continue;
    const role = (n.getAttribute('role') || '').trim();
    let modal = false;
    try {
      modal = n.matches(':modal');
    } catch (e) { /* unsupported */ }
    const declared = modal || n.getAttribute('aria-modal') === 'true' || role === 'dialog' || role === 'alertdialog'
      || (n.tagName.toLowerCase() === 'dialog' && n.open);
    let kind = null;
    const g = geo(n);
    if (!g.vis) continue;
    if (declared) kind = modal || n.getAttribute('aria-modal') === 'true' ? 'modal' : 'dialog';
    else {
      // Area first (cheap, from the cached box), then the computed style.
      const r = g.r;
      const w = Math.max(0, Math.min(r.right, VX1) - Math.max(r.left, VX0));
      const h = Math.max(0, Math.min(r.bottom, VY1) - Math.max(r.top, VY0));
      if ((w * h) / vpArea < 0.4) continue;
      const pos = style(n).position;
      if ((pos === 'fixed' || pos === 'absolute') && painted(n)) {
        // An overlay sits over content that is still rendered underneath; a screen that
        // replaced the previous one (display:none swaps) covers nothing.
        let over = 0;
        for (const c of candidates) {
          if (over >= 1) break;
          if (n.contains(c.el) || c.el.contains(n)) continue;
          const cg = geo(c.el);
          if (!cg.vis) continue;
          const cx = cg.r.left + cg.r.width / 2;
          const cy = cg.r.top + cg.r.height / 2;
          if (cx < r.left || cx > r.right || cy < r.top || cy > r.bottom || cx < VX0 || cy < VY0 || cx >= VX1 || cy >= VY1) continue;
          const top = document.elementFromPoint(cx, cy);
          if (top && n.contains(top)) over += 1;
        }
        if (over) kind = 'sheet';
      }
    }
    if (!kind) continue;
    if (layers.some((l) => l.node.contains(n))) continue; // keep the outermost
    for (let i = layers.length - 1; i >= 0; i--) if (n.contains(layers[i].node)) layers.splice(i, 1);
    layers.push({ node: n, kind });
  }
  // Containment in the flat tree (slotted content, dialogs inside shadow roots).
  const inFlat = (root, n) => {
    for (let x = n; x; x = x.assignedSlot || x.parentNode || x.host) if (x === root) return true;
    return false;
  };
  // A layer's overlay root: its outermost fixed ancestor below <body> that is not the
  // app shell (most content lies outside it), e.g. a portal holding a dialog container
  // that keeps focus on itself and the role=dialog paper inside it (MUI).
  const overlayRoot = (node) => {
    let root = node;
    for (let n = node.parentElement; n && n !== document.body && n !== document.documentElement; n = n.parentElement) {
      if (style(n).position === 'fixed') root = n;
    }
    if (root === node) return node;
    const inside = candidates.filter((c) => root.contains(c.el)).length;
    return inside <= candidates.length / 2 ? root : node;
  };
  // The next element Tab reaches from the focused one (document order, tabindex >= 0).
  let nextTab = null;
  if (!focusOnBody) {
    const tabbable = [...document.querySelectorAll('a[href], button, input, select, textarea, summary, [tabindex], [contenteditable=""], [contenteditable="true"]')]
      .filter((t) => t.tabIndex >= 0 && !t.disabled && t.getClientRects().length > 0 && !(t.closest && t.closest('[inert]')));
    nextTab = tabbable.find((t) => deep.compareDocumentPosition(t) & Node.DOCUMENT_POSITION_FOLLOWING && !deep.contains(t)) || null;
  }
  const layerOut = layers.map(({ node, kind }) => {
    const root = overlayRoot(node);
    return {
      selector: uniqueSelector(node), dom_id: node.id || null, kind,
      box: { x: round2(geo(node).r.left), y: round2(geo(node).r.top), w: round2(geo(node).r.width), h: round2(geo(node).r.height) },
      // Focus on the overlay root counts only when the root wraps the layer (a portal or
      // dialog container that focuses itself), not when it merely holds the trigger too.
      contains_focus: !focusOnBody && (inFlat(node, deep) || (root !== node && inFlat(root, deep) && inFlat(deep, node))),
      follows_focus: !!nextTab && inFlat(node, nextTab),
      overlay_root: root !== node ? uniqueSelector(root) : null,
    };
  });
  if (panned && (VX0 || VY0)) {
    // Report DOM geometry relative to the screen (hotspots keep their own coordinates).
    const shift = (b) => { if (b) { b.x = round2(b.x - VX0); b.y = round2(b.y - VY0); } };
    for (const e of elements) {
      if (e.source !== 'dom') continue;
      shift(e.box);
      shift(e.visible_box);
      for (const hb of e.hit_boxes || []) shift(hb);
      for (const p of e.paint?.parts || []) shift(p.box);
      if (e.occluder) shift(e.occluder.box);
      if (e.glyph_cover) shift(e.glyph_cover.box);
    }
    if (active) { active.x = round2(active.x - VX0); active.y = round2(active.y - VY0); }
    for (const l of layerOut) shift(l.box);
  }
  const se = document.scrollingElement || document.documentElement;
  return {
    elements,
    candidates: candidates.length + spots.size,
    truncated: candidates.length > cap,
    viewport: { w: vw, h: vh },
    scroll: { x: round2(window.scrollX), y: round2(window.scrollY), width: se ? se.scrollWidth : null, height: se ? se.scrollHeight : null },
    visual: vvp ? { offset_x: round2(vvp.offsetLeft), offset_y: round2(vvp.offsetTop), width: round2(vvp.width), height: round2(vvp.height), scale: round2(vvp.scale) } : null,
    active,
    focus: {
      on_body: focusOnBody, tag: focusOnBody ? null : deep.tagName.toLowerCase(), dom_id: focusOnBody ? null : (deep.id || null),
      expanded: !focusOnBody && deep.getAttribute('aria-expanded') === 'true',
      controls: focusOnBody ? [] : (deep.getAttribute('aria-controls') || '').split(/\s+/).filter(Boolean).slice(0, 8),
    },
    layers: layerOut,
    layout_outliers: (() => {
      if (panned && (VX0 || VY0)) for (const o of layoutOutliers) { o.box.x = round2(o.box.x - VX0); o.box.y = round2(o.box.y - VY0); }
      return layoutOutliers;
    })(),
    pageHotspotError,
    unknownRoles: [...unknownRoles],
  };
}

/**
 * Nearest extracted element id for a DOM element (walks up to ancestors, e.g. a
 * text match inside a button). `exact` is false when an ancestor supplied the id.
 */
export function idForElement(el, key) {
  const state = window[Symbol.for(key)];
  let interactive = false;
  try {
    interactive = el.matches('a, button, input, select, textarea, summary, canvas, [role], [onclick], [tabindex]');
  } catch (e) { /* ignore */ }
  if (!state || !state.ids) return { id: null, exact: false, interactive };
  for (let n = el; n; n = n.parentElement || (n.getRootNode && n.getRootNode() !== document ? n.getRootNode().host : null)) {
    const id = state.ids.get(n);
    if (id) return { id, exact: n === el, interactive };
  }
  return { id: null, exact: false, interactive };
}

/** Element id at a viewport point: hotspots first (last declared on top), then the DOM hit. */
export function idAtPoint(args) {
  const state = window[Symbol.for(args.key)];
  if (!state) return { id: null, hotspot: false };
  const spots = state.hotspots || [];
  for (let i = spots.length - 1; i >= 0; i--) {
    const b = spots[i].box;
    if (args.x >= b.x && args.x <= b.x + b.w && args.y >= b.y && args.y <= b.y + b.h) return { id: spots[i].elementId, hotspot: true };
  }
  // Points are screen (visual viewport) coordinates; hit testing takes layout ones.
  const vvp = window.visualViewport;
  const lx = args.x + (vvp && Math.abs(vvp.scale - 1) < 0.01 ? vvp.offsetLeft : 0);
  const ly = args.y + (vvp && Math.abs(vvp.scale - 1) < 0.01 ? vvp.offsetTop : 0);
  let n = document.elementFromPoint(lx, ly);
  while (n && n.shadowRoot) {
    const inner = n.shadowRoot.elementFromPoint(lx, ly);
    if (!inner || inner === n) break;
    n = inner;
  }
  for (; n; n = n.parentElement || (n.getRootNode && n.getRootNode() !== document ? n.getRootNode().host : null)) {
    const id = state.ids ? state.ids.get(n) : null;
    if (id) return { id, hotspot: false };
  }
  return { id: null, hotspot: false };
}

/**
 * What a click landed on (SM-08): the element (a handle, or the top-most element at
 * {x, y}), whether it or an ancestor within five levels is a control a keyboard or
 * screen reader can operate (native control, widget role, tabindex >= 0, a label with
 * a control, contenteditable), whether it contains one, and its ancestor ids.
 * Never reads values.
 */
export function controlOf(arg) {
  // Points are screen (visual viewport) coordinates; hit testing takes layout ones.
  const vvp = window.visualViewport;
  const lx = arg && arg.nodeType !== 1 ? arg.x + (vvp && Math.abs(vvp.scale - 1) < 0.01 ? vvp.offsetLeft : 0) : 0;
  const ly = arg && arg.nodeType !== 1 ? arg.y + (vvp && Math.abs(vvp.scale - 1) < 0.01 ? vvp.offsetTop : 0) : 0;
  let el = arg && arg.nodeType === 1 ? arg : (arg ? document.elementFromPoint(lx, ly) : null);
  while (el && el.shadowRoot && arg && arg.nodeType !== 1) {
    const inner = el.shadowRoot.elementFromPoint(lx, ly);
    if (!inner || inner === el) break;
    el = inner;
  }
  if (!el) return null;
  const NATIVE = ['button', 'input', 'select', 'textarea', 'summary', 'option', 'details', 'video', 'audio', 'iframe', 'canvas'];
  const WIDGET = ['button', 'link', 'checkbox', 'radio', 'switch', 'tab', 'menuitem', 'menuitemcheckbox', 'menuitemradio', 'option',
    'slider', 'spinbutton', 'textbox', 'searchbox', 'combobox', 'listbox', 'treeitem', 'gridcell', 'scrollbar'];
  const LANDMARK = ['body', 'main', 'nav', 'header', 'footer', 'aside', 'form'];
  // Flat-tree parent: through slots and out of shadow roots (web components).
  const up = (n) => n.assignedSlot || n.parentElement || (n.getRootNode && n.getRootNode() instanceof ShadowRoot ? n.getRootNode().host : null);
  // A native control the keyboard can reach: not type=hidden, rendered, not
  // visibility:hidden, not inert (opacity:0 or clipped inputs still take focus).
  const usable = (c) => !!c && !(c.tagName === 'INPUT' && (c.type || '').toLowerCase() === 'hidden') && c.getClientRects().length > 0
    && (typeof c.checkVisibility !== 'function' || c.checkVisibility({ visibilityProperty: true })) && !(c.closest && c.closest('[inert]'));
  const plain = (n) => {
    const tag = n.tagName.toLowerCase();
    if (NATIVE.includes(tag)) return usable(n);
    if (tag === 'a' && n.hasAttribute('href')) return true;
    if (tag === 'label') return !!n.control && usable(n.control);
    const role = (n.getAttribute('role') || '').trim().split(/\s+/)[0];
    if (WIDGET.includes(role)) return true;
    const t = n.getAttribute('tabindex');
    return (t !== null && parseInt(t, 10) >= 0) || n.isContentEditable;
  };
  // A web component is a control when it delegates focus or holds one in its open shadow tree.
  const isControl = (n) => plain(n) || (!!n.shadowRoot && (n.shadowRoot.delegatesFocus || [...n.shadowRoot.querySelectorAll('*')].slice(0, 200).some(plain)));
  const holds = (root) => [...root.querySelectorAll('*')].slice(0, 300).some(isControl);
  let control = false;
  for (let n = el, i = 0; n && n.nodeType === 1 && i < 5; n = up(n), i++) {
    if (isControl(n)) {
      control = true;
      break;
    }
  }
  // Links and buttons at any depth (a heading inside a large link card).
  for (let n = el; !control && n && n.nodeType === 1; n = up(n)) {
    const tag = n.tagName.toLowerCase();
    const role = (n.getAttribute('role') || '').trim().split(/\s+/)[0];
    if ((tag === 'a' && n.hasAttribute('href')) || tag === 'button' || tag === 'summary' || role === 'button' || role === 'link') control = true;
  }
  let contains = holds(el);
  // The child of `root` on the way up from `node`.
  const branch = (root, node) => {
    let b = node;
    while (b && up(b) !== root) b = up(b);
    return b;
  };
  const peers = (root) => {
    const cb = branch(root, el);
    if (!cb) return false;
    const rb = cb.getBoundingClientRect();
    const ac = rb.width * rb.height;
    return [...root.querySelectorAll('*')].slice(0, 300).filter(isControl).some((c) => {
      const b = branch(root, c);
      if (!b || b === cb || !isControl(b)) return false;
      const r = b.getBoundingClientRect();
      const ab = r.width * r.height;
      return ab > 0 && ac > 0 && ab < 3 * ac && ac < 3 * ab && Math.abs(r.height - rb.height) <= 0.5 * Math.max(r.height, rb.height);
    });
  };
  // A card whose own link or button the keyboard reaches: the click on its image or
  // price has a keyboard equivalent right there.
  let card = null;
  if (!control && !contains) {
    const r0 = el.getBoundingClientRect();
    const area0 = Math.max(48 * 48, r0.width * r0.height);
    for (let n = up(el), i = 0; n && n.nodeType === 1 && i < 8; n = up(n), i++) {
      const tag = n.tagName.toLowerCase();
      if (LANDMARK.includes(tag) || ['main', 'navigation', 'banner', 'contentinfo', 'complementary', 'form'].includes(n.getAttribute('role') || '')) break;
      const r = n.getBoundingClientRect();
      if (r.width * r.height > 4 * area0) break;
      if (holds(n)) {
        // Not a card when what was clicked looks operable on its own (a pointer cursor
        // the candidate card does not have), or when a control there is a peer item of
        // it (a chip row where one chip is a role-less div): another option, not the
        // card's own link.
        const own = getComputedStyle(el).cursor === 'pointer' && getComputedStyle(n).cursor !== 'pointer';
        // The card's own way in: a link, or its one control. A card whose only controls are
        // side actions (wishlist, add to cart) leaves its main click without a keyboard way.
        const ctrls = [...n.querySelectorAll('*')].slice(0, 300).filter(isControl);
        const link = ctrls.some((c) => (c.localName === 'a' && c.hasAttribute('href')) || (c.getAttribute('role') || '').split(/\s+/)[0] === 'link');
        if (!own && (link || ctrls.length === 1) && !peers(n)) card = n;
        break;
      }
    }
  }
  const ids = [];
  for (let n = el.parentElement; n && ids.length < 6; n = n.parentElement) if (n.id) ids.push(n.id);
  return {
    tag: el.tagName.toLowerCase(), role: (el.getAttribute('role') || '').trim() || null, dom_id: el.id || null, control,
    contains_control: contains || !!card, card_control: !!card, hidden: !!(el.closest && el.closest('[aria-hidden="true"],[inert]')),
    ancestor_ids: ids, text: (el.innerText || el.getAttribute('aria-label') || '').replace(/\s+/g, ' ').trim().slice(0, 40),
  };
}

// Native boolean evidence reuses the protected-target rule the task-state
// sampler applies (inlined in armBinaryControl: evaluate() ships only the
// function body): a credential-like or explicitly protected control's state
// must not be recorded even when its label looks harmless.

/**
 * Arm native binary-control activation evidence for one action: resolve the
 * checkbox/radio input the action activates — the element itself, or the control
 * of an associated <label> (explicit `for` or nested; `label.control`, the same
 * label rule controlOf uses) within five flat-tree levels — snapshot its boolean
 * `checked` state, and timestamp the control's own trusted `input`/`change`
 * events together with the boolean observed at event time. Reads only
 * tag/type/id and the boolean: never text or field values. opts.redactSelectors
 * are the run's opted-out regions; a control or label inside one is not armed.
 * Returns a bounded descriptor, `{protected: true}` for a protected control,
 * or null when the target is no binary control. Self-contained: no module
 * references (evaluate() ships only this function's source).
 */
export function armBinaryControl(arg, keyArg) {
  const opts = keyArg && typeof keyArg === 'object' ? keyArg : { key: keyArg };
  const key = arg && arg.nodeType === 1 ? opts.key : arg && arg.key;
  const state = key ? window[Symbol.for(key)] : null;
  if (!state) return null;
  // Every new arm replaces the previous action's watch, including no-op and
  // protected targets. The helper stays inside this page-evaluated function.
  const disposeWatch = (w) => {
    w.closed = true;
    for (const timer of w.timers || []) clearTimeout(timer);
    try { w.el.removeEventListener('input', w.onInput, true); } catch (e) { /* element gone */ }
    try { w.el.removeEventListener('change', w.onChange, true); } catch (e) { /* element gone */ }
  };
  if (state.binaryWatch) disposeWatch(state.binaryWatch);
  state.binaryWatch = null;
  const now = () => performance.timeOrigin + performance.now();
  const vvp = window.visualViewport;
  let el = arg && arg.nodeType === 1 ? arg : null;
  if (!el && arg) {
    // Points are screen (visual viewport) coordinates; hit testing takes layout ones.
    const lx = arg.x + (vvp && Math.abs(vvp.scale - 1) < 0.01 ? vvp.offsetLeft : 0);
    const ly = arg.y + (vvp && Math.abs(vvp.scale - 1) < 0.01 ? vvp.offsetTop : 0);
    el = document.elementFromPoint(lx, ly);
    while (el && el.shadowRoot) {
      const inner = el.shadowRoot.elementFromPoint(lx, ly);
      if (!inner || inner === el) break;
      el = inner;
    }
  }
  if (!el) return null;
  const binary = (n) => !!n && n.tagName === 'INPUT' && ['checkbox', 'radio'].includes((n.type || '').toLowerCase());
  const up = (n) => n.assignedSlot || n.parentElement || (n.getRootNode && n.getRootNode() instanceof ShadowRoot ? n.getRootNode().host : null);
  let ctl = null;
  let via = null;
  let label = null;
  for (let n = el, i = 0; n && n.nodeType === 1 && i < 5 && !ctl; n = up(n), i++) {
    if (binary(n)) {
      ctl = n;
      via = 'direct';
    } else if (n.tagName === 'LABEL' && binary(n.control)) {
      ctl = n.control;
      label = n;
      via = n.contains(n.control) ? 'nested_label' : 'label_for';
    }
  }
  if (!ctl) return null;
  // Privacy boundary (fail closed), the protected-target rule the task-state
  // sampler already applies: a credential-like or opted-out control's boolean
  // state is never recorded, whatever harmless element the action targeted —
  // the baseline exposing a raw id does not authorize a new state leak.
  const credential = 'input[type="password"], input[type="hidden"], input[type="url"], [data-sensitive], [data-private], [autocomplete="username"], [autocomplete*="password"], [autocomplete="one-time-code"]';
  const sensitiveId = /(?:password|passwd|secret|token|credential|api.?key|authorization)/i;
  try {
    const inside = (node, selector) => {
      for (let n = node; n && n.nodeType === 1; n = up(n)) if (n.matches(selector)) return true;
      return false;
    };
    if (ctl.matches(credential) || inside(ctl, '[data-sensitive], [data-private]')
      || (label && inside(label, '[data-sensitive], [data-private]'))
      || sensitiveId.test(`${ctl.getAttribute('name') || ''} ${ctl.id}`)
      || (label && sensitiveId.test(`${label.getAttribute('name') || ''} ${label.id}`))) return { protected: true };
    for (const selector of opts.redactSelectors || (arg && arg.redactSelectors) || []) {
      if (inside(ctl, selector) || (label && inside(label, selector))) return { protected: true };
    }
  } catch (e) { return { protected: true }; }
  const watch = {
    el: ctl, via, type: (ctl.type || '').toLowerCase(), dom_id: ctl.id && ctl.id.length <= 200 ? ctl.id : null,
    before: !!ctl.checked, events: [], timers: new Set(), closed: false,
  };
  // Only browser-trusted events on the resolved control count, and each records
  // the boolean observed at event time: a handler that immediately restores the
  // old state must not lend its timestamp to a later untrusted change.
  const rec = (kind) => (e) => {
    if (!e || !e.isTrusted || e.target !== ctl || watch.closed || watch.events.length + watch.timers.size >= 64) return;
    const event = { kind, t: now(), checked: !!ctl.checked };
    // A native event's capture listener runs before page handlers. Confirm the
    // exact event-time state after dispatch completes; a synchronous restoration
    // (including a microtask) cannot lend its timestamp to a later property flip.
    const timer = setTimeout(() => {
      watch.timers.delete(timer);
      if (!watch.closed && ctl.checked === event.checked) watch.events.push(event);
    }, 0);
    watch.timers.add(timer);
  };
  watch.onInput = rec('input');
  watch.onChange = rec('change');
  try {
    ctl.addEventListener('input', watch.onInput, true);
    ctl.addEventListener('change', watch.onChange, true);
  } catch (e) { disposeWatch(watch); return null; }
  watch.dispose = () => disposeWatch(watch);
  state.binaryWatch = watch;
  return { via: watch.via, type: watch.type, dom_id: watch.dom_id, before: watch.before };
}

/**
 * Read and clear the watch armed by armBinaryControl: the boolean state after
 * the action, whether it truly changed and stayed changed (`stable`), and the
 * first trusted input/change event for the same control not earlier than
 * args.t0 (page-clock epoch ms) whose state-at-event both differs from the
 * armed state and matches the observed end state — the event that evidences
 * the reported transition. Other trusted events are not reported: their
 * timestamps must not be inherited by a later programmatic change.
 */
export async function readBinaryControl(args) {
  const state = window[Symbol.for(args.key)];
  const w = state && state.binaryWatch;
  if (!w) return null;
  if (w.timers.size) await new Promise((resolve) => setTimeout(resolve, 0));
  if (state.binaryWatch === w) state.binaryWatch = null;
  try { w.dispose(); } catch (e) { /* element gone */ }
  const after = !!w.el.checked;
  if (args.stable_ms > 0) await new Promise((resolve) => setTimeout(resolve, args.stable_ms));
  const settled = !!w.el.checked;
  const ev = w.events.find((e) => (args.t0 == null || e.t >= args.t0) && (args.t1 == null || e.t <= args.t1)
    && e.checked !== w.before && e.checked === after) || null;
  return {
    via: w.via, type: w.type, dom_id: w.dom_id,
    before: w.before, after, changed: after !== w.before, stable: settled === after,
    event: ev ? ev.kind : null, event_ms: ev ? ev.t : null,
  };
}

/** Drop a watch that a failed action left armed: listeners off, state cleared. */
export function disposeBinaryControl(args) {
  const state = window[Symbol.for(args.key)];
  const w = state && state.binaryWatch;
  if (!w) return false;
  state.binaryWatch = null;
  try { w.dispose(); } catch (e) { /* element gone */ }
  return true;
}

/** Is the top-most element at (x, y) the target element or inside it? */
export function hitTest(el, pt) {
  // Points are screen (visual viewport) coordinates; hit testing takes layout ones.
  const vvp = window.visualViewport;
  const lx = pt.x + (vvp && Math.abs(vvp.scale - 1) < 0.01 ? vvp.offsetLeft : 0);
  const ly = pt.y + (vvp && Math.abs(vvp.scale - 1) < 0.01 ? vvp.offsetTop : 0);
  let n = document.elementFromPoint(lx, ly);
  while (n && n.shadowRoot) {
    const inner = n.shadowRoot.elementFromPoint(lx, ly);
    if (!inner || inner === n) break;
    n = inner;
  }
  for (; n; n = n.parentElement || (n.getRootNode && n.getRootNode() !== document ? n.getRootNode().host : null)) {
    if (n === el) return true;
  }
  return false;
}
