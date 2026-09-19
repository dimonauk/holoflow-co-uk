"""
record.py — viewport animation for the GUE spacing-surface entry.
Morphs through Basis → SK_GOE → SK_MC → SK_Poisson and back,
visualising the transition from the full β-family surface to individual
cross-sections. Outputs to public/library/videos/scripting/<slug>/viewport.mp4.

Run AFTER blueprint.py has built and saved gue_spacing_floor.blend.
Total render: 5 s × 30 fps = 150 frames.  Phase durations:
  frames  0–37:  fade Basis → SK_GOE  (1.25 s)
  frames 38–75:  hold SK_GOE          (1.25 s)
  frames 76–112: fade SK_GOE → SK_MC  (1.25 s)
  frames113–150: fade SK_MC → SK_Pois (1.25 s)
"""

import bpy, math, os

FPS        = 30
DURATION_S = 5
OUT_PATH   = "//../../videos/scripting/python-numpy-gue-gaussian-unitary-ensemble-montgomery-1973-pair-correlation-sine-kernel-wigner-dyson-beta-family-stage-floor-webxr/viewport.mp4"
BLEND_PATH = "//gue_spacing_floor.blend"

PHASES = [
    # (start_frame, end_frame, key_start, key_end)
    (0,   37,  "Basis",      "SK_GOE"),
    (38,  75,  "SK_GOE",     "SK_GOE"),
    (76,  112, "SK_GOE",     "SK_MC"),
    (113, 150, "SK_MC",      "SK_Poisson"),
]


def setup_camera() -> None:
    cam_data = bpy.data.cameras.new("RecordCam")
    cam_obj  = bpy.data.objects.new("RecordCam", cam_data)
    bpy.context.collection.objects.link(cam_obj)
    cam_obj.location      = (0.0, -5.5, 3.5)
    cam_obj.rotation_euler = (math.radians(52), 0.0, 0.0)
    cam_data.lens         = 50.0
    bpy.context.scene.camera = cam_obj


def setup_lighting() -> None:
    sun = bpy.data.lights.new("Sun", type="SUN")
    sun.energy = 3.0
    sun_obj = bpy.data.objects.new("Sun", sun)
    bpy.context.collection.objects.link(sun_obj)
    sun_obj.rotation_euler = (math.radians(45), 0.0, math.radians(30))


def keyframe_shape_keys(obj: bpy.types.Object) -> None:
    """Animate shape key values to morph through PHASES."""
    keys = obj.data.shape_keys.key_blocks
    sk_names = [k.name for k in keys if k.name != "Basis"]

    def set_all(frame: int, active: str, value: float, others: float) -> None:
        bpy.context.scene.frame_set(frame)
        for n in sk_names:
            v = value if n == active else others
            keys[n].value = v
            keys[n].keyframe_insert("value", frame=frame)

    # Walk through phases
    for sf, ef, k_start, k_end in PHASES:
        mid = (sf + ef) // 2
        if k_start == k_end:
            set_all(sf,  k_start, 1.0, 0.0)
            set_all(ef,  k_end,   1.0, 0.0)
        else:
            set_all(sf,  k_start, 1.0, 0.0)
            set_all(mid, k_start, 0.0, 0.0)  # crossfade midpoint
            set_all(mid, k_end,   0.0, 0.0)
            set_all(ef,  k_end,   1.0, 0.0)


def main() -> None:
    # Load the saved blend built by blueprint.py
    bpy.ops.wm.open_mainfile(filepath=bpy.path.abspath(BLEND_PATH))

    obj = bpy.data.objects.get("gue_spacing_floor")
    if obj is None:
        raise RuntimeError("Object 'gue_spacing_floor' not found — run blueprint.py first.")

    setup_camera()
    setup_lighting()

    scene = bpy.context.scene
    scene.frame_start = 0
    scene.frame_end   = FPS * DURATION_S
    scene.render.fps  = FPS

    scene.render.image_settings.file_format = "FFMPEG"
    scene.render.ffmpeg.format   = "MPEG4"
    scene.render.ffmpeg.codec    = "H264"
    scene.render.ffmpeg.constant_rate_factor = "MEDIUM"
    scene.render.resolution_x    = 1280
    scene.render.resolution_y    = 720
    scene.render.filepath        = bpy.path.abspath(OUT_PATH)

    keyframe_shape_keys(obj)
    bpy.ops.render.render(animation=True)
    print("[GUE record] viewport.mp4 written.")


if __name__ == "__main__":
    main()
