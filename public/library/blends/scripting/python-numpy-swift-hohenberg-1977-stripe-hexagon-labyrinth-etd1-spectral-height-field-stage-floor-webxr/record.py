"""
record.py — viewport animation render for Swift-Hohenberg stage floor
Outputs: public/library/videos/scripting/<slug>/viewport.mp4
Duration: ~10 seconds (250 frames @ 25 fps)
Technique: morph-target scrub from Basis → SK_Hex → SK_Labyrinth → SK_Inverted,
           with camera orbiting overhead to reveal the pattern topology.
Run from Blender's Python console AFTER running blueprint.py in the same session.
"""

import bpy, math

# ── parameters ────────────────────────────────────────────────────────────────
FPS          = 25
TOTAL_FRAMES = 250          # 10 s
OUT_PATH     = "//../../videos/scripting/" \
               "python-numpy-swift-hohenberg-1977-stripe-hexagon-labyrinth-" \
               "etd1-spectral-height-field-stage-floor-webxr/viewport.mp4"

OBJ_NAME     = "sh_pattern_floor"
CAM_HEIGHT   = 6.0          # metres above floor
CAM_RADIUS   = 5.0          # orbit radius
CAM_TILT_DEG = 55.0         # camera tilt from vertical

# shape key morph schedule (frame, key_name, value)
# Transition: each key rises to 1 then falls back to 0
MORPH_SCHEDULE = [
    # Frame  key             value
    (0,     "SK_Hex",        0.0),
    (60,    "SK_Hex",        1.0),   # cross-fade to hexagons
    (100,   "SK_Hex",        1.0),
    (130,   "SK_Hex",        0.0),
    (130,   "SK_Labyrinth",  0.0),
    (170,   "SK_Labyrinth",  1.0),
    (200,   "SK_Labyrinth",  1.0),
    (220,   "SK_Labyrinth",  0.0),
    (220,   "SK_Inverted",   0.0),
    (250,   "SK_Inverted",   1.0),
]


def setup_scene():
    scene = bpy.context.scene
    scene.render.fps              = FPS
    scene.frame_start             = 1
    scene.frame_end               = TOTAL_FRAMES
    scene.render.filepath         = OUT_PATH
    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format    = 'MPEG4'
    scene.render.ffmpeg.codec     = 'H264'
    scene.render.ffmpeg.constant_rate_factor = 'MEDIUM'
    scene.render.resolution_x     = 1920
    scene.render.resolution_y     = 1080
    scene.render.resolution_percentage = 100


def setup_camera():
    """Orbit camera: starts top-down, slowly circles the floor."""
    cam_data = bpy.data.cameras.new("RecordCam")
    cam_obj  = bpy.data.objects.new("RecordCam", cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

    tilt = math.radians(CAM_TILT_DEG)
    for frame in range(1, TOTAL_FRAMES + 1):
        angle = 2.0 * math.pi * (frame - 1) / TOTAL_FRAMES
        x = CAM_RADIUS * math.cos(angle)
        y = CAM_RADIUS * math.sin(angle)
        z = CAM_HEIGHT
        cam_obj.location = (x, y, z)
        # Tilt toward the floor centre
        cam_obj.rotation_euler = (tilt, 0.0, angle + math.pi / 2.0)
        cam_obj.keyframe_insert('location',       frame=frame)
        cam_obj.keyframe_insert('rotation_euler', frame=frame)


def setup_lighting():
    """Simple three-point Eevee rig: sun + two area lights."""
    # Sun (key)
    sun = bpy.data.lights.new("RecordSun", type='SUN')
    sun.energy = 3.0
    sun_obj = bpy.data.objects.new("RecordSun", sun)
    bpy.context.scene.collection.objects.link(sun_obj)
    sun_obj.rotation_euler = (math.radians(45), 0, math.radians(30))

    # Fill area light
    fill = bpy.data.lights.new("RecordFill", type='AREA')
    fill.energy = 200.0
    fill_obj = bpy.data.objects.new("RecordFill", fill)
    bpy.context.scene.collection.objects.link(fill_obj)
    fill_obj.location = (-4, 4, 5)


def keyframe_morphs():
    obj = bpy.data.objects.get(OBJ_NAME)
    if obj is None or obj.data.shape_keys is None:
        print("[record] ERROR: sh_pattern_floor not found — run blueprint.py first")
        return
    keys = obj.data.shape_keys.key_blocks
    # Initialise all SK values to 0
    for kb in keys:
        if kb.name != "Basis":
            kb.value = 0.0
            kb.keyframe_insert('value', frame=1)

    for (frame, key_name, val) in MORPH_SCHEDULE:
        if key_name in keys:
            keys[key_name].value = val
            keys[key_name].keyframe_insert('value', frame=frame)


def render():
    bpy.ops.render.render(animation=True, write_still=False)
    print(f"[record] Render complete → {OUT_PATH}")


setup_scene()
setup_camera()
setup_lighting()
keyframe_morphs()
render()
