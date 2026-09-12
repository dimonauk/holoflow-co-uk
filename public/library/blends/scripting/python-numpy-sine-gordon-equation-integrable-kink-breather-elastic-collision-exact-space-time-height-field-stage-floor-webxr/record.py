"""
record.py — Viewport animation for sine_gordon_floor
Output: public/library/videos/scripting/
        python-numpy-sine-gordon-equation-integrable-kink-breather-
        elastic-collision-exact-space-time-height-field-stage-floor-webxr/
        viewport.mp4

Usage:
  blender --background sine_gordon_floor.blend --python record.py

Blueprint must have been run first (sg_floor object present in scene).
The script adds a camera, keyframes an orbit + shape-key morph, then
renders via EEVEE Next.
"""

import bpy
import math

# ── Render settings ──────────────────────────────────────────
OUTPUT_PATH = (
    "//../../public/library/videos/scripting/"
    "python-numpy-sine-gordon-equation-integrable-kink-breather-"
    "elastic-collision-exact-space-time-height-field-stage-floor-webxr/"
    "viewport.mp4"
)
FPS           = 30
TOTAL_FRAMES  = 270          # 9 s — enough for four shape-key phases
RES_X, RES_Y  = 1920, 1080

# Camera orbit — elevated three-quarter view of the stage floor
CAM_DIST    = 6.2            # metres from centre
CAM_HEIGHT  = 2.6            # metres above XY-plane
ANG_START   = -25.0          # degrees; scene looks down the t-axis initially
ANG_END     = 215.0          # total 240° sweep over 9 s

# Shape-key morph schedule (start, end, from-key, to-key)
# 67-frame segments: hold 45 frames, morph over 22 frames
_SK_SCHED = [
    (  1,  45, "Basis",        "Basis"),
    ( 45,  67, "Basis",        "SK_Breather"),
    ( 67, 112, "SK_Breather",  "SK_Breather"),
    (112, 134, "SK_Breather",  "SK_Collision"),
    (134, 179, "SK_Collision", "SK_Collision"),
    (179, 201, "SK_Collision", "SK_TwoKink"),
    (201, 270, "SK_TwoKink",   "SK_TwoKink"),
]
ALL_SK = ["SK_Breather", "SK_Collision", "SK_TwoKink"]


def setup_render():
    sc = bpy.context.scene
    sc.render.engine     = "BLENDER_EEVEE_NEXT"
    sc.render.fps        = FPS
    sc.frame_start       = 1
    sc.frame_end         = TOTAL_FRAMES
    sc.render.filepath   = OUTPUT_PATH
    sc.render.image_settings.file_format = "FFMPEG"
    sc.render.ffmpeg.format  = "MPEG4"
    sc.render.ffmpeg.codec   = "H264"
    sc.render.ffmpeg.constant_rate_factor = "MEDIUM"
    sc.render.resolution_x   = RES_X
    sc.render.resolution_y   = RES_Y
    sc.render.resolution_percentage = 100

    eevee = sc.eevee
    eevee.bloom_threshold = 0.28
    eevee.bloom_intensity = 0.30
    eevee.bloom_radius    = 4.0

    # Deep-space backdrop — lets the cobalt-to-amber ramp glow
    world = bpy.data.worlds.get("World")
    if world and world.node_tree:
        bg = world.node_tree.nodes.get("Background")
        if bg:
            bg.inputs[0].default_value = (0.005, 0.003, 0.012, 1.0)
            bg.inputs[1].default_value = 0.8   # strength


def add_camera():
    bpy.ops.object.camera_add()
    cam = bpy.context.object
    cam.name = "RecordCam"
    bpy.context.scene.camera = cam
    cam.data.lens = 50        # 50 mm — neutral perspective
    return cam


def orbit_camera(cam):
    """Keyframe a smooth orbit at constant elevation."""
    for f in range(1, TOTAL_FRAMES + 1):
        t  = (f - 1) / max(TOTAL_FRAMES - 1, 1)
        angle = math.radians(ANG_START + (ANG_END - ANG_START) * t)
        cam.location = (
            CAM_DIST * math.sin(angle),
           -CAM_DIST * math.cos(angle),
            CAM_HEIGHT,
        )
        # Point camera at origin
        dx = -cam.location.x
        dy = -cam.location.y
        dz = -cam.location.z
        dist_xy = math.sqrt(dx * dx + dy * dy)
        cam.rotation_euler = (
            math.atan2(-dz, dist_xy) + math.pi,  # tilt down
            0.0,
            math.atan2(dx, -dy),
        )
        cam.keyframe_insert("location",       frame=f)
        cam.keyframe_insert("rotation_euler", frame=f)

    for fc in cam.animation_data.action.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = "LINEAR"


def morph_shape_keys(obj):
    kb = obj.data.shape_keys.key_blocks

    # Initialise all non-Basis keys to 0 across the whole timeline
    for f in range(1, TOTAL_FRAMES + 1):
        for name in ALL_SK:
            kb[name].value = 0.0
            kb[name].keyframe_insert("value", frame=f)

    # Write the schedule
    for (f0, f1, from_sk, to_sk) in _SK_SCHED:
        for f in range(f0, f1 + 1):
            t = (f - f0) / max(f1 - f0, 1)
            for name in ALL_SK:
                if name == from_sk and name == to_sk:
                    val = 1.0
                elif name == from_sk:
                    val = 1.0 - t
                elif name == to_sk:
                    val = t
                else:
                    val = 0.0
                kb[name].value = val
                kb[name].keyframe_insert("value", frame=f)

    # Linearise shape-key fcurves
    for fc in obj.data.shape_keys.animation_data.action.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = "LINEAR"


def main():
    setup_render()

    obj = bpy.data.objects.get("sg_floor")
    if obj is None:
        raise RuntimeError("sg_floor not found — run blueprint.py first.")

    cam = add_camera()
    orbit_camera(cam)

    if obj.data.shape_keys:
        morph_shape_keys(obj)

    bpy.ops.render.render(animation=True)
    print("✓ Viewport animation rendered →", OUTPUT_PATH)


if __name__ == "__main__":
    main()
