// Crops and contact sheets for the layout scan (ergoqa/scan.py): cut each region out of its
// screenshot and outline the element in red, and lay a device's screens side by side in
// scroll order. Node decodes a device-scale screenshot in well under a second; the
// pure-Python decoder takes several.
//
//   node drivers/web/crop.mjs JOBS.json
//
// JOBS.json: [{ "src": PNG, "out": PNG, "x", "y", "w", "h", "outline": [x, y, w, h], "thickness" }]
// in screenshot pixels; the outline is relative to the crop. A sheet job is
// { "sheet": [PNG, ...], "out": PNG, "cols", "scale": 1 or 0.5, "gap" }: the screens left to
// right and top to bottom on grey, each scaled by 1 or by half. Prints {"written": n}; a job
// that fails is reported on stderr and left to the caller.
import fs from 'node:fs';
import { decodePng, encodeRgbPng } from './png.mjs';

const all = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const jobs = all.filter((job) => !job.sheet);
jobs.sort((a, b) => (a.src < b.src ? -1 : a.src > b.src ? 1 : 0));
let img = null;
let imgSrc = null;
let written = 0;
for (const job of jobs) {
  try {
    if (imgSrc !== job.src) {
      img = decodePng(fs.readFileSync(job.src));
      imgSrc = job.src;
    }
    const x0 = Math.max(0, job.x);
    const y0 = Math.max(0, job.y);
    const x1 = Math.min(img.width, job.x + job.w);
    const y1 = Math.min(img.height, job.y + job.h);
    if (x1 <= x0 || y1 <= y0) continue;
    const w = x1 - x0;
    const h = y1 - y0;
    const ch = img.channels;
    const out = Buffer.alloc(w * h * 3);
    for (let y = 0; y < h; y++) {
      for (let x = 0; x < w; x++) {
        const i = ((y0 + y) * img.width + x0 + x) * ch;
        const o = (y * w + x) * 3;
        let r = img.data[i];
        let g = ch >= 3 ? img.data[i + 1] : r;
        let b = ch >= 3 ? img.data[i + 2] : r;
        const a = ch === 4 ? img.data[i + 3] : ch === 2 ? img.data[i + 1] : 255;
        if (a < 255) {
          const f = a / 255;
          r = r * f + 255 * (1 - f);
          g = g * f + 255 * (1 - f);
          b = b * f + 255 * (1 - f);
        }
        out[o] = r;
        out[o + 1] = g;
        out[o + 2] = b;
      }
    }
    const [ox, oy, ow, oh] = job.outline;
    const t = Math.max(1, job.thickness | 0);
    const fill = (ax, ay, bx, by) => {
      for (let y = Math.max(0, ay); y < Math.min(h, by); y++) {
        for (let x = Math.max(0, ax); x < Math.min(w, bx); x++) {
          const o = (y * w + x) * 3;
          out[o] = 230;
          out[o + 1] = 30;
          out[o + 2] = 30;
        }
      }
    };
    fill(ox, oy, ox + ow, oy + t);
    fill(ox, oy + oh - t, ox + ow, oy + oh);
    fill(ox, oy, ox + t, oy + oh);
    fill(ox + ow - t, oy, ox + ow, oy + oh);
    fs.writeFileSync(job.out, encodeRgbPng(w, h, out));
    written++;
  } catch (err) {
    console.error(`${job.out}: ${String(err.message).split('\n')[0]}`);
  }
}

// RGB over white, halved by averaging 2x2 blocks when scale is 0.5.
function rgbOf(img, scale) {
  const f = scale < 1 ? 2 : 1;
  const w = Math.floor(img.width / f);
  const h = Math.floor(img.height / f);
  const ch = img.channels;
  const rgb = Buffer.alloc(w * h * 3);
  for (let y = 0; y < h; y++) {
    for (let x = 0; x < w; x++) {
      let r = 0;
      let g = 0;
      let b = 0;
      for (let dy = 0; dy < f; dy++) {
        for (let dx = 0; dx < f; dx++) {
          const i = ((y * f + dy) * img.width + x * f + dx) * ch;
          const a = ch === 4 ? img.data[i + 3] / 255 : ch === 2 ? img.data[i + 1] / 255 : 1;
          const v = img.data[i];
          r += (v * a + 255 * (1 - a));
          g += ((ch >= 3 ? img.data[i + 1] : v) * a + 255 * (1 - a));
          b += ((ch >= 3 ? img.data[i + 2] : v) * a + 255 * (1 - a));
        }
      }
      const o = (y * w + x) * 3;
      const n = f * f;
      rgb[o] = Math.round(r / n);
      rgb[o + 1] = Math.round(g / n);
      rgb[o + 2] = Math.round(b / n);
    }
  }
  return { width: w, height: h, rgb };
}

for (const job of all.filter((j) => j.sheet)) {
  try {
    const tiles = job.sheet.map((src) => rgbOf(decodePng(fs.readFileSync(src)), job.scale || 1));
    const gap = job.gap ?? 8;
    const cols = Math.max(1, Math.min(job.cols || 1, tiles.length));
    const tw = Math.max(...tiles.map((t) => t.width));
    const th = Math.max(...tiles.map((t) => t.height));
    const rows = Math.ceil(tiles.length / cols);
    const W = cols * tw + (cols - 1) * gap;
    const H = rows * th + (rows - 1) * gap;
    const out = Buffer.alloc(W * H * 3, 160);
    tiles.forEach((t, k) => {
      const ox = (k % cols) * (tw + gap);
      const oy = Math.floor(k / cols) * (th + gap);
      for (let y = 0; y < t.height; y++) t.rgb.copy(out, ((oy + y) * W + ox) * 3, y * t.width * 3, (y + 1) * t.width * 3);
    });
    fs.writeFileSync(job.out, encodeRgbPng(W, H, out));
    written++;
  } catch (err) {
    console.error(`${job.out}: ${String(err.message).split('\n')[0]}`);
  }
}
console.log(JSON.stringify({ written }));

