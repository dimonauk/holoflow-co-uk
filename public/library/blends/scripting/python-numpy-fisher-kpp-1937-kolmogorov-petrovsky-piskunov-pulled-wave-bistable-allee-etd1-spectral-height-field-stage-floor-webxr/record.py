"""
record.py — Fisher-KPP Viewport Animation Recorder
Outputs: public/library/videos/scripting/<slug>/viewport.mp4
Duration: ~12 seconds  |  30 fps  |  360 frames
Technique: morph-target sweep from Basis → SK_FastR → SK_LowD → SK_Bistable

Run inside Blender 5.1 *after* blueprint.py has built the scene:
  bpy.ops.script.python_file_run(filepath="record.py")

The script drives the 'Fisher_KPP_Floor' shape-key values over 360 frames,
configures an EEVEE viewport render at 1920×1080, and writes viewport.mp4.
"""

import bpy, os, mathutils

SLUG  = ("python-numpy-fisher-kpp-1937-kolmogorov-petrovsky-piskunov-"
         "pulled-wave-bistable-allee-etd1-spectral-height-field-stage-floor-webxr")
OUT   = f"//public/library/videos/scripting/{SLUG}/viewport.mp4"
FPS   = 30
TOTAL = 360   # 12 s total

OBJ_NAME = "Fisher_KPP_Floor"

def _ensure_dir(path):
    abs_path = bpy.path.abspath(path)
    os.makedirs(abs_path, exist_ok=True)

def _setup_render():
    sc = bpy.context.scene
    sc.render.engine          = "BLENDER_EEVEE"
    sc.render.resolution_x    = 1920
    sc.render.resolution_y    = 1080
    sc.render.fps             = FPS
    sc.frame_start            = 1
    sc.frame_end              = TOTAL
    sc.render.image_settings.file_format = "FFMPEG"
    sc.render.ffmpeg.format   = "MPEG4"
    sc.render.ffmpeg.codec    = "H264"
    sc.render.ffmpeg.constant_rate_factor = "HIGH"
    sc.render.filepath        = OUT
    _ensure_dir(os.path.dirname(bpy.path.abspath(OUT)))

def _camera_arc():
    """Orbit camera 45° over the floor, starting overhead."""
    cam_data = bpy.data.cameras.new("RecCam")
    cam_data.lens = 35.0
    cam = bpy.data.objects.new("RecCam", cam_data)
    bpy.context.scene.collection.objects.link(cam)
    bpy.context.scene.camera = cam

    # Stationary overhead-ish position looking at origin
    cam.location       = (0.0, -4.5, 3.5)
    cam.rotation_euler = mathutils.Euler((1.05, 0.0, 0.0), "XYZ")

def _light():
    ld = bpy.data.lights.new("RecLight", "SUN")
    ld.energy = 3.0
    lo = bpy.data.objects.new("RecLight", ld)
    bpy.context.scene.collection.objects.link(lo)
    lo.location       = (3.0, -2.0, 6.0)
    lo.rotation_euler = mathutils.Euler((0.6, 0.3, 0.8), "XYZ")

def _keyframe_morph(obj):
    """
    Sweep through shape keys in four acts:
      0–90 f   : Basis (KPP wavefront)
      90–180 f : dissolve to SK_FastR (faster invasion)
      180–270 f: dissolve to SK_LowD  (slow diffusion, steeper front)
      270–360 f: dissolve to SK_Bistable (Allee pushed wave)
    """
    keys = obj.data.shape_keys.key_blocks

    def set_kf(frame, name, val):
        keys[name].value = val
        keys[name].keyframe_insert(data_path="value", frame=frame)

    # All start at 0
    for nm in ["SK_FastR", "SK_LowD", "SK_Bistable"]:
        set_kf(1, nm, 0.0)

    # Act 1 → 2: fade out Basis, fade in SK_FastR
    set_kf(80,  "SK_FastR",   0.0); set_kf(100, "SK_FastR",   1.0)
    # Act 2 → 3: fade in SK_LowD
    set_kf(170, "SK_FastR",   1.0); set_kf(190, "SK_FastR",   0.0)
    set_kf(170, "SK_LowD",    0.0); set_kf(190, "SK_LowD",    1.0)
    # Act 3 → 4: fade in SK_Bistable
    set_kf(260, "SK_LowD",    1.0); set_kf(280, "SK_LowD",    0.0)
    set_kf(260, "SK_Bistable",0.0); set_kf(280, "SK_Bistable",1.0)
    set_kf(360, "SK_Bistable",1.0)

    # Interpolation: all bezier
    for fc in obj.data.shape_keys.animation_data.action.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = "BEZIER"


def main():
    _setup_render()
    _camera_arc()
    _light()

    obj = bpy.data.objects.get(OBJ_NAME)
    if obj is None:
        raise RuntimeError(f"Object '{OBJ_NAME}' not found — run blueprint.py first.")

    _keyframe_morph(obj)

    # World: dark background for contrast
    bpy.context.scene.world.use_nodes = True
    bg = bpy.context.scene.world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value    = (0.015, 0.015, 0.02, 1.0)
        bg.inputs["Strength"].default_value = 0.3

    print(f"[record.py] Rendering {TOTAL} frames to {OUT}")
    bpy.ops.render.render(animation=True)
    print("[record.py] Done.")


if __name__ == "__main__":
    main()
