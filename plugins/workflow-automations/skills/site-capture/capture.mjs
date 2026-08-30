// Screen-capture engine for scripted website demos. Never edit this file for a
// particular site; it takes a flow module that describes the beats.
//
//   node capture.mjs --url http://127.0.0.1:4321 --flow ./flow.mjs --name demo
//
// Flags: --url --flow --name --out --width --height --zoom --theme --speed
//        --pace --cursor --headed
//
// The flow module default-exports `async (ctx) => {...}`. See SKILL.md for ctx.

import { mkdir, rename, rm } from 'node:fs/promises';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { resolve } from 'node:path';

const args = process.argv.slice(2);
const flag = (name, fallback) => {
  const index = args.indexOf(`--${name}`);
  return index === -1 ? fallback : args[index + 1];
};

const url = flag('url');
const flowPath = flag('flow');
if (!url || !flowPath) throw new Error('Both --url and --flow are required');

const name = flag('name', 'capture');
const outDir = resolve(flag('out', './capture-out'));
const width = Number(flag('width', 1440));
const height = Number(flag('height', 900));
// CSS zoom on the root. Never resize the viewport to zoom: Playwright records at
// the CSS viewport size and pads when asked for a larger output. Never use
// `transform` either; it creates a containing block and breaks fixed/sticky.
const zoom = Number(flag('zoom', 1));
const theme = flag('theme', '');
const SPEED = Number(flag('speed', 460)); // px per second, constant across beats
const PACE = Number(flag('pace', 1)); // scales every dwell
const CURSOR_SCALE = Number(flag('cursor', 1.5));

// Playwright is resolved from wherever it is installed rather than being a
// dependency of every project this runs against.
const playwright = await (async () => {
  for (const specifier of [
    process.env.PLAYWRIGHT_MODULE,
    'playwright',
    'playwright-core',
  ].filter(Boolean)) {
    try {
      const loaded = await import(specifier);
      return loaded.default ?? loaded;
    } catch (error) {
      if (error?.code !== 'ERR_MODULE_NOT_FOUND') throw error;
    }
  }
  throw new Error('Playwright not found. `npm i --no-save playwright` or set PLAYWRIGHT_MODULE.');
})();

await mkdir(outDir, { recursive: true });
const rawDir = resolve(outDir, '.raw');
await rm(rawDir, { force: true, recursive: true });
await mkdir(rawDir, { recursive: true });

const browser = await playwright.chromium.launch({ headless: !args.includes('--headed') });
const context = await browser.newContext({
  colorScheme: theme === 'light' ? 'light' : 'dark',
  deviceScaleFactor: 1,
  recordVideo: { dir: rawDir, size: { height, width } },
  reducedMotion: 'no-preference', // or every animation you came to film is skipped
  viewport: { height, width },
});

if (theme) {
  // Set before first paint so no frame shows the other palette.
  await context.addInitScript((value) => {
    try {
      localStorage.setItem('theme', value);
    } catch {
      /* storage blocked; colorScheme emulation still applies */
    }
  }, theme);
}

if (zoom !== 1) {
  await context.addInitScript((value) => {
    const apply = () => {
      if (!document.documentElement) return void requestAnimationFrame(apply);
      const style = document.createElement('style');
      style.textContent = `html { zoom: ${value} }`;
      (document.head ?? document.documentElement).appendChild(style);
    };
    apply();
  }, zoom);
}

