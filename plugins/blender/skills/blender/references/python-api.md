# Python API

Use the absolute skill path discovered from SKILL.md; never rely on the current working directory or a development checkout path.

```python
import sys

sys.path.insert(0, "/absolute/path/to/blender/scripts")
import blender as B
from jobs import start_job, job_status, cancel_job

print(B.status())
print(B.scene(offset=0, limit=50, collection=None))
print(B.object_info("Cube", mesh=True))
print(B.material_info("Material"))
B.run_script("/absolute/project/build.py", {"height": 2.0})
B.screenshot("/absolute/project/tmp/view.png")
```

| Function | Result / behavior |
| --- | --- |
| `status()` | Blender version, add-on version/protocol, core capabilities |
| `scene(offset=0, limit=50, collection=None)` | Current scene, selected objects, paginated objects, next offset, camera, render settings |
| `object_info(name, mesh=False)` | Bounds, transforms, modifiers, constraints, materials, animation; optional base mesh statistics |
| `material_info(name)` | Nodes, socket values, links and texture paths |
| `execute(code)` | Run trusted Python in the live instance; return printed text |
| `run_script(path, parameters=None)` | Run a saved script in Blender; supplies `PARAMS` and `__file__` |
| `screenshot(path, max_size=1400)` | Write viewport PNG; returns its absolute path |
| `checkpoint(path)` | Save a .blend copy without switching the active file path |
| `save(path, copy=False, pack=False)` | Save a .blend, optionally pack resources |
| `validate(collection=None, mesh=False)` | Findings for transforms, file resources, optional base mesh topology; not a visual quality score |
| `describe_node_type(bl_idname=..., property_overrides=None)` | Live node socket/property schema |
| `api_lookup(query=...)` | Live RNA/operator schema, e.g. `bpy.ops.mesh.primitive_cube_add` |
| `export_scene(path, format='glb', object_names=None, selection_only=False, apply_modifiers=True)` | GLB/FBX export; checks file exists and is nonempty |
| `render_preview(output_dir, camera=None, frame=None, resolution=640, samples=32, blender_binary=None)` | Start background preview; returns `job_dir` and `image`. Resolution is width; samples applies to Cycles. |
| `verify_file(path, output_dir, blender_binary=None)` | Background reopen/reimport; returns job_dir and report path |
| `call(command, **params)` | Direct add-on command; see command catalogue when a named helper is insufficient |

Connection overrides on `call`, `execute`, `run_script`, `screenshot`, and `status`: `port`, `timeout`. Set `BLENDER_PORT` for the whole workflow; default 9876. `call(..., params={...})` avoids collisions with helper parameter names. Calls are sequential; never issue concurrent mutations against one scene. Other helpers use that environment/default connection.

Print only the fields needed for the decision; avoid dumping entire scene/material reports or image data into the conversation. For successful job polls, state and artifact paths usually suffice; inspect log_tail on failure or when diagnosing slow progress.

The CLI uses the same functions:

```sh
python3 /absolute/skill/scripts/blender.py scene --params '{"limit": 20}'
python3 /absolute/skill/scripts/blender.py run-script /absolute/project/build.py --params '{"parameters": {"height": 2.0}}'
python3 /absolute/skill/scripts/blender.py screenshot /absolute/project/tmp/view.png
python3 /absolute/skill/scripts/blender.py call bpy_api_lookup --params '{"query": "Object.ray_cast"}'
```

`BlenderError` means a connection or reported execution error. `OutcomeUnknown` means a submitted operation lost its response; inspect before deciding to retry. Do not parse success from text alone; background jobs have explicit states.

For an additional add-on command, read only its entry in `references/commands.json`, e.g. with Python `json.load(...)[command]`. The catalogue is extracted from the pinned upstream add-on; it describes socket commands, whose names may differ from MCP tool names. The generic call is not an MCP tools/call wrapper. Service commands require their scene integration enabled and credentials where applicable.
