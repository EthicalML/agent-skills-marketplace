---
name: site-capture
description: Record a scripted screen capture of a website as video or GIF, with human-paced scrolling, clicks through pages and a visible cursor. Use when asked for a demo video, launch video, product walkthrough, animated README asset, or a GIF of a site or web app.
---

# Recording a site capture

Produces an mp4/GIF of a real browser walking a site. `capture.mjs` is the engine and is never edited per site; you write a flow file describing the beats.

## 1. Settle the brief

Ask only if the answer changes what you record. Decide and state your assumption otherwise.

- **What to walk through.** A section list, or "the homepage". If the user names pages to click into, note that each visit-and-return costs 8-15s.
- **Length.** If it must match a voiceover, count the words: ~150 words/minute. Tell them the number now if the ask is impossible (a 45s script cannot narrate a 20s walk).
- **Viewport.** Default 1440x900. Use 1920x1080 only if asked; the site fits more in frame and needs no zoom.
- **Deliverable.** mp4, GIF, or both. GIFs over ~20s get large; see step 7.

If they described a visual result you cannot see (a reference video, "like X does it"), ask for it. Do not build from an unseen reference.

## 2. Serve the site

Capture against a local build, not a dev server, unless told otherwise: dev overlays and HMR sockets end up on film.

Verify it answers before recording, and again if a run fails mid-way — long sessions outlive their servers:

```bash
curl -s -o /dev/null -w "%{http_code}\n" <url>
```

Playwright must be importable. If `capture.mjs` reports it is missing, `npm i --no-save playwright` in the project, or point `PLAYWRIGHT_MODULE` at an existing install.

## 3. Map the page

Author beats from measured offsets, never from guesses about layout. Run this against each page you will walk:

```bash
node --input-type=module -e '
const pw = await import(process.env.PLAYWRIGHT_MODULE ?? "playwright");
const b = await (pw.default ?? pw).chromium.launch();
const p = await b.newPage({ viewport: { width: 1440, height: 900 } });
await p.goto("<url>", { waitUntil: "networkidle" });
console.table(await p.evaluate(() => [...document.querySelectorAll("h1,h2,h3")].map((h) => ({
  text: h.textContent.trim().replace(/\s+/g, " ").slice(0, 44),
  top: Math.round(h.getBoundingClientRect().top + scrollY),
}))));
console.table((await p.evaluate(() => [...document.querySelectorAll("a[href],button")].map((e) => ({
  tag: e.tagName, href: e.getAttribute("href") ?? "", vis: !!(e.offsetWidth || e.offsetHeight),
  text: e.textContent.trim().replace(/\s+/g, " ").slice(0, 34),
  top: Math.round(e.getBoundingClientRect().top + scrollY),
})))).slice(0, 40));
await b.close();
'
```

`--input-type=module` must precede `-e`, or the top-level `await` fails to parse.

Read two things off it. **What each control actually does** — a tab that looks in-page may navigate, and the first match for a selector is often an invisible carousel or menu duplicate, so filter by `vis: true` and by class. And **whether a block sits near the page bottom**, which decides `centreOnHeading` over `scrollToHeading` in step 4.

## 4. Write the flow

Create `flow.mjs` next to where you will run. Default-export an async function taking the context below.

| Helper | Use |
| --- | --- |
| `goto(path)` | Navigate and settle |
| `scrollTo(y)` | Absolute offset |
| `scrollToHeading(text, clearance)` | Put a heading `clearance` px below the top |
| `centreOnHeading(text, bias)` | Centre a block; use for anything low on the page |
| `clickAfterDwell(locator, dwell)` | Glide the cursor in and click, consuming `dwell` ms |
| `back(offset)` | Browser back, restored to `offset` without a jolt |
| `pause(ms)`, `mark(label)` | Dwell; log a timestamped beat |
| `page`, `cursor`, `scrollY()`, `settle()` | Escape hatches |

```js
export default async function flow({ back, clickAfterDwell, mark, page, pause, scrollToHeading, scrollY, settle }) {
  // The engine has already loaded the landing page; the load itself is on film.
  await pause(2500);
  mark('hero');

  await scrollToHeading('What we do', 150);
  await pause(1200);
  mark('overview');

  const returnTo = await scrollY();
  await clickAfterDwell(page.locator('a[href="/pricing/"]:visible').first(), 900);
  await page.waitForURL('**/pricing/');
  await settle();
  await pause(2000);
  mark('pricing');

  await back(returnTo);
  await pause(600);
}
```

