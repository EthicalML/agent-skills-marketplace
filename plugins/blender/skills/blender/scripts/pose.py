"""Small in-memory pose helpers; use inside Blender. No keyframes or mesh edits."""
from mathutils import Matrix

def snapshot_pose(armature):
    return {bone.name: bone.matrix_basis.copy() for bone in armature.pose.bones}

def restore_pose(armature, snapshot):
    missing = set(snapshot) - set(armature.pose.bones.keys())
    if missing:
        raise ValueError(f'Missing bones: {sorted(missing)}')
    for name, matrix in snapshot.items():
        armature.pose.bones[name].matrix_basis = matrix

def reset_except(armature, snapshot, preserve):
    """Caller supplies asset-specific names; keep POSE mode, never change bind/rest data."""
    preserve = set(preserve)
    unknown = preserve - (set(snapshot) & set(armature.pose.bones.keys()))
    if unknown:
        raise ValueError(f'Unknown preserved bones: {sorted(unknown)}')
    armature.data.pose_position = 'POSE'
    for bone in armature.pose.bones:
        bone.matrix_basis = snapshot[bone.name] if bone.name in preserve else Matrix.Identity(4)
