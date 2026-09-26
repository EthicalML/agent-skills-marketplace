"""Run with Blender --background --python-exit-code 1 --python this_file.py.

Checks context restoration, pagination, material inspection and copied resources.
Uses a unique directory under repository tmp; never touches the live Blender.
"""

import importlib.util
import json
import struct
import tempfile
from pathlib import Path

import bpy

root = Path(__file__).resolve().parents[3]
(root / "tmp").mkdir(exist_ok=True)
work = Path(tempfile.mkdtemp(prefix="blender-runtime-", dir=root / "tmp"))
spec = importlib.util.spec_from_file_location(
    "runtime", Path(__file__).resolve().parents[1] / "skills/blender/scripts/runtime.py"
)
R = importlib.util.module_from_spec(spec)
spec.loader.exec_module(R)

bpy.ops.wm.read_factory_settings(use_empty=True)
for i in range(12):
    bpy.ops.mesh.primitive_cube_add(location=(i * 3, 0, 0))
    bpy.context.object.name = f"Test{i:02d}"
assert R.inspect_scene(limit=5)["next_offset"] == 5
assert len(R.inspect_scene(offset=10, limit=5)["objects"]) == 2
obj = bpy.data.objects["Test00"]
for o in bpy.context.selected_objects:
    o.select_set(False)
obj.select_set(True)
bpy.context.view_layer.objects.active = obj
bpy.ops.object.mode_set(mode="EDIT")
other_scene = bpy.data.scenes.new("UnrelatedScene")
foreign = bpy.data.objects.new("MustNotExport", bpy.data.meshes.new("ForeignMesh"))
other_scene.collection.objects.link(foreign)
R.export_file(str(work / "asset.glb"), object_names=["Test01"])
wire = (work / "asset.glb").read_bytes()
chunk_length = struct.unpack_from("<I", wire, 12)[0]
gltf = json.loads(wire[20 : 20 + chunk_length])
assert len(gltf["scenes"]) == 1, gltf["scenes"]
assert {n["name"] for n in gltf["nodes"]} == {"Test01"}, gltf["nodes"]
assert bpy.context.mode == "EDIT_MESH"
assert bpy.context.view_layer.objects.active == obj
assert [o.name for o in bpy.context.selected_objects] == ["Test00"]
bpy.ops.object.mode_set(mode="OBJECT")
mat = bpy.data.materials.new("TextureMaterial")
obj.data.materials.append(mat)
image = bpy.data.images.new("Texture", width=8, height=8)
image.filepath_raw = str(work / "texture.png")
image.file_format = "PNG"
image.save()
node = mat.node_tree.nodes.new("ShaderNodeTexImage")
node.image = image
assert R.inspect_material(mat.name)["nodes"]
R.save_file(str(work / "original.blend"))
image.filepath = "//texture.png"
R.save_file(str(work / "original.blend"))
R.save_file(str(work / "nested/copy.blend"), copy=True)
assert bpy.data.filepath == str(work / "original.blend")
bpy.ops.wm.open_mainfile(filepath=str(work / "nested/copy.blend"))
assert not R.validate_scene()["issues"], R.validate_scene()
assert Path(bpy.path.abspath(bpy.data.images["Texture"].filepath)).is_file()
print(json.dumps({"runtime_checks": "passed", "directory": str(work)}))
