"""
record.py — viewport animation for the Hofstadter Butterfly floor.

Renders a 12-second clip at 24 fps cycling through the four shape keys:
  Basis   → full butterfly (all α ∈ [0,1])
  SK_Half → left half zoomed (symmetry of the butterfly)
  SK_Zoom → 1/3 sub-butterfly (fractal self-similarity)
  SK_NNN  → NNN-modified butterfly (particle-hole symmetry broken)

Output → public/library/videos/scripting/
  python-numpy-hofstadter-butterfly-1976-fractal-energy-spectrum-
  bloch-electrons-magnetic-flux-harper-equation-height-field-stage-floor-webxr/
  viewport.mp4

Run AFTER blueprint.py has built the scene.  Licence: CC0.
"""

import bpy

DURATION_S   = 12
FPS          = 24
TOTAL_FRAMES = DURATION_S * FPS   # 288

OUTPUT_PATH = (
    "//../../../../videos/scripting/"
    "python-numpy-hofstadter-butterfly-1976-fractal-energy-spectrum-"
    "bloch-electrons-magnetic-flux-harper-equation-height-field-stage-floor-webxr"
    "/viewport"
)

RESOLUTION_X = 1920
RESOLUTION_Y = 1080

# Hold 50 frames each, crossfade 20 frames between them
KEYFRAMES = [
    (1,   "Basis",   1.0),
    (55,  "Basis",   1.0),
    (75,  "SK_Half", 1.0),
    (125, "SK_Half", 1.0),
    (145, "SK_Zoom", 1.0),
    (200, "SK_Zoom", 1.0),
    (220, "SK_NNN",  1.0),
    (270, "SK_NNN",  1.0),
    (288, "Basis",   1.0),
]


def _setup_camera() -> None:
    cam_data = bpy.data.cameras.new("RecordCam")
    cam_data.lens = 35
    cam_obj = bpy.data.objects.new("RecordCam", cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)
    cam_obj.location       = (0.0, -0.95, 0.72)
    cam_obj.rotation_euler = (1.08, 0.0, 0.0)
    bpy.context.scene.camera = cam_obj


def _setup_light() -> None:
    sun_data = bpy.data.lights.new("RecordSun", type="SUN")
    sun_data.energy = 3.0
    sun_obj = bpy.data.objects.new("RecordSun", sun_data)
    bpy.context.scene.collection.objects.link(sun_obj)
    sun_obj.rotation_euler = (0.5, 0.2, 0.9)


def _setup_render() -> None:
    scene = bpy.context.scene
    scene.render.engine                      = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x               = RESOLUTION_X
    scene.render.resolution_y               = RESOLUTION_Y
    scene.render.fps                        = FPS
    scene.frame_start                       = 1
    scene.frame_end                         = TOTAL_FRAMES
    scene.render.image_settings.file_format = "FFMPEG"
    scene.render.ffmpeg.format              = "MPEG4"
    scene.render.ffmpeg.codec               = "H264"
    scene.render.ffmpeg.constant_rate_factor = "MEDIUM"
    scene.render.filepath                   = OUTPUT_PATH


def _animate_shape_keys(obj: bpy.types.Object) -> None:
    keys = obj.data.shape_keys
    if keys is None:
        raise RuntimeError("No shape keys — run blueprint.py first.")
    key_blocks = {kb.name: kb for kb in keys.key_blocks}
    for kb in keys.key_blocks:
        kb.value = 0.0
    for frame, sk_name, value in KEYFRAMES:
        if sk_name not in key_blocks:
            print(f"Warning: shape key '{sk_name}' not found — skipping.")
            continue
        bpy.context.scene.frame_set(frame)
        for kb in keys.key_blocks:
            kb.value = value if kb.name == sk_name else 0.0
            kb.keyframe_insert(data_path="value", frame=frame)


def main() -> None:
    _setup_camera()
    _setup_light()
    _setup_render()
    obj = bpy.data.objects.get("hofstadter_floor")
    if obj is None:
        raise RuntimeError(
            "Object 'hofstadter_floor' not found.  Run blueprint.py first.")
    _animate_shape_keys(obj)
    print(f"[record.py] Rendering {TOTAL_FRAMES} frames → {OUTPUT_PATH}.mp4")
    bpy.ops.render.render(animation=True)
    print("[record.py] Done.")


if __name__ == "__main__":
    main()
