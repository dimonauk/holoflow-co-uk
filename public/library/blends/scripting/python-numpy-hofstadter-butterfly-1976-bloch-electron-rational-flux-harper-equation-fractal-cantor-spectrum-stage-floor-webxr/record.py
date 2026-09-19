"""
Viewport animation recorder for Hofstadter Butterfly blueprint.
Run AFTER blueprint.py has created the object in the scene.

Records a 10-second (300-frame) clip that:
  1. Orbits the camera slowly from a top-down bird's-eye view while showing Basis.
  2. Cross-fades through SK_Coarse → SK_Dense → SK_Central to show the
     fractal Cantor-set structure revealing itself at finer and finer scales.
Output: public/library/videos/scripting/
        python-numpy-hofstadter-butterfly-1976-bloch-electron-rational-flux-harper-equation-fractal-cantor-spectrum-stage-floor-webxr/
        viewport.mp4
"""

import bpy
import math

FPS        = 30
DURATION_S = 10
N_FRAMES   = FPS * DURATION_S   # 300
OUT_PATH   = (
    "//../../videos/scripting/"
    "python-numpy-hofstadter-butterfly-1976-bloch-electron-rational-flux-harper-equation-fractal-cantor-spectrum-stage-floor-webxr/"
    "viewport"
)

# Shape-key schedule: (frame, Basis, SK_Coarse, SK_Dense, SK_Central)
KEY_SCHEDULE = [
    (1,   1.0, 0.0, 0.0, 0.0),   # Basis: full butterfly q≤100
    (80,  0.0, 1.0, 0.0, 0.0),   # SK_Coarse: sparse main wings
    (160, 0.0, 0.0, 1.0, 0.0),   # SK_Dense: fine fractal branches
    (240, 0.0, 0.0, 0.0, 1.0),   # SK_Central: zoomed self-similar core
    (300, 1.0, 0.0, 0.0, 0.0),   # back to Basis
]


def setup_camera():
    """Slightly angled overhead view; orbit slowly during the clip."""
    cam_data = bpy.data.cameras.new("RecordCam")
    cam_obj  = bpy.data.objects.new("RecordCam", cam_data)
    bpy.context.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj
    cam_data.lens = 28

    # Start above-and-behind; camera parent empty orbits over 300 frames
    empty = bpy.data.objects.new("CamPivot", None)
    bpy.context.collection.objects.link(empty)
    empty.location = (0, 0, 0)
    cam_obj.parent = empty
    cam_obj.location = (0.0, -3.2, 4.5)
    cam_obj.rotation_euler = (math.radians(38), 0.0, 0.0)

    # One slow orbit: 0° → 25° over the clip
    empty.rotation_euler = (0, 0, 0)
    empty.keyframe_insert("rotation_euler", frame=1)
    empty.rotation_euler = (0, 0, math.radians(25))
    empty.keyframe_insert("rotation_euler", frame=N_FRAMES)

    return cam_obj


def insert_shape_key_frames(obj, frame, vals):
    """vals: (v_basis, v_coarse, v_dense, v_central)"""
    kb    = obj.data.shape_keys.key_blocks
    names = ["SK_Coarse", "SK_Dense", "SK_Central"]
    for i, name in enumerate(names):
        if name in kb:
            kb[name].value = vals[i + 1]
            kb[name].keyframe_insert("value", frame=frame)


def main():
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end   = N_FRAMES
    scene.render.fps  = FPS

    obj = bpy.data.objects.get("hofstadter_butterfly_floor")
    if obj is None:
        print("record.py: object not found — run blueprint.py first.")
        return

    setup_camera()

    for frame, *vals in KEY_SCHEDULE:
        scene.frame_set(frame)
        insert_shape_key_frames(obj, frame, vals)

    # Sunlight from upper left
    bpy.ops.object.light_add(type="SUN", location=(0, 0, 5))
    sun = bpy.context.active_object
    sun.data.energy = 2.8
    sun.rotation_euler = (math.radians(35), 0, math.radians(55))

    # Render
    scene.render.engine       = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.image_settings.file_format = "FFMPEG"
    scene.render.ffmpeg.format  = "MPEG4"
    scene.render.ffmpeg.codec   = "H264"
    scene.render.ffmpeg.constant_rate_factor = "HIGH"
    scene.render.filepath = bpy.path.abspath(OUT_PATH)

    bpy.ops.render.render(animation=True)
    print("Record complete:", bpy.path.abspath(OUT_PATH) + ".mp4")


main()
