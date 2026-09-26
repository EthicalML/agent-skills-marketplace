"""Detached Blender jobs operating on saved files, separate from the live scene."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
from pathlib import Path


def _absolute(path):
    path = Path(path).expanduser()
    if not path.is_absolute():
        raise ValueError(f"Expected an absolute path: {path}")
    return path.resolve()


def start_job(blend_path, script_path, output_dir, blender_binary=None, threads=4):
    """Run a script against a saved blend file; return immediately with job_dir.

    The script receives BLENDER_JOB_DIR in its environment and runs with that
    directory as its working directory. It must explicitly save its outputs.
    No live scene changes are included unless saved before this call.
    """
    if not isinstance(threads, int) or threads < 1:
        raise ValueError("threads must be a positive integer")
    blend_path, script_path = _absolute(blend_path), _absolute(script_path)
    for path in (blend_path, script_path):
        if not path.is_file():
            raise FileNotFoundError(path)
    if blender_binary is None:
        blender_binary = shutil.which("blender")
        if not blender_binary:
            blender_binary = "/Applications/Blender.app/Contents/MacOS/Blender"
    binary = _absolute(blender_binary)
    if not binary.is_file() or not os.access(binary, os.X_OK):
        raise FileNotFoundError(f"Blender executable not found: {binary}")
    output_dir = _absolute(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    job_dir = Path(tempfile.mkdtemp(prefix="blender-job-", dir=output_dir))
    spec = {
        "job_dir": str(job_dir),
        "command": [
            str(binary),
            "--background",
            str(blend_path),
            "--threads",
            str(threads),
            "--python-exit-code",
            "1",
            "--python",
            str(script_path),
        ],
    }
    (job_dir / "job.json").write_text(json.dumps(spec, indent=2))
    (job_dir / "status.json").write_text(json.dumps({"state": "queued"}))
    try:
        with (job_dir / "worker.log").open("ab") as log:
            worker = subprocess.Popen(
                [
                    sys.executable,
                    str(Path(__file__).with_name("job_worker.py")),
                    str(job_dir),
                ],
                stdin=subprocess.DEVNULL,
                stdout=log,
                stderr=subprocess.STDOUT,
                start_new_session=True,
                close_fds=True,
            )
            # Reap when used from a long-lived Python session; a short-lived
            # caller can exit without waiting for the detached worker.
            threading.Thread(target=worker.wait, daemon=True).start()
    except OSError as exc:
        (job_dir / "status.json").write_text(
            json.dumps({"state": "failed", "error": str(exc)})
        )
        raise
    return job_status(job_dir)


def job_status(job_dir):
    """Return persisted state and the last 8 KiB of Blender output."""
    job_dir = _absolute(job_dir)
    status = json.loads((job_dir / "status.json").read_text())
    status["job_dir"] = str(job_dir)
    if (job_dir / "artifacts.json").exists():
        status.update(json.loads((job_dir / "artifacts.json").read_text()))
    status["cancel_requested"] = (job_dir / "cancel.request").exists()
    log_path = job_dir / "blender.log"
    status["log_tail"] = ""
    if log_path.exists():
        with log_path.open("rb") as log:
            log.seek(max(0, log_path.stat().st_size - 8192))
            status["log_tail"] = log.read(8192).decode("utf-8", errors="replace")
    return status


def cancel_job(job_dir):
    """Request cancellation. Only the worker terminates its own Blender child."""
    job_dir = _absolute(job_dir)
    status = job_status(job_dir)
    if status["state"] not in ("succeeded", "failed", "cancelled"):
        (job_dir / "cancel.request").touch()
    return job_status(job_dir)
