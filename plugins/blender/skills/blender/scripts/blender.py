"""Direct live-Blender client. Python stdlib only; no MCP process or SDK.

Import this module, or run `python blender.py --help`. Blender must be open
with the pinned MCP for Blender add-on listener enabled on localhost.
"""

from __future__ import annotations

import argparse
import json
import os
import socket
import sys
import time
import uuid
from pathlib import Path


class BlenderError(RuntimeError):
    """A reported Blender or connection failure."""


class OutcomeUnknown(BlenderError):
    """A submitted operation may have executed. Inspect; never blindly retry."""


def call(
    command: str,
    *,
    port: int | None = None,
    timeout: float = 30,
    params: dict | None = None,
    **kwargs,
):
    """Call an add-on command, returning its result. One request per connection.

    Only loopback is supported. `params` accepts names reserved by this helper.
    The socket protocol is raw UTF-8 JSON, not MCP or JSON-RPC.
    """
    port = int(port or os.environ.get("BLENDER_PORT", "9876"))
    arguments = dict(params or {})
    arguments.update(kwargs)
    payload = json.dumps({"type": command, "params": arguments}).encode()
    try:
        connection = socket.create_connection(("127.0.0.1", port), timeout=timeout)
    except OSError as exc:
        raise BlenderError(
            f"Cannot connect to Blender on localhost:{port}: {exc}. "
            "Open Blender and start its add-on listener; see references/setup.md."
        ) from exc
    with connection:
        deadline = time.monotonic() + timeout
        try:
            connection.sendall(payload)
            response = bytearray()
            while True:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise TimeoutError("deadline exceeded")
                connection.settimeout(remaining)
                chunk = connection.recv(65536)
                if not chunk:
                    raise ConnectionError(
                        "connection closed before a complete response"
                    )
                response.extend(chunk)
                if len(response) > 32 * 1024 * 1024:
                    raise ConnectionError(
                        "response exceeded 32 MiB; use a narrower query"
                    )
                try:
                    result = json.loads(response.decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError):
                    continue
                break
        except OSError as exc:
            raise OutcomeUnknown(
                f"{command}: outcome unknown after submission ({exc}). "
                "The command may still run. Inspect the scene before retrying."
            ) from exc
    if not isinstance(result, dict) or result.get("status") != "success":
        detail = result.get("message", result) if isinstance(result, dict) else result
        if isinstance(detail, str):
            try:
                error = json.loads(detail)
            except json.JSONDecodeError:
                error = None
            if isinstance(error, dict) and error.get("traceback"):
                detail = f"{error.get('exception_type', 'Error')}: {error.get('message', '')}\n{error['traceback']}"
        raise BlenderError(f"{command}: {detail}")
    value = result.get("result")
    if isinstance(value, dict) and value.get("error"):
        raise BlenderError(f"{command}: {value['error']}")
    return value


def status(**connection):
    """Read Blender/add-on versions and core capabilities without modifying it."""
    return call("get_addon_info", **connection)


def execute(code: str, **connection):
    """Run trusted Python in Blender; return captured stdout. Changes aren't atomic."""
    return call("execute_code", code=code, **connection)["result"]


def run_script(path, parameters=None, **connection):
    """Run a local UTF-8 script in Blender with a JSON-compatible `PARAMS` dict.

    __file__ points to the script. Imports require explicit paths as usual.
    """
    path = Path(path).expanduser().resolve()
    code = path.read_text(encoding="utf-8")
    return execute(
        f"import json\nPARAMS = json.loads({json.dumps(parameters or {})!r})\n"
        f'__name__ = "__main__"\n__file__ = {str(path)!r}\nexec(compile({code!r}, __file__, "exec"))',
        **connection,
    )


def _runtime(function, *, timeout=30, **kwargs):
    source = Path(__file__).with_name("runtime.py").read_text(encoding="utf-8")
    marker = "__BLENDER_RESULT_" + uuid.uuid4().hex + "__"
    code = (
        f'import json\nexec(compile({source!r}, "blender_skill_runtime", "exec"))\n'
        f"_args = json.loads({json.dumps(kwargs)!r})\n"
        f"print({marker!r} + json.dumps({function}(**_args)))"
    )
    output = execute(code, timeout=timeout)
    for line in reversed(output.splitlines()):
        if line.startswith(marker):
            return json.loads(line[len(marker) :])
    raise BlenderError(f"Missing structured response from {function}: {output[-2000:]}")


def scene(offset=0, limit=50, collection=None):
    """Paginated scene objects plus context, render settings and collection names."""
    return _runtime("inspect_scene", offset=offset, limit=limit, collection=collection)


def object_info(name, mesh=False):
    """Transforms, bounds, modifiers, constraints, animation and optional mesh checks."""
    return _runtime("inspect_object", name=name, mesh=mesh)


def material_info(name):
    """Material node inputs and links, including texture paths."""
    return _runtime("inspect_material", name=name)


def screenshot(path, max_size=1400, **connection):
    """Write a viewport screenshot to an explicit local path; return the path."""
    path = Path(path).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    call(
        "get_viewport_screenshot",
        filepath=str(path),
        max_size=max_size,
        format="png",
        **connection,
    )
    if not path.is_file() or path.stat().st_size == 0:
        raise BlenderError(f"Blender did not write screenshot: {path}")
    return str(path)


def save(path, *, copy=False, pack=False):
    """Save a blend file; copy=True checkpoints without changing the active path."""
    return _runtime(
        "save_file",
        path=str(Path(path).expanduser().resolve()),
        copy=copy,
        pack=pack,
        timeout=180,
    )


def checkpoint(path):
    return save(path, copy=True)


