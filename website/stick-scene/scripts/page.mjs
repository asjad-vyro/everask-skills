// Checks a page that embeds scenes the way a visitor sees it: loads it at desktop and phone widths,
// scrolls each <stick-scene> into view, waits for the action to play, and screenshots the page.
// Reports page errors and any scene that never started or drew nothing.
// usage: node page.mjs --url <file path or http(s) URL> [--out /tmp/page] [--wait 3] [--widths 1280,390]
// Writes <out>-<width>.png per width. Exit code 2 when something is wrong.
import { writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
import { launch, parseArgs } from './browser.mjs';

const opt = parseArgs(process.argv.slice(2));
if (!opt.url) {
  console.error('need --url <page.html or URL>');
  process.exit(1);
}
const url = /^[a-z]+:\/\//i.test(opt.url) ? opt.url : pathToFileURL(resolve(opt.url)).href;
const widths = (opt.widths || '1280,390').split(',').map(Number).filter(Boolean);
const wait = Number(opt.wait || 3) * 1000;
const base = resolve(opt.out || 'page');

let b;
try {
  b = await launch();
} catch (e) {
  console.error(e.message);
  process.exit(1);
}
const problems = [];
for (const w of widths) {
  const p = await b.newPage({ width: w, height: 900, scale: 1 });
  await p.goto(url);
  await p.waitFor('document.readyState === "complete"', 10000);
  const n = await p.evaluate(() => document.querySelectorAll('stick-scene').length);
  if (!n) {
    problems.push(`${w}px: no <stick-scene> on the page`);
  }
  // Scroll through every scene so play="view" fires, then let the last action run.
  for (let i = 0; i < n; i++) {
    await p.evaluate((k) => document.querySelectorAll('stick-scene')[k].scrollIntoView({ block: 'center' }), i);
    await new Promise((r) => setTimeout(r, 400));
  }
  await new Promise((r) => setTimeout(r, wait));
  await p.evaluate(() => scrollTo(0, 0));
  const report = await p.evaluate(() =>
    [...document.querySelectorAll('stick-scene')].map((el) => {
      const id = el.getAttribute('scene');
      const r = el.getBoundingClientRect();
      if (!el.v || !el.cv) {
        return { id, ok: false, why: 'never started (wrong id, or stick.js loaded after the scene script?)' };
      }
      if (r.width < 40 || r.height < 40) {
        return { id, ok: false, why: `box is ${Math.round(r.width)}x${Math.round(r.height)}px; give it a CSS height` };
      }
      const g = el.cv.getContext('2d');
      const d = g.getImageData(0, 0, el.cv.width, el.cv.height).data;
      let ink = 0;
      for (let i = 0; i < d.length; i += 4 * 7) {
        if (d[i + 3] > 0 && d[i] + d[i + 1] + d[i + 2] < 200) {
          ink++;
        }
      }
      return ink > 20 ? { id, ok: true } : { id, ok: false, why: 'canvas is blank' };
    }),
  );
  for (const s of report) {
    if (!s.ok) {
      problems.push(`${w}px: ${s.id}: ${s.why}`);
    }
  }
  const out = `${base}-${w}.png`;
  writeFileSync(out, await p.screenshot('body'));
  console.log(`${out}  (${report.filter((s) => s.ok).length}/${report.length} scenes drawn)`);
  problems.push(...p.errors.map((e) => `${w}px: ${e}`));
}
await b.close();
if (problems.length) {
  console.log('problems:\n' + [...new Set(problems)].join('\n'));
  process.exitCode = 2;
}
