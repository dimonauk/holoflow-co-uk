"""
Viewport animation record — 1D FDTD Maxwell / Yee 1966
Animates the four shape keys (free space → dielectric → cavity → PML) to show
each EM wave scenario in sequence.  Output: viewport.mp4 (5 s at 30 fps).

Run AFTER blueprint.py has saved fdtd_field_floor.blend.
Open that blend in Blender 5.1, switch to Scripting, run this script.
"""

import bpy
import math

FPS      = 30
DURATION = 5
N_FRAMES = FPS * DURATION   # 150

OUT_PATH = (
    "//../../videos/scripting/"
    "python-numpy-yee-1966-fdtd-1d-maxwell-equations-em-wave-dielectric-pml-"
    "space-time-height-field-stage-floor-webxr/viewport.mp4"
)


def find_fdtd_obj() -> bpy.types.Object:
    for obj in bpy.data.objects:
        if obj.type == "MESH" and "fdtd" in obj.name.lower():
            return obj
    raise RuntimeError("FDTD mesh not found — run blueprint.py first.")


def kf(obj: bpy.types.Object, sk_name: str, value: float, frame: int) -> None:
    kb = obj.data.shape_keys.key_blocks[sk_name]
    kb.value = value
    kb.keyframe_insert("value", frame=frame)


def setup_camera() -> None:
    bpy.ops.object.camera_add(location=(0.0, -4.0, 3.5))
    cam = bpy.context.object
    cam.rotation_euler = (math.radians(50), 0.0, 0.0)
    bpy.context.scene.camera = cam


def setup_render() -> None:
    sc = bpy.context.scene
    sc.render.engine                        = "BLENDER_EEVEE_NEXT"
    sc.render.fps                           = FPS
    sc.frame_start                          = 1
    sc.frame_end                            = N_FRAMES
    sc.render.image_settings.file_format    = "FFMPEG"
    sc.render.ffmpeg.format                 = "MPEG4"
    sc.render.ffmpeg.codec                  = "H264"
    sc.render.ffmpeg.constant_rate_factor   = "HIGH"
    sc.render.filepath                      = bpy.path.abspath(OUT_PATH)
    sc.render.resolution_x                  = 1920
    sc.render.resolution_y                  = 1080


def animate_shape_keys(obj: bpy.types.Object) -> None:
    """
    Sequence (each hold for ~1 s, cross-fade in ~0.5 s):
      f1–30    Basis (free space, bouncing pulses)
      f31–60   SK_Dielectric (Fresnel reflection at ε interface)
      f61–90   SK_Cavity (standing wave resonance)
      f91–120  SK_PML (clean absorption at boundaries)
      f121–150 return to Basis
    """
    sk_names = ["Basis", "SK_Dielectric", "SK_Cavity", "SK_PML"]
    for name in sk_names:
        obj.data.shape_keys.key_blocks[name].value = 0.0

    schedule = [
        (1,   "Basis",           1.0),
        (30,  "Basis",           1.0),
        (45,  "Basis",           0.0),
        (45,  "SK_Dielectric",   1.0),
        (75,  "SK_Dielectric",   1.0),
        (90,  "SK_Dielectric",   0.0),
        (90,  "SK_Cavity",       1.0),
        (120, "SK_Cavity",       1.0),
        (135, "SK_Cavity",       0.0),
        (135, "SK_PML",          1.0),
        (150, "SK_PML",          1.0),
    ]
    for frame, name, val in schedule:
        kf(obj, name, val, frame)


def main() -> None:
    obj = find_fdtd_obj()
    setup_camera()
    setup_render()
    animate_shape_keys(obj)

    bpy.ops.object.light_add(type="AREA", location=(0.0, -2.0, 4.0))
    light = bpy.context.object
    light.data.energy = 250
    light.data.size   = 3.0
    light.rotation_euler = (math.radians(45), 0.0, 0.0)

    bpy.ops.render.render(animation=True)
    print(f"[FDTD record] viewport.mp4 → {OUT_PATH}")


if __name__ == "__main__":
    main()