// Back navigation lands at the top of a re-parsed document, which reads as a
// jolt. `back()` stashes the offset and this pins it across the first frames.
await context.addInitScript(() => {
  try {
    history.scrollRestoration = 'manual';
    const raw = localStorage.getItem('captureRestoreY');
    if (!raw) return;
    localStorage.removeItem('captureRestoreY');
    const y = Number(raw);
    const apply = () => window.scrollTo({ behavior: 'instant', top: y });
    document.addEventListener('DOMContentLoaded', apply);
    window.addEventListener('load', apply);
    const until = performance.now() + 650;
    const tick = () => {
      apply();
      if (performance.now() < until) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  } catch {
    /* fall back to whatever the browser restores */
  }
});

// Headless Chromium composites no system pointer into the screencast, so the
// cursor is drawn into the page. SPA routers swap <body> on navigation and
// destroy it while `window.__cursor` survives as a stale handle, so every entry
// point re-ensures the node exists rather than trusting the one it installed.
await context.addInitScript((scale) => {
  let root = null;
  let ring = null;
  let x = -200;
  let y = -200;

  const build = () => {
    root = document.createElement('div');
    root.id = 'capture-cursor';
    root.innerHTML =
      `<svg width="${22 * scale}" height="${32 * scale}" viewBox="0 0 22 32" fill="none">` +
      `<path d="M2 1.6 L2 24.4 L8 19 L11.8 27.9 L15.6 26.2 L11.9 17.4 L19.6 16.9 Z" ` +
      `fill="#fff" stroke="#111" stroke-width="1.6" stroke-linejoin="round"/></svg>`;
    Object.assign(root.style, {
      filter: 'drop-shadow(0 2px 5px rgba(0,0,0,0.55))',
      left: '0',
      opacity: '0',
      pointerEvents: 'none',
      position: 'fixed',
      top: '0',
      transition: 'opacity 200ms ease',
      zIndex: '2147483647',
    });
    ring = document.createElement('i');
    Object.assign(ring.style, {
      border: `${2 * scale}px solid rgba(255,255,255,0.95)`,
      borderRadius: '50%',
      height: `${26 * scale}px`,
      left: `${-9 * scale}px`,
      opacity: '0',
      pointerEvents: 'none',
      position: 'absolute',
      top: `${-9 * scale}px`,
      transform: 'scale(0.35)',
      width: `${26 * scale}px`,
    });
    root.appendChild(ring);
    document.body.appendChild(root);
    root.style.transform = `translate(${x}px, ${y}px)`;
  };

  const ensure = () => {
    if (!document.body) return false;
    if (!root || !root.isConnected) build();
    return true;
  };

  addEventListener(
    'mousemove',
    (event) => {
      x = event.clientX;
      y = event.clientY;
      if (root && root.isConnected) root.style.transform = `translate(${x}px, ${y}px)`;
    },
    { capture: true, passive: true },
  );

  window.__cursor = {
    hide: () => ensure() && (root.style.opacity = '0'),
    press: () => {
      if (!ensure()) return;
      ring.style.transition = 'none';
      ring.style.opacity = '0.95';
      ring.style.transform = 'scale(0.35)';
      requestAnimationFrame(() => {
        ring.style.transition = 'opacity 420ms ease, transform 420ms ease';
        ring.style.opacity = '0';
        ring.style.transform = 'scale(1.6)';
      });
    },
    show: () => ensure() && (root.style.opacity = '1'),
  };
}, CURSOR_SCALE);

const page = await context.newPage();
const startedAt = Date.now();
const elapsed = () => ((Date.now() - startedAt) / 1000).toFixed(1);

const pause = (ms) => page.waitForTimeout(Math.round(ms * PACE));
const mark = (label) => console.log(`  ${elapsed()}s  ${label}`);

const settle = async () => {
  await page.waitForLoadState('networkidle');
  await page.evaluate(() => document.fonts.ready);
};

// Eased travel at a constant rate: duration follows distance, so no beat looks
// faster than another. The ease shapes only the outer fifths.
const scrollTo = async (target, speed = SPEED) => {
  const distance = await page.evaluate((value) => Math.abs(value - window.scrollY), target);
  if (distance < 4) return;
  const duration = Math.max(320, Math.round((distance / speed) * 1000));
  await page.evaluate(
    ({ duration: ms, target: end }) =>
      new Promise((done) => {
        const from = window.scrollY;
        const delta = end - from;
        const t0 = performance.now();
        const ease = (t) => {
          const edge = 0.2;
          if (t < edge) return (t * t) / (2 * edge) / (1 - edge);
          if (t > 1 - edge) return 1 - ((1 - t) * (1 - t)) / (2 * edge) / (1 - edge);
          return (t - edge / 2) / (1 - edge);
        };
        const step = (now) => {
          const t = Math.min(1, (now - t0) / ms);
          window.scrollTo({ behavior: 'instant', top: from + delta * ease(t) });
          if (t < 1) requestAnimationFrame(step);
          else done();
        };
        requestAnimationFrame(step);
      }),
    { duration, target },
  );
};

const offsetOfHeading = (text, mode, amount) =>
  page.evaluate(
    ({ amount: value, mode: how, text: needle }) => {
      const heading = [...document.querySelectorAll('h1,h2,h3')].find((element) =>
        element.textContent.trim().includes(needle),
      );
      if (!heading) return null;
      const rect = heading.getBoundingClientRect();
      const top = rect.top + window.scrollY;
      const limit = document.documentElement.scrollHeight - window.innerHeight;
      const target =
        how === 'centre'
          ? top + rect.height / 2 - window.innerHeight / 2 + value
          : top - value;
      return Math.max(0, Math.min(limit, target));
    },
    { amount, mode, text },
  );

const scrollToHeading = async (text, clearance = 150) => {
  const target = await offsetOfHeading(text, 'top', clearance);
  if (target === null) throw new Error(`No heading contains "${text}"`);
  await scrollTo(target);
  return target;
};

// Use for blocks low on the page: pinning them near the top drags whatever
// follows into frame.
const centreOnHeading = async (text, bias = 0) => {
  const target = await offsetOfHeading(text, 'centre', bias);
  if (target === null) throw new Error(`No heading contains "${text}"`);
  await scrollTo(target);
  return target;
};

const cursor = {
  hide: () => page.evaluate(() => window.__cursor?.hide()),
  press: () => page.evaluate(() => window.__cursor?.press()),
  show: () => page.evaluate(() => window.__cursor?.show()),
};

// The glide is spent inside the dwell this beat already had, so showing a
// cursor costs no runtime and the click lands when it was always going to.
const clickAfterDwell = async (locator, dwell = 900, steps = 22) => {
  const box = await locator.boundingBox();
  if (!box) throw new Error('Click target is not rendered');
  const x = box.x + box.width / 2;
  const y = box.y + box.height / 2;
  if (x < 0 || y < 0 || x > width || y > height) {
    throw new Error(
      `Click target is outside the viewport at (${Math.round(x)}, ${Math.round(y)}). ` +
        'Scroll it into view in the beat before clicking: mouse coordinates are ' +
        'viewport-relative and Playwright clamps them, so this would click the wrong place.',
    );
  }
  const budget = dwell * PACE;
  const began = Date.now();
  await cursor.show();
  await page.mouse.move(x, y, { steps });
  const remaining = budget - (Date.now() - began) - 200;
  if (remaining > 0) await page.waitForTimeout(remaining);
  await cursor.press();
  await page.mouse.down();
  await page.waitForTimeout(90);
  await page.mouse.up();
};

const back = async (offset) => {
  await page.evaluate((value) => localStorage.setItem('captureRestoreY', String(value)), offset);
  await page.goBack({ waitUntil: 'domcontentloaded' });
  await settle();
  await page.waitForTimeout(700); // outlast the pinning loop before scrolling again
  await page.evaluate(() => localStorage.removeItem('captureRestoreY'));
};

const goto = async (path) => {
  await page.goto(new URL(path, url).href, { waitUntil: 'networkidle' });
  await settle();
};

const scrollY = () => page.evaluate(() => window.scrollY);

const { default: flow } = await import(pathToFileURL(resolve(flowPath)).href);
console.log(`  viewport ${width}x${height}, zoom ${zoom}${theme ? `, theme ${theme}` : ''}`);

// The flow starts on the landing page; recording begins with the page created,
// so the load itself is on film.
await goto('/');

await flow({
  back,
  centreOnHeading,
  clickAfterDwell,
  cursor,
  goto,
  mark,
  page,
  pause,
  scrollTo,
  scrollToHeading,
  scrollY,
  settle,
});

// The video is only written out when the context closes.
const video = page.video();
await context.close();
await browser.close();
const target = resolve(outDir, `${name}.webm`);
await rename(await video.path(), target);
await rm(rawDir, { force: true, recursive: true });
console.log(`captured ${target}`);
