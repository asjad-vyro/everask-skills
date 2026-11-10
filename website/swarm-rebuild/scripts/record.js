#!/usr/bin/env node
// Records a Swarm Rebuild video of a web page.
//
// Headless Chrome opens the page, swarm.js (next to this file) blanks it, and a
// swarm of cursors builds it back with Tour on. A virtual clock steps the
// animation one frame at a time, so the video is smooth however slow the
// machine is. The swarm's sounds are rendered offline from its event log and
// mixed in. If Chrome dies partway, the video fades back to the page from there.
//
//   node record.js --url https://example.com --preview /tmp/.scratch/swarm/preview.png
//   node record.js --url https://example.com --out /tmp/.scratch/swarm/swarm-rebuild.mp4
//
// Options:
//   --format landscape|vertical|square  1920x1080 (default), 1080x1920 or 1080x1080
//   --speed auto|1|2|3   build speed; auto (default) picks it from how many pieces the page has
//   --max-seconds N      longest video; past it the swarm hands back to the page (default 75)
//   --hide "a, b"        CSS selectors to remove first: cookie banners, chat bubbles, popups
//   --end live|hold      end on the real page (default) or on the finished rebuild
//   --no-sound           silent video
//   --wait MS            extra wait after the page loads (default 1500)
//   --budget S           wall-clock seconds to finish in, encoding included (default 540)
//
// Prints one JSON line at the end. Exit code 1 means it failed; the JSON says why.
// SWARM_DEBUG=1 logs progress, and Chrome's own log, to stderr.

const { execSync, spawn } = require("node:child_process");
const fs = require("node:fs");
const { createRequire } = require("node:module");
const os = require("node:os");
const path = require("node:path");
const { pathToFileURL } = require("node:url");

const FORMATS = {
  landscape: { width: 1280, height: 720, scale: 1.5 },
  vertical: { width: 405, height: 720, scale: 8 / 3 },
  square: { width: 720, height: 720, scale: 1.5 },
};
const FPS = 30;
const PRE_SECONDS = 1; // the real page, before it dissolves
const HOLD_SECONDS = 3; // the finished rebuild and its closing chord
const TAIL_SECONDS = 2.2; // the fade back to the real page

// For one screenshot, show only what the DOM can't give back (WebGL canvases,
// playing video, cross-origin iframes) so the swarm can crop it, as the extension does.
const MEDIA_ONLY_CSS = `
html body *:not(canvas):not(video):not(iframe):not(embed):not(object) { visibility: hidden !important; }
html body canvas, html body video, html body iframe, html body embed, html body object { visibility: visible !important; }
`;

class UserError extends Error {}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const debug = (...parts) => {
  if (process.env.SWARM_DEBUG) process.stderr.write(`[swarm ${process.uptime().toFixed(1)}s] ${parts.join(" ")}\n`);
};

function kill(browser) {
  const proc = browser && browser.process();
  if (proc && proc.exitCode === null && proc.signalCode === null) proc.kill("SIGKILL");
}

function done(result, code = 0) {
  process.stdout.write(JSON.stringify(result) + "\n");
  process.exit(code);
}

function parseArgs(argv) {
  const o = {
    url: "", out: "", preview: "", format: "landscape", speed: 0, maxSeconds: 75,
    hide: "", end: "live", sound: true, wait: 1500, budget: 540,
  };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    const value = () => {
      if (i + 1 >= argv.length) throw new UserError(`${a} needs a value`);
      return argv[++i];
    };
    if (a === "--url") o.url = value();
    else if (a === "--out") o.out = value();
    else if (a === "--preview") o.preview = value();
    else if (a === "--format") o.format = value();
    else if (a === "--speed") {
      const v = value();
      o.speed = v === "auto" ? 0 : Number(v);
    }
    else if (a === "--max-seconds") o.maxSeconds = Number(value());
    else if (a === "--hide") o.hide = value();
    else if (a === "--end") o.end = value();
    else if (a === "--no-sound") o.sound = false;
    else if (a === "--wait") o.wait = Number(value());
    else if (a === "--budget") o.budget = Number(value());
    else throw new UserError(`unknown option ${a}`);
  }
  if (!o.url) throw new UserError("--url is required");
  if (!o.out && !o.preview) throw new UserError("give --out (a video) or --preview (a still)");
  if (!FORMATS[o.format]) throw new UserError("--format is landscape, vertical or square");
  if (![0, 1, 2, 3].includes(o.speed)) throw new UserError("--speed is auto, 1, 2 or 3");
  if (!["live", "hold"].includes(o.end)) throw new UserError("--end is live or hold");
  if (!(o.maxSeconds >= 10 && o.maxSeconds <= 180)) throw new UserError("--max-seconds is 10 to 180");
  if (!(o.wait >= 0 && o.wait <= 30000)) throw new UserError("--wait is 0 to 30000");
  if (!(o.budget >= 60)) throw new UserError("--budget is at least 60");
  if (!/^(https?|file):\/\//i.test(o.url)) {
    if (fs.existsSync(o.url)) o.url = pathToFileURL(path.resolve(o.url)).href;
    else if (/^[\w-]+(\.[\w-]+)+(\/|$)/.test(o.url)) o.url = `https://${o.url}`;
    else throw new UserError(`not a URL or a file: ${o.url}`);
  }
  return o;
}

