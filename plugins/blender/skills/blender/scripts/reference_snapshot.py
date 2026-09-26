"""Read-only pose-aware measurements, usable inside Blender on explicit model objects."""
import numpy as np


def snapshot(objects, rigs=()):
    """Return tight world bounds and rig anchors in height-normalized coordinates.

    Caller excludes floors/accessories and supplies the model's rig(s). Bone anchors
    are controls, not automatically identified surface/anatomical landmarks.
    """
    import bpy

    bpy.context.view_layer.update()
    graph = bpy.context.evaluated_depsgraph_get()
    parts = {}
    for obj in objects:
        if obj.type != 'MESH':
            raise ValueError(f'Expected mesh object: {obj.name}')
        evaluated = obj.evaluated_get(graph)
        mesh = evaluated.to_mesh()
        try:
            points = np.empty((len(mesh.vertices), 3), dtype=np.float64)
            mesh.vertices.foreach_get('co', points.ravel())
            matrix = np.asarray(evaluated.matrix_world)
            points = points @ matrix[:3, :3].T + matrix[:3, 3]
            if not len(points) or not np.isfinite(points).all():
                raise ValueError(f'Empty or non-finite mesh: {obj.name}')
            parts[obj.name] = {
                'minimum': points.min(axis=0).tolist(),
                'maximum': points.max(axis=0).tolist(),
                'base_vertices': len(obj.data.vertices),
                'base_polygons': len(obj.data.polygons),
                'evaluated_vertices': len(points),
            }
        finally:
            evaluated.to_mesh_clear()
    if not parts:
        raise ValueError('Supply at least one model mesh')
    low = np.min([p['minimum'] for p in parts.values()], axis=0)
    high = np.max([p['maximum'] for p in parts.values()], axis=0)
    height = float(high[2] - low[2])
    if height <= 1e-9:
        raise ValueError('Model needs a positive Z height')
    origin = (low + high) / 2
    origin[2] = low[2]
    for part in parts.values():
        for key in ('minimum', 'maximum'):
            part['normalized_' + key] = ((np.array(part[key]) - origin) / height).tolist()
    anchors = {}
    states = {}
    for rig in rigs:
        if rig.type != 'ARMATURE':
            raise ValueError(f'Expected armature: {rig.name}')
        evaluated = rig.evaluated_get(graph)
        states[rig.name] = rig.data.pose_position
        for bone in evaluated.pose.bones:
            anchors[f'{rig.name}/{bone.name}'] = {
                key: ((np.array(evaluated.matrix_world @ getattr(bone, key)) - origin) / height).tolist()
                for key in ('head', 'tail')
            }
    return {
        'schema': 1,
        'frame': bpy.context.scene.frame_current,
        'origin_world': origin.tolist(),
        'height_world': height,
        'normalization': '(world_point - origin_world) / height_world; Z up; orientation unchanged',
        'parts': parts,
        'rig_pose_positions': states,
        'normalized_bone_anchors': anchors,
        'limits': 'Bone endpoints are rig anchors, not surface landmarks. Orientation and expression must be aligned separately.',
    }