Rules that decide whether the result looks deliberate or accidental:

- **One scroll speed.** The engine holds it constant. Vary dwells, never speed.
- **Scroll the target into view in the beat before clicking it.** `clickAfterDwell` throws if the target is outside the viewport, because mouse coordinates are viewport-relative and Playwright silently clamps them — an unclamped-looking click would land somewhere else entirely.
- **Give each click its dwell, not an extra pause.** The cursor glide is spent inside `dwell`, so a cursor costs no runtime.
- **Two or three stops per section.** More reads as hunting.
- **`centreOnHeading` for blocks near the page bottom.** Anchoring them near the top drags the footer or contact form into most of the frame.
- **A hover sweep must end on the menu you are about to click.** Sweeping past it and doubling back reads as a mistake.

If an intro animation runs on a timer and you do not want to wait it out, seed its clock rather than pausing: find the element's animation origin (often a `startedAt` on a custom element; TypeScript `private` is compile-time only) and set it back via `page.evaluate`. Say so when you deliver — it changes what a visitor would see.

## 5. Record

```bash
node ~/.claude/skills/site-capture/capture.mjs \
  --url <url> --flow ./flow.mjs --name demo --out ./capture-out \
  --width 1440 --height 900 --theme dark
```

`--pace 0.6` scales every dwell to retime against a voiceover; `--speed` sets px/second; `--cursor 2` enlarges the pointer; `--zoom 1.1` zooms in.

**Zoom is a CSS zoom on the root, never a viewport resize.** Playwright records the screencast at the CSS viewport size and ignores `deviceScaleFactor` for video, so asking for an output larger than the viewport pads the frame instead of scaling it — a silent letterbox that looks like nothing happened. The engine handles this; do not "fix" a zoom request by changing `--width`.

## 6. Verify on the frames

The beat log proves the script ran, not that the video shows anything. Always check the frames.

```bash
# Every beat, one tile per 1.5s
ffmpeg -v error -y -i capture-out/demo.webm -vf "fps=1/1.5,scale=340:-1,tile=8x5" -frames:v 1 grid.png
# Content must fill the frame; a bbox smaller than the frame means padding, not zoom
magick identify -format '%wx%h\n' capture-out/demo.webm 2>/dev/null
ffmpeg -v error -y -ss 3 -i capture-out/demo.webm -frames:v 1 f.png
magick f.png -colorspace Gray -threshold 4% -format 'frame %wx%h content %@\n' info:
```

Read `grid.png` and confirm each beat shows what it was for. Then sample the moment **just before** each click (marks are printed after the beat's dwell, so subtract it) and confirm the cursor is on the target with its ring firing.

If the cursor appears on the first click only, the site is an SPA whose router swaps `<body>` and destroyed it. The engine rebuilds on use, so this should not happen — if it does, check `window.__cursor` exists *and* `document.getElementById('capture-cursor')` is non-null on the second page; a true/false pair is the signature.

If a return-navigation jolts to the top, the offset was not pinned; confirm `back()` was used rather than `page.goBack()`.

## 7. Encode

```bash
ffmpeg -v error -y -i capture-out/demo.webm -c:v libx264 -preset slow -crf 22 \
  -pix_fmt yuv420p -movflags +faststart capture-out/demo.mp4
```

For a GIF, prefer `gifski`; extract frames first so the frame rate is exact:

```bash
mkdir -p frames && ffmpeg -v error -t 20 -i capture-out/demo.webm \
  -vf "fps=10,scale=880:-2:flags=lanczos" frames/%05d.png
gifski -o capture-out/demo.gif --fps 10 --quality 80 --width 880 frames/*.png && rm -rf frames
```

To hit a size cap, drop **fps first** — it is the only lever that costs nothing visually when the motion is eased scrolling. 12.5 to 10 fps saves about 20%. Then width. Reduce quality last: flat dark backgrounds show quantisation banding before they show softness.

Report the measured duration and file size, and name anything you traded away.