// puppeteer-core ships with the hyperframes CLI in the sandbox; use that copy.
function loadPuppeteer() {
  const pick = (m) => (m && m.default && m.default.launch ? m.default : m);
  const attempts = [];
  const tryLoad = (load) => {
    try {
      return pick(load());
    } catch (err) {
      attempts.push(String(err.message).split("\n")[0]);
      return null;
    }
  };
  let mod = process.env.PUPPETEER_CORE ? tryLoad(() => require(process.env.PUPPETEER_CORE)) : null;
  mod = mod || tryLoad(() => require("puppeteer-core"));
  let root = "";
  try {
    root = execSync("npm root -g", { encoding: "utf8", stdio: ["ignore", "pipe", "ignore"] }).trim();
  } catch {}
  if (!mod && root) {
    mod = tryLoad(() => createRequire(path.join(root, "hyperframes", "package.json"))("puppeteer-core"))
      || tryLoad(() => require(path.join(root, "puppeteer-core")))
      || tryLoad(() => require(path.join(root, "puppeteer")));
  }
  if (!mod) {
    const dir = path.join(os.homedir(), ".cache", "swarm-rebuild");
    fs.mkdirSync(dir, { recursive: true });
    try {
      execSync("npm install --no-audit --no-fund --silent --prefix . puppeteer-core@25", { cwd: dir, stdio: "ignore", timeout: 120000 });
      mod = tryLoad(() => require(path.join(dir, "node_modules", "puppeteer-core")));
    } catch (err) {
      attempts.push(`npm install puppeteer-core: ${err.message}`);
    }
  }
  if (!mod) throw new UserError(`puppeteer-core not found (${attempts.join("; ")})`);
  return mod;
}

// chrome-headless-shell is pre-cached under ~/.cache/puppeteer in the sandbox.
function findChrome() {
  if (process.env.CHROME_PATH && fs.existsSync(process.env.CHROME_PATH)) {
    return { path: process.env.CHROME_PATH, shell: /headless-shell/.test(process.env.CHROME_PATH) };
  }
  const roots = [...new Set([process.env.PUPPETEER_CACHE_DIR, path.join(os.homedir(), ".cache", "puppeteer"), "/root/.cache/puppeteer"].filter(Boolean))];
  const found = [];
  const list = (dir) => {
    try {
      return fs.readdirSync(dir);
    } catch {
      return [];
    }
  };
  for (const root of roots) {
    for (const kind of ["chrome-headless-shell", "chrome"]) {
      for (const version of list(path.join(root, kind))) {
        for (const sub of list(path.join(root, kind, version))) {
          const base = path.join(root, kind, version, sub);
          const exes = kind === "chrome"
            ? [path.join(base, "chrome"), path.join(base, "Google Chrome for Testing.app", "Contents", "MacOS", "Google Chrome for Testing")]
            : [path.join(base, "chrome-headless-shell")];
          for (const exe of exes) if (fs.existsSync(exe)) found.push({ path: exe, shell: kind !== "chrome", version });
        }
      }
    }
  }
  const num = (v) => (v.match(/\d+/g) || []).map(Number);
  found.sort((a, b) => {
    if (a.shell !== b.shell) return a.shell ? -1 : 1;
    const x = num(a.version);
    const y = num(b.version);
    for (let i = 0; i < Math.max(x.length, y.length); i++) if ((x[i] || 0) !== (y[i] || 0)) return (y[i] || 0) - (x[i] || 0);
    return 0;
  });
  return found[0] || null;
}

