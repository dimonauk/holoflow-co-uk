"""
φ⁴ Kink Floor — viewport animation recording (Blender 5.1).
Run AFTER blueprint.py.  Orbits camera 160° while cycling shape keys:
Basis (v=0.10 bion) → SK_TwoBounce (v=0.193) → SK_Escape (v=0.40)
→ back to Basis — rendered via EEVEE Next.

Output: public/library/videos/scripting/
        python-numpy-phi4-kink-antikink-collision-resonance-windows-
        campbell-1983-space-time-height-field-stage-floor-webxr/viewport.mp4
Duration: ~10 s  (300 frames @ 30 fps)
"""
import bpy
import math
import pathlib

FPS          = 30
TOTAL_FRAMES = 300

# Camera orbit
CAM_RADIUS  = 4.5
CAM_ELEV    = 2.0
CAM_LENS    = 50
ORBIT_START = -70
ORBIT_END   = 90

OUTPUT_PATH = str(
    pathlib.Path(bpy.path.abspath("//")).parents[3]
    / "videos" / "scripting"
    / "python-numpy-phi4-kink-antikink-collision-resonance-windows-"
      "campbell-1983-space-time-height-field-stage-floor-webxr"
    / "viewport.mp4"
)

# Shape-key schedule (all crossfades LINEAR):
#   F  1– 50  : Basis  (bion capture)
#   F 51–100  : fade → SK_TwoBounce
#   F101–160  : SK_TwoBounce  (two bounces then escape)
#   F161–210  : fade → SK_Escape
#   F211–270  : SK_Escape  (clean exit + radiation plumes)
#   F271–300  : fade → Basis  (hold)


def _setup_render() -> None:
    sc = bpy.context.scene
    sc.render.engine                      = 'BLENDER_EEVEE_NEXT'
    sc.render.fps                         = FPS
    sc.frame_start                        = 1
    sc.frame_end                          = TOTAL_FRAMES
    sc.render.filepath                    = OUTPUT_PATH
    sc.render.image_settings.file_format  = 'FFMPEG'
    sc.render.ffmpeg.format               = 'MPEG4'
    sc.render.ffmpeg.codec                = 'H264'
    sc.render.ffmpeg.constant_rate_factor = 'MEDIUM'
    sc.render.resolution_x               = 1920
    sc.render.resolution_y               = 1080
    sc.render.resolution_percentage      = 100
    sc.eevee.use_bloom                   = True
    sc.eevee.bloom_threshold             = 0.18
    sc.eevee.bloom_intensity             = 0.50
    sc.eevee.bloom_radius                = 4.0


def _add_camera():
    bpy.ops.object.camera_add()
    cam = bpy.context.active_object
    cam.data.lens = CAM_LENS
    bpy.context.scene.camera = cam
    return cam


def _add_lights() -> None:
    bpy.ops.object.light_add(type='AREA', location=(0, 1.5, 5))
    bpy.context.active_object.data.energy = 200
    bpy.context.active_object.data.size   = 6
    bpy.ops.object.light_add(type='AREA', location=(3, -3, 2.5))
    bpy.context.active_object.data.energy = 80
    bpy.context.active_object.data.size   = 2


def _orbit_keyframes(cam) -> None:
    import mathutils
    for f in (1, TOTAL_FRAMES):
        frac  = (f - 1) / (TOTAL_FRAMES - 1)
        angle = math.radians(ORBIT_START + (ORBIT_END - ORBIT_START) * frac)
        x = CAM_RADIUS * math.cos(angle)
        y = CAM_RADIUS * math.sin(angle)
        z = CAM_ELEV
        cam.location        = (x, y, z)
        direction           = mathutils.Vector((0, 1.5, 0)) - mathutils.Vector((x, y, z))
        cam.rotation_euler  = direction.to_track_quat('-Z', 'Y').to_euler()
        cam.keyframe_insert(data_path="location",       frame=f)
        cam.keyframe_insert(data_path="rotation_euler", frame=f)
    if cam.animation_data:
        for fc in cam.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = 'LINEAR'


def _sk_kf(key, value: float, frame: int) -> None:
    key.value = value
    key.keyframe_insert(data_path="value", frame=frame)


def _shape_key_schedule(ob) -> None:
    sk_data = ob.data.shape_keys
    if sk_data is None:
        return
    k = sk_data.key_blocks
    basis = k.get("Basis")
    two   = k.get("SK_TwoBounce")
    esc   = k.get("SK_Escape")
    if None in (basis, two, esc):
        print("[record.py] Shape keys not found — skipping animation.")
        return

    # Basis
    for f in (1, 50, 270, 300):
        _sk_kf(basis, 1.0, f)
    _sk_kf(basis, 0.0, 100)
    _sk_kf(basis, 0.0, 270)

    # SK_TwoBounce
    _sk_kf(two, 0.0, 50)
    _sk_kf(two, 1.0, 100)
    _sk_kf(two, 1.0, 160)
    _sk_kf(two, 0.0, 210)
    _sk_kf(two, 0.0, 300)

    # SK_Escape
    _sk_kf(esc, 0.0, 160)
    _sk_kf(esc, 1.0, 210)
    _sk_kf(esc, 1.0, 270)
    _sk_kf(esc, 0.0, 300)

    if sk_data.animation_data:
        for fc in sk_data.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = 'LINEAR'


def main() -> None:
    _setup_render()
    cam = _add_camera()
    _add_lights()
    _orbit_keyframes(cam)

    ob = bpy.data.objects.get(OBJ_NAME := "phi4_kink_floor")
    if ob:
        _shape_key_schedule(ob)
    else:
        print("[record.py] Object 'phi4_kink_floor' not found. Run blueprint.py first.")

    pathlib.Path(OUTPUT_PATH).parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.render.render(animation=True)
    print(f"[record.py] Saved → {OUTPUT_PATH}")


main()
