"""
record.py — viewport animation renderer for Vicsek active-matter entry.
Outputs: public/library/videos/scripting/<slug>/viewport.mp4

Run from Blender:
  blender --background vicsek_floor.blend --python record.py

Animation: morphs Basis (ordered) → SK_Bands → SK_Crit → SK_Dis → Basis
over 120 frames at 30 fps (4 seconds), camera orbiting 30° overhead.
"""

import bpy
import numpy as np

SLUG = (
    "python-numpy-vicsek-1995-active-matter-self-propelled-particles-polar-order"
    "-parameter-flocking-phase-transition-height-field-stage-floor-webxr"
)
OUT_PATH = f"//../../videos/scripting/{SLUG}/viewport.mp4"

FPS      = 30
N_FRAMES = 120   # 4-second clip

sc = bpy.context.scene
sc.render.fps                        = FPS
sc.render.resolution_x               = 1920
sc.render.resolution_y               = 1080
sc.render.image_settings.file_format = 'FFMPEG'
sc.render.ffmpeg.format              = 'MPEG4'
sc.render.ffmpeg.codec               = 'H264'
sc.render.ffmpeg.constant_rate_factor = 'HIGH'
sc.render.filepath = OUT_PATH
sc.frame_start = 1
sc.frame_end   = N_FRAMES

obj = bpy.data.objects.get("vicsek_floor")
if obj is None:
    raise RuntimeError("vicsek_floor not found — run blueprint.py first")

keys     = obj.data.shape_keys.key_blocks
SK_CYCLE = ["Basis", "SK_Bands", "SK_Crit", "SK_Dis", "Basis"]

# Zero all keys at frame 1
for sk in keys:
    sk.value = 0.0
    sk.keyframe_insert("value", frame=1)

# Keyframe each phase at equally-spaced frames
n_seg  = len(SK_CYCLE) - 1
stride = N_FRAMES // n_seg
for seg, name in enumerate(SK_CYCLE):
    frame = min(1 + seg * stride, N_FRAMES)
    for sk in keys:
        sk.value = 1.0 if sk.name == name else 0.0
        sk.keyframe_insert("value", frame=frame)

# Camera — 40° above-horizon orbit
cam_data = bpy.data.cameras.new("RecordCam")
cam_data.lens = 35.0
cam  = bpy.data.objects.new("RecordCam", cam_data)
bpy.context.collection.objects.link(cam)
sc.camera = cam

elev  = np.radians(40)
r_cam = 8.0
cam.location     = (0.0, -r_cam * np.cos(elev), r_cam * np.sin(elev))
cam.rotation_euler = (elev, 0.0, 0.0)

# Slow 30° orbit around Z over the full clip
for f, z_deg in ((1, 15), (N_FRAMES, -15)):
    cam.rotation_euler[2] = np.radians(z_deg)
    cam.keyframe_insert("rotation_euler", frame=f)

bpy.ops.render.render(animation=True)
