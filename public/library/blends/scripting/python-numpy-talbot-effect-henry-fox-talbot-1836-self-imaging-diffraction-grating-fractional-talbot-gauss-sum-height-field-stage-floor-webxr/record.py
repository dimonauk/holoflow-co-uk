"""
record.py — Viewport animation for the Talbot Effect floor mesh
Renders a 360° camera orbit + shape-key sweep to viewport.mp4 (OpenGL).

Run after blueprint.py has been executed.
Output: public/library/videos/scripting/
        python-numpy-talbot-effect-henry-fox-talbot-1836-self-imaging-diffraction-grating-
        fractional-talbot-gauss-sum-height-field-stage-floor-webxr/viewport.mp4
"""

import sys

try:
    import bpy
    from mathutils import Vector
except ModuleNotFoundError:
    sys.exit("Run inside Blender.")

# ── constants ─────────────────────────────────────────────────────────────────
OBJ_NAME    = "Talbot_Floor"
FPS         = 24
CAM_RADIUS  = 12.0
CAM_ELEV    = 0.45           # radians above horizon (~26°)
ORBIT_DEG   = 360            # full rotation
N_ORBIT     = FPS * 12       # 12 s orbit
N_SWEEP     = FPS * 12       # 4 × 3 s SK sweeps
FADE_FRAMES = 12             # blend window between keys
TOTAL       = N_ORBIT + N_SWEEP

import math, os

VIDEO_DIR = os.path.join(
    os.path.dirname(bpy.data.filepath),
    "../../../../../../videos/scripting/"
    "python-numpy-talbot-effect-henry-fox-talbot-1836-self-imaging-diffraction-"
    "grating-fractional-talbot-gauss-sum-height-field-stage-floor-webxr"
)

# ── scene setup ───────────────────────────────────────────────────────────────
scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end   = TOTAL
scene.render.fps  = FPS
scene.render.image_settings.file_format  = "FFMPEG"
scene.render.ffmpeg.format               = "MPEG4"
scene.render.ffmpeg.codec                = "H264"
scene.render.ffmpeg.constant_rate_factor = "HIGH"
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
os.makedirs(VIDEO_DIR, exist_ok=True)
scene.render.filepath = os.path.join(VIDEO_DIR, "viewport.mp4")

# ── camera ────────────────────────────────────────────────────────────────────
if "RecordCam" in bpy.data.cameras:
    bpy.data.cameras.remove(bpy.data.cameras["RecordCam"])
cam_data = bpy.data.cameras.new("RecordCam")
cam_ob   = bpy.data.objects.new("RecordCam", cam_data)
bpy.context.collection.objects.link(cam_ob)
scene.camera = cam_ob

floor_ob = bpy.data.objects.get(OBJ_NAME)
if floor_ob is None:
    sys.exit(f"Object '{OBJ_NAME}' not found — run blueprint.py first.")

def _set_cam(frame: int):
    scene.frame_set(frame)
    t        = (frame - 1) / max(N_ORBIT - 1, 1)
    angle    = math.radians(ORBIT_DEG) * t
    cx       = CAM_RADIUS * math.cos(angle + math.pi * 0.25)
    cy       = CAM_RADIUS * math.sin(angle + math.pi * 0.25) * math.cos(CAM_ELEV)
    cz       = CAM_RADIUS * math.sin(CAM_ELEV)
    cam_ob.location = Vector((cx, cy, cz))
    direction = Vector((0, 0, 0)) - cam_ob.location
    cam_ob.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    cam_ob.keyframe_insert("location",       frame=frame)
    cam_ob.keyframe_insert("rotation_euler", frame=frame)

for f in range(1, N_ORBIT + 1, max(1, N_ORBIT // 72)):
    _set_cam(f)
_set_cam(N_ORBIT)

# ── shape-key animation ───────────────────────────────────────────────────────
if floor_ob.data.shape_keys is None:
    sys.exit("No shape keys found on the floor object.")

keys_order = ["Basis", "SK_Sine", "SK_Blazed", "SK_Phase"]
n_keys     = len(keys_order)
seg_frames = N_SWEEP // n_keys     # frames per shape-key hold
sk_block   = bpy.data.shape_keys.get(floor_ob.data.shape_keys.name)

def _zero_all(frame: int):
    scene.frame_set(frame)
    for kb in floor_ob.data.shape_keys.key_blocks:
        kb.value = 0.0
        kb.keyframe_insert("value", frame=frame)

def _set_sk(sk_name: str, val: float, frame: int):
    scene.frame_set(frame)
    kb = floor_ob.data.shape_keys.key_blocks.get(sk_name)
    if kb:
        kb.value = val
        kb.keyframe_insert("value", frame=frame)

# Start of SK section: Basis at 1.0
start = N_ORBIT + 1
for ki, sk_name in enumerate(keys_order):
    seg_start = start + ki * seg_frames
    seg_end   = seg_start + seg_frames - 1
    # Fade in
    _zero_all(seg_start)
    _set_sk(sk_name, 0.0, seg_start)
    _set_sk(sk_name, 1.0, seg_start + FADE_FRAMES)
    # Hold
    _set_sk(sk_name, 1.0, seg_end - FADE_FRAMES)
    # Fade out
    _set_sk(sk_name, 0.0, seg_end)

# ── render ────────────────────────────────────────────────────────────────────
print("[TalbotRecord] Rendering viewport.mp4 …")
bpy.ops.render.opengl(animation=True)
print(f"[TalbotRecord] Done → {scene.render.filepath}")
