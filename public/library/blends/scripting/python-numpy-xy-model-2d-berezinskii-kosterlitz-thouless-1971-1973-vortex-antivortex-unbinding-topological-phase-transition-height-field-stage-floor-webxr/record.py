"""
record.py — viewport animation for the XY Model BKT floor.

Renders a 12-second clip at 24 fps showing all four thermal regimes
in sequence, with smooth shape-key interpolation.
Output → public/library/videos/scripting/
  python-numpy-xy-model-2d-berezinskii-kosterlitz-thouless-1971-1973-vortex-antivortex-unbinding-topological-phase-transition-height-field-stage-floor-webxr/viewport.mp4

Run AFTER blueprint.py has built the scene.
"""

import bpy

DURATION_S   = 12
FPS          = 24
TOTAL_FRAMES = DURATION_S * FPS   # 288

OUTPUT_PATH = (
    "//../../../../videos/scripting/"
    "python-numpy-xy-model-2d-berezinskii-kosterlitz-thouless-1971-1973-"
    "vortex-antivortex-unbinding-topological-phase-transition-height-field-"
    "stage-floor-webxr/viewport"
)

RESOLUTION_X = 1920
RESOLUTION_Y = 1080

# Shape-key sequence:  hold 50 frames, crossfade 20 frames
# Basis → SK_BKT → SK_Unbound → SK_HighT → Basis (loop)
KEYFRAMES = [
    (1,   "Basis",      1.0),
    (55,  "Basis",      1.0),
    (75,  "SK_BKT",     1.0),
    (125, "SK_BKT",     1.0),
    (145, "SK_Unbound", 1.0),
    (200, "SK_Unbound", 1.0),
    (220, "SK_HighT",   1.0),
    (270, "SK_HighT",   1.0),
    (288, "Basis",      1.0),
]


def _setup_camera() -> None:
    cam_data = bpy.data.cameras.new("RecordCam")
    cam_data.lens = 35
    cam_obj  = bpy.data.objects.new("RecordCam", cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)
    cam_obj.location       = (0.0, -9.0, 6.0)
    cam_obj.rotation_euler = (1.10, 0.0, 0.0)
    bpy.context.scene.camera = cam_obj


def _setup_light() -> None:
    sun_data = bpy.data.lights.new("RecordSun", type="SUN")
    sun_data.energy = 3.0
    sun_obj = bpy.data.objects.new("RecordSun", sun_data)
    bpy.context.scene.collection.objects.link(sun_obj)
    sun_obj.rotation_euler = (0.5, 0.2, 0.9)


def _setup_render() -> None:
    scene             = bpy.context.scene
    scene.render.engine            = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x      = RESOLUTION_X
    scene.render.resolution_y      = RESOLUTION_Y
    scene.render.fps               = FPS
    scene.frame_start              = 1
    scene.frame_end                = TOTAL_FRAMES
    scene.render.image_settings.file_format = "FFMPEG"
    scene.render.ffmpeg.format     = "MPEG4"
    scene.render.ffmpeg.codec      = "H264"
    scene.render.ffmpeg.constant_rate_factor = "MEDIUM"
    scene.render.filepath          = OUTPUT_PATH


def _animate_shape_keys(obj: bpy.types.Object) -> None:
    """Insert shape-key value keyframes to drive the morph sequence."""
    keys = obj.data.shape_keys
    if keys is None:
        raise RuntimeError("No shape keys found — run blueprint.py first.")

    key_blocks = {kb.name: kb for kb in keys.key_blocks}

    # Zero out all shape-key values at frame 1
    for kb in keys.key_blocks:
        kb.value = 0.0

    for frame, sk_name, value in KEYFRAMES:
        if sk_name not in key_blocks:
            print(f"Warning: shape key '{sk_name}' not found — skipping.")
            continue
        bpy.context.scene.frame_set(frame)
        # Set the target key to value, others to 0
        for kb in keys.key_blocks:
            kb.value = value if kb.name == sk_name else 0.0
            kb.keyframe_insert(data_path="value", frame=frame)


def main() -> None:
    _setup_camera()
    _setup_light()
    _setup_render()

    obj = bpy.data.objects.get("xy_bkt_floor")
    if obj is None:
        raise RuntimeError(
            "Object 'xy_bkt_floor' not found.  Run blueprint.py first.")

    _animate_shape_keys(obj)

    print(f"[record.py] Rendering {TOTAL_FRAMES} frames → {OUTPUT_PATH}.mp4")
    bpy.ops.render.render(animation=True)
    print("[record.py] Done.")


if __name__ == "__main__":
    main()
