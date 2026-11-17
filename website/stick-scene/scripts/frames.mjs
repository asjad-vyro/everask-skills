// Renders a scene frozen at several moments into one contact sheet PNG, and reports page errors.
// usage: node frames.mjs --scene <id> --src <scene.js> [--src more.js] [--frames "idle:0,idle:3,s:1,s:2.5"] [--out sheet.png] [--fw 360 --fh 230 --cols 4] [--theme '{"butter":"#…"}']
// frames: idle:<seconds> = resting loop at that time; s:<seconds> = into the action; u:<0..1> = fraction of the action.
//         Add @<n> to render the nth play (s:2.4@1).
// Needs only Node and a Chrome binary (see browser.mjs). Exit code 2 when the page logged errors.
import { writeFileSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { launch, parseArgs } from './browser.mjs';

const opt = parseArgs(process.argv.slice(2));
if (!opt.scene || !opt.src.length) {
  console.error('need --scene <id> and --src <scene.js>');
  process.exit(1);
}
const here = dirname(fileURLToPath(import.meta.url));
const preview = pathToFileURL(resolve(here, '../templates/preview.html'));
const frames = opt.frames || 'idle:0,idle:2.5,u:0.1,u:0.25,u:0.4,u:0.55,u:0.7,u:0.85';
const q = new URLSearchParams({ scene: opt.scene, frames, cols: opt.cols || '4' });
for (const s of opt.src) {
  q.append('src', pathToFileURL(resolve(s)).href);
}
if (opt.fw) q.set('fw', opt.fw);
if (opt.fh) q.set('fh', opt.fh);
if (opt.theme) q.set('theme', opt.theme);

let b;
try {
  b = await launch();
} catch (e) {
  console.error(e.message);
  process.exit(1);
}
const cols = Number(opt.cols || 4), fw = Number(opt.fw || 360);
const p = await b.newPage({ width: cols * (fw + 14) + 60, height: 1000, scale: 2 });
await p.goto(`${preview.href}?${q}`);
if (!(await p.waitFor('document.body && document.body.dataset.ready'))) {
  p.errors.push('scene never became ready (wrong id or a throw in draw?)');
}
const out = resolve(opt.out || `${opt.scene}-frames.png`);
try {
  writeFileSync(out, await p.screenshot('#root'));
} catch (e) {
  p.errors.push(`screenshot failed: ${e.message}`);
}
await b.close();
console.log(out);
if (p.errors.length) {
  console.log('errors:\n' + p.errors.join('\n'));
  process.exitCode = 2;
}