function getChrome() {
  let chrome = findChrome();
  if (!chrome) {
    try {
      execSync("npx --yes @puppeteer/browsers install chrome-headless-shell@stable --path ~/.cache/puppeteer", { stdio: "ignore", timeout: 180000 });
    } catch {}
    chrome = findChrome();
  }
  if (!chrome) throw new UserError("no headless Chrome found under ~/.cache/puppeteer, and installing one failed");
  return chrome;
}

// Runs in the page: fixed and sticky elements that may be cookie banners,
// popups or chat bubbles, with a selector for --hide.
function findOverlays() {
  const vw = innerWidth;
  const vh = innerHeight;
  const listed = [];
  const out = [];
  const css = (s) => (window.CSS && CSS.escape ? CSS.escape(s) : s);
  const selector = (el) => {
    if (el.id) return `#${css(el.id)}`;
    const classes = [...el.classList].slice(0, 2).map((c) => `.${css(c)}`).join("");
    return el.tagName.toLowerCase() + classes;
  };
  for (const el of document.body ? document.body.querySelectorAll("*") : []) {
    if (listed.some((p) => p.contains(el))) continue;
    const cs = getComputedStyle(el);
    if (cs.position !== "fixed" && cs.position !== "sticky") continue;
    if (cs.display === "none" || cs.visibility === "hidden" || Number(cs.opacity) === 0) continue;
    const r = el.getBoundingClientRect();
    const w = Math.min(r.right, vw) - Math.max(r.left, 0);
    const h = Math.min(r.bottom, vh) - Math.max(r.top, 0);
    if (w <= 0 || h <= 0 || (w * h) / (vw * vh) < 0.002) continue;
    listed.push(el);
    const sel = selector(el);
    let matches = 0;
    try {
      matches = document.querySelectorAll(sel).length;
    } catch {}
    out.push({
      selector: sel,
      matches,
      position: cs.position,
      where: r.top <= vh * 0.1 ? "top" : r.bottom >= vh * 0.9 ? "bottom" : "middle",
      share: `${Math.round(((w * h) / (vw * vh)) * 1000) / 10}%`,
      text: (el.innerText || el.getAttribute("aria-label") || el.getAttribute("title") || "").replace(/\s+/g, " ").trim().slice(0, 90),
    });
    if (out.length >= 12) break;
  }
  return out;
}

