# Long-running jobs

Use the generic job runner for renders, animation frames, baking, or batch validation that would block the live GUI. It runs Blender in a separate process on a saved file. It does not change or merge into the open scene.

```python
from jobs import start_job, job_status, cancel_job

B.checkpoint("/absolute/project/tmp/bake-input.blend")
job = start_job(
    "/absolute/project/tmp/bake-input.blend",
    "/absolute/project/bake.py",
    "/absolute/project/tmp/jobs",
)
print(job["job_dir"])
```

All job paths must be absolute. The Blender binary is found from PATH, then the macOS application path; pass blender_binary explicitly for another location. Jobs default to four render threads to keep the GUI responsive; pass threads to start_job if needed. Run heavyweight jobs sequentially on a workstation unless there is a reason to parallelize. Keep input .blend and script files unchanged until the job finishes. The worker runs in its unique job directory, exposed to the script as `BLENDER_JOB_DIR`. Save outputs explicitly. Relative image/library paths resolve from the saved blend file; pack or verify resources before expensive jobs.

Poll with `job_status(job_dir)` at sensible intervals. States are queued, running, succeeded, failed, cancelled; the log tail carries Blender's own progress and traceback. Do not declare completion until succeeded and expected outputs are checked. Exit code zero alone does not prove a script produced the intended result. If a machine or supervisor dies, a saved running state may be stale; check worker.log/process state instead of assuming progress or resubmitting writes.

`cancel_job(job_dir)` requests cancellation; poll until cancelled or another terminal state. It only terminates the Blender child owned by that job. Partial files may remain. It never kills the interactive Blender application. No operation is retried automatically.

A bake script must save its baked image/cache and, if needed, a new .blend. An animation script should select its scene, frame range, output format and filepath before `bpy.ops.render.render(animation=True, scene=scene.name)`. Use an image sequence for restartable production renders, then encode it using tools available in the project. This skill does not install a video encoder or silently switch render engines.
