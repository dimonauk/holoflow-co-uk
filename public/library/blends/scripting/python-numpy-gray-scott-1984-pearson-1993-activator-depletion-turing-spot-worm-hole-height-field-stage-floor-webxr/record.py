"""
record.py — Gray–Scott Pattern Atlas Viewport Animation
========================================================
Assumes blueprint.py has already been run and gray_scott_floor.blend is saved
alongside this script. Opens the blend, configures a camera + lighting, animates
shape-key morphing through all four Pearson pattern classes, and renders to
viewport.mp4 at 1280×720 30fps via EEVEE.

Run inside Blender 5.1:
  blender gray_scott_floor.blend --python record.py

Output: public/library/videos/scripting/<slug>/viewport.mp4
"""

import bpy, mathutils, pathlib

# ── Output path ────────────────────────────────────────────────────────────────
SLUG       = "python-numpy-gray-scott-1984-pearson-1993-activator-depletion-turing-spot-worm-hole-height-field-stage-floor-webxr"
VIDEO_OUT  = pathlib.Path(__file__).parents[4] / "videos" / "scripting" / SLUG / "viewport.mp4"
VIDEO_OUT.parent.mkdir(parents=True, exist_ok=True)

OBJ_NAME   = "gray_scott_floor"
FPS        = 30
HOLD       = 24     # frames to hold each state (0.8 s)
BLEND_DUR  = 24     # frames for each morph transition (0.8 s)
# Total: 4 holds + 4 transitions → 4×24 + 4×24 = 192 frames ≈ 6.4 s


def _setup_camera():
    """Perspective camera looking down at the floor at a slight angle."""
    cam_data = bpy.data.cameras.new("RecordCam")
    cam_data.lens = 35.0
    cam_obj  = bpy.data.objects.new("RecordCam", cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)

    # Position: above and slightly to the side
    cam_obj.location = mathutils.Vector((1.8, -6.5, 5.2))
    cam_obj.rotation_euler = mathutils.Euler((0.95, 0.0, 0.22), "XYZ")
    bpy.context.scene.camera = cam_obj
    return cam_obj


def _setup_lighting():
    """Key sun light + soft fill area light for clean shading."""
    sun_data = bpy.data.lights.new("Sun", type="SUN")
    sun_data.energy = 3.0
    sun_data.angle  = 0.05   # narrow = hard shadows, good for fine pattern texture
    sun_obj  = bpy.data.objects.new("Sun", sun_data)
    bpy.context.scene.collection.objects.link(sun_obj)
    sun_obj.rotation_euler = mathutils.Euler((0.6, 0.0, 0.8), "XYZ")

    fill_data = bpy.data.lights.new("Fill", type="AREA")
    fill_data.energy = 120.0
    fill_data.size   = 6.0
    fill_obj  = bpy.data.objects.new("Fill", fill_data)
    bpy.context.scene.collection.objects.link(fill_obj)
    fill_obj.location = mathutils.Vector((-4.0, -4.0, 6.0))
    fill_obj.rotation_euler = mathutils.Euler((0.9, 0.0, -0.8), "XYZ")


def _keyframe_shape_key(obj, sk_name: str, value: float, frame: int):
    """Insert a shape key value keyframe on the given object."""
    sk_block = obj.data.shape_keys.key_blocks.get(sk_name)
    if sk_block is None:
        return
    sk_block.value = value
    sk_block.keyframe_insert("value", frame=frame)


def _animate_morphing(obj):
    """
    Morph sequence: Basis → SK_Worm → SK_Hole → SK_Mitosis → Basis
    All shape keys start at 0 except the active one which ramps to 1.
    Transitions use linear interpolation (keyframes at start/end of ramp).

    State encoding: Blender shape keys are additive from Basis.
    Setting SK_Worm = 1 (and SK_Hole = 0, SK_Mitosis = 0) means:
    the mesh interpolates 100% toward SK_Worm vertex positions.
    """
    sk_names = ["SK_Worm", "SK_Hole", "SK_Mitosis"]
    scene    = bpy.context.scene
    scene.frame_start = 1
    frame    = 1

    def hold(n_frames):
        nonlocal frame
        frame += n_frames

    def ramp_in(target: str, n_frames: int):
        """Morph toward target shape key over n_frames."""
        nonlocal frame
        f_start = frame
        f_end   = frame + n_frames
        # Zero all keys at start of ramp
        for sk in sk_names:
            _keyframe_shape_key(obj, sk, 0.0 if sk != target else 0.0, f_start)
        # Full target at end
        _keyframe_shape_key(obj, target, 1.0, f_end)
        # Others stay at 0
        for sk in sk_names:
            if sk != target:
                _keyframe_shape_key(obj, sk, 0.0, f_end)
        frame = f_end

    def ramp_out(current: str, n_frames: int):
        """Morph away from current shape key back to Basis."""
        nonlocal frame
        f_start = frame
        f_end   = frame + n_frames
        _keyframe_shape_key(obj, current, 1.0, f_start)
        _keyframe_shape_key(obj, current, 0.0, f_end)
        frame = f_end

    # Initial state: all at 0 (Basis)
    for sk in sk_names:
        _keyframe_shape_key(obj, sk, 0.0, 1)

    # 1 — Hold Basis
    hold(HOLD)

    # 2 — Ramp to SK_Worm
    ramp_in("SK_Worm", BLEND_DUR)
    hold(HOLD)

    # 3 — Ramp to SK_Hole
    ramp_out("SK_Worm", BLEND_DUR // 2)
    ramp_in("SK_Hole", BLEND_DUR // 2)
    hold(HOLD)

    # 4 — Ramp to SK_Mitosis
    ramp_out("SK_Hole", BLEND_DUR // 2)
    ramp_in("SK_Mitosis", BLEND_DUR // 2)
    hold(HOLD)

    # 5 — Return to Basis
    ramp_out("SK_Mitosis", BLEND_DUR)
    hold(HOLD // 2)

    scene.frame_end = frame


def _configure_eevee():
    """EEVEE render settings for a clean 1280×720 30fps animation."""
    sc = bpy.context.scene
    sc.render.engine          = "BLENDER_EEVEE_NEXT"
    sc.render.resolution_x    = 1280
    sc.render.resolution_y    = 720
    sc.render.fps             = FPS
    sc.render.film_transparent = False
    sc.render.filepath        = str(VIDEO_OUT)
    sc.render.image_settings.file_format  = "FFMPEG"
    sc.render.ffmpeg.format               = "MPEG4"
    sc.render.ffmpeg.codec                = "H264"
    sc.render.ffmpeg.constant_rate_factor = "MEDIUM"
    sc.render.ffmpeg.ffmpeg_preset        = "GOOD"
    eevee = sc.eevee
    eevee.taa_render_samples = 32
    eevee.use_bloom          = True
    eevee.bloom_threshold    = 0.8
    eevee.bloom_intensity    = 0.06


def main():
    obj = bpy.data.objects.get(OBJ_NAME)
    if obj is None:
        print(f"[record] ERROR — '{OBJ_NAME}' not found; run blueprint.py first.")
        return

    # Remove any existing cameras/lights from the blueprint scene
    for o in bpy.data.objects:
        if o.type in {"CAMERA", "LIGHT"}:
            bpy.data.objects.remove(o, do_unlink=True)

    _setup_camera()
    _setup_lighting()
    _animate_morphing(obj)
    _configure_eevee()

    print(f"[record] Rendering {bpy.context.scene.frame_end} frames → {VIDEO_OUT}")
    bpy.ops.render.render(animation=True)
    print("[record] Done.")


if __name__ == "__main__":
    main()