// Runs in the page. Replaces the clock the swarm reads (performance.now,
// requestAnimationFrame, setTimeout, setInterval) with one that only moves when
// tick() is called, and pins the swarm's CSS transitions to that clock.
function installClock() {
  if (window.__vclock) return window.__vclock.now;
  let vt = performance.now();
  let reads = 0;
  let seq = 1e7;
  const timers = new Map();
  let rafs = new Map();
  const started = new WeakMap();
  const flush = () => new Promise((resolve) => {
    const ch = new MessageChannel();
    ch.port1.onmessage = () => resolve();
    ch.port2.postMessage(0);
  });
  // A page script that busy-waits on performance.now() would spin forever on a
  // stopped clock, so after very many reads in one frame the clock creeps forward.
  performance.now = () => (++reads > 50000 ? (vt += 0.01) : vt);
  window.setTimeout = (fn, ms, ...args) => {
    const id = ++seq;
    timers.set(id, { due: vt + Math.max(0, Number(ms) || 0), fn, args, every: 0 });
    return id;
  };
  window.setInterval = (fn, ms, ...args) => {
    const id = ++seq;
    const every = Math.max(4, Number(ms) || 0);
    timers.set(id, { due: vt + every, fn, args, every });
    return id;
  };
  window.clearTimeout = window.clearInterval = (id) => {
    timers.delete(id);
  };
  window.requestAnimationFrame = (fn) => {
    const id = ++seq;
    rafs.set(id, fn);
    return id;
  };
  window.cancelAnimationFrame = (id) => {
    rafs.delete(id);
  };
  const clock = {
    host: null,
    get now() {
      return vt;
    },
    async tick(ms) {
      reads = 0;
      const target = vt + ms;
      for (let guard = 0; guard < 20000; guard++) {
        let id = null;
        let next = null;
        for (const [k, t] of timers) if (t.due <= target && (!next || t.due < next.due)) {
          id = k;
          next = t;
        }
        if (!next) break;
        vt = Math.max(vt, next.due);
        if (next.every) next.due += next.every;
        else timers.delete(id);
        try {
          if (typeof next.fn === "function") next.fn(...next.args);
        } catch (err) {
          console.error(err);
        }
        await flush();
      }
      vt = Math.max(vt, target);
      const callbacks = [...rafs.values()];
      rafs = new Map();
      for (const cb of callbacks) {
        try {
          cb(vt);
        } catch (err) {
          console.error(err);
        }
      }
      await flush();
      const app = window.__swarmRebuild && window.__swarmRebuild.app;
      if (app && app.view && app.view.host) clock.host = app.view.host;
      const host = clock.host;
      // A video has no one to click the swarm's buttons, so show only its counter.
      if (host && host.shadowRoot && !host.shadowRoot.getElementById("__swarm_rec")) {
        const style = document.createElement("style");
        style.id = "__swarm_rec";
        style.textContent = ".hud button{display:none!important}.hud{padding-right:12px!important}";
        host.shadowRoot.appendChild(style);
      }
      if (host && host.isConnected) {
        const anims = [...host.getAnimations(), ...(host.shadowRoot ? host.shadowRoot.getAnimations() : [])];
        for (const a of anims) {
          let s = started.get(a);
          if (s === undefined) {
            s = vt - ms;
            started.set(a, s);
            try {
              a.pause();
            } catch {}
          }
          try {
            const end = a.effect ? a.effect.getComputedTiming().endTime : Infinity;
            if (vt - s >= end && Number.isFinite(end)) a.finish();
            else a.currentTime = vt - s;
          } catch {}
        }
      }
    },
  };
  window.__vclock = clock;
  window.__swarmSfxLog = [];
  window.__swarmStep = async (ms) => {
    await clock.tick(ms);
    const app = window.__swarmRebuild && window.__swarmRebuild.app;
    const E = app && app.engine;
    return {
      alive: !!app,
      ready: !!(E && E.ready),
      started: !!(E && E.started),
      complete: !!(app && app.complete),
      layers: E && E.tasks ? E.tasks.length : 0,
      built: E ? E.doneCount || 0 : 0,
      agents: E && E.cursors ? E.cursors.length : 0,
      host: !!(clock.host && clock.host.isConnected),
      sfx: window.__swarmSfxLog.splice(0),
    };
  };
  return vt;
}

// Runs in the page: the Tour button (auto-scroll at the pace the swarm keeps
// up with), then the speed button until it shows the asked-for speed.
function pressTour(speed) {
  const app = window.__swarmRebuild && window.__swarmRebuild.app;
  if (!app || !app.view || !app.view.root) return false;
  const root = app.view.root;
  const tour = root.querySelector('[data-a="tour"]');
  if (tour && !app.tour) tour.click();
  const fast = root.querySelector('[data-a="speed"]');
  for (let i = 0; fast && i < 3 && app.engine.speed !== speed; i++) fast.click();
  return app.tour;
}

