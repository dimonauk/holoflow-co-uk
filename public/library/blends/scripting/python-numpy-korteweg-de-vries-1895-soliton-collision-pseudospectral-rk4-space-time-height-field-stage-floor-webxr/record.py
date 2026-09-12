"""
KdV Soliton Floor — viewport animation recording script (Blender 5.1).
Run AFTER blueprint.py.  Orbits the camera 180° while cycling shape keys:
Basis (2-soliton collision) → SK_Single (single soliton) → SK_Three
(triple interaction) → back to Basis, all rendered via EEVEE Next.
Output: public/library/videos/scripting/
        python-numpy-korteweg-de-vries-1895-soliton-collision-.../viewport.mp4
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
    / "python-numpy-korteweg-de-vries-1895-soliton-collision-"
      "pseudospectral-rk4-space-time-height-field-stage-floor-webxr"
    / "viewport.mp4"
)

# ── Camera orbit parameters ────────────────────────────────────────────────────
CAM_RADIUS  = 3.80    # metres from origin
CAM_ELEV    = 1.70    # height above origin (metres)
CAM_LENS    = 50      # focal length (mm)
ORBIT_START = -90     # degrees (looks from +x side)
ORBIT_END   =  90     # degrees (looks from −x side, 180° total orbit)

# Shape-key fade schedule (frame ranges, inclusive):
#   F0-F40    : Basis (2-soliton, collision visible)
#   F41-F80   : crossfade Basis → SK_Single
#   F81-F120  : SK_Single (single soliton, ridge)
#   F121-F160 : crossfade SK_Single → SK_Three
#   F161-F210 : SK_Three (triple interaction)
#   F211-F250 : crossfade SK_Three → Basis
#   F251-F270 : Basis (hold)


def _setup_render():
    sc  = bpy.context.scene
    sc.render.engine          = 'BLENDER_EEVEE_NEXT'
    sc.render.fps             = FPS
    sc.frame_start            = 1
    sc.frame_end              = TOTAL_FRAMES
    sc.render.filepath        = OUTPUT_PATH
    sc.render.image_settings.file_format = 'FFMPEG'
    sc.render.ffmpeg.format              = 'MPEG4'
    sc.render.ffmpeg.codec               = 'H264'
    sc.render.ffmpeg.constant_rate_factor = 'MEDIUM'
    sc.render.resolution_x    = 1920
    sc.render.resolution_y    = 1080
    sc.render.resolution_percentage = 100
    # EEVEE bloom for soliton glow
    sc.eevee.use_bloom        = True
    sc.eevee.bloom_threshold  = 0.30
    sc.eevee.bloom_intensity  = 0.40
    sc.eevee.bloom_radius     = 3.5


def _add_camera():
    bpy.ops.object.camera_add()
    cam = bpy.context.active_object
    cam.data.lens = CAM_LENS
    bpy.context.scene.camera = cam
    return cam


def _add_lights():
    # Soft overhead fill + rimlight for the floor ridges
    bpy.ops.object.light_add(type='AREA', location=(0, 0, 4))
    key = bpy.context.active_object
    key.data.energy = 200
    key.data.size   = 4

    bpy.ops.object.light_add(type='AREA', location=(3, -3, 2))
    rim = bpy.context.active_object
    rim.data.energy = 80
    rim.data.size   = 2


def _orbit_keyframes(cam):
    """Keyframe camera on an arc from ORBIT_START to ORBIT_END degrees."""
    import mathutils
    sc = bpy.context.scene
    for f in (1, TOTAL_FRAMES):
        angle = math.radians(
            ORBIT_START + (ORBIT_END - ORBIT_START) * (f - 1) / (TOTAL_FRAMES - 1)
        )
        x = CAM_RADIUS * math.cos(angle)
        y = CAM_RADIUS * math.sin(angle)
        z = CAM_ELEV
        cam.location = (x, y, z)
        # Point camera at origin
        direction = mathutils.Vector((0, 0, 0)) - mathutils.Vector((x, y, z))
        rot_quat  = direction.to_track_quat('-Z', 'Y')
        cam.rotation_euler = rot_quat.to_euler()
        cam.keyframe_insert(data_path="location",       frame=f)
        cam.keyframe_insert(data_path="rotation_euler", frame=f)
    # Linearise curves
    if cam.animation_data:
        for fc in cam.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = 'LINEAR'


def _shape_key_keyframes(ob):
    """Keyframe shape-key values for the fade schedule."""
    sk_data = ob.data.shape_keys
    if sk_data is None:
        return
    keys = sk_data.key_blocks
    basis   = keys.get("Basis")
    single  = keys.get("SK_Single")
    three   = keys.get("SK_Three")
    if None in (basis, single, three):
        return

    def kf(key, value, frame):
        key.value = value
        key.keyframe_insert(data_path="value", frame=frame)

    # Basis on: F1-80, off: F81-F120 (faded by F80), back: F211-F270
    kf(basis, 1.0, 1);   kf(basis, 1.0, 40)
    kf(basis, 0.0, 80);  kf(basis, 0.0, 160)
    kf(basis, 1.0, 210); kf(basis, 1.0, TOTAL_FRAMES)

    # SK_Single on: F81-F160, off elsewhere
    kf(single, 0.0, 40);  kf(single, 1.0, 80)
    kf(single, 1.0, 120); kf(single, 0.0, 160)
    kf(single, 0.0, TOTAL_FRAMES)

    # SK_Three on: F161-F250
    kf(three, 0.0, 120);  kf(three, 1.0, 160)
    kf(three, 1.0, 210);  kf(three, 0.0, TOTAL_FRAMES)

    # Linearise all shape-key curves
    if sk_data.animation_data:
        for fc in sk_data.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = 'LINEAR'


def main():
    _setup_render()
    cam = _add_camera()
    _add_lights()
    _orbit_keyframes(cam)

    # Find the floor object (built by blueprint.py)
    ob = bpy.data.objects.get("kdv_soliton_floor")
    if ob:
        _shape_key_keyframes(ob)
    else:
        print("[record.py] Warning: 'kdv_soliton_floor' not found. "
              "Run blueprint.py first.")

    pathlib.Path(OUTPUT_PATH).parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.render.render(animation=True)
    print(f"[record.py] Viewport animation saved → {OUTPUT_PATH}")


main()
