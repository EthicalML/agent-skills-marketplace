"""Executed inside Blender by blender.py; not imported by the external Python."""

import math
from pathlib import Path

import bpy
from mathutils import Vector


def plain(value):
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, bpy.types.ID):
        return value.name
    try:
        return [plain(v) for v in value]
    except TypeError:
        return str(value)


def properties(value):
    result = {}
    for prop in value.bl_rna.properties:
        if prop.identifier == "rna_type" or prop.type == "COLLECTION":
            continue
        try:
            result[prop.identifier] = plain(getattr(value, prop.identifier))
        except (AttributeError, TypeError, ValueError):
            pass
    return result


def selected_objects(collection=None):
    if collection is not None:
        if collection not in bpy.data.collections:
            raise ValueError(f"Unknown collection: {collection}")
        return list(bpy.data.collections[collection].all_objects)
    return list(bpy.context.scene.objects)


def inspect_scene(offset=0, limit=50, collection=None):
    if offset < 0 or not 1 <= limit <= 500:
        raise ValueError("offset must be >= 0; limit must be 1..500")
    scene = bpy.context.scene
    objects = sorted(selected_objects(collection), key=lambda obj: obj.name)
    end = offset + limit
    return {
        "name": scene.name,
        "file": bpy.data.filepath,
        "dirty": bpy.data.is_dirty,
        "version": bpy.app.version_string,
        "mode": bpy.context.mode,
        "active": bpy.context.view_layer.objects.active.name
        if bpy.context.view_layer.objects.active
        else None,
        "selected": [o.name for o in bpy.context.selected_objects],
        "object_count": len(objects),
        "offset": offset,
        "next_offset": end if end < len(objects) else None,
        "objects": [
            {
                "name": o.name,
                "type": o.type,
                "location": list(o.matrix_world.translation),
                "dimensions": list(o.dimensions),
                "hidden_render": o.hide_render,
                "collections": [c.name for c in o.users_collection],
            }
            for o in objects[offset:end]
        ],
        "scenes": [s.name for s in bpy.data.scenes],
        "collections": [c.name for c in scene.collection.children],
        "camera": scene.camera.name if scene.camera else None,
        "world": scene.world.name if scene.world else None,
        "frame": scene.frame_current,
        "frame_range": [scene.frame_start, scene.frame_end],
        "fps": scene.render.fps / scene.render.fps_base,
        "units": {
            "system": scene.unit_settings.system,
            "scale": scene.unit_settings.scale_length,
        },
        "render": {
            "engine": scene.render.engine,
            "resolution": [scene.render.resolution_x, scene.render.resolution_y],
            "percentage": scene.render.resolution_percentage,
            "output": scene.render.filepath,
            "format": scene.render.image_settings.file_format,
            "view_transform": scene.view_settings.view_transform,
        },
    }


def animation_info(obj):
    data = obj.animation_data
    if not data:
        return None
    action = data.action
    result = {
        "action": action.name if action else None,
        "frame_range": list(action.frame_range) if action else None,
        "drivers": [
            {"path": f.data_path, "expression": f.driver.expression}
            for f in data.drivers
        ],
        "nla_tracks": [t.name for t in data.nla_tracks],
    }
    if action:
        curves = []
        if hasattr(action, "layers") and data.action_slot:
            for layer in action.layers:
                for strip in layer.strips:
                    if hasattr(strip, "channelbag"):
                        bag = strip.channelbag(data.action_slot)
                        if bag:
                            curves.extend(bag.fcurves)
        elif hasattr(action, "fcurves"):
            curves.extend(action.fcurves)
        result["channels"] = [
            {
                "path": f.data_path,
                "index": f.array_index,
                "keys": len(f.keyframe_points),
            }
            for f in curves
        ]
    return result


def mesh_info(obj):
    if obj.type != "MESH":
        return None
    import bmesh

    bm = bmesh.new()
    try:
        bm.from_mesh(obj.data)
        return {
            "vertices": len(bm.verts),
            "edges": len(bm.edges),
            "faces": len(bm.faces),
            "non_manifold_edges": sum(not e.is_manifold for e in bm.edges),
            "loose_vertices": sum(not v.link_edges for v in bm.verts),
            "degenerate_faces": sum(f.calc_area() < 1e-12 for f in bm.faces),
            "uv_layers": [uv.name for uv in obj.data.uv_layers],
            "note": "Base mesh in object space; modifiers not evaluated. Open surfaces can be intentional.",
        }
    finally:
        bm.free()


def inspect_object(name, mesh=False):
    obj = bpy.data.objects[name]
    result = {
        "name": obj.name,
        "type": obj.type,
        "location": list(obj.location),
        "rotation": list(obj.rotation_euler),
        "scale": list(obj.scale),
        "dimensions": list(obj.dimensions),
        "world_matrix": [list(row) for row in obj.matrix_world],
        "world_bounds": [list(obj.matrix_world @ Vector(v)) for v in obj.bound_box],
        "parent": obj.parent.name if obj.parent else None,
        "materials": [
            s.material.name if s.material else None for s in obj.material_slots
        ],
        "modifiers": [properties(m) for m in obj.modifiers],
        "constraints": [properties(c) for c in obj.constraints],
        "animation": animation_info(obj),
        "hidden_render": obj.hide_render,
    }
    if obj.type in {"CAMERA", "LIGHT"}:
        result["data"] = properties(obj.data)
    if mesh:
        result["mesh"] = mesh_info(obj)
    return result


