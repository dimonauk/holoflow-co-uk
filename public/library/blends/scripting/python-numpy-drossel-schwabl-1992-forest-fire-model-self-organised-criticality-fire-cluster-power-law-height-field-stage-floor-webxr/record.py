"""
record.py — viewport animation renderer for the Drossel–Schwabl Forest Fire
tutorial.  Run this AFTER blueprint.py has created drossel_schwabl_forest_floor.blend.

Outputs:
  public/library/videos/scripting/<slug>/viewport.mp4

Duration: 120 frames at 24 fps = 5 seconds.
  Frames   0–29  : Basis (SOC steady state — fade in shape key 0)
  Frames  30–59  : SK_LowP (sparse savanna) visible
  Frames  60–89  : SK_HighP (dense forest with large fires)
  Frames  90–119 : SK_AllTrees (maximum forest — pre-ignition saturation)

The camera orbits the stage floor at elevation 45° and distance 10 m, giving a
bird's-eye perspective that shows the 2D spatial structure clearly.
"""

import bpy
import os
import math

SLUG  = ("python-numpy-drossel-schwabl-1992-forest-fire-model-self-organised"
         "-criticality-fire-cluster-power-law-height-field-stage-floor-webxr")
OUT   = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "..", "..", "..", "..", "videos", "scripting", SLUG, "viewport.mp4",
)
SHAPE_KEYS = ["Basis", "SK_LowP", "SK_HighP", "SK_AllTrees"]
FPS        = 24
FRAMES_PER_KEY = 30   # 4 × 30 = 120 frames total


def setup_render():
    scene = bpy.context.scene
    scene.render.engine            = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x      = 1920
    scene.render.resolution_y      = 1080
    scene.render.fps               = FPS
    scene.frame_start              = 0
    scene.frame_end                = FPS * 4 * (FRAMES_PER_KEY // FPS) - 1
    scene.render.image_settings.file_format = "FFMPEG"
    scene.render.ffmpeg.format     = "MPEG4"
    scene.render.ffmpeg.codec      = "H264"
    scene.render.ffmpeg.constant_rate_factor = "HIGH"
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    scene.render.filepath          = OUT


def add_camera():
    bpy.ops.object.camera_add()
    cam = bpy.context.object
    cam.name = "RecordCam"
    # Position above and to one side, looking down at origin
    dist = 10.0
    elev = math.radians(50)
    cam.location = (
        dist * math.cos(math.radians(35)) * math.cos(elev),
        dist * math.sin(math.radians(35)) * math.cos(elev),
        dist * math.sin(elev),
    )
    # Point at origin
    dx, dy, dz = -cam.location.x, -cam.location.y, -cam.location.z
    cam.rotation_euler = (
        math.atan2(math.sqrt(dx**2 + dy**2), -dz),
        0,
        math.atan2(dx, -dy) + math.pi,
    )
    bpy.context.scene.camera = cam


def add_light():
    bpy.ops.object.light_add(type="SUN", location=(5, 5, 8))
    sun = bpy.context.object
    sun.data.energy = 3.0
    sun.data.angle  = math.radians(5)


def keyframe_shape_keys(ob):
    """
    For each shape key window, set that key's value to 1.0 and all others
    to 0.0 across a block of FRAMES_PER_KEY frames.
    """
    keys = ob.data.shape_keys.key_blocks
    for ki, key_name in enumerate(SHAPE_KEYS):
        frame_start = ki * FRAMES_PER_KEY
        frame_end   = frame_start + FRAMES_PER_KEY - 1

        for kn in SHAPE_KEYS:
            target_val = 1.0 if kn == key_name else 0.0
            # Snap to value at window start and end
            keys[kn].value = target_val
            keys[kn].keyframe_insert("value", frame=frame_start)
            keys[kn].keyframe_insert("value", frame=frame_end)


def main():
    # Expect drossel_schwabl_forest_floor to already be in the scene
    ob = bpy.data.objects.get("drossel_schwabl_forest_floor")
    if ob is None:
        raise RuntimeError("Run blueprint.py first — object not found in scene.")

    # Clear existing animation data for shape keys
    if ob.data.shape_keys.animation_data:
        ob.data.shape_keys.animation_data_clear()

    setup_render()
    add_camera()
    add_light()
    keyframe_shape_keys(ob)

    bpy.ops.render.render(animation=True)
    print(f"Viewport render saved to: {OUT}")


main()