// Runs in a blank tab with swarm.js loaded: replays the swarm's sound events
// (each with its time in the video) through the swarm's own sound engine into an
// OfflineAudioContext, and returns a 16-bit stereo WAV as base64.
async function renderAudio({ log, seconds }) {
  const rate = 48000;
  const ctx = new OfflineAudioContext(2, Math.ceil(seconds * rate), rate);
  const sound = new window.__swarmRebuild.debug.Sound();
  sound.on = true;
  if (!sound.init(ctx)) throw new Error("the sound engine didn't start");
  const events = log.filter((ev) => ev.at >= 0 && ev.at <= seconds - 0.05 && typeof sound[ev.fn] === "function").sort((a, b) => a.at - b.at);
  // Make each sound's nodes just before it plays, as the live page does. A graph
  // holding every node of a long video at once takes far too long to render.
  const STEP = 0.25;
  let next = 0;
  let played = 0;
  const playUntil = (end) => {
    for (; next < events.length && events[next].at < end; next++) {
      const ev = events[next];
      sound.fakeNow = ev.at;
      try {
        sound[ev.fn](...ev.args);
        played++;
      } catch {}
    }
  };
  playUntil(STEP);
  for (let at = STEP; at < seconds - 0.05; at += STEP) {
    const from = at;
    ctx.suspend(from).then(() => {
      playUntil(from + STEP);
      return ctx.resume();
    }).catch(() => {});
  }
  const buf = await ctx.startRendering();
  const n = buf.length;
  const channels = [buf.getChannelData(0), buf.getChannelData(1)];
  const view = new DataView(new ArrayBuffer(44 + n * 4));
  const text = (o, s) => {
    for (let i = 0; i < s.length; i++) view.setUint8(o + i, s.charCodeAt(i));
  };
  text(0, "RIFF");
  view.setUint32(4, 36 + n * 4, true);
  text(8, "WAVE");
  text(12, "fmt ");
  view.setUint32(16, 16, true);
  view.setUint16(20, 1, true);
  view.setUint16(22, 2, true);
  view.setUint32(24, rate, true);
  view.setUint32(28, rate * 4, true);
  view.setUint16(32, 4, true);
  view.setUint16(34, 16, true);
  text(36, "data");
  view.setUint32(40, n * 4, true);
  let o = 44;
  for (let i = 0; i < n; i++) {
    for (const ch of channels) {
      const v = Math.max(-1, Math.min(1, ch[i]));
      view.setInt16(o, v < 0 ? v * 0x8000 : v * 0x7fff, true);
      o += 2;
    }
  }
  const data = await new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result).split(",")[1]);
    reader.onerror = () => reject(reader.error);
    reader.readAsDataURL(new Blob([view.buffer], { type: "audio/wav" }));
  });
  return { data, events: events.length, played };
}

// First pass of loudnorm: the sound's measured loudness, or null if there's too little of it.
function measureLoudness(file) {
  return new Promise((resolve) => {
    const ff = spawn("ffmpeg", ["-hide_banner", "-nostats", "-i", file, "-af", "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"], { stdio: ["ignore", "ignore", "pipe"] });
    let err = "";
    ff.stderr.on("data", (d) => (err += d));
    ff.on("error", () => resolve(null));
    ff.on("close", () => {
      try {
        const m = JSON.parse(err.slice(err.lastIndexOf("{"), err.lastIndexOf("}") + 1));
        resolve(Number.isFinite(Number(m.input_i)) && Number(m.input_i) > -70 ? m : null);
      } catch {
        resolve(null);
      }
    });
  });
}

function runFfmpeg(args) {
  return new Promise((resolve, reject) => {
    const ff = spawn("ffmpeg", ["-hide_banner", "-loglevel", "error", "-y", ...args], { stdio: ["ignore", "ignore", "pipe"] });
    let err = "";
    ff.stderr.on("data", (d) => (err += d));
    ff.on("error", reject);
    ff.on("close", (code) => (code === 0 ? resolve() : reject(new Error(`ffmpeg failed: ${err.slice(-800)}`))));
  });
}

function launchBrowser(puppeteer, chrome, fmt) {
  return puppeteer.launch({
    executablePath: chrome.path,
    headless: chrome.shell ? "shell" : true,
    args: [
      "--no-sandbox",
      "--disable-dev-shm-usage",
      "--hide-scrollbars",
      "--mute-audio",
      "--autoplay-policy=no-user-gesture-required",
      "--force-color-profile=srgb",
      "--disable-background-timer-throttling",
      "--disable-renderer-backgrounding",
      "--disable-backgrounding-occluded-windows",
      `--window-size=${fmt.width},${fmt.height}`,
    ],
    defaultViewport: { width: fmt.width, height: fmt.height, deviceScaleFactor: fmt.scale },
    protocolTimeout: 90000,
    dumpio: !!process.env.SWARM_DEBUG,
  });
}

const connected = (browser) => (typeof browser.connected === "boolean" ? browser.connected : browser.isConnected());