def validate(collection=None, mesh=False):
    """Report missing resources, zero-scale objects, and optional mesh issues."""
    return _runtime("validate_scene", collection=collection, mesh=mesh)


def describe_node_type(**params):
    return call("describe_node_type", **params)


def api_lookup(**params):
    return call("bpy_api_lookup", **params)


def export_scene(
    path, format="glb", object_names=None, selection_only=False, apply_modifiers=True
):
    path = Path(path).expanduser().resolve()
    result = _runtime(
        "export_file",
        path=str(path),
        format=format,
        object_names=object_names,
        selection_only=selection_only,
        apply_modifiers=apply_modifiers,
        timeout=180,
    )
    if not path.is_file() or path.stat().st_size == 0:
        raise BlenderError(f"Export missing or empty: {path}")
    return result


def render_preview(
    output_dir,
    *,
    camera=None,
    frame=None,
    resolution=640,
    samples=32,
    blender_binary=None,
):
    """Snapshot current work, render it in a separate Blender process, return job.

    Poll job_status(job['job_dir']); the live scene stays interactive. Render uses
    the selected scene from the snapshot. Read job log on failure.
    """
    from jobs import start_job

    directory = Path(output_dir).expanduser().resolve() / (
        "preview-" + uuid.uuid4().hex[:12]
    )
    directory.mkdir(parents=True)
    snapshot = directory / "scene.blend"
    image = directory / "render.png"
    current = scene(limit=1)
    save(snapshot, copy=True)
    script = directory / "render.py"
    script.write_text(
        "import bpy\n"
        f"scene = bpy.data.scenes[{current['name']!r}]\n"
        + (f"scene.camera = bpy.data.objects[{camera!r}]\n" if camera else "")
        + (f"scene.frame_set({int(frame)})\n" if frame is not None else "")
        + f"scene.render.resolution_percentage = 100\n"
        f"ratio = scene.render.resolution_y / max(1, scene.render.resolution_x)\n"
        f"scene.render.resolution_x = {int(resolution)}\n"
        f"scene.render.resolution_y = max(1, round({int(resolution)} * ratio))\n"
        f'scene.render.image_settings.file_format = "PNG"\n'
        f"scene.render.filepath = {str(image)!r}\n"
        f'if scene.render.engine == "CYCLES": scene.cycles.samples = {int(samples)}\n'
        "bpy.ops.render.render(write_still=True, scene=scene.name)\n",
        encoding="utf-8",
    )
    result = start_job(snapshot, script, directory, blender_binary=blender_binary)
    return _artifacts(result, image=str(image))


def _artifacts(job, **artifacts):
    (Path(job["job_dir"]) / "artifacts.json").write_text(json.dumps(artifacts))
    return {**job, **artifacts}


def verify_file(path, output_dir, blender_binary=None):
    """Reopen a blend or reimport GLB/FBX in background Blender and write report."""
    from jobs import start_job

    path = Path(path).expanduser().resolve()
    if path.suffix.lower() not in {".blend", ".glb", ".fbx"} or not path.is_file():
        raise ValueError("Expected an existing .blend, .glb or .fbx file")
    directory = Path(output_dir).expanduser().resolve() / (
        "verify-" + uuid.uuid4().hex[:12]
    )
    directory.mkdir(parents=True)
    snapshot = path if path.suffix.lower() == ".blend" else directory / "input.blend"
    if snapshot != path:
        save(snapshot, copy=True)
    report = directory / "report.json"
    runtime = Path(__file__).with_name("runtime.py").read_text(encoding="utf-8")
    code = "import bpy, json\nfrom pathlib import Path\n"
    if path.suffix.lower() != ".blend":
        code += "bpy.ops.wm.read_factory_settings(use_empty=True)\n"
        operator = "gltf" if path.suffix.lower() == ".glb" else "fbx"
        code += f"bpy.ops.import_scene.{operator}(filepath={str(path)!r})\n"
    code += f'exec(compile({runtime!r}, "blender_skill_runtime", "exec"))\n'
    code += "result = {'scene': inspect_scene(limit=500), 'validation': validate_scene(), 'objects': [inspect_object(o.name) for o in bpy.context.scene.objects]}\n"
    code += f"Path({str(report)!r}).write_text(json.dumps(result, indent=2))\n"
    code += (
        "assert result['scene']['object_count'] > 0, 'No objects in delivered scene'\n"
    )
    code += (
        "assert not result['validation']['issues'], result['validation']['issues']\n"
    )
    script = directory / "verify.py"
    script.write_text(code, encoding="utf-8")
    result = start_job(snapshot, script, directory, blender_binary=blender_binary)
    return _artifacts(result, report=str(report))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "action",
        choices=[
            "status",
            "scene",
            "object",
            "material",
            "execute",
            "run-script",
            "screenshot",
            "save",
            "checkpoint",
            "validate",
            "export",
            "preview",
            "call",
            "verify-file",
            "job-status",
            "job-cancel",
        ],
    )
    parser.add_argument("value", nargs="?")
    parser.add_argument(
        "--params", default="{}", help="JSON keyword arguments for the action"
    )
    args = parser.parse_args()
    from jobs import cancel_job, job_status

    actions = {
        "status": status,
        "scene": scene,
        "object": object_info,
        "material": material_info,
        "execute": execute,
        "run-script": run_script,
        "screenshot": screenshot,
        "save": save,
        "checkpoint": checkpoint,
        "validate": validate,
        "export": export_scene,
        "preview": render_preview,
        "call": call,
        "verify-file": verify_file,
        "job-status": job_status,
        "job-cancel": cancel_job,
    }
    try:
        params = json.loads(args.params)
        positional = [args.value] if args.value is not None else []
        result = actions[args.action](*positional, **params)
        print(json.dumps(result, indent=2))
    except Exception as exc:
        print(f"{type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
