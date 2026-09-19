"""
record.py — SSH Spectral-Flow Viewport Animation
=================================================
Assumes blueprint.py has already been run and ssh_spectrum_floor.blend saved
alongside this script.  Opens the blend, configures camera + lighting,
animates shape-key morphing through all four spectral-flow variants, and
renders to viewport.mp4 at 1280×720 30fps via EEVEE.

Run inside Blender 5.1:
  blender ssh_spectrum_floor.blend --python record.py

Output: public/library/videos/scripting/<slug>/viewport.mp4
"""

import bpy, mathutils, pathlib

SLUG      = ("python-numpy-ssh-su-schrieffer-heeger-1979-zak-phase-"
             "topological-edge-states-spectral-flow-stage-floor-webxr")
VIDEO_OUT = (pathlib.Path(__file__).parents[4]
             / "videos" / "scripting" / SLUG / "viewport.mp4")
VIDEO_OUT.parent.mkdir(parents=True, exist_ok=True)

OBJ_NAME  = "ssh_spectrum_floor"
FPS       = 30
HOLD      = 20   # frames per state
TRANS     = 20   # morph-transition frames
# States: Basis → SK_Periodic → SK_NNN → SK_SymBreak → Basis
# Total: 4 × (HOLD + TRANS) = 160 frames ≈ 5.3 s


def _setup_camera():
    cam_data = bpy.data.cameras.new("RecordCam")
    cam_data.lens = 32.0
    cam_obj  = bpy.data.objects.new("RecordCam", cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)
    cam_obj.location       = mathutils.Vector((2.0, -7.0, 4.8))
    cam_obj.rotation_euler = mathutils.Euler((0.90, 0.0, 0.25), "XYZ")
    bpy.context.scene.camera = cam_obj


def _setup_lighting():
    sun  = bpy.data.lights.new("Sun",  type="SUN");  sun.energy  = 2.5
    sun_obj = bpy.data.objects.new("Sun", sun)
    bpy.context.scene.collection.objects.link(sun_obj)
    sun_obj.rotation_euler = mathutils.Euler((0.6, 0.0, 0.9), "XYZ")

    fill = bpy.data.lights.new("Fill", type="AREA"); fill.energy = 100.0
    fill.size = 8.0
    fill_obj = bpy.data.objects.new("Fill", fill)
    bpy.context.scene.collection.objects.link(fill_obj)
    fill_obj.location       = mathutils.Vector((-4.0, -4.0, 6.0))
    fill_obj.rotation_euler = mathutils.Euler((0.9, 0.0, -0.8), "XYZ")


def _keyframe_sk(obj, sk_name: str, value: float, frame: int):
    obj.data.shape_keys.key_blocks[sk_name].value = value
    obj.data.shape_keys.key_blocks[sk_name].keyframe_insert("value", frame=frame)


def _build_animation(obj):
    """
    Animate shape-key morph:
      [0..HOLD]              Basis=1, others=0   (open BC, edge states visible)
      [HOLD..HOLD+TRANS]     cross-fade → SK_Periodic
      [HOLD+TRANS..2HOLD+TRANS] SK_Periodic=1
      … and so on for SK_NNN, SK_SymBreak, then back to Basis
    """
    keys = ["Basis", "SK_Periodic", "SK_NNN", "SK_SymBreak", "Basis"]
    t = 0
    for step, (from_k, to_k) in enumerate(zip(keys, keys[1:])):
        # hold from_k at 1.0
        _keyframe_sk(obj, from_k, 1.0, t)
        for k in keys[:-1]:
            if k != from_k:
                _keyframe_sk(obj, k, 0.0, t)
        t += HOLD

        # transition out from_k, in to_k
        _keyframe_sk(obj, from_k, 0.0, t + TRANS)
        _keyframe_sk(obj, to_k,   1.0, t + TRANS)
        for k in keys[:-1]:
            if k not in (from_k, to_k):
                _keyframe_sk(obj, k, 0.0, t + TRANS)
        t += TRANS


def _setup_eevee():
    sc = bpy.context.scene
    sc.render.engine          = "BLENDER_EEVEE_NEXT"
    sc.render.resolution_x    = 1280
    sc.render.resolution_y    = 720
    sc.render.fps             = FPS
    sc.frame_start            = 1
    sc.frame_end              = 4 * (HOLD + TRANS)
    sc.render.filepath        = str(VIDEO_OUT)
    sc.render.image_settings.file_format = "FFMPEG"
    sc.render.ffmpeg.format   = "MPEG4"
    sc.render.ffmpeg.codec    = "H264"
    sc.render.ffmpeg.constant_rate_factor = "MEDIUM"


def main():
    obj = bpy.data.objects.get(OBJ_NAME)
    if obj is None:
        raise RuntimeError(f"Object '{OBJ_NAME}' not found — run blueprint.py first.")

    _setup_camera()
    _setup_lighting()
    _build_animation(obj)
    _setup_eevee()
    bpy.ops.render.render(animation=True)
    print(f"[SSH record] written → {VIDEO_OUT}")


main()
