"""
Viewport animation record script — Kuramoto Phase Oscillator Model
Drives shape key values over 150 frames to animate the phase landscape
through four synchronisation regimes. Output: viewport.mp4 (5 s at 30 fps).

Run AFTER blueprint.py has saved kuramoto_phase_floor.blend.
Open that blend, switch to Scripting workspace, run this script.
"""

import bpy
import math

FPS      = 30
DURATION = 5          # seconds
N_FRAMES = FPS * DURATION   # 150

BLEND_PATH = "//kuramoto_phase_floor.blend"
OUT_PATH   = "//../../videos/scripting/python-numpy-kuramoto-2d-phase-oscillators-synchronisation-spiral-wave-chimera-stage-floor-webxr/viewport.mp4"


def find_kuramoto_obj() -> bpy.types.Object:
    for obj in bpy.data.objects:
        if obj.type == "MESH" and "Kuramoto" in obj.name:
            return obj
    raise RuntimeError("Kuramoto mesh not found — run blueprint.py first.")


def keyframe_shape_key(obj: bpy.types.Object, sk_name: str,
                       value: float, frame: int) -> None:
    kb = obj.data.shape_keys.key_blocks[sk_name]
    kb.value = value
    kb.keyframe_insert("value", frame=frame)


def setup_camera() -> None:
    bpy.ops.object.camera_add(location=(0.0, -3.5, 3.2))
    cam = bpy.context.object
    cam.rotation_euler = (math.radians(52), 0.0, 0.0)
    bpy.context.scene.camera = cam


def setup_render() -> None:
    sc = bpy.context.scene
    sc.render.engine             = "BLENDER_EEVEE_NEXT"
    sc.render.fps                = FPS
    sc.frame_start               = 1
    sc.frame_end                 = N_FRAMES
    sc.render.image_settings.file_format = "FFMPEG"
    sc.render.ffmpeg.format      = "MPEG4"
    sc.render.ffmpeg.codec       = "H264"
    sc.render.ffmpeg.constant_rate_factor = "HIGH"
    sc.render.filepath           = bpy.path.abspath(OUT_PATH)
    sc.render.resolution_x       = 1920
    sc.render.resolution_y       = 1080


def animate_shape_keys(obj: bpy.types.Object) -> None:
    """
    Sequence: Basis (spirals) → SK_LowK (turbulent) → SK_HighK (locked) → Basis
    Timing: each transition takes 1 second; holds for 0.5 s each.
    """
    sk_names = ["Basis", "SK_LowK", "SK_HighK", "SK_BroadW"]
    # initialise all to zero
    for name in sk_names:
        kb = obj.data.shape_keys.key_blocks[name]
        kb.value = 0.0

    # frame schedule:  f0=1, f1=30(end Basis), f2=60(LowK peak), f3=90(HighK),
    #                  f4=120(BroadW), f5=150(back to Basis)
    schedule = [
        (1,   "Basis",    1.0),
        (30,  "Basis",    1.0),
        (45,  "Basis",    0.0),
        (45,  "SK_LowK",  1.0),
        (75,  "SK_LowK",  1.0),
        (90,  "SK_LowK",  0.0),
        (90,  "SK_HighK", 1.0),
        (120, "SK_HighK", 1.0),
        (135, "SK_HighK", 0.0),
        (135, "SK_BroadW", 1.0),
        (150, "SK_BroadW", 1.0),
    ]
    for frame, name, val in schedule:
        keyframe_shape_key(obj, name, val, frame)


def main() -> None:
    obj = find_kuramoto_obj()
    setup_camera()
    setup_render()
    animate_shape_keys(obj)

    # add a warm area light
    bpy.ops.object.light_add(type="AREA", location=(1.0, -1.0, 3.0))
    light = bpy.context.object
    light.data.energy = 200
    light.data.size   = 2.0
    light.rotation_euler = (math.radians(45), 0.0, math.radians(30))

    bpy.ops.render.render(animation=True)
    print(f"[Kuramoto record] viewport.mp4 written to {OUT_PATH}")


if __name__ == "__main__":
    main()
