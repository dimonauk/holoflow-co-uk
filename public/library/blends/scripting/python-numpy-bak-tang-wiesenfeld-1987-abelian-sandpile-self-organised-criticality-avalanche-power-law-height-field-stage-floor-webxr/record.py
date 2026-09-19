"""
record.py — viewport animation recorder for the BTW Sandpile tutorial.

Outputs  public/library/videos/scripting/<slug>/viewport.mp4
Run from Blender's script editor AFTER blueprint.py has been executed
(so btw_sandpile_floor exists in the scene with its shape keys).

Animation design (30 fps, 150 frames = 5 s):
  0– 40 f  : Basis (critical state height map)
  40– 80 f : morph to SK_SmallAval (small fractal cluster rises)
  80–110 f : morph to SK_LargeAval (large avalanche footprint)
 110–150 f : morph to SK_Maximal   (uniform h=3 plateau)

Camera orbits 60° during the clip for spatial depth.
"""

import bpy
import os

# ── output path ───────────────────────────────────────────────────────────────
SLUG = (
    "python-numpy-bak-tang-wiesenfeld-1987-abelian-sandpile-"
    "self-organised-criticality-avalanche-power-law-height-field-"
    "stage-floor-webxr"
)
OUT_DIR = os.path.join(
    bpy.path.abspath("//"),
    "..", "..", "..", "..", "..", "..",
    "public", "library", "videos", "scripting", SLUG,
)
os.makedirs(OUT_DIR, exist_ok=True)
OUT_PATH = os.path.join(OUT_DIR, "viewport")   # Blender appends .mp4

# ── render settings ───────────────────────────────────────────────────────────
TOTAL_FRAMES = 150
FPS          = 30
WIDTH        = 1920
HEIGHT       = 1080

scene = bpy.context.scene
scene.render.resolution_x         = WIDTH
scene.render.resolution_y         = HEIGHT
scene.render.fps                  = FPS
scene.frame_start                 = 1
scene.frame_end                   = TOTAL_FRAMES
scene.render.image_settings.file_format = "FFMPEG"
scene.render.ffmpeg.format        = "MPEG4"
scene.render.ffmpeg.codec         = "H264"
scene.render.ffmpeg.constant_rate_factor = "MEDIUM"
scene.render.filepath             = OUT_PATH

# ── camera ────────────────────────────────────────────────────────────────────
import mathutils, math

def _ensure_camera() -> bpy.types.Object:
    cam_data = bpy.data.cameras.new("RecordCam")
    cam_data.lens = 50
    cam = bpy.data.objects.new("RecordCam", cam_data)
    bpy.context.scene.collection.objects.link(cam)
    scene.camera = cam
    return cam


cam = _ensure_camera()
cam.location = mathutils.Vector((0.0, -10.0, 6.5))
cam.rotation_euler = mathutils.Euler((math.radians(55), 0, 0), "XYZ")
cam.keyframe_insert("location", frame=1)
cam.keyframe_insert("rotation_euler", frame=1)

# orbit 60° over the full clip
cam_end_euler = mathutils.Euler(
    (math.radians(55), 0, math.radians(60)), "XYZ"
)
cam.rotation_euler = cam_end_euler
cam.keyframe_insert("rotation_euler", frame=TOTAL_FRAMES)

# ── lighting ──────────────────────────────────────────────────────────────────
def _ensure_light(name: str, kind: str, loc: tuple,
                  energy: float) -> bpy.types.Object:
    ld = bpy.data.lights.new(name=name, type=kind)
    ld.energy = energy
    lo = bpy.data.objects.new(name=name, object_data=ld)
    bpy.context.scene.collection.objects.link(lo)
    lo.location = mathutils.Vector(loc)
    return lo


_ensure_light("KeyLight",  "AREA", ( 5.0,  5.0, 8.0), 800)
_ensure_light("FillLight", "AREA", (-4.0, -3.0, 6.0), 200)

# ── shape-key animation ───────────────────────────────────────────────────────
obj = bpy.data.objects.get("btw_sandpile_floor")
if obj is None:
    raise RuntimeError("btw_sandpile_floor not found; run blueprint.py first")

sk_root = obj.data.shape_keys

def _key(name: str) -> bpy.types.ShapeKey:
    return sk_root.key_blocks[name]


# All keys at rest
for kname in ("Basis", "SK_SmallAval", "SK_LargeAval", "SK_Maximal"):
    _key(kname).value = 0.0


# f1→40 : pure Basis
_key("Basis").value = 1.0
for kname in ("Basis", "SK_SmallAval", "SK_LargeAval", "SK_Maximal"):
    _key(kname).keyframe_insert("value", frame=1)
    _key(kname).keyframe_insert("value", frame=40)

# f40→80 : morph Basis→SmallAval
_key("Basis").value       = 0.0
_key("SK_SmallAval").value = 1.0
for kname in ("Basis", "SK_SmallAval"):
    _key(kname).keyframe_insert("value", frame=80)

# f80→110 : SmallAval→LargeAval
_key("SK_SmallAval").value = 0.0
_key("SK_LargeAval").value = 1.0
for kname in ("SK_SmallAval", "SK_LargeAval"):
    _key(kname).keyframe_insert("value", frame=110)

# f110→150 : LargeAval→Maximal
_key("SK_LargeAval").value = 0.0
_key("SK_Maximal").value   = 1.0
for kname in ("SK_LargeAval", "SK_Maximal"):
    _key(kname).keyframe_insert("value", frame=150)

# Smooth interpolation on all fcurves
if sk_root.animation_data and sk_root.animation_data.action:
    for fc in sk_root.animation_data.action.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = "BEZIER"

# ── render ────────────────────────────────────────────────────────────────────
scene.render.engine = "BLENDER_EEVEE_NEXT"
bpy.ops.render.render(animation=True)
print(f"Viewport render saved to {OUT_PATH}.mp4")
