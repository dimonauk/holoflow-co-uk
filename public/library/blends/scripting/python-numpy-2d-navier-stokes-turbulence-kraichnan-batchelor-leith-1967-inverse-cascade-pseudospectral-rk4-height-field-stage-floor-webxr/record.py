"""
record.py — viewport animation render for the NS2D turbulence floor
Outputs: public/library/videos/scripting/<slug>/viewport.mp4
Run inside Blender 5.1 after opening ns2d_turbulence_floor.blend.
Duration: ~8 seconds at 30 fps = 240 frames, shape-key sweep.
"""

import bpy, pathlib

SLUG    = "python-numpy-2d-navier-stokes-turbulence-kraichnan-batchelor-leith-1967-inverse-cascade-pseudospectral-rk4-height-field-stage-floor-webxr"
OUT_DIR = pathlib.Path(f"public/library/videos/scripting/{SLUG}")
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT  = str(OUT_DIR / "viewport.mp4")

FPS     = 30
FRAMES  = 240   # 8 s total: 60 f Basis, 60 f SK_Cascade, 60 f SK_Condensed, 60 f SK_Forced
KEYS    = ["Basis", "SK_Cascade", "SK_Condensed", "SK_Forced"]
FRAMES_PER_KEY = FRAMES // len(KEYS)

# ── scene and render settings ─────────────────────────────────────────────────

scene = bpy.context.scene
scene.render.engine           = "BLENDER_EEVEE_NEXT"
scene.render.resolution_x     = 1920
scene.render.resolution_y     = 1080
scene.render.fps               = FPS
scene.render.image_settings.file_format = "FFMPEG"
scene.render.ffmpeg.format     = "MPEG4"
scene.render.ffmpeg.codec      = "H264"
scene.render.ffmpeg.constant_rate_factor = "HIGH"
scene.render.filepath          = OUTPUT
scene.frame_start              = 1
scene.frame_end                = FRAMES

# ── camera ────────────────────────────────────────────────────────────────────

cam_data = bpy.data.cameras.new("RecordCam")
cam_obj  = bpy.data.objects.new("RecordCam", cam_data)
bpy.context.scene.collection.objects.link(cam_obj)
scene.camera = cam_obj

# Bird's-eye view, slightly angled to show height variation
cam_obj.location = (0.0, -10.0, 12.0)
cam_obj.rotation_euler = (0.72, 0.0, 0.0)   # ~41° tilt
cam_data.lens = 35.0

# ── lighting ─────────────────────────────────────────────────────────────────

world = bpy.context.scene.world
if not world:
    world = bpy.data.worlds.new("World")
    scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[1].default_value = 0.04   # near-black

sun      = bpy.data.lights.new("Sun", "SUN")
sun_obj  = bpy.data.objects.new("Sun", sun)
bpy.context.scene.collection.objects.link(sun_obj)
sun_obj.rotation_euler = (0.6, 0.3, 0.8)
sun.energy = 2.5

# ── shape-key animation keyframes ────────────────────────────────────────────

obj = bpy.data.objects.get("NS2D_Turb")
if obj and obj.data.shape_keys:
    kb = obj.data.shape_keys.key_blocks
    for ki, key_name in enumerate(KEYS):
        start_frame = ki * FRAMES_PER_KEY + 1
        end_frame   = start_frame + FRAMES_PER_KEY - 1
        for kname in KEYS:
            if kname in kb:
                kb[kname].value = 1.0 if kname == key_name else 0.0
                kb[kname].keyframe_insert("value", frame=start_frame)
                kb[kname].keyframe_insert("value", frame=end_frame)

# ── render ────────────────────────────────────────────────────────────────────

bpy.ops.render.render(animation=True)
print(f"Viewport render done → {OUTPUT}")
