"""
record.py — Haldane Berry Curvature Atlas Viewport Animation
=============================================================
Assumes blueprint.py has already been run and haldane_floor.blend is saved
alongside this script. Opens the blend, configures a camera + lighting,
animates shape-key morphing through all four parameter variants, and renders
to viewport.mp4 at 1280×720 30fps via EEVEE.

Run inside Blender 5.1:
  blender haldane_floor.blend --python record.py
"""

import bpy, mathutils, pathlib

SLUG      = "python-numpy-haldane-1988-chern-insulator-berry-curvature-topological-phase-diagram-honeycomb-height-field-stage-floor-webxr"
VIDEO_OUT = pathlib.Path(__file__).parents[4] / "videos" / "scripting" / SLUG / "viewport.mp4"
VIDEO_OUT.parent.mkdir(parents=True, exist_ok=True)

OBJ_NAME  = "haldane_floor"
FPS       = 30
HOLD      = 24   # frames to hold each state (0.8 s)
TRANS     = 20   # transition duration


def _setup_camera():
    cam_data = bpy.data.cameras.new("RecordCam")
    cam_data.lens = 35.0
    cam_obj  = bpy.data.objects.new("RecordCam", cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)
    cam_obj.location       = mathutils.Vector((1.5, -6.0, 5.0))
    cam_obj.rotation_euler = mathutils.Euler((0.93, 0.0, 0.20), "XYZ")
    bpy.context.scene.camera = cam_obj


def _setup_lighting():
    sun_data = bpy.data.lights.new("Sun", type="SUN")
    sun_data.energy = 3.5
    sun_data.angle  = 0.04
    sun_obj  = bpy.data.objects.new("Sun", sun_data)
    bpy.context.scene.collection.objects.link(sun_obj)
    sun_obj.rotation_euler = mathutils.Euler((0.6, 0.0, 0.8), "XYZ")

    fill_data = bpy.data.lights.new("Fill", type="AREA")
    fill_data.energy = 100.0
    fill_data.size   = 6.0
    fill_obj  = bpy.data.objects.new("Fill", fill_data)
    bpy.context.scene.collection.objects.link(fill_obj)
    fill_obj.location      = mathutils.Vector((-4.0, -4.0, 6.0))
    fill_obj.rotation_euler = mathutils.Euler((0.9, 0.0, -0.8), "XYZ")


def _kf(obj, sk_name, value, frame):
    blk = obj.data.shape_keys.key_blocks.get(sk_name)
    if blk:
        blk.value = value
        blk.keyframe_insert("value", frame=frame)


def _animate(obj):
    sk_names = ["SK_PhiPi4", "SK_NearCrit", "SK_Trivial"]
    scene    = bpy.context.scene
    scene.frame_start = 1
    f = 1

    for sk in sk_names:
        _kf(obj, sk, 0.0, f)

    # Hold Basis
    f += HOLD

    for sk in sk_names:
        # Ramp in
        f_start = f
        f_end   = f + TRANS
        _kf(obj, sk, 0.0, f_start)
        _kf(obj, sk, 1.0, f_end)
        for other in sk_names:
            if other != sk:
                _kf(obj, other, 0.0, f_end)
        f = f_end
        f += HOLD
        # Ramp out
        _kf(obj, sk, 1.0, f)
        _kf(obj, sk, 0.0, f + TRANS)
        f += TRANS

    scene.frame_end = f + HOLD // 2


def _configure_eevee():
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
    eevee.bloom_intensity    = 0.08


def main():
    obj = bpy.data.objects.get(OBJ_NAME)
    if obj is None:
        print(f"[record] ERROR — '{OBJ_NAME}' not found; run blueprint.py first.")
        return

    for o in bpy.data.objects:
        if o.type in {"CAMERA", "LIGHT"}:
            bpy.data.objects.remove(o, do_unlink=True)

    _setup_camera()
    _setup_lighting()
    _animate(obj)
    _configure_eevee()

    print(f"[record] Rendering {bpy.context.scene.frame_end} frames → {VIDEO_OUT}")
    bpy.ops.render.render(animation=True)
    print("[record] Done.")


if __name__ == "__main__":
    main()
