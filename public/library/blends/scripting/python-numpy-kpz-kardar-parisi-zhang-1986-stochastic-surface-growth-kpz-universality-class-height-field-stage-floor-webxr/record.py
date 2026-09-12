"""
Holoflow Studio — viewport.mp4 recorder for KPZ Growth Floor.
Run AFTER blueprint.py in the same Blender session (or re-open the .blend).
Outputs: public/library/videos/scripting/<slug>/viewport.mp4
Duration: 12 s · 30 fps (360 frames)
Content: morphs Basis → SK_Long to show KPZ surface roughening in time;
         then cross-fades SK_Long → SK_EW to compare KPZ vs Edwards–Wilkinson.
"""
import bpy, os

SLUG = (
    "python-numpy-kpz-kardar-parisi-zhang-1986-stochastic-surface-growth-"
    "kpz-universality-class-height-field-stage-floor-webxr"
)
OBJ_NAME = "kpz_growth_floor"
FPS      = 30
FRAMES   = 360   # 12 s total


def setup_render():
    scene = bpy.context.scene
    scene.render.engine       = 'BLENDER_EEVEE_NEXT'
    scene.render.fps          = FPS
    scene.frame_start         = 1
    scene.frame_end           = FRAMES
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format               = 'MPEG4'
    scene.render.ffmpeg.codec                = 'H264'
    scene.render.ffmpeg.constant_rate_factor = 'HIGH'

    repo_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../../../")
    )
    out_dir = os.path.join(
        repo_root, "public", "library", "videos", "scripting", SLUG
    )
    os.makedirs(out_dir, exist_ok=True)
    scene.render.filepath = os.path.join(out_dir, "viewport.mp4")


def setup_camera():
    """Position camera above the floor, looking down at an oblique angle."""
    cam_data = bpy.data.cameras.new("RecordCam")
    cam_obj  = bpy.data.objects.new("RecordCam", cam_data)
    bpy.context.collection.objects.link(cam_obj)
    cam_obj.location = (0.0, -9.0, 6.5)
    cam_obj.rotation_euler = (0.82, 0.0, 0.0)  # ~47° tilt
    bpy.context.scene.camera = cam_obj


def keyframe_morphs():
    """
    Animate shape key values:
      Frames   1–30:  hold Basis (early KPZ, t=3 s)
      Frames  30–150: morph Basis → SK_Long (developed KPZ surface)
      Frames 150–180: hold SK_Long
      Frames 180–300: morph SK_Long → SK_EW (same t, λ=0 comparison)
      Frames 300–360: hold SK_EW
    The SK_Long/SK_EW comparison makes the KPZ nonlinearity visible:
    SK_Long has steeper grooves and a Tracy–Widom-skewed height distribution;
    SK_EW is smoother with Gaussian statistics.
    """
    ob = bpy.data.objects.get(OBJ_NAME)
    if ob is None:
        raise RuntimeError("Run blueprint.py first to create the mesh.")
    keys   = ob.data.shape_keys.key_blocks
    sk_long   = keys.get("SK_Long")
    sk_ew     = keys.get("SK_EW")
    if sk_long is None or sk_ew is None:
        raise RuntimeError("Expected shape keys SK_Long and SK_EW not found.")

    def kf(key, val, frame):
        key.value = val
        key.keyframe_insert("value", frame=frame)

    # SK_Long: 0 → 0 → 1 → 1 → 0 → 0
    kf(sk_long, 0.0, 1)
    kf(sk_long, 0.0, 30)
    kf(sk_long, 1.0, 150)
    kf(sk_long, 1.0, 300)
    kf(sk_long, 0.0, 300)  # snap off when EW takes over
    kf(sk_long, 0.0, 360)

    # SK_EW: 0 → 0 → 0 → 1 → 1
    kf(sk_ew, 0.0, 1)
    kf(sk_ew, 0.0, 180)
    kf(sk_ew, 1.0, 300)
    kf(sk_ew, 1.0, 360)


def add_floor_light():
    """Three-point lighting rig: key above-left, fill right, rim behind."""
    for name, loc, energy in [
        ("KPZ_Key",  ( 5.0,  5.0, 10.0), 800),
        ("KPZ_Fill", (-6.0, -2.0,  6.0), 300),
        ("KPZ_Rim",  ( 0.0, 10.0,  4.0), 200),
    ]:
        d = bpy.data.lights.new(name, type='POINT')
        d.energy = energy
        o = bpy.data.objects.new(name, d)
        bpy.context.collection.objects.link(o)
        o.location = loc


def main():
    setup_render()
    setup_camera()
    add_floor_light()
    keyframe_morphs()
    bpy.ops.render.render(animation=True, write_still=False)
    print("viewport.mp4 written to", bpy.context.scene.render.filepath)


main()
