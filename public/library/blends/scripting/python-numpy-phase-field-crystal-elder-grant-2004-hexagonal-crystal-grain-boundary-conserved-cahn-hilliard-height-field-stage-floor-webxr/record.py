"""
Viewport animation recorder — PFC Phase-Field Crystal
Outputs: public/library/videos/scripting/<slug>/viewport.mp4

Renders a 5-second (150-frame) fly-through that morphs from the Basis
hexagonal crystal → SK_GrainBnd → SK_Stripe → SK_Coexist → back to Basis,
giving the viewer a quick tour of the four PFC phases.

Run AFTER blueprint.py has created the scene (pfc_crystal_floor object).
"""

import bpy, math

OBJ_NAME   = "pfc_crystal_floor"
OUTPUT_DIR = "//../../videos/scripting/python-numpy-phase-field-crystal-elder-grant-2004-hexagonal-crystal-grain-boundary-conserved-cahn-hilliard-height-field-stage-floor-webxr/"
FPS        = 30
DURATION_S = 10           # seconds
N_FRAMES   = FPS * DURATION_S

scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end   = N_FRAMES
scene.render.fps  = FPS
scene.render.image_settings.file_format = 'FFMPEG'
scene.render.ffmpeg.format               = 'MPEG4'
scene.render.ffmpeg.codec                = 'H264'
scene.render.ffmpeg.constant_rate_factor = 'MEDIUM'
scene.render.filepath = OUTPUT_DIR + "viewport"
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080

obj = bpy.data.objects[OBJ_NAME]
sk  = obj.data.shape_keys

# Shape key evaluation time (absolute keys) cycling:
# Frames 1–50   : Basis
# Frames 51–100 : SK_GrainBnd
# Frames 101–150: SK_Stripe
# Frames 151–200: SK_Coexist
# Frames 201–240: back to Basis
sk.eval_time = 0.0
sk.keyframe_insert("eval_time", frame=1)
sk.eval_time = 10.0     # Basis key is index 0, 10 units each
sk.keyframe_insert("eval_time", frame=50)
sk.eval_time = 20.0     # SK_GrainBnd index 1
sk.keyframe_insert("eval_time", frame=100)
sk.eval_time = 30.0     # SK_Stripe index 2
sk.keyframe_insert("eval_time", frame=150)
sk.eval_time = 40.0     # SK_Coexist index 3
sk.keyframe_insert("eval_time", frame=200)
sk.eval_time = 0.0
sk.keyframe_insert("eval_time", frame=N_FRAMES)

# Smooth interpolation
for fcurve in sk.animation_data.action.fcurves:
    for kp in fcurve.keyframe_points:
        kp.interpolation = 'BEZIER'
        kp.easing = 'EASE_IN_OUT'

# Camera: elevated arc circling the mesh at radius ~110 units
cam_data = bpy.data.cameras.new("RecordCam")
cam_data.lens = 35
cam_obj  = bpy.data.objects.new("RecordCam", cam_data)
bpy.context.collection.objects.link(cam_obj)
scene.camera = cam_obj

cx, cy = 64.0, 64.0   # mesh centre (N/2 × DX)
for f in range(1, N_FRAMES + 1):
    t   = (f - 1) / N_FRAMES
    ang = t * 2 * math.pi
    x   = cx + 110 * math.cos(ang)
    y   = cy + 110 * math.sin(ang)
    cam_obj.location = (x, y, 90)
    cam_obj.keyframe_insert("location", frame=f)
    # Always point at mesh centre
    cam_obj.rotation_euler = (
        math.radians(55),
        0,
        ang + math.radians(90),
    )
    cam_obj.keyframe_insert("rotation_euler", frame=f)

# Smooth out cam rotation curve
for fcurve in cam_obj.animation_data.action.fcurves:
    for kp in fcurve.keyframe_points:
        kp.interpolation = 'LINEAR'

# Environment light
world = bpy.context.scene.world
world.use_nodes = True
bg = world.node_tree.nodes['Background']
bg.inputs['Color'].default_value = (0.04, 0.04, 0.06, 1.0)
bg.inputs['Strength'].default_value = 1.0

bpy.ops.render.render(animation=True)
print(f"Viewport render done → {OUTPUT_DIR}viewport.mp4")