def inspect_material(name):
    mat = bpy.data.materials[name]
    tree = mat.node_tree
    return {
        "name": name,
        "nodes": [
            {
                "name": n.name,
                "type": n.bl_idname,
                "inputs": [
                    {
                        "name": s.name,
                        "identifier": s.identifier,
                        "linked": s.is_linked,
                        "value": plain(s.default_value)
                        if hasattr(s, "default_value")
                        else None,
                    }
                    for s in n.inputs
                ],
                "image": n.image.filepath if hasattr(n, "image") and n.image else None,
            }
            for n in tree.nodes
        ]
        if tree
        else [],
        "links": [
            {
                "from": [link.from_node.name, link.from_socket.identifier],
                "to": [link.to_node.name, link.to_socket.identifier],
            }
            for link in tree.links
        ]
        if tree
        else [],
    }


def save_file(path, copy=False, pack=False):
    target = Path(path)
    if target.suffix.lower() != ".blend":
        raise ValueError("Save path must end with .blend")
    target.parent.mkdir(parents=True, exist_ok=True)
    if pack:
        bpy.ops.file.pack_all()
    # Remap relative resource paths for the new snapshot location.
    bpy.ops.wm.save_as_mainfile(filepath=str(target), copy=copy, relative_remap=True)
    return {
        "path": str(target),
        "bytes": target.stat().st_size,
        "copy": copy,
        "packed": pack,
    }


def validate_scene(collection=None, mesh=False):
    objects = selected_objects(collection)
    issues = []
    for obj in objects:
        if any(abs(v) < 1e-10 for v in obj.scale):
            issues.append({"object": obj.name, "kind": "zero_scale"})
        if not all(math.isfinite(v) for row in obj.matrix_world for v in row):
            issues.append({"object": obj.name, "kind": "non_finite_transform"})
        if mesh and obj.type == "MESH":
            info = mesh_info(obj)
            for key in ("non_manifold_edges", "loose_vertices", "degenerate_faces"):
                if info[key]:
                    issues.append({"object": obj.name, "kind": key, "count": info[key]})
    for image in bpy.data.images:
        if (
            image.users
            and image.source == "FILE"
            and image.filepath
            and not image.packed_file
        ):
            path = bpy.path.abspath(image.filepath, library=image.library)
            if not Path(path).exists():
                issues.append(
                    {"image": image.name, "kind": "missing_image", "path": path}
                )
    for library in bpy.data.libraries:
        path = bpy.path.abspath(library.filepath)
        if not Path(path).exists():
            issues.append({"kind": "missing_library", "path": path})
    return {
        "objects_checked": len(objects),
        "issues": issues,
        "camera": bpy.context.scene.camera.name if bpy.context.scene.camera else None,
        "scope": "Transforms and file resources; base mesh topology when requested. Visual and task-specific checks still required.",
    }


def export_file(
    path, format="glb", object_names=None, selection_only=False, apply_modifiers=True
):
    if format not in {"glb", "fbx"}:
        raise ValueError("format must be glb or fbx")
    if Path(path).suffix.lower() != "." + format:
        raise ValueError("Export extension must match format")
    context = bpy.context
    previous_selected = list(context.selected_objects)
    previous_active = context.view_layer.objects.active
    previous_mode = previous_active.mode if previous_active else "OBJECT"
    try:
        if previous_mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
        if object_names is not None:
            targets = set()
            for name in object_names:
                obj = context.scene.objects.get(name)
                if obj is None:
                    raise ValueError(f"Object not in current scene: {name}")
                targets.add(obj)
                targets.update(obj.children_recursive)
            if not targets:
                raise ValueError("No objects requested for export")
            for obj in context.selected_objects:
                obj.select_set(False)
            for obj in targets:
                obj.select_set(True)
            selection_only = True
        elif selection_only and not context.selected_objects:
            raise ValueError("Nothing selected for export")
        names = (
            [obj.name for obj in context.selected_objects]
            if selection_only
            else [obj.name for obj in context.scene.objects]
        )
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        if format == "glb":
            bpy.ops.export_scene.gltf(
                filepath=path,
                export_format="GLB",
                use_active_scene=True,
                use_selection=selection_only,
                export_apply=apply_modifiers,
            )
        else:
            bpy.ops.export_scene.fbx(
                filepath=path,
                use_selection=selection_only,
                use_mesh_modifiers=apply_modifiers,
            )
        return {"path": path, "bytes": Path(path).stat().st_size, "objects": names}
    finally:
        for obj in context.selected_objects:
            obj.select_set(False)
        for obj in previous_selected:
            obj.select_set(True)
        context.view_layer.objects.active = previous_active
        if previous_active and previous_mode != "OBJECT":
            bpy.ops.object.mode_set(mode=previous_mode)
