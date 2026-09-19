"""
record.py — viewport animation for Kane-Mele QSH floor
Outputs: public/library/videos/scripting/
  kane-mele-2005-quantum-spin-hall-z2-topological-insulator/viewport.mp4
Run inside Blender 5.1 after blueprint.py has built the scene.
Duration: 10 s at 30 fps = 300 frames.
"""

import bpy
import math
import pathlib

OUT_DIR = pathlib.Path(__file__).parent.parent.parent.parent / (
    "videos/scripting/"
    "kane-mele-2005-quantum-spin-hall-z2-topological-insulator"
)
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_FILE = str(OUT_DIR / "viewport.mp4")

# ── Scene / render settings ───────────────────────────────────────────────────
scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end   = 300
scene.render.fps  = 30

scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.image_settings.file_format = 'FFMPEG'
scene.render.ffmpeg.format              = 'MPEG4'
scene.render.ffmpeg.codec               = 'H264'
scene.render.ffmpeg.constant_rate_factor = 'MEDIUM'
scene.render.filepath = OUT_FILE

# ── Camera orbit ──────────────────────────────────────────────────────────────
cam_data = bpy.data.cameras.new("RecCam")
cam_data.lens = 35
cam = bpy.data.objects.new("RecCam", cam_data)
bpy.context.collection.objects.link(cam)
scene.camera = cam

empty = bpy.data.objects.new("CamTarget", None)
bpy.context.collection.objects.link(empty)
empty.location = (0, 0, 0.35)

track = cam.constraints.new(type='TRACK_TO')
track.target = empty
track.track_axis  = 'TRACK_NEGATIVE_Z'
track.up_axis     = 'UP_Y'

RADIUS = 7.5
TILT   = math.radians(38)

for frame in range(1, 301):
    angle = math.radians(360) * (frame - 1) / 300.0   # full revolution
    cam.location = (
        RADIUS * math.cos(angle),
        RADIUS * math.sin(angle),
        RADIUS * math.sin(TILT),
    )
    cam.keyframe_insert(data_path="location", frame=frame)

# ── Shape-key morph: Basis → SK_StrongSOC → SK_NearCrit → SK_Trivial ─────────
obj = bpy.data.objects.get("kane_mele_floor")
if obj and obj.data.shape_keys:
    keys = obj.data.shape_keys.key_blocks
    sk_names = ["SK_StrongSOC", "SK_NearCrit", "SK_Trivial"]
    schedule = [(1, 60), (80, 140), (160, 220), (240, 300)]  # (in, out) frames

    for key in keys:
        key.value = 0.0
        key.keyframe_insert(data_path="value", frame=1)

    def _morph(from_key, to_key, f_start, f_end):
        for key in keys:
            key.value = 1.0 if key.name == from_key else 0.0
            key.keyframe_insert(data_path="value", frame=f_start)
        for key in keys:
            key.value = 1.0 if key.name == to_key else 0.0
            key.keyframe_insert(data_path="value", frame=f_end)

    # Basis holds frames 1–59
    keys["Basis"].value = 1.0
    keys["Basis"].keyframe_insert(data_path="value", frame=1)
    keys["Basis"].keyframe_insert(data_path="value", frame=60)

    _morph("Basis",       "SK_StrongSOC",  60,  80)
    _morph("SK_StrongSOC", "SK_NearCrit",  140, 160)
    _morph("SK_NearCrit",  "SK_Trivial",   220, 240)

# ── World (black) + HDRI-style ambient ───────────────────────────────────────
world = bpy.data.worlds.new("RecWorld")
world.use_nodes = True
bpy.context.scene.world = world
bg = world.node_tree.nodes["Background"]
bg.inputs["Color"].default_value   = (0.01, 0.01, 0.02, 1.0)
bg.inputs["Strength"].default_value = 0.3

scene.render.engine = 'BLENDER_EEVEE_NEXT'
bpy.ops.render.opengl(animation=True)
print(f"✓ Kane-Mele record → {OUT_FILE}")
