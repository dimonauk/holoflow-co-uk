"""
record.py — viewport animation for bz_oregonator_floor.blend
Outputs: public/library/videos/scripting/
         python-numpy-oregonator-belousov-zhabotinsky-bz-fkn-1972-chemical-spiral-wave-height-field-stage-floor-webxr/
         viewport.mp4

Strategy: animate the shape key influence from Basis → SK_Fast → SK_Rings
over 10 seconds (240 frames at 24 fps) so the viewer sees the spiral pattern
morph — compressed wavefronts in SK_Fast, concentric rings in SK_Rings.
Camera orbits 30° around the floor to emphasise the height relief.

Run this AFTER blueprint.py has created bz_oregonator_floor.blend.
"""

import bpy, math, os

# ── output path ──────────────────────────────────────────────────────────────
SLUG = (
    "python-numpy-oregonator-belousov-zhabotinsky-bz-fkn-1972-"
    "chemical-spiral-wave-height-field-stage-floor-webxr"
)
OUT_DIR = os.path.join(
    bpy.path.abspath("//../../videos/scripting"), SLUG
)
os.makedirs(OUT_DIR, exist_ok=True)
OUT_FILE = os.path.join(OUT_DIR, "viewport.mp4")

FPS     = 24
FRAMES  = 240    # 10 seconds

# ── scene setup ──────────────────────────────────────────────────────────────
scn = bpy.context.scene
scn.frame_start = 1
scn.frame_end   = FRAMES
scn.render.fps  = FPS
scn.render.resolution_x = 1920
scn.render.resolution_y = 1080
scn.render.image_settings.file_format = "FFMPEG"
scn.render.ffmpeg.format             = "MPEG4"
scn.render.ffmpeg.codec              = "H264"
scn.render.ffmpeg.constant_rate_factor = "HIGH"
scn.render.filepath = OUT_FILE

# ── camera orbit ─────────────────────────────────────────────────────────────
cam_data = bpy.data.cameras.new("RecordCam")
cam      = bpy.data.objects.new("RecordCam", cam_data)
bpy.context.collection.objects.link(cam)
scn.camera = cam
cam_data.lens = 35.0

# empty at origin that camera tracks
empty = bpy.data.objects.new("CamTarget", None)
empty.location = (0, 0, 0.20)
bpy.context.collection.objects.link(empty)
tc = cam.constraints.new("TRACK_TO")
tc.target = empty
tc.track_axis = "TRACK_NEGATIVE_Z"
tc.up_axis    = "UP_Y"

def set_cam_frame(f, angle_deg, height, radius):
    a = math.radians(angle_deg)
    cam.location = (radius * math.cos(a), radius * math.sin(a), height)
    cam.keyframe_insert("location", frame=f)

# start overhead-ish, orbit gently around
set_cam_frame(1,    30,  7.0, 9.0)
set_cam_frame(80,   60,  5.5, 8.0)
set_cam_frame(160,  90,  4.5, 7.5)
set_cam_frame(240, 120,  4.0, 7.0)

# ── shape key animation ───────────────────────────────────────────────────────
obj = bpy.data.objects.get("bz_oregonator_floor")
if obj and obj.data.shape_keys:
    sks = obj.data.shape_keys.key_blocks

    def sk_val(name, frame, val):
        if name in sks:
            sks[name].value = val
            sks[name].keyframe_insert("value", frame=frame)

    # frame 1: pure Basis
    for sk in ["SK_Fast", "SK_Rings", "SK_Meander"]:
        sk_val(sk, 1, 0.0)

    # frame 80: crossfade to SK_Fast
    sk_val("SK_Fast",    80, 1.0)
    sk_val("SK_Rings",   80, 0.0)
    sk_val("SK_Meander", 80, 0.0)

    # frame 160: crossfade to SK_Rings
    sk_val("SK_Fast",    160, 0.0)
    sk_val("SK_Rings",   160, 1.0)
    sk_val("SK_Meander", 160, 0.0)

    # frame 240: back to Basis
    for sk in ["SK_Fast", "SK_Rings", "SK_Meander"]:
        sk_val(sk, 240, 0.0)

# ── lighting ─────────────────────────────────────────────────────────────────
light_data = bpy.data.lights.new("RecordLight", "SUN")
light      = bpy.data.objects.new("RecordLight", light_data)
bpy.context.collection.objects.link(light)
light.location      = (5, -5, 10)
light.rotation_euler = (0.5, 0, 0.8)
light_data.energy   = 4.0

# ── render ───────────────────────────────────────────────────────────────────
bpy.ops.render.render(animation=True)
print(f"record.py → {OUT_FILE}")
