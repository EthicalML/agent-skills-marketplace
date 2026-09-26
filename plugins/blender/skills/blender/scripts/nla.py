"""Small NLA strip helper; invoke inside Blender. No rig-specific bone names."""
import math

def add_strip(track, action, start, source_start, source_end, *, name=None,
              repeat=1, blend_in=0, blend_out=0, slot=None):
    """Add an explicitly ranged REPLACE strip without hold outside its interval.

    Multiple-slot actions require an explicit slot. This helper sequences strips;
    bone masks must already be encoded by the Action's keyed channels.
    """
    values=[start,source_start,source_end,repeat,blend_in,blend_out]
    if not all(math.isfinite(v) for v in values):
        raise ValueError('Strip settings must be finite')
    duration=(source_end-source_start)*repeat
    if source_end<=source_start or repeat<=0 or min(blend_in,blend_out)<0 or blend_in+blend_out>duration:
        raise ValueError('Invalid source range, repetition or blend duration')
    slots=list(getattr(action,'slots',[]))
    if slot is None:
        if len(slots)>1:
            raise ValueError('Choose a slot for an Action with multiple slots')
        slot=slots[0] if slots else None
    elif slot not in slots:
        raise ValueError('Slot does not belong to this Action')
    end=start+duration
    if any(start<s.frame_end and end>s.frame_start for s in track.strips):
        raise ValueError('Overlapping strips need separate NLA tracks')
    strip=track.strips.new(name or action.name,int(start),action)
    try:
        if slot is not None:strip.action_slot=slot
        strip.action_frame_start=source_start;strip.action_frame_end=source_end
        strip.repeat=repeat;strip.frame_start=start;strip.frame_end=end
        strip.extrapolation='NOTHING';strip.blend_type='REPLACE'
        strip.blend_in=blend_in;strip.blend_out=blend_out
    except Exception:
        track.strips.remove(strip)
        raise
    return strip
