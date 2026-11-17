// A minimal headless-Chrome driver over the DevTools pipe, with no npm dependencies.
// frames.mjs and motion.mjs use it so the checks run anywhere a Chrome binary exists:
// the sandbox image pre-caches chrome-headless-shell under ~/.cache/puppeteer, and no
// playwright or puppeteer module has to be installed.
//
// Binary lookup order: $STICK_CHROME, $CHROME, the puppeteer cache, the playwright cache,
// chromium / google-chrome / chrome-headless-shell on PATH, then the macOS Chrome app.
import { spawn } from 'node:child_process';
import { mkdtempSync, readdirSync, rmSync, statSync } from 'node:fs';
import { homedir, tmpdir } from 'node:os';
import { delimiter, join } from 'node:path';

const isFile = (p) => {
  try {
    return statSync(p).isFile();
  } catch {
    return false;
  }
};
const subdirs = (p) => {
  try {
    return readdirSync(p, { withFileTypes: true }).filter((d) => d.isDirectory()).map((d) => join(p, d.name));
  } catch {
    return [];
  }
};
// <root>/<version>/<platform-dir>/<binary>, newest version first.
const cached = (root, names) => {
  const out = [];
  for (const ver of subdirs(root).sort().reverse()) {
    for (const plat of subdirs(ver)) {
      for (const n of names) {
        out.push(join(plat, n));
      }
    }
  }
  return out;
};

