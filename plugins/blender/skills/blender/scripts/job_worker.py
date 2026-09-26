"""Internal detached supervisor. Use jobs.start_job rather than invoking directly."""

import json
import os
import subprocess
import sys
import time
from pathlib import Path


def run(job_dir):
    job_dir = Path(job_dir).resolve()
    started = time.time()

    def update(state, **fields):
        status = {"state": state, "started_at": started, **fields}
        if state in ("succeeded", "failed", "cancelled"):
            status["finished_at"] = time.time()
        temporary = job_dir / "status.json.tmp"
        temporary.write_text(json.dumps(status, indent=2))
        temporary.replace(job_dir / "status.json")

    child = None
    try:
        spec = json.loads((job_dir / "job.json").read_text())
        if (job_dir / "cancel.request").exists():
            update("cancelled", exit_code=None)
            return
        with (job_dir / "blender.log").open("ab") as log:
            child = subprocess.Popen(
                spec["command"],
                cwd=job_dir,
                env={
                    **os.environ,
                    "BLENDER_JOB_DIR": str(job_dir),
                    "PYTHONUNBUFFERED": "1",
                },
                stdin=subprocess.DEVNULL,
                stdout=log,
                stderr=subprocess.STDOUT,
            )
            update("running")
            while child.poll() is None:
                if (job_dir / "cancel.request").exists():
                    child.terminate()
                    try:
                        child.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        child.kill()
                        child.wait()
                    update("cancelled", exit_code=child.returncode)
                    return
                time.sleep(0.2)
            update(
                "succeeded" if child.returncode == 0 else "failed",
                exit_code=child.returncode,
            )
    except Exception as exc:
        if child is not None and child.poll() is None:
            child.kill()
            child.wait()
        update("failed", error=str(exc), exit_code=child.returncode if child else None)


if __name__ == "__main__":
    run(sys.argv[1])
