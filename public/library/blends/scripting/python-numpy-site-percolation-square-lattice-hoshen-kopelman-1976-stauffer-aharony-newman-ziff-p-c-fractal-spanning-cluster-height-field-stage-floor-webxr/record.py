# ============================================================
# RECORD.PY  |  Percolation viewport animation  |  Blender 5.1
# ============================================================
# Run this script inside Blender (with the percolation floor object
# already in the scene from blueprint.py) to bake a 300-frame
# viewport animation that morphs Basis → SK_Critical → SK_Above
# → SK_Bond → Basis, looping once through the phase diagram.
# Output: public/library/videos/scripting/<slug>/viewport.mp4
# Requires: FFmpeg available to Blender; script must run from the
# .blend file directory so relative paths resolve correctly.
# ============================================================

import bpy, os, math

SLUG = (
    "python-numpy-site-percolation-square-lattice-hoshen-kopelman-1976"
    "-stauffer-aharony-newman-ziff-p-c-fractal-spanning-cluster"
    "-height-field-stage-floor-webxr"
)
FPS          = 30
TOTAL_FRAMES = 300          # 10 s at 30 fps
OUT_DIR      = os.path.join(
    bpy.path.abspath("//"), "..", "..", "..", "..",
    "videos", "scripting", SLUG,
)
OUT_PATH     = os.path.join(OUT_DIR, "viewport.mp4")

# Ease function: smooth step
def _ease(t: float) -> float:
    return t * t * (3.0 - 2.0 * t)

# Key schedule: (start_frame, end_frame, from_sk, to_sk)
_SCHEDULE = [
    (  1,  75, "Basis",       "SK_Critical"),
    ( 75, 150, "SK_Critical", "SK_Above"),
    (150, 225, "SK_Above",    "SK_Bond"),
    (225, 300, "SK_Bond",     "Basis"),
]


def _setup_output() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    scene = bpy.context.scene
    scene.render.resolution_x      = 1920
    scene.render.resolution_y      = 1080
    scene.render.fps               = FPS
    scene.frame_start              = 1
    scene.frame_end                = TOTAL_FRAMES
    scene.render.image_settings.file_format = "FFMPEG"
    scene.render.ffmpeg.format     = "MPEG4"
    scene.render.ffmpeg.codec      = "H264"
    scene.render.ffmpeg.constant_rate_factor = "HIGH"
    scene.render.filepath          = OUT_PATH


def _find_object() -> bpy.types.Object:
    for ob in bpy.data.objects:
        if ob.type == "MESH" and ob.data.shape_keys:
            return ob
    raise RuntimeError("No mesh with shape keys found. Run blueprint.py first.")


def _clear_shape_key_animations(obj: bpy.types.Object) -> None:
    kb = obj.data.shape_keys
    if kb and kb.animation_data:
        kb.animation_data_clear()


def _insert_key(kb, sk_name: str, value: float, frame: int) -> None:
    block = kb.key_blocks.get(sk_name)
    if block is None:
        return
    block.value = value
    block.keyframe_insert(data_path="value", frame=frame)


def _bake_animation(obj: bpy.types.Object) -> None:
    """Insert keyframes so each shape key segment fades in/out."""
    kb = obj.data.shape_keys
    all_keys = [b.name for b in kb.key_blocks if b.name != "Basis"]

    # Zero out everything at frame 1
    for name in all_keys:
        _insert_key(kb, name, 0.0, 1)

    for start, end, from_sk, to_sk in _SCHEDULE:
        # from_sk fades out start→end
        if from_sk in all_keys:
            _insert_key(kb, from_sk, 1.0, start)
            _insert_key(kb, from_sk, 0.0, end)
        # to_sk fades in start→end
        if to_sk in all_keys:
            _insert_key(kb, to_sk, 0.0, start)
            _insert_key(kb, to_sk, 1.0, end)

    # Set interpolation to BEZIER for all shape key curves
    if kb.animation_data and kb.animation_data.action:
        for fc in kb.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = "BEZIER"


def _setup_camera_and_light() -> None:
    scene = bpy.context.scene
    # Camera: bird's-eye view tilted at 55°
    if "RecordCam" not in bpy.data.cameras:
        cam_data = bpy.data.cameras.new("RecordCam")
        cam_obj  = bpy.data.objects.new("RecordCam", cam_data)
        bpy.context.collection.objects.link(cam_obj)
    else:
        cam_obj = bpy.data.objects["RecordCam"]
    cam_obj.location     = (0.0, -2.2, 2.4)
    cam_obj.rotation_euler = (math.radians(55), 0, 0)
    scene.camera = cam_obj

    # Simple sun lamp
    if "RecordSun" not in bpy.data.lights:
        sun_data = bpy.data.lights.new("RecordSun", type="SUN")
        sun_obj  = bpy.data.objects.new("RecordSun", sun_data)
        bpy.context.collection.objects.link(sun_obj)
    else:
        sun_obj = bpy.data.objects["RecordSun"]
    sun_obj.location     = (3.0, 3.0, 5.0)
    sun_obj.data.energy  = 4.0


def run() -> None:
    _setup_output()
    obj = _find_object()
    _clear_shape_key_animations(obj)
    _bake_animation(obj)
    _setup_camera_and_light()

    # Render to file
    bpy.context.scene.render.use_overwrite = True
    bpy.ops.render.render(animation=True, use_viewport=False)
    print(f"[record] viewport animation saved → {OUT_PATH}")


run()