export function findChrome() {
  if (process.env.STICK_CHROME) {
    // An explicit choice: use it or fail, never silently fall through to another browser.
    return isFile(process.env.STICK_CHROME) ? process.env.STICK_CHROME : null;
  }
  const home = homedir();
  const shell = ['chrome-headless-shell', 'chrome-headless-shell.exe'];
  const full = ['chrome', 'chrome.exe', 'Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing'];
  const candidates = [
    process.env.CHROME,
    ...cached(join(home, '.cache/puppeteer/chrome-headless-shell'), shell),
    ...cached(join(home, '.cache/puppeteer/chrome'), full),
  ];
  for (const root of [join(home, '.cache/ms-playwright'), join(home, 'Library/Caches/ms-playwright')]) {
    for (const d of subdirs(root).sort().reverse()) {
      const base = d.split(/[\\/]/).pop();
      if (base.startsWith('chromium_headless_shell-')) {
        candidates.push(...subdirs(d).flatMap((p) => shell.map((n) => join(p, n))));
      } else if (base.startsWith('chromium-')) {
        candidates.push(...subdirs(d).flatMap((p) => [join(p, 'chrome'), join(p, 'Chromium.app/Contents/MacOS/Chromium')]));
      }
    }
  }
  for (const dir of (process.env.PATH || '').split(delimiter).filter(Boolean)) {
    for (const n of ['chrome-headless-shell', 'chromium', 'chromium-browser', 'google-chrome', 'google-chrome-stable']) {
      candidates.push(join(dir, n));
    }
  }
  candidates.push('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '/Applications/Chromium.app/Contents/MacOS/Chromium');
  return candidates.find((p) => p && isFile(p)) || null;
}

export async function launch() {
  const bin = findChrome();
  if (!bin) {
    throw new Error(
      process.env.STICK_CHROME
        ? `STICK_CHROME=${process.env.STICK_CHROME} is not a file.`
        : 'no Chrome binary found. Looked in $CHROME, ~/.cache/puppeteer, the playwright cache, PATH and /Applications. ' +
        'Set STICK_CHROME=/path/to/chrome-headless-shell, or fall back to the browser tools (see SKILL.md).',
    );
  }
  const profile = mkdtempSync(join(tmpdir(), 'stick-chrome-'));
  const args = [
    '--headless',
    '--no-sandbox',
    '--disable-gpu',
    '--disable-dev-shm-usage',
    '--hide-scrollbars',
    '--mute-audio',
    '--no-first-run',
    '--no-default-browser-check',
    '--disable-extensions',
    '--force-color-profile=srgb',
    '--font-render-hinting=none',
    '--allow-file-access-from-files',
    '--remote-debugging-pipe',
    `--user-data-dir=${profile}`,
    'about:blank',
  ];
  const proc = spawn(bin, args, { stdio: ['ignore', 'ignore', 'pipe', 'pipe', 'pipe'] });
  let stderr = '';
  proc.stderr.on('data', (d) => {
    stderr = (stderr + d).slice(-4000);
  });
  const toChrome = proc.stdio[3];
  const fromChrome = proc.stdio[4];
  let seq = 0;
  const pending = new Map();
  const listeners = [];
  let buf = '';
  let dead = null;
  const failAll = (err) => {
    dead = err;
    for (const { reject } of pending.values()) {
      reject(err);
    }
    pending.clear();
  };
  proc.on('exit', (code) => failAll(new Error(`Chrome exited (${code}). ${stderr.trim().split('\n').slice(-3).join(' ')}`)));
  proc.on('error', (e) => failAll(e));
  fromChrome.on('data', (chunk) => {
    buf += chunk.toString('utf8');
    let i;
    while ((i = buf.indexOf('\0')) >= 0) {
      const raw = buf.slice(0, i);
      buf = buf.slice(i + 1);
      let msg;
      try {
        msg = JSON.parse(raw);
      } catch {
        continue;
      }
      if (msg.id != null && pending.has(msg.id)) {
        const { resolve, reject, method } = pending.get(msg.id);
        pending.delete(msg.id);
        if (msg.error) {
          reject(new Error(`${method}: ${msg.error.message}`));
        } else {
          resolve(msg.result);
        }
      } else if (msg.method) {
        for (const fn of listeners) {
          fn(msg);
        }
      }
    }
  });
  const send = (method, params = {}, sessionId) =>
    new Promise((resolve, reject) => {
      if (dead) {
        reject(dead);
        return;
      }
      const id = ++seq;
      pending.set(id, { resolve, reject, method });
      toChrome.write(JSON.stringify(sessionId ? { id, method, params, sessionId } : { id, method, params }) + '\0');
    });

  await send('Browser.getVersion');

  const close = async () => {
    let timer;
    await Promise.race([send('Browser.close').catch(() => {}), new Promise((r) => (timer = setTimeout(r, 2000)))]);
    clearTimeout(timer);
    if (proc.exitCode == null) {
      proc.kill('SIGKILL');
    }
    for (const st of [toChrome, fromChrome, proc.stderr]) {
      st.destroy();
    }
    try {
      rmSync(profile, { recursive: true, force: true });
    } catch {}
  };

  // console: also collect console.warn/error calls and failed resource loads (frames.mjs does,
  // like upstream; motion.mjs only counts uncaught exceptions).
  const newPage = async ({ width = 800, height = 600, scale = 1, console: withConsole = true } = {}) => {
    const { targetId } = await send('Target.createTarget', { url: 'about:blank' });
    const { sessionId } = await send('Target.attachToTarget', { targetId, flatten: true });
    const s = (method, params) => send(method, params, sessionId);
    const errors = [];
    const waiters = [];
    listeners.push((msg) => {
      if (msg.sessionId !== sessionId) {
        return;
      }
      const p = msg.params || {};
      if (msg.method === 'Runtime.exceptionThrown') {
        const d = p.exceptionDetails || {};
        errors.push((d.exception && d.exception.description) || d.text || 'uncaught exception');
      } else if (withConsole && msg.method === 'Runtime.consoleAPICalled' && !['log', 'info', 'debug', 'dir', 'table'].includes(p.type)) {
        errors.push(`${p.type}: ${(p.args || []).map((a) => a.value ?? a.description ?? '').join(' ')}`);
      } else if (withConsole && msg.method === 'Log.entryAdded' && p.entry && p.entry.level === 'error') {
        errors.push(`${p.entry.level}: ${p.entry.text}${p.entry.url ? ' ' + p.entry.url : ''}`);
      } else if (msg.method === 'Page.loadEventFired') {
        waiters.splice(0).forEach((r) => r());
      }
    });
    await s('Page.enable');
    await s('Runtime.enable');
    await s('Log.enable');
    const viewport = (w, h) => s('Emulation.setDeviceMetricsOverride', { width: w, height: h, deviceScaleFactor: scale, mobile: false });
    await viewport(width, height);

    const evaluate = async (fn, arg) => {
      const expression = typeof fn === 'function' ? `(${fn})(${arg === undefined ? '' : JSON.stringify(arg)})` : String(fn);
      const r = await s('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true, userGesture: true });
      if (r.exceptionDetails) {
        const d = r.exceptionDetails;
        throw new Error((d.exception && d.exception.description) || d.text || 'evaluate failed');
      }
      return r.result ? r.result.value : undefined;
    };
    const goto = async (url, timeout = 15000) => {
      const loaded = new Promise((r) => waiters.push(r));
      await s('Page.navigate', { url });
      let timer;
      await Promise.race([loaded, new Promise((r) => (timer = setTimeout(r, timeout)))]);
      clearTimeout(timer);
    };
    const setContent = (html) =>
      evaluate((h) => {
        document.open();
        document.write(h);
        document.close();
      }, html);
    // Adds a classic <script> with inline source, like playwright's addScriptTag({ content }).
    const addScript = (code) =>
      evaluate((c) => {
        const el = document.createElement('script');
        el.textContent = c;
        document.head.appendChild(el);
      }, code);
    const waitFor = async (expr, timeout = 15000) => {
      const end = Date.now() + timeout;
      while (Date.now() < end) {
        if (await evaluate(`!!(${expr})`)) {
          return true;
        }
        await new Promise((r) => setTimeout(r, 50));
      }
      return false;
    };
    // PNG of one element, growing the viewport first so nothing below the fold is cut.
    const screenshot = async (selector) => {
      const box = await evaluate((sel) => {
        const el = document.querySelector(sel);
        if (!el) {
          return null;
        }
        const r = el.getBoundingClientRect();
        return { x: r.left + scrollX, y: r.top + scrollY, w: r.width, h: r.height, dw: document.documentElement.scrollWidth, dh: document.documentElement.scrollHeight };
      }, selector);
      if (!box || box.w < 1 || box.h < 1) {
        throw new Error(`nothing to screenshot at ${selector}`);
      }
      await viewport(Math.max(width, Math.ceil(box.dw)), Math.max(height, Math.ceil(box.dh)));
      await new Promise((r) => setTimeout(r, 100));
      const { data } = await s('Page.captureScreenshot', {
        format: 'png',
        clip: { x: box.x, y: box.y, width: box.w, height: box.h, scale: 1 },
        captureBeyondViewport: true,
      });
      return Buffer.from(data, 'base64');
    };
    return { evaluate, goto, setContent, addScript, waitFor, screenshot, errors };
  };

  return { bin, newPage, close };
}

// Shared CLI parsing for the check scripts: --key value pairs, --src repeatable.
export function parseArgs(argv) {
  const opt = { src: [] };
  for (let i = 0; i < argv.length; i += 2) {
    const k = argv[i].replace(/^--/, '');
    if (k === 'src') {
      opt.src.push(argv[i + 1]);
    } else {
      opt[k] = argv[i + 1];
    }
  }
  return opt;
}
