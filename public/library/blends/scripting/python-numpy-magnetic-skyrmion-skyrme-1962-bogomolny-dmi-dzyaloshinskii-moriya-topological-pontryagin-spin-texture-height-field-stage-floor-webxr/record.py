"""
record.py — viewport animation renderer for magnetic-skyrmion entry.
Outputs: public/library/videos/scripting/<slug>/viewport.mp4

Run from Blender:
  blender --background skyrmion_floor.blend --python record.py

Animation: morphs Basis (single skyrmion) → SK_Lattice → SK_Helical →
SK_FM → Basis over 150 frames (5 seconds) at 30 fps.
Camera is placed 40° above the XY plane and orbits ±20° around Z.
"""

import bpy
import numpy as np

SLUG = (
    "python-numpy-magnetic-skyrmion-skyrme-1962-bogomolny-dmi-dzyaloshinskii"
    "-moriya-topological-pontryagin-spin-texture-height-field-stage-floor-webxr"
)
OUT_PATH = f"//../../videos/scripting/{SLUG}/viewport.mp4"

FPS      = 30
N_FRAMES = 150   # 5-second clip

sc = bpy.context.scene
sc.render.fps                         = FPS
sc.render.resolution_x                = 1920
sc.render.resolution_y                = 1080
sc.render.image_settings.file_format  = 'FFMPEG'
sc.render.ffmpeg.format               = 'MPEG4'
sc.render.ffmpeg.codec                = 'H264'
sc.render.ffmpeg.constant_rate_factor = 'HIGH'
sc.render.filepath = OUT_PATH
sc.frame_start = 1
sc.frame_end   = N_FRAMES

obj = bpy.data.objects.get("skyrmion_floor")
if obj is None:
    raise RuntimeError("skyrmion_floor not found — run blueprint.py first")

keys     = obj.data.shape_keys.key_blocks
SK_CYCLE = ["Basis", "SK_Lattice", "SK_Helical", "SK_FM", "Basis"]

# Zero all keys at frame 1
for sk in keys:
    sk.value = 0.0
    sk.keyframe_insert("value", frame=1)

# Keyframe each phase peak at equally-spaced frames
n_seg  = len(SK_CYCLE) - 1
stride = N_FRAMES // n_seg
for seg, name in enumerate(SK_CYCLE):
    frame = min(1 + seg * stride, N_FRAMES)
    for sk in keys:
        sk.value = 1.0 if sk.name == name else 0.0
        sk.keyframe_insert("value", frame=frame)

# Camera — 40° elevation, slow ±20° orbit around Z
cam_data = bpy.data.cameras.new("RecordCam")
cam_data.lens = 35.0
cam = bpy.data.objects.new("RecordCam", cam_data)
bpy.context.collection.objects.link(cam)
sc.camera = cam

elev    = np.radians(40)
r_cam   = 8.0
cam.location      = (0.0, -r_cam * np.cos(elev), r_cam * np.sin(elev))
cam.rotation_euler = (elev, 0.0, 0.0)

for f, z_deg in ((1, 20), (N_FRAMES, -20)):
    cam.rotation_euler[2] = np.radians(z_deg)
    cam.keyframe_insert("rotation_euler", frame=f)

bpy.ops.render.render(animation=True)
