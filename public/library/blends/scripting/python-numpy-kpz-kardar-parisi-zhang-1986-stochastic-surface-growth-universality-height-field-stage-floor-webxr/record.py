"""
Holoflow Studio — viewport.mp4 recorder for KPZ Stage Floor.
Run AFTER blueprint.py in the same Blender session (or re-open kpz_floor.blend).
Output: public/library/videos/scripting/<slug>/viewport.mp4

Duration : 10 s · 30 fps (300 frames)
Content  : morphs Basis (EW limit) → SK_KPZ → SK_Long, showing how the
           nonlinear term and longer evolution change the surface character.
"""
import bpy, os, math

SLUG = (
    "python-numpy-kpz-kardar-parisi-zhang-1986-stochastic-surface-growth-"
    "universality-height-field-stage-floor-webxr"
)
OBJ_NAME = "KPZ_Floor"
FPS      = 30
FRAMES   = 300   # 10 s


def setup_render():
    sc = bpy.context.scene
    sc.render.engine       = "BLENDER_EEVEE_NEXT"
    sc.render.fps          = FPS
    sc.frame_start         = 1
    sc.frame_end           = FRAMES
    sc.render.resolution_x = 1920
    sc.render.resolution_y = 1080
    sc.render.image_settings.file_format    = "FFMPEG"
    sc.render.ffmpeg.format                 = "MPEG4"
    sc.render.ffmpeg.codec                  = "H264"
    sc.render.ffmpeg.constant_rate_factor   = "HIGH"

    repo_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../../../")
    )
    out_dir = os.path.join(
        repo_root, "public", "library", "videos", "scripting", SLUG
    )
    os.makedirs(out_dir, exist_ok=True)
    sc.render.filepath = os.path.join(out_dir, "viewport.mp4")


def keyframe_morphs():
    """
    Sequence:
      f   1– 30  Hold at Basis (EW, λ=0, t=4) so viewer reads the smooth surface.
      f  30–120  SK_KPZ fades in  (0→1) — nonlinear ridges appear.
      f 120–150  Hold SK_KPZ at full value.
      f 150–240  SK_Long fades in (0→1) while SK_KPZ fades out (1→0).
      f 240–300  Hold SK_Long — well-developed long-run morphology.
    """
    ob = bpy.data.objects.get(OBJ_NAME)
    if ob is None:
        raise RuntimeError("KPZ_Floor not found — run blueprint.py first.")
    keys   = ob.data.shape_keys.key_blocks
    sk_kpz  = keys.get("SK_KPZ")
    sk_long = keys.get("SK_Long")
    if sk_kpz is None or sk_long is None:
        raise RuntimeError("Shape keys missing.")

    def kf(sk, val, frame):
        sk.value = val
        sk.keyframe_insert("value", frame=frame)

    # SK_KPZ fade-in
    kf(sk_kpz,  0.0,  1)
    kf(sk_kpz,  0.0, 30)
    kf(sk_kpz,  1.0, 120)
    kf(sk_kpz,  1.0, 150)
    kf(sk_kpz,  0.0, 240)
    kf(sk_kpz,  0.0, 300)

    # SK_Long fade-in (crossfade from SK_KPZ)
    kf(sk_long, 0.0,   1)
    kf(sk_long, 0.0, 150)
    kf(sk_long, 1.0, 240)
    kf(sk_long, 1.0, 300)


def setup_camera():
    sc = bpy.context.scene
    cam_data             = bpy.data.cameras.new("RecordCam")
    cam_data.type        = "ORTHO"
    cam_data.ortho_scale = 10.5
    cam_obj = bpy.data.objects.new("RecordCam", cam_data)
    bpy.context.collection.objects.link(cam_obj)
    cam_obj.location       = (0.8, -5.5, 10.0)
    cam_obj.rotation_euler = (math.radians(70), 0.0, math.radians(8))
    sc.camera = cam_obj


def setup_lighting():
    # Low-angle sun lamp to rake across surface ridges
    sun_data             = bpy.data.lights.new("RecordSun", "SUN")
    sun_data.energy      = 3.5
    sun_data.angle       = math.radians(5)
    sun_obj = bpy.data.objects.new("RecordSun", sun_data)
    bpy.context.collection.objects.link(sun_obj)
    sun_obj.rotation_euler = (math.radians(25), 0.0, math.radians(-50))

    # Fill area light — softens hard shadows on rough surface
    area_data            = bpy.data.lights.new("RecordFill", "AREA")
    area_data.energy     = 120
    area_data.size       = 8.0
    area_obj = bpy.data.objects.new("RecordFill", area_data)
    bpy.context.collection.objects.link(area_obj)
    area_obj.location    = (4.0, -1.0, 7.0)

    bpy.context.scene.world.use_nodes = True
    bg = bpy.context.scene.world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value    = (0.02, 0.02, 0.04, 1.0)
        bg.inputs["Strength"].default_value = 0.08


def main():
    setup_render()
    keyframe_morphs()
    setup_camera()
    setup_lighting()
    bpy.ops.render.render(animation=True)
    print(f"[KPZ record] → {bpy.context.scene.render.filepath}")


main()
