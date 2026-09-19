"""
Viewport animation recorder for Anderson Localisation blueprint.
Run AFTER blueprint.py has created the object in the scene.

Records a 5-second (150-frame) clip that cycles through the four disorder
regimes: Basis → SK_Medium → SK_Strong → SK_MaxIPR → back to Basis.
Output: public/library/videos/scripting/
        python-numpy-anderson-localization-2d-tight-binding-disorder-ipr-height-field-stage-floor-webxr/
        viewport.mp4
"""

import bpy
import math

FPS        = 30
DURATION_S = 5
N_FRAMES   = FPS * DURATION_S   # 150
OUT_PATH   = (
    "//../../videos/scripting/"
    "python-numpy-anderson-localization-2d-tight-binding-disorder-ipr-height-field-stage-floor-webxr/"
    "viewport"
)

KEY_SCHEDULE = [
    # (frame, Basis, SK_Medium, SK_Strong, SK_MaxIPR)
    (1,   1.0, 0.0, 0.0, 0.0),   # pure Basis (W=0.5, extended)
    (40,  0.0, 1.0, 0.0, 0.0),   # SK_Medium  (W=2.0)
    (80,  0.0, 0.0, 1.0, 0.0),   # SK_Strong  (W=5.0, localised)
    (120, 0.0, 0.0, 0.0, 1.0),   # SK_MaxIPR  (W=8.0, peak)
    (150, 1.0, 0.0, 0.0, 0.0),   # back to Basis
]


def setup_camera(obj):
    cam_data = bpy.data.cameras.new("RecordCam")
    cam_obj  = bpy.data.objects.new("RecordCam", cam_data)
    bpy.context.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

    # Bird's-eye view, slightly angled
    cam_obj.location    = (0.0, -2.8, 3.2)
    cam_obj.rotation_euler = (math.radians(45), 0.0, 0.0)
    cam_data.lens = 35


def insert_shape_key_keyframes(obj, frame, vals):
    kb = obj.data.shape_keys.key_blocks
    names = ["SK_Medium", "SK_Strong", "SK_MaxIPR"]
    for i, name in enumerate(names):
        if name in kb:
            kb[name].value = vals[i + 1]
            kb[name].keyframe_insert("value", frame=frame)


def main():
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end   = N_FRAMES
    scene.render.fps  = FPS

    obj = bpy.data.objects.get("anderson_localization_floor")
    if obj is None:
        print("Record.py: object not found — run blueprint.py first.")
        return

    setup_camera(obj)

    for frame, v_basis, v_med, v_str, v_max in KEY_SCHEDULE:
        scene.frame_set(frame)
        insert_shape_key_keyframes(obj, frame, (v_basis, v_med, v_str, v_max))

    # Light
    bpy.ops.object.light_add(type="SUN", location=(0, 0, 5))
    sun = bpy.context.active_object
    sun.data.energy = 3.0
    sun.rotation_euler = (math.radians(30), 0, math.radians(45))

    # Render settings
    scene.render.engine          = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x    = 1920
    scene.render.resolution_y    = 1080
    scene.render.image_settings.file_format  = "FFMPEG"
    scene.render.ffmpeg.format   = "MPEG4"
    scene.render.ffmpeg.codec    = "H264"
    scene.render.ffmpeg.constant_rate_factor = "HIGH"
    scene.render.filepath        = bpy.path.abspath(OUT_PATH)

    bpy.ops.render.render(animation=True)
    print("Record complete:", bpy.path.abspath(OUT_PATH) + ".mp4")


main()
