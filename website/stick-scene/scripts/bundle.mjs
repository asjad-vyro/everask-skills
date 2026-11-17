// Builds the deliverables for one or more finished scenes:
//   --out page.html  one self-contained HTML page (runtime, scenes and the Balsamiq Sans face inlined,
//                    no network at all), each scene in a framed card. Publish it as kind="html_preview".
//   --kit <dir>      the embed kit for the user's own site: stick.js, the scene files, the font,
//                    and embed.html with the markup and frame CSS to paste.
// usage: node bundle.mjs --scene <id>[,<id>...] --src <scene.js> [--src more.js] --out page.html
//                        [--kit dir] [--title "…"] [--play view|click|hover|loop|idle] [--height 230] [--width 560]
//                        [--theme '{"butter":"#…"}']
import { copyFileSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { basename, dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { parseArgs } from './browser.mjs';

const opt = parseArgs(process.argv.slice(2));
if (!opt.scene || !opt.src.length || !(opt.out || opt.kit)) {
  console.error('need --scene <id>[,<id>...], --src <scene.js> and --out <page.html> and/or --kit <dir>');
  process.exit(1);
}
const here = dirname(fileURLToPath(import.meta.url));
const runtimePath = resolve(here, '../runtime/stick.js');
const fontPath = resolve(here, '../assets/balsamiq-sans-400.woff2');
const ids = opt.scene.split(',').map((s) => s.trim()).filter(Boolean);
const play = opt.play || 'view';
const height = Number(opt.height || 230);
const width = Number(opt.width || 560);
const title = opt.title || ids.join(', ');
let theme = '';
if (opt.theme) {
  JSON.parse(opt.theme); // fail early on bad JSON
  theme = `STICK.theme(${opt.theme});`;
}
const srcs = opt.src.map((s) => resolve(s));
for (const s of srcs) {
  const code = readFileSync(s, 'utf8');
  if (code.includes('</script')) {
    console.error(`${s} contains "</script", which would end the inline script early. Split the string ('<' + '/script').`);
    process.exit(1);
  }
}
const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;');
const attrs = `play="${esc(play)}"`;

// Shared frame: a rounded card, 1px border, white, a faint dot grid, floor band kept on.
const frameCss = `.stick-frame{max-width:${width}px;margin:0 auto 20px;border:1px solid #e6e6e6;border-radius:14px;overflow:hidden;background:#fff radial-gradient(#e6e6e6 1px,transparent 1.2px) 0 0/14px 14px}
.stick-frame stick-scene{height:${height}px}`;

if (opt.out) {
  const font = readFileSync(fontPath).toString('base64');
  const inline = (code) => `<script>\n${code}\n</script>`;
  const cards = ids.map((id) => `  <div class="stick-frame"><stick-scene scene="${esc(id)}" ${attrs} no-font></stick-scene></div>`).join('\n');
  const hint = play === 'view' || play === 'click' ? 'Click a scene to play it again.' : play === 'hover' ? 'Hover a scene to play it.' : '';
  const html = `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(title)}</title>
<style>
@font-face{font-family:'Balsamiq Sans';font-weight:400;font-display:block;src:url(data:font/woff2;base64,${font}) format('woff2')}
html,body{margin:0;background:#fff;color:#555;font:13px/1.4 system-ui,sans-serif}
main{padding:24px 16px}
${frameCss}
.stick-hint{text-align:center;color:#999;font-size:12px;margin:0}
</style>
</head>
<body>
<main>
${cards}
  ${hint ? `<p class="stick-hint">${hint}</p>` : ''}
</main>
${inline(readFileSync(runtimePath, 'utf8'))}
${srcs.map((s) => inline(readFileSync(s, 'utf8'))).join('\n')}
${theme ? inline(theme) : ''}
<script>document.fonts && document.fonts.load("400 10px 'Balsamiq Sans'");</script>
</body>
</html>
`;
  const out = resolve(opt.out);
  mkdirSync(dirname(out), { recursive: true });
  writeFileSync(out, html);
  console.log(out);
}

if (opt.kit) {
  const kit = resolve(opt.kit);
  mkdirSync(kit, { recursive: true });
  copyFileSync(runtimePath, resolve(kit, 'stick.js'));
  copyFileSync(fontPath, resolve(kit, 'balsamiq-sans-400.woff2'));
  copyFileSync(resolve(here, '../assets/OFL.txt'), resolve(kit, 'OFL-balsamiq-sans.txt'));
  copyFileSync(resolve(here, '../LICENSE'), resolve(kit, 'LICENSE-stick-scene.txt'));
  const names = srcs.map((s) => {
    copyFileSync(s, resolve(kit, basename(s)));
    return basename(s);
  });
  const embed = `<!-- stick-scene embed. Put these files in your static folder as /scenes/ (or change the paths).
     stick.js must load before every scene script; deferred scripts run in document order.
     Astro: use <script is:inline ... defer>.
     Self-hosted font: keep the @font-face and no-font. To load Balsamiq Sans from Google Fonts instead,
     drop both. -->
<style>
@font-face{font-family:'Balsamiq Sans';font-weight:400;font-display:swap;src:url(/scenes/balsamiq-sans-400.woff2) format('woff2')}
${frameCss}
</style>

${ids.map((id) => `<div class="stick-frame"><stick-scene scene="${esc(id)}" ${attrs} no-font></stick-scene></div>`).join('\n')}

<script src="/scenes/stick.js" defer></script>
${names.map((n) => `<script src="/scenes/${n}" defer></script>`).join('\n')}
${theme ? `<script>addEventListener('DOMContentLoaded', () => ${theme.replace(/;$/, '')});</script>\n` : ''}`;
  writeFileSync(resolve(kit, 'embed.html'), embed);
  console.log(kit);
}
