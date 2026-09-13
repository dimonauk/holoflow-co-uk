"""
record.py — Viewport animation renderer for the Schnakenberg Turing blueprint.

Renders a 5-15 s flythrough of the four shape-key states to:
  public/library/videos/scripting/
  python-numpy-schnakenberg-1979-activator-substrate-turing-instability-
  spots-stripes-height-field-stage-floor-webxr/viewport.mp4

Run AFTER blueprint.py has created the Schnakenberg_Floor object.
In Blender 5.1: open Scripting workspace, run blueprint.py, then this file.
"""

import bpy, math

FPS        = 30
HOLD_F     = 20   # frames to hold on each shape-key extreme
BLEND_F    = 20   # frames to crossfade between shape keys
OUT_PATH   = ("//../../videos/scripting/"
              "python-numpy-schnakenberg-1979-activator-substrate-turing-"
              "instability-spots-stripes-height-field-stage-floor-webxr/"
              "viewport.mp4")

# ─── Find the mesh object ─────────────────────────────────────
obj = bpy.data.objects.get("Schnakenberg_Floor")
if obj is None:
    raise RuntimeError("Run blueprint.py first to create Schnakenberg_Floor.")

keys = obj.data.shape_keys
kb   = keys.key_blocks

# ─── Camera rig ──────────────────────────────────────────────
cam_data = bpy.data.cameras.new("RecordCam")
cam_data.lens = 35
cam = bpy.data.objects.new("RecordCam", cam_data)
bpy.context.collection.objects.link(cam)
bpy.context.scene.camera = cam

# Isometric-ish top angle: 45° elevation, 30° azimuth
cam.location  = (3.5, -3.5, 5.0)
cam.rotation_euler = (math.radians(50), 0, math.radians(45))

# ─── World & render settings ─────────────────────────────────
scene = bpy.context.scene
scene.render.engine          = 'BLENDER_EEVEE_NEXT'
scene.render.resolution_x    = 1920
scene.render.resolution_y    = 1080
scene.render.fps             = FPS
scene.render.image_settings.file_format = 'FFMPEG'
scene.render.ffmpeg.format   = 'MPEG4'
scene.render.ffmpeg.codec    = 'H264'
scene.render.ffmpeg.constant_rate_factor = 'MEDIUM'
scene.render.filepath        = OUT_PATH

# Flat studio light from above
if "RecordSun" not in bpy.data.objects:
    sun_data = bpy.data.lights.new("RecordSun", type='SUN')
    sun_data.energy = 3.0
    sun = bpy.data.objects.new("RecordSun", sun_data)
    bpy.context.collection.objects.link(sun)
    sun.rotation_euler = (math.radians(45), 0, math.radians(30))

world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new("RecordWorld")
    scene.world = world
world.color = (0.03, 0.03, 0.06)  # dark studio

# ─── Quick vertex-colour material ────────────────────────────
if obj.data.materials:
    obj.data.materials.clear()
mat = bpy.data.materials.new("SC_Display")
mat.use_nodes = True
nt = mat.node_tree
nt.nodes.clear()
attr_n = nt.nodes.new('ShaderNodeAttribute')
attr_n.attribute_name = "SC_Activator"
emit_n = nt.nodes.new('ShaderNodeEmission')
emit_n.inputs['Strength'].default_value = 1.2
out_n  = nt.nodes.new('ShaderNodeOutputMaterial')
nt.links.new(attr_n.outputs['Color'], emit_n.inputs['Color'])
nt.links.new(emit_n.outputs['Emission'], out_n.inputs['Surface'])
obj.data.materials.append(mat)

# ─── Shape-key animation ─────────────────────────────────────
# All shape-key values start at 0 except Basis which is always 1.
key_names = ["SK_Coarse", "SK_Fine", "SK_Bloom"]
for sk in kb:
    sk.value = 0.0

frame = 1
scene.frame_start = frame

def hold(f_count):
    global frame
    frame += f_count

def blend_to(target_name, f_blend, f_hold):
    """Cross-fade to target shape key over f_blend, hold for f_hold."""
    global frame
    # Key out current values (all at their current state)
    for sk in kb:
        sk.keyframe_insert(data_path="value", frame=frame)
    frame += f_blend
    # Drive target to 1, all others to 0
    for sk in kb:
        sk.value = 1.0 if sk.name == target_name else 0.0
        sk.keyframe_insert(data_path="value", frame=frame)
    frame += f_hold

# Basis → SK_Coarse → SK_Fine → SK_Bloom → Basis
hold(HOLD_F)
for kn in key_names:
    blend_to(kn, BLEND_F, HOLD_F)
blend_to("Basis", BLEND_F, HOLD_F)

scene.frame_end = frame
scene.frame_current = 1

bpy.ops.render.render(animation=True)
print(f"Rendered {scene.frame_end} frames → {OUT_PATH}")
