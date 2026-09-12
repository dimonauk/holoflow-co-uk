"""
record.py — Viewport animation recorder for the Gierer-Meinhardt floor
Output: public/library/videos/scripting/
        python-numpy-gierer-meinhardt-activator-inhibitor-turing-morphogenesis-1972-spot-stripe-height-field-stage-floor-webxr/
        viewport.mp4

Run AFTER blueprint.py has built the scene.
Duration: 10 s @ 30 fps = 300 frames
  F  1–  60  Basis (spots)
  F 61– 150  morph → SK_Labyrinthine  (ease in/out)
  F151– 200  hold SK_Labyrinthine
  F201– 270  morph → SK_Dense
  F271– 300  hold + return to Basis
Camera orbits 60° around Z during the sequence.
"""

import bpy, math

# ── constants ──────────────────────────────────────────────────────────────────
OBJ_NAME   = "gm_activator_floor"
TOTAL_FRAMES = 300
FPS          = 30
OUTPUT_PATH  = "//../../videos/scripting/" \
    "python-numpy-gierer-meinhardt-activator-inhibitor-turing-morphogenesis" \
    "-1972-spot-stripe-height-field-stage-floor-webxr/viewport.mp4"

CAM_DIST  = 9.0    # metres from centre
CAM_ELEV  = 5.5    # elevation (m above floor)
CAM_START = 0.0    # orbit start (radians)
CAM_SWEEP = math.radians(60)


def _ease(t: float) -> float:
    """Smoothstep 3t²−2t³ — zero first derivative at endpoints,
    so shape-key transitions feel physically settled rather than abrupt."""
    return 3 * t * t - 2 * t * t * t


def _insert_sk(obj, key_name: str, val: float, frame: int):
    sk_data = obj.data.shape_keys
    sk_data.key_blocks[key_name].value = val
    sk_data.key_blocks[key_name].keyframe_insert("value", frame=frame)


def setup_camera():
    cam_data = bpy.data.cameras.new("RecordCam")
    cam_data.lens = 35.0
    cam = bpy.data.objects.new("RecordCam", cam_data)
    bpy.context.scene.collection.objects.link(cam)
    bpy.context.scene.camera = cam

    pivot = bpy.data.objects.new("CamPivot", None)
    bpy.context.scene.collection.objects.link(pivot)
    cam.parent = pivot

    cam.location = (CAM_DIST, 0, CAM_ELEV)
    cam.rotation_euler = (math.atan2(CAM_ELEV, CAM_DIST), 0, math.radians(90))

    pivot.rotation_euler[2] = CAM_START
    pivot.keyframe_insert("rotation_euler", frame=1)
    pivot.rotation_euler[2] = CAM_START + CAM_SWEEP
    pivot.keyframe_insert("rotation_euler", frame=TOTAL_FRAMES)
    for fcurve in pivot.animation_data.action.fcurves:
        for kp in fcurve.keyframe_points:
            kp.interpolation = 'LINEAR'
    return cam


def setup_lighting():
    world = bpy.context.scene.world
    if world is None:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Strength"].default_value = 0.6

    sun = bpy.data.lights.new("RecordSun", 'SUN')
    sun.energy = 3.0
    sun_obj = bpy.data.objects.new("RecordSun", sun)
    bpy.context.scene.collection.objects.link(sun_obj)
    sun_obj.rotation_euler = (math.radians(55), 0, math.radians(30))


def keyframe_shape_keys(obj):
    sk = obj.data.shape_keys
    keys = ["Basis", "SK_Labyrinthine", "SK_Dense", "SK_Seascape"]

    # zero all at frame 1
    for k in keys:
        sk.key_blocks[k].value = 0.0
        sk.key_blocks[k].keyframe_insert("value", frame=1)
    sk.key_blocks["Basis"].value = 1.0
    sk.key_blocks["Basis"].keyframe_insert("value", frame=1)

    # F61-150: cross-fade Basis → SK_Labyrinthine
    n_trans = 90
    for f in range(61, 151):
        t = (f - 61) / n_trans
        e = _ease(t)
        _insert_sk(obj, "Basis",           1.0 - e, f)
        _insert_sk(obj, "SK_Labyrinthine", e,        f)

    # F151-200: hold SK_Labyrinthine
    _insert_sk(obj, "SK_Labyrinthine", 1.0, 200)

    # F201-270: cross-fade SK_Lab → SK_Dense
    for f in range(201, 271):
        t = (f - 201) / 70
        e = _ease(t)
        _insert_sk(obj, "SK_Labyrinthine", 1.0 - e, f)
        _insert_sk(obj, "SK_Dense",        e,        f)

    # F271-300: hold then return to Basis
    _insert_sk(obj, "SK_Dense", 1.0,  271)
    _insert_sk(obj, "SK_Dense", 0.0,  300)
    _insert_sk(obj, "Basis",    1.0,  300)


def configure_render():
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end   = TOTAL_FRAMES
    scene.render.fps  = FPS
    scene.render.engine                  = 'BLENDER_EEVEE_NEXT'
    scene.eevee.use_bloom                = True
    scene.eevee.bloom_threshold          = 0.6
    scene.eevee.bloom_intensity          = 0.4
    scene.render.resolution_x            = 1920
    scene.render.resolution_y            = 1080
    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format           = 'MPEG4'
    scene.render.ffmpeg.codec            = 'H264'
    scene.render.ffmpeg.constant_rate_factor = 'MEDIUM'
    scene.render.filepath                = OUTPUT_PATH


def record():
    obj = bpy.data.objects.get(OBJ_NAME)
    if obj is None:
        raise RuntimeError("Run blueprint.py first to build the scene.")
    setup_camera()
    setup_lighting()
    keyframe_shape_keys(obj)
    configure_render()
    bpy.ops.render.render(animation=True)
    print(f"[GM record] Written → {OUTPUT_PATH}")


record()
