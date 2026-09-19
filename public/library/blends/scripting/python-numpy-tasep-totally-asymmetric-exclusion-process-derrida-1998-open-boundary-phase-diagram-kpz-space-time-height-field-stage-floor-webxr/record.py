"""
record.py — viewport animation renderer for TASEP kymograph entry.
Outputs: public/library/videos/scripting/<slug>/viewport.mp4
Run from Blender: blender --background tasep_floor.blend --python record.py

Animation: morphs Basis → SK_MaxCurr → SK_Shock → SK_HDphase → Basis
over 90 frames at 30 fps (3 seconds).  Camera orbits overhead.
"""

import bpy
import numpy as np

OUT_PATH  = "//../../videos/scripting/python-numpy-tasep-totally-asymmetric-exclusion-process-derrida-1998-open-boundary-phase-diagram-kpz-space-time-height-field-stage-floor-webxr/viewport.mp4"
FPS       = 30
N_FRAMES  = 90         # 3-second clip: LD → MC → Shock → HD → LD

sc  = bpy.context.scene
sc.render.fps            = FPS
sc.render.resolution_x   = 1920
sc.render.resolution_y   = 1080
sc.render.image_settings.file_format = 'FFMPEG'
sc.render.ffmpeg.format              = 'MPEG4'
sc.render.ffmpeg.codec               = 'H264'
sc.render.ffmpeg.constant_rate_factor = 'HIGH'
sc.render.filepath = OUT_PATH
sc.frame_start = 1
sc.frame_end   = N_FRAMES

obj = bpy.data.objects.get("tasep_floor")
if obj is None:
    raise RuntimeError("tasep_floor not found — run blueprint.py first")

keys = obj.data.shape_keys.key_blocks
SK_NAMES = ["Basis", "SK_MaxCurr", "SK_Shock", "SK_HDphase", "Basis"]

# keyframe schedule: each phase holds for 18 frames, 4 transitions × 4 frames
# [frame: (active_key, value)]
schedule = []
for seg, name in enumerate(SK_NAMES):
    f_start = seg * (N_FRAMES // (len(SK_NAMES) - 1))
    schedule.append((min(f_start, N_FRAMES), name))

# zero all keys at frame 1
for sk in keys:
    sk.value = 0.0
    sk.keyframe_insert("value", frame=1)

for frame, active in schedule:
    for sk in keys:
        sk.value = 1.0 if sk.name == active else 0.0
        sk.keyframe_insert("value", frame=max(1, frame))

# camera: 45° overhead orbit
cam_data = bpy.data.cameras.new("RecordCam")
cam_data.lens = 35.0
cam = bpy.data.objects.new("RecordCam", cam_data)
bpy.context.collection.objects.link(cam)
sc.camera = cam

# position: above and angled
r = 7.0
cam.location = (0.0, -r * np.sin(np.radians(45)), r * np.cos(np.radians(45)))
cam.rotation_euler = (np.radians(45), 0.0, 0.0)

# subtle orbit: rotate around Z over full clip
for f in [1, N_FRAMES]:
    angle = np.radians(30) if f == 1 else np.radians(-30)
    cam.rotation_euler[2] = angle
    cam.keyframe_insert("rotation_euler", frame=f)

bpy.ops.render.render(animation=True)