// When Chrome dies before the swarm can hand back, fade from the last frame to
// the real page with ffmpeg instead, the way "Go live" does.
function handBack(video, still, seconds, fmt, out) {
  const w = Math.round(fmt.width * fmt.scale);
  const h = Math.round(fmt.height * fmt.scale);
  return runFfmpeg([
    "-i", video, "-loop", "1", "-framerate", String(FPS), "-t", String(TAIL_SECONDS), "-i", still,
    "-filter_complex",
    `[0:v]tpad=stop_mode=clone:stop_duration=${TAIL_SECONDS},setsar=1,fps=${FPS},settb=AVTB,format=yuv420p[a];` +
      `[1:v]scale=${w}:${h},setsar=1,fps=${FPS},settb=AVTB,format=yuv420p[b];` +
      `[a][b]xfade=transition=fade:duration=1.15:offset=${seconds.toFixed(3)},format=yuv420p[v]`,
    "-map", "[v]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-r", String(FPS), "-movflags", "+faststart", out,
  ]);
}

async function main() {
  const opts = parseArgs(process.argv.slice(2));
  const t0wall = Date.now();
  const wall = () => (Date.now() - t0wall) / 1000;
  const fmt = FORMATS[opts.format];
  const swarmSrc = fs.readFileSync(path.join(__dirname, "swarm.js"), "utf8");
  const puppeteer = loadPuppeteer();
  const chrome = getChrome();
  let browser = await launchBrowser(puppeteer, chrome, fmt);
  // If the page or Chrome hangs, still answer before the terminal's 10-minute limit.
  setTimeout(() => {
    kill(browser);
    done({ ok: false, error: `gave up after ${opts.budget + 40} seconds; the page or Chrome hung` }, 1);
  }, (opts.budget + 40) * 1000).unref();
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "swarm-rebuild-"));
  let crashed = "";
  try {
    const page = await browser.newPage();
    page.on("error", (err) => {
      crashed = `Chrome's tab crashed (${String(err.message).split("\n")[0]})`;
    });
    if (process.env.SWARM_DEBUG) {
      page.on("pageerror", (err) => process.stderr.write(`[pageerror] ${String(err.message).split("\n")[0]}\n`));
    }
    await page.setViewport({ width: fmt.width, height: fmt.height, deviceScaleFactor: fmt.scale });
    await page.setBypassCSP(true);
    await page.setUserAgent((await browser.userAgent()).replace(/HeadlessChrome/g, "Chrome"));
    let status = null;
    try {
      const resp = await page.goto(opts.url, { waitUntil: "load", timeout: 30000 });
      status = resp ? resp.status() : null;
    } catch (err) {
      if (!/timeout/i.test(String(err.message))) throw new UserError(`couldn't open ${opts.url}: ${String(err.message).split("\n")[0]}`);
    }
    debug("loaded", status);
    await page.waitForNetworkIdle({ idleTime: 800, timeout: 8000 }).catch(() => {});
    await sleep(opts.wait);
    const hide = opts.hide.split(",").map((s) => s.trim()).filter(Boolean);
    const removed = await page.evaluate((selectors) => {
      let n = 0;
      for (const s of selectors) {
        try {
          document.querySelectorAll(s).forEach((el) => {
            el.remove();
            n++;
          });
        } catch {}
      }
      window.scrollTo(0, 0);
      return n;
    }, hide);
    await sleep(300);
    const info = await page.evaluate(() => ({
      title: document.title,
      url: location.href,
      page_height: Math.max(document.documentElement.scrollHeight, document.body ? document.body.scrollHeight : 0),
    }));
    const base = { url: info.url, title: info.title, status, removed, page_height: info.page_height };
    if (status && status >= 400) base.warning = `the page answered HTTP ${status}`;
    debug("ready to shoot");

    if (opts.preview) {
      fs.mkdirSync(path.dirname(path.resolve(opts.preview)), { recursive: true });
      await page.screenshot({ path: opts.preview, type: "png" });
      const overlays = await page.evaluate(findOverlays).catch(() => []);
      return { ok: true, preview: path.resolve(opts.preview), ...base, overlays };
    }

    const shot = (type) => page.screenshot({ type, ...(type === "jpeg" ? { quality: 90 } : {}), optimizeForSpeed: true, encoding: "base64" });

    const videoTmp = path.join(tmp, "video.mp4");
    const ff = spawn("ffmpeg", [
      "-hide_banner", "-loglevel", "error", "-y",
      "-f", "image2pipe", "-c:v", "mjpeg", "-framerate", String(FPS), "-i", "-",
      "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-r", String(FPS),
      "-movflags", "+faststart", videoTmp,
    ], { stdio: ["pipe", "ignore", "pipe"] });
    let ffErr = "";
    ff.stderr.on("data", (d) => (ffErr += d));
    ff.stdin.on("error", () => {});
    const ffClosed = new Promise((resolve) => ff.on("close", resolve));
    const ffDied = ffClosed.then(() => {
      throw new Error(`ffmpeg stopped early: ${ffErr.slice(-800)}`);
    });
    ffDied.catch(() => {});
    const write = (buf) => (ff.stdin.write(buf) ? Promise.resolve() : Promise.race([new Promise((r) => ff.stdin.once("drain", r)), ffDied]));

    // The real page first, before it dissolves.
    const first = Buffer.from(await shot("jpeg"), "base64");
    const preFrames = Math.round(PRE_SECONDS * FPS);
    for (let i = 0; i < preFrames; i++) await write(first);
    debug("pre-roll written");

    const hasMedia = await page.evaluate(() => {
      for (const el of document.querySelectorAll("canvas, video, iframe, embed, object")) {
        const r = el.getBoundingClientRect();
        if (r.width > 8 && r.height > 8 && r.bottom > 0 && r.right > 0 && r.top < innerHeight && r.left < innerWidth) return true;
      }
      return false;
    });
    if (hasMedia) {
      await page.evaluate((css) => {
        const s = document.createElement("style");
        s.id = "__swarm_media_only";
        s.textContent = css;
        document.documentElement.appendChild(s);
      }, MEDIA_ONLY_CSS);
      await sleep(150);
      const png = await shot("png");
      await page.evaluate((src) => {
        window.__swarmShot = src;
        window.__swarmHidden = true;
        window.__swarmUnhide = () => {
          const s = document.getElementById("__swarm_media_only");
          if (s) s.remove();
        };
      }, `data:image/png;base64,${png}`);
    }

    const frameMs = 1000 / FPS;
    const t0 = await page.evaluate(installClock);
    await page.evaluate(swarmSrc);
    debug("swarm injected, media:", hasMedia);

    const maxFrames = Math.round(opts.maxSeconds * FPS);
    const holdFrames = Math.round(HOLD_SECONDS * FPS);
    const tailFrames = Math.round(TAIL_SECONDS * FPS);
    const sfx = []; // the swarm's sound events, with their time in the video
    let frames = 0;
    let speed = opts.speed;
    let toured = false;
    let completeAt = -1;
    let stopAt = -1;
    let cut = "";
    let failure = "";
    let last = null;
    const loopStart = Date.now();
    for (;;) {
      try {
        const st = await page.evaluate((ms) => window.__swarmStep(ms), frameMs);
        for (const ev of st.sfx) sfx.push({ at: preFrames / FPS + (ev.t * 1000 - t0 - frameMs) / 1000, fn: ev.fn, args: ev.args });
        last = st.alive ? st : last;
        if (st.started && !toured) {
          speed = opts.speed || (st.layers > 350 ? 3 : st.layers > 120 ? 2 : 1);
          toured = await page.evaluate(pressTour, speed);
        }
        await write(Buffer.from(await shot("jpeg"), "base64"));
        frames++;
        if (frames % 30 === 0) debug("frame", frames, JSON.stringify({ ...st, sfx: st.sfx.length }), `${Math.round((Date.now() - loopStart) / frames)}ms/frame`);
        if (st.complete && completeAt < 0) completeAt = frames;
        const perFrame = (Date.now() - loopStart) / 1000 / frames;
        const videoSeconds = (preFrames + frames) / FPS;
        // Keep enough time for the hand-back, the sound and the encode.
        const reserve = tailFrames * perFrame + 30 + videoSeconds * 0.5;
        if (stopAt < 0) {
          const outOfTime = frames >= maxFrames || wall() + reserve > opts.budget;
          if (completeAt >= 0 && frames - completeAt >= holdFrames) {
            if (opts.end === "hold") break;
            await page.evaluate(() => window.__swarmRebuild.stop(true));
            stopAt = frames;
          } else if (outOfTime) {
            cut = frames >= maxFrames ? "max-seconds" : "budget";
            if (opts.end === "hold") break;
            await page.evaluate(() => window.__swarmRebuild && window.__swarmRebuild.stop(true));
            stopAt = frames;
          } else if (!st.alive && frames > 3 * FPS) {
            throw new UserError("the swarm stopped early; this page may not be rebuildable");
          }
        } else if (frames - stopAt >= tailFrames) {
          break;
        }
        if (frames > 20 * 60 * FPS) break;
      } catch (err) {
        // Chrome crashed or stopped answering. Keep what's recorded if there's enough of it.
        if (err instanceof UserError || frames < 3 * FPS || ffErr) throw err;
        failure = crashed || String(err.message).split("\n")[0];
        debug("chrome failed at frame", frames, failure);
        break;
      }
    }
    ff.stdin.end();
    await ffClosed;
    if (ff.exitCode !== 0) throw new Error(`ffmpeg failed: ${ffErr.slice(-800)}`);

    let seconds = (preFrames + frames) / FPS;
    let video = videoTmp;
    if (failure) {
      const still = path.join(tmp, "page.jpg");
      fs.writeFileSync(still, first);
      video = path.join(tmp, "video-handback.mp4");
      await handBack(videoTmp, still, seconds, fmt, video);
      sfx.push({ at: seconds, fn: "release", args: [] });
      seconds += TAIL_SECONDS;
      cut = "chrome";
      await Promise.race([page.close().catch(() => {}), sleep(5000)]);
    }
    const out = path.resolve(opts.out);
    fs.mkdirSync(path.dirname(out), { recursive: true });
    let sound = null;
    if (opts.sound) {
      // A fresh blank tab plays the sounds back, so a heavy or broken page can't slow it down.
      if (!connected(browser)) {
        kill(browser);
        browser = await launchBrowser(puppeteer, chrome, fmt);
      }
      const player = await browser.newPage();
      await player.setContent("<!doctype html><title>sound</title><body></body>");
      await player.evaluate(swarmSrc);
      await player.evaluate(() => window.__swarmRebuild.stop(false));
      const audio = await player.evaluate(renderAudio, { log: sfx, seconds });
      const wav = path.join(tmp, "sound.wav");
      fs.writeFileSync(wav, Buffer.from(audio.data, "base64"));
      const level = await measureLoudness(wav);
      const norm = level
        ? `loudnorm=I=-16:TP=-1.5:LRA=11:measured_I=${level.input_i}:measured_TP=${level.input_tp}:measured_LRA=${level.input_lra}:measured_thresh=${level.input_thresh}:offset=${level.target_offset}:linear=true`
        : "anull";
      await runFfmpeg([
        "-i", video, "-i", wav, "-map", "0:v:0", "-map", "1:a:0", "-af", `${norm},alimiter=limit=0.84:level=disabled,aresample=48000`,
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out,
      ]);
      sound = { events: audio.events, played: audio.played };
    } else {
      fs.copyFileSync(video, out);
    }
    let size = "";
    try {
      const probe = JSON.parse(execSync(`ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of json ${JSON.stringify(out)}`, { encoding: "utf8" }));
      size = `${probe.streams[0].width}x${probe.streams[0].height}`;
    } catch {}
    const result = {
      ok: true,
      out,
      seconds: Math.round(seconds * 10) / 10,
      size,
      mb: Math.round((fs.statSync(out).size / 1048576) * 10) / 10,
      rebuilt: completeAt >= 0,
      cut: cut || null,
      speed,
      layers: last ? last.layers : 0,
      built: last ? last.built : 0,
      agents: last ? last.agents : 0,
      sound,
      wall_seconds: Math.round(wall()),
      ...base,
    };
    if (failure) result.warning = `Chrome failed at ${Math.round(((preFrames + frames) / FPS) * 10) / 10}s, so the video fades back to the page from there (${failure})`;
    return result;
  } catch (err) {
    if (crashed) throw new UserError(crashed);
    if (/TargetClose|Target closed|Connection closed|timed out/i.test(String(err && err.message))) {
      throw new UserError(`Chrome stopped responding (${String(err.message).split("\n")[0]})`);
    }
    throw err;
  } finally {
    await Promise.race([browser.close().catch(() => {}), sleep(5000)]);
    kill(browser);
    fs.rmSync(tmp, { recursive: true, force: true });
  }
}

main().then(
  (result) => done(result),
  (err) => done({ ok: false, error: err instanceof UserError ? err.message : String((err && err.stack) || err) }, 1),
);
