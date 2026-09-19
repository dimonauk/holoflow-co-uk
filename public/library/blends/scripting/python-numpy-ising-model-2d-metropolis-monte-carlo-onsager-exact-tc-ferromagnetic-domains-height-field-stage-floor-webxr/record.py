"""
record.py — viewport animation for the Ising spin floor.

Renders a 10-second clip at 24 fps showing the four shape-key states
in sequence with interpolation.  Output → public/library/videos/scripting/
python-numpy-ising-model-2d-metropolis-monte-carlo-onsager-exact-tc-ferromagnetic-domains-height-field-stage-floor-webxr/viewport.mp4

Run this script AFTER blueprint.py has built the scene.
"""

import bpy

# ── scene / render settings ───────────────────────────────────────────────────
DURATION_S   = 10
FPS          = 24
TOTAL_FRAMES = DURATION_S * FPS          # 240 frames

OUTPUT_PATH = "//../../../../videos/scripting/" \
              "python-numpy-ising-model-2d-metropolis-monte-carlo-onsager-exact-tc" \
              "-ferromagnetic-domains-height-field-stage-floor-webxr/viewport"

RESOLUTION_X = 1920
RESOLUTION_Y = 1080

# ── key-frame schedule ────────────────────────────────────────────────────────
# Each shape key holds for ~50 frames then cross-fades over 20 frames.
# Timeline (frames):   0 → Basis(cold)  60 → SK_Critical  120 → SK_Hot  180 → SK_Quench  240

KEYFRAMES = [
    (1,   "Basis",       1.0),
    (50,  "Basis",       1.0),
    (70,  "SK_Critical", 1.0),
    (110, "SK_Critical", 1.0),
    (130, "SK_Hot",      1.0),
    (170, "SK_Hot",      1.0),
    (190, "SK_Quench",   1.0),
    (240, "SK_Quench",   1.0),
]


def _setup_camera() -> None:
    cam_data = bpy.data.cameras.new("RecordCam")
    cam_data.lens = 35
    cam_obj = bpy.data.objects.new("RecordCam", cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)

    cam_obj.location = (0.0, -8.0, 5.5)
    cam_obj.rotation_euler = (1.15, 0.0, 0.0)

    bpy.context.scene.camera = cam_obj


def _setup_light() -> None:
    sun_data = bpy.data.lights.new("RecordSun", type="SUN")
    sun_data.energy = 3.0
    sun_obj = bpy.data.objects.new("RecordSun", sun_data)
    bpy.context.scene.collection.objects.link(sun_obj)
    sun_obj.rotation_euler = (0.6, 0.2, 0.8)


def _animate_shape_keys(obj: bpy.types.Object) -> None:
    """Insert value keyframes on each shape key to drive the animation."""
    sk = obj.data.shape_keys
    if not sk:
        print("[record.py] No shape keys found — run blueprint.py first.")
        return

    # zero all keys at frame 1
    for key in sk.key_blocks:
        key.value = 0.0
        key.keyframe_insert("value", frame=1)

    # lock Basis to 1.0 throughout (it's the reference mesh)
    basis = sk.key_blocks.get("Basis")
    if basis:
        basis.value = 1.0
        for f in (1, TOTAL_FRAMES):
            basis.keyframe_insert("value", frame=f)

    # animate non-basis keys
    active_keys = ["SK_Critical", "SK_Hot", "SK_Quench"]
    windows = [
        (50,  70,  110, 130),   # SK_Critical: fade in 50-70, hold, fade out 110-130
        (110, 130, 170, 190),   # SK_Hot
        (170, 190, 220, 240),   # SK_Quench
    ]
    for key_name, (fin_s, fin_e, fout_s, fout_e) in zip(active_keys, windows):
        k = sk.key_blocks.get(key_name)
        if not k:
            continue
        k.value = 0.0
        k.keyframe_insert("value", frame=fin_s)
        k.value = 1.0
        k.keyframe_insert("value", frame=fin_e)
        k.keyframe_insert("value", frame=fout_s)
        k.value = 0.0
        k.keyframe_insert("value", frame=fout_e)


def main() -> None:
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end   = TOTAL_FRAMES

    scene.render.resolution_x      = RESOLUTION_X
    scene.render.resolution_y      = RESOLUTION_Y
    scene.render.fps                = FPS
    scene.render.image_settings.file_format = "FFMPEG"
    scene.render.ffmpeg.format      = "MPEG4"
    scene.render.ffmpeg.codec       = "H264"
    scene.render.ffmpeg.constant_rate_factor = "MEDIUM"
    scene.render.filepath           = OUTPUT_PATH

    # use Workbench for speed — Studio Light preset
    scene.render.engine = "BLENDER_WORKBENCH"
    scene.display.shading.light    = "STUDIO"
    scene.display.shading.color_type = "VERTEX"

    _setup_camera()
    _setup_light()

    obj = bpy.data.objects.get("ising_spin_floor")
    if obj is None:
        print("[record.py] Object 'ising_spin_floor' not found.")
        return

    _animate_shape_keys(obj)

    bpy.ops.render.render(animation=True)
    print(f"[record.py] Rendered {TOTAL_FRAMES} frames → {OUTPUT_PATH}.mp4")


if __name__ == "__main__":
    main()
