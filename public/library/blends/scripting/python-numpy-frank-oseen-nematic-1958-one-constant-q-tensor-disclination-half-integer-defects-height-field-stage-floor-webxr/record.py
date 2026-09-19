# ============================================================
# RECORD.PY  |  Frank-Oseen Nematic LC viewport animation  |  Blender 5.1
# ============================================================
# Run after blueprint.py. Bakes shape-key keyframes and renders
# a 300-frame (10 s) animation morphing through all four defect
# configurations: quadrupole → comet → hedgehog → annihilating pair.
# Output: public/library/videos/scripting/<slug>/viewport.mp4
# ============================================================

import bpy, os, math

SLUG = (
    "python-numpy-frank-oseen-nematic-1958-one-constant-q-tensor"
    "-disclination-half-integer-defects-height-field-stage-floor-webxr"
)
FPS          = 30
TOTAL_FRAMES = 300               # 10 s
OUT_DIR      = os.path.join(
    bpy.path.abspath("//"),
    "..", "..", "..", "..",
    "videos", "scripting", SLUG,
)
OUT_PATH = os.path.join(OUT_DIR, "viewport.mp4")

_SCHEDULE = [
    (  1,  75, "Basis",        "SK_Comet"),
    ( 75, 150, "SK_Comet",     "SK_Hedgehog"),
    (150, 225, "SK_Hedgehog",  "SK_Anneal"),
    (225, 300, "SK_Anneal",    "Basis"),
]


def _setup_output():
    os.makedirs(OUT_DIR, exist_ok=True)
    sc = bpy.context.scene
    sc.render.resolution_x = 1920
    sc.render.resolution_y = 1080
    sc.render.fps          = FPS
    sc.frame_start         = 1
    sc.frame_end           = TOTAL_FRAMES
    sc.render.image_settings.file_format = "FFMPEG"
    sc.render.ffmpeg.format              = "MPEG4"
    sc.render.ffmpeg.codec               = "H264"
    sc.render.ffmpeg.constant_rate_factor = "HIGH"
    sc.render.filepath                   = OUT_PATH


def _find_mesh_obj():
    for ob in bpy.data.objects:
        if ob.type == "MESH" and ob.data.shape_keys:
            return ob
    raise RuntimeError("No mesh with shape keys found — run blueprint.py first.")


def _insert_key(kb, name, value, frame):
    blk = kb.key_blocks.get(name)
    if blk is None:
        return
    blk.value = value
    blk.keyframe_insert(data_path="value", frame=frame)


def _bake_animation(obj):
    kb       = obj.data.shape_keys
    all_keys = [b.name for b in kb.key_blocks if b.name != "Basis"]
    if kb.animation_data:
        kb.animation_data_clear()
    for name in all_keys:
        _insert_key(kb, name, 0.0, 1)
    for start, end, from_sk, to_sk in _SCHEDULE:
        if from_sk in all_keys:
            _insert_key(kb, from_sk, 1.0, start)
            _insert_key(kb, from_sk, 0.0, end)
        if to_sk in all_keys:
            _insert_key(kb, to_sk, 0.0, start)
            _insert_key(kb, to_sk, 1.0, end)
    if kb.animation_data and kb.animation_data.action:
        for fc in kb.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = "BEZIER"


def _setup_camera_and_light():
    sc = bpy.context.scene
    if "RecordCam" not in bpy.data.cameras:
        cam_data = bpy.data.cameras.new("RecordCam")
        cam_obj  = bpy.data.objects.new("RecordCam", cam_data)
        bpy.context.collection.objects.link(cam_obj)
    else:
        cam_obj = bpy.data.objects["RecordCam"]
    cam_obj.location       = (0.0, -2.4, 2.6)
    cam_obj.rotation_euler = (math.radians(52), 0.0, 0.0)
    sc.camera              = cam_obj

    if "RecordSun" not in bpy.data.lights:
        sun_data = bpy.data.lights.new("RecordSun", type="SUN")
        sun_obj  = bpy.data.objects.new("RecordSun", sun_data)
        bpy.context.collection.objects.link(sun_obj)
    else:
        sun_obj = bpy.data.objects["RecordSun"]
    sun_obj.location    = (3.0, 2.0, 5.0)
    sun_obj.data.energy = 4.5


def run():
    _setup_output()
    obj = _find_mesh_obj()
    _bake_animation(obj)
    _setup_camera_and_light()
    bpy.context.scene.render.use_overwrite = True
    bpy.ops.render.render(animation=True, use_viewport=False)
    print(f"[record] → {OUT_PATH}")


run()
