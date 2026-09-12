"""
Burgers Shock Floor — viewport animation recording (Blender 5.1).
Run AFTER blueprint.py.  Orbits camera 180° while cycling shape keys:
Basis (sin-IC, ν=0.010) → SK_HighNu (over-damped) → SK_LowNu (sharp)
→ back to Basis, all rendered via EEVEE Next.
Output: public/library/videos/scripting/
        python-numpy-burgers-equation-1948-cole-hopf-exact-.../viewport.mp4
Duration: ~9 s (270 frames @ 30 fps)
"""
import bpy, math, pathlib

# ── Render settings ────────────────────────────────────────────────────────────
FPS          = 30
TOTAL_FRAMES = 270
OUTPUT_PATH  = str(
    pathlib.Path(bpy.path.abspath("//")).parents[3]
    / "videos"
    / "scripting"
    / "python-numpy-burgers-equation-1948-cole-hopf-exact-shock-formation-"
      "viscous-regularisation-height-field-stage-floor-webxr"
    / "viewport.mp4"
)

# ── Camera orbit parameters ────────────────────────────────────────────────────
CAM_RADIUS  = 4.20    # metres from origin
CAM_ELEV    = 1.80    # height above origin
CAM_LENS    = 50      # focal length (mm)
ORBIT_START = -90     # degrees — starts from +x side
ORBIT_END   =  90     # degrees — ends at −x side (180° total)

# Shape-key fade schedule (frame ranges, inclusive):
#   F1-40    : Basis (ν=0.010, moderate shock)
#   F41-80   : crossfade Basis → SK_HighNu
#   F81-120  : SK_HighNu (ν=0.100, diffusion-dominated)
#   F121-160 : crossfade SK_HighNu → SK_LowNu
#   F161-210 : SK_LowNu (ν=0.005, near-inviscid sharp shock)
#   F211-250 : crossfade SK_LowNu → Basis
#   F251-270 : Basis (hold)


def _setup_render():
    sc  = bpy.context.scene
    sc.render.engine          = 'BLENDER_EEVEE_NEXT'
    sc.render.fps             = FPS
    sc.frame_start            = 1
    sc.frame_end              = TOTAL_FRAMES
    sc.render.filepath        = OUTPUT_PATH
    sc.render.image_settings.file_format  = 'FFMPEG'
    sc.render.ffmpeg.format               = 'MPEG4'
    sc.render.ffmpeg.codec                = 'H264'
    sc.render.ffmpeg.constant_rate_factor = 'MEDIUM'
    sc.render.resolution_x    = 1920
    sc.render.resolution_y    = 1080
    sc.render.resolution_percentage = 100
    sc.eevee.use_bloom        = True
    sc.eevee.bloom_threshold  = 0.20
    sc.eevee.bloom_intensity  = 0.45
    sc.eevee.bloom_radius     = 3.0


def _add_camera():
    bpy.ops.object.camera_add()
    cam = bpy.context.active_object
    cam.data.lens = CAM_LENS
    bpy.context.scene.camera = cam
    return cam


def _add_lights():
    bpy.ops.object.light_add(type='AREA', location=(0, 0, 5))
    key = bpy.context.active_object
    key.data.energy = 220
    key.data.size   = 5

    bpy.ops.object.light_add(type='AREA', location=(4, -4, 2))
    rim = bpy.context.active_object
    rim.data.energy = 90
    rim.data.size   = 2


def _orbit_keyframes(cam):
    import mathutils
    for f in (1, TOTAL_FRAMES):
        angle = math.radians(
            ORBIT_START + (ORBIT_END - ORBIT_START) * (f - 1) / (TOTAL_FRAMES - 1)
        )
        x = CAM_RADIUS * math.cos(angle)
        y = CAM_RADIUS * math.sin(angle)
        z = CAM_ELEV
        cam.location = (x, y, z)
        direction = mathutils.Vector((0, 0, 0)) - mathutils.Vector((x, y, z))
        rot_quat  = direction.to_track_quat('-Z', 'Y')
        cam.rotation_euler = rot_quat.to_euler()
        cam.keyframe_insert(data_path="location",       frame=f)
        cam.keyframe_insert(data_path="rotation_euler", frame=f)
    if cam.animation_data:
        for fc in cam.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = 'LINEAR'


def _shape_key_keyframes(ob):
    sk_data = ob.data.shape_keys
    if sk_data is None:
        return
    keys  = sk_data.key_blocks
    basis = keys.get("Basis")
    high  = keys.get("SK_HighNu")
    low   = keys.get("SK_LowNu")
    if None in (basis, high, low):
        return

    def kf(key, value, frame):
        key.value = value
        key.keyframe_insert(data_path="value", frame=frame)

    kf(basis, 1.0, 1);   kf(basis, 1.0, 40)
    kf(basis, 0.0, 80);  kf(basis, 0.0, 160)
    kf(basis, 1.0, 210); kf(basis, 1.0, TOTAL_FRAMES)

    kf(high, 0.0, 40);  kf(high, 1.0, 80)
    kf(high, 1.0, 120); kf(high, 0.0, 160)
    kf(high, 0.0, TOTAL_FRAMES)

    kf(low, 0.0, 120);  kf(low, 1.0, 160)
    kf(low, 1.0, 210);  kf(low, 0.0, TOTAL_FRAMES)

    if sk_data.animation_data:
        for fc in sk_data.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = 'LINEAR'


def main():
    _setup_render()
    cam = _add_camera()
    _add_lights()
    _orbit_keyframes(cam)

    ob = bpy.data.objects.get("burgers_shock_floor")
    if ob:
        _shape_key_keyframes(ob)
    else:
        print("[record.py] Warning: 'burgers_shock_floor' not found. "
              "Run blueprint.py first.")

    pathlib.Path(OUTPUT_PATH).parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.render.render(animation=True)
    print(f"[record.py] Viewport animation saved → {OUTPUT_PATH}")


main()
