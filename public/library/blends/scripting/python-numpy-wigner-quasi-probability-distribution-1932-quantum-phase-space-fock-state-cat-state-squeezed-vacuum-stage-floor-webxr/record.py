"""
record.py — Viewport animation for the Wigner quasi-probability floor.

Run this inside Blender 5.1 after blueprint.py has built the scene.
It sweeps the active shape key from Basis → SK_Cat → SK_Fock5 → SK_Squeezed
over 90 frames (3 s at 30 fps), then renders a 720p viewport animation
to public/library/videos/scripting/<slug>/viewport.mp4.

WHY viewport render, not Cycles: the goal is a quick preview video
showing the shape-key morphing live — viewport render captures the
cobalt/amber colour attribute which Cycles also picks up, but Cycles
at 128 samples per frame would take ~40 min for 90 frames. The Workbench
renderer with MatCap captures the phase-space topology clearly.
"""

import bpy
import os

SLUG = (
    "python-numpy-wigner-quasi-probability-distribution-1932-quantum-phase-space"
    "-fock-state-cat-state-squeezed-vacuum-stage-floor-webxr"
)

FPS        = 30
DURATION_S = 5
N_FRAMES   = FPS * DURATION_S    # 150 frames

OUT_DIR  = os.path.normpath(
    os.path.join(
        bpy.path.abspath("//"),
        "..", "..", "..", "..", "..", "..",   # repo root
        "public", "library", "videos", "scripting", SLUG,
    )
)
os.makedirs(OUT_DIR, exist_ok=True)

scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end   = N_FRAMES
scene.render.fps  = FPS
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.filepath = os.path.join(OUT_DIR, "viewport")
scene.render.image_settings.file_format = 'FFMPEG'
scene.render.ffmpeg.format = 'MPEG4'
scene.render.ffmpeg.codec  = 'H264'
scene.render.ffmpeg.constant_rate_factor = 'MEDIUM'

# ── Workbench renderer for colour-attribute visibility ────────────────────────
scene.render.engine = 'BLENDER_WORKBENCH'
scene.display.shading.color_type = 'VERTEX'
scene.display.shading.light = 'MATCAP'

# ── Camera setup: top-down angled view of the floor ──────────────────────────
cam_data = bpy.data.cameras.new("RecordCam")
cam_data.lens = 35
cam_obj  = bpy.data.objects.new("RecordCam", cam_data)
bpy.context.collection.objects.link(cam_obj)
cam_obj.location = (0.0, -4.5, 3.5)
cam_obj.rotation_euler = (1.05, 0.0, 0.0)   # ~60° tilt
scene.camera = cam_obj

# ── Keyframe shape-key weights ───────────────────────────────────────────────
floor_obj = bpy.data.objects.get("wigner_phase_floor")
if floor_obj is None:
    raise RuntimeError("Run blueprint.py first to create 'wigner_phase_floor'.")

kb = floor_obj.data.shape_keys.key_blocks

# Sequence: Basis (1-30) → SK_Fock1 (30-60) → SK_Cat (60-90) → SK_Fock5 (90-120) → SK_Squeezed (120-150)
TIMELINE = [
    (1,   "Basis",       1.0),
    (30,  "Basis",       0.0),
    (30,  "SK_Fock1",    1.0),
    (60,  "SK_Fock1",    0.0),
    (60,  "SK_Cat",      1.0),
    (90,  "SK_Cat",      0.0),
    (90,  "SK_Fock5",    1.0),
    (120, "SK_Fock5",    0.0),
    (120, "SK_Squeezed", 1.0),
    (150, "SK_Squeezed", 0.0),
]

for key_name in ("SK_Fock1", "SK_Cat", "SK_Fock5", "SK_Squeezed"):
    kb[key_name].value = 0.0

for frame, sk_name, val in TIMELINE:
    scene.frame_set(frame)
    kb[sk_name].value = val
    kb[sk_name].keyframe_insert("value", frame=frame)

# ── Render ────────────────────────────────────────────────────────────────────
bpy.ops.render.opengl(animation=True)
print(f"[record] viewport.mp4 → {OUT_DIR}")
