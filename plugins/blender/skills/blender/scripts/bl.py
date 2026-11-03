#!/usr/bin/env python3
"""Headless Blender loop: build a scene script, render stills or an animation, encode, open.

  bl.py probe
  bl.py stills  SCENE.py --frames 1,120,240 [--preview] [--out DIR] [-- scene args]
  bl.py animate SCENE.py [--out DIR] [-- scene args]
  bl.py open    FILE.blend

Every run builds the scene from scratch with --factory-startup, saves OUT/scene.blend,
and fails on any Python exception in the scene script.
"""
import argparse, math, os, shutil, subprocess, sys, time
from pathlib import Path


def blender_bin():
    for c in (os.environ.get("BLENDER"), shutil.which("blender"),
              "/Applications/Blender.app/Contents/MacOS/Blender"):
        if c and Path(c).exists():
            return c
    sys.exit("Blender not found. Set BLENDER=/path/to/blender.")


# Runs inside Blender after the scene script has built the scene.
RENDER_EXPR = r'''
import bpy, os, time, json
cfg = json.loads(os.environ["BL_CFG"])
s = bpy.context.scene
r = s.render
bpy.ops.wm.save_as_mainfile(filepath=cfg["blend"])
if cfg["preview"]:
    r.resolution_percentage = 50
    r.use_motion_blur = False
    if r.engine == "CYCLES":
        s.cycles.samples = 32
    else:
        s.eevee.taa_render_samples = 16
print("BL_INFO", json.dumps({"engine": r.engine, "res": [r.resolution_x, r.resolution_y, r.resolution_percentage],
      "frames": [s.frame_start, s.frame_end], "fps": r.fps, "camera": s.camera.name if s.camera else None}))
if s.camera is None:
    raise SystemExit("Scene has no camera")
r.image_settings.file_format = "PNG"
if cfg["mode"] == "stills":
    for f in cfg["frames"]:
        s.frame_set(f)
        r.filepath = os.path.join(cfg["out"], f"still_{f:04d}.png")
        t = time.time()
        bpy.ops.render.render(write_still=True)
        print(f"BL_FRAME {f} {time.time() - t:.1f}s")
else:
    r.filepath = os.path.join(cfg["out"], "frames", "f_")
    r.use_overwrite = False          # re-running resumes where it stopped
    bpy.ops.render.render(animation=True)
'''


def run_blender(scene, out, mode, frames=(), preview=False, scene_args=()):
    out = Path(out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    cfg = {"out": str(out), "blend": str(out / "scene.blend"), "mode": mode,
           "frames": list(frames), "preview": preview}
    env = dict(os.environ, BL_CFG=__import__("json").dumps(cfg))
    cmd = [blender_bin(), "-b", "--factory-startup", "--python-exit-code", "1",
           "--python", str(Path(scene).resolve()), "--python-expr", RENDER_EXPR, "--", *scene_args]
    log = out / f"{mode}.log"
    print(f"log: {log}")
    t0 = time.time()
    with open(log, "w") as fh:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env)
        for line in p.stdout:
            fh.write(line)
            if line.startswith(("BL_", "Traceback", "Error", "  File")) or "Error:" in line or \
               (mode == "animate" and "Saved:" in line):
                print(line.rstrip(), flush=True)
        p.wait()
    if p.returncode != 0:
        print("".join(open(log).readlines()[-30:]))
        sys.exit(f"Blender failed (exit {p.returncode}). Fix the scene script; full log: {log}")
    print(f"done in {time.time() - t0:.0f}s; blend: {cfg['blend']}")
    return out


def contact_sheet(images, dest, width=640):
    images = [str(i) for i in images]
    if len(images) == 1:
        shutil.copy(images[0], dest)
        return dest
    cols = 2 if len(images) <= 4 else 3
    rows = math.ceil(len(images) / cols)
    ins = sum((["-i", i] for i in images), [])
    graph = "".join(f"[{k}]" for k in range(len(images)))
    graph += f"concat=n={len(images)}:v=1:a=0,scale={width}:-2,tile={cols}x{rows}"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *ins, "-filter_complex", graph,
                    "-frames:v", "1", str(dest)], check=True)
    return dest


def cmd_probe(_):
    b = blender_bin()
    print("blender:", b)
    print(subprocess.run([b, "--version"], capture_output=True, text=True).stdout.splitlines()[0])
    print("ffmpeg:", shutil.which("ffmpeg") or "MISSING (needed for contact sheets and mp4)")


def cmd_stills(a):
    frames = [int(f) for f in a.frames.split(",")]
    out = run_blender(a.scene, a.out, "stills", frames, a.preview, a.scene_args)
    sheet = contact_sheet([out / f"still_{f:04d}.png" for f in frames], out / "contact.png")
    print(f"contact sheet: {sheet}")


def cmd_animate(a):
    out = run_blender(a.scene, a.out, "animate", scene_args=a.scene_args)
    frames = sorted((out / "frames").glob("f_*.png"))
    if not frames:
        sys.exit("No frames rendered.")
    import json, re
    info = next(json.loads(l.split(" ", 1)[1]) for l in open(out / "animate.log") if l.startswith("BL_INFO"))
    start = int(re.search(r"f_(\d+)", frames[0].name).group(1))
    mp4 = out / f"{Path(a.scene).stem}.mp4"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-framerate", str(info["fps"]),
                    "-start_number", str(start), "-i", str(out / "frames" / "f_%04d.png"),
                    "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p",
                    "-movflags", "+faststart", str(mp4)], check=True)
    picks = [frames[round(i * (len(frames) - 1) / 5)] for i in range(6)]
    print(f"video: {mp4} ({len(frames)} frames)")
    print(f"contact sheet: {contact_sheet(picks, out / 'video_contact.png')}")


def cmd_open(a):
    path = str(Path(a.blend).resolve())
    if sys.platform == "darwin":
        app = Path(blender_bin()).parents[2]
        subprocess.run(["open", "-n", "-a", str(app), "--args", path], check=True)
    else:
        subprocess.Popen([blender_bin(), path], start_new_session=True)
    print(f"opened in a new Blender instance: {path}")


def main():
    argv = sys.argv[1:]
    scene_args = argv[argv.index("--") + 1:] if "--" in argv else []
    argv = argv[:argv.index("--")] if "--" in argv else argv
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("probe").set_defaults(fn=cmd_probe)
    p = sub.add_parser("stills"); p.set_defaults(fn=cmd_stills)
    p.add_argument("scene"); p.add_argument("--frames", default="1")
    p.add_argument("--preview", action="store_true"); p.add_argument("--out", default="tmp/stills")
    p = sub.add_parser("animate"); p.set_defaults(fn=cmd_animate)
    p.add_argument("scene"); p.add_argument("--out", default="tmp/animate")
    p = sub.add_parser("open"); p.set_defaults(fn=cmd_open); p.add_argument("blend")
    a = ap.parse_args(argv)
    a.scene_args = scene_args
    a.fn(a)


if __name__ == "__main__":
    main()
