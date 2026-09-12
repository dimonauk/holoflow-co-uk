"""
Holoflow Studio — viewport.mp4 recorder for GPE BEC Vortex Lattice.
Run AFTER blueprint.py in the same Blender session (or re-open the .blend).

Outputs: public/library/videos/scripting/<slug>/viewport.mp4
Duration: 15 s · 30 fps (450 frames)
Content:
  0– 3 s   Basis (smooth Thomas-Fermi, no vortices) — hold
  3– 7 s   Morph Basis → SK_Hex7  (7-vortex Abrikosov lattice nucleates)
  7–11 s   Hold SK_Hex7
 11–14 s   Morph SK_Hex7 → SK_Hex19 (lattice densifies)
 14–15 s   Hold SK_Hex19

Camera: overhead orthographic, 15° tilt — reveals the hexagonal lattice
symmetry without perspective foreshortening.
"""
import bpy, os, math

SLUG = (
    "python-numpy-gross-pitaevskii-bec-rotating-vortex-lattice-"
    "abrikosov-imaginary-time-stage-floor-webxr"
)
OBJ_NAME = "gpe_bec_vortex"
FPS      = 30
FRAMES   = 450   # 15 s


def setup_render():
    sc = bpy.context.scene
    sc.render.engine                          = 'BLENDER_EEVEE_NEXT'
    sc.render.fps                             = FPS
    sc.frame_start                            = 1
    sc.frame_end                              = FRAMES
    sc.render.resolution_x                    = 1920
    sc.render.resolution_y                    = 1080
    sc.render.image_settings.file_format      = 'FFMPEG'
    sc.render.ffmpeg.format                   = 'MPEG4'
    sc.render.ffmpeg.codec                    = 'H264'
    sc.render.ffmpeg.constant_rate_factor     = 'HIGH'
    repo_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../../../")
    )
    out_dir = os.path.join(
        repo_root, "public", "library", "videos", "scripting", SLUG
    )
    os.makedirs(out_dir, exist_ok=True)
    sc.render.filepath = os.path.join(out_dir, "viewport.mp4")


def setup_camera():
    """
    Orthographic overhead, tilted 15° forward.
    WHY ortho: removes perspective distortion so the hexagonal lattice
    geometry reads accurately — equidistant vortex cores look equidistant.
    """
    sc = bpy.context.scene
    # remove any existing record camera
    for obj in list(bpy.data.objects):
        if obj.name == "RecordCam":
            bpy.data.objects.remove(obj, do_unlink=True)
    cam_data              = bpy.data.cameras.new("RecordCam")
    cam_data.type         = 'ORTHO'
    cam_data.ortho_scale  = 10.0
    cam_obj               = bpy.data.objects.new("RecordCam", cam_data)
    bpy.context.collection.objects.link(cam_obj)
    cam_obj.location       = (0.0, -5.5, 11.0)
    cam_obj.rotation_euler = (math.radians(75), 0.0, 0.0)
    sc.camera              = cam_obj


def add_light():
    """Single area light for soft directional illumination."""
    for ob in list(bpy.data.objects):
        if ob.name == "RecordLight":
            bpy.data.objects.remove(ob, do_unlink=True)
    light_data        = bpy.data.lights.new("RecordLight", type='AREA')
    light_data.energy = 800
    light_data.size   = 8.0
    light_obj         = bpy.data.objects.new("RecordLight", light_data)
    bpy.context.collection.objects.link(light_obj)
    light_obj.location       = (4.0, -4.0, 10.0)
    light_obj.rotation_euler = (math.radians(40), math.radians(20), 0.0)


def keyframe_morph():
    """
    Drive shape key values to animate vortex lattice nucleation.
    SK_Hex7 goes 0→1 in frames 90–210 (t=3s→7s).
    SK_Hex19 goes 0→1 in frames 330–420 (t=11s→14s).
    Both use BEZIER interpolation for smooth onset.
    """
    ob = bpy.data.objects.get(OBJ_NAME)
    if ob is None:
        raise RuntimeError(f"Object '{OBJ_NAME}' not found — run blueprint.py first.")
    keys = ob.data.shape_keys.key_blocks

    def kf(key_name, frame, val):
        k = keys.get(key_name)
        if k is None:
            raise RuntimeError(f"Shape key '{key_name}' missing.")
        k.value = val
        k.keyframe_insert("value", frame=frame)

    # SK_Hex7: 0 → 1 → stays 1 until end
    kf("SK_Hex7",  1,   0.0)
    kf("SK_Hex7",  90,  0.0)   # hold 3 s at Basis
    kf("SK_Hex7",  210, 1.0)   # morph ends at 7 s
    kf("SK_Hex7",  450, 1.0)   # hold to end

    # SK_Hex19: 0 → 1 at 11–14 s
    kf("SK_Hex19", 1,   0.0)
    kf("SK_Hex19", 330, 0.0)
    kf("SK_Hex19", 420, 1.0)
    kf("SK_Hex19", 450, 1.0)

    # SK_Hex7 fades out as SK_Hex19 comes in (crossfade)
    kf("SK_Hex7",  330, 1.0)
    kf("SK_Hex7",  420, 0.0)

    # Apply BEZIER easing to all inserted fcurves
    action = ob.data.shape_keys.animation_data.action
    if action:
        for fc in action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = 'BEZIER'


def main():
    setup_render()
    setup_camera()
    add_light()
    keyframe_morph()
    bpy.ops.render.render(animation=True)
    print(f"viewport.mp4 written — {FRAMES} frames @ {FPS} fps")


main()
