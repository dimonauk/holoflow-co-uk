"""
record.py — KP-II Web Soliton viewport animation
=================================================
Cycles through all four shape keys over 90 frames at 24 fps (~3.75 s),
rendering each to:
  public/library/videos/scripting/
  python-numpy-kadomtsev-petviashvili-kp-ii-1970-exact-web-soliton-hirota-tau-stage-floor-webxr/
  viewport.mp4

Run inside Blender's scripting workspace after blueprint.py has been executed.
The render uses EEVEE-Next (Blender 5.1 default) to keep render time short.
"""

import bpy, pathlib, math

# ── Output path ────────────────────────────────────────────────────────────────
VIDEO_DIR = (
    pathlib.Path(bpy.path.abspath("//"))
    .parents[3]
    / "videos"
    / "scripting"
    / "python-numpy-kadomtsev-petviashvili-kp-ii-1970-exact-web-soliton-hirota-tau-stage-floor-webxr"
)
VIDEO_DIR.mkdir(parents=True, exist_ok=True)

# ── Scene render settings ──────────────────────────────────────────────────────
scene = bpy.context.scene
scene.render.engine       = 'BLENDER_EEVEE_NEXT'
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.fps          = 24
scene.frame_start         = 1
scene.frame_end           = 90

scene.render.image_settings.file_format = 'FFMPEG'
scene.render.ffmpeg.format              = 'MPEG4'
scene.render.ffmpeg.codec               = 'H264'
scene.render.ffmpeg.constant_rate_factor = 'MEDIUM'
scene.render.filepath = str(VIDEO_DIR / "viewport.mp4")

# ── Shape key animation: 1 key per 22-frame segment ───────────────────────────
ob = bpy.context.scene.objects.get("kp_ii_web_soliton")
if ob is None:
    raise RuntimeError("Run blueprint.py first to create the mesh object.")

sk_keys = ["Basis", "SK_YJunction", "SK_Web4", "SK_Temporal"]
# Map: frame 1→Basis, 23→SK_YJunction, 46→SK_Web4, 68→SK_Temporal, 90→Basis
frames   = [1, 23, 46, 68, 90]
key_seq  = sk_keys + [sk_keys[0]]

kb = ob.data.shape_keys.key_blocks
for sk in kb:
    sk.value = 0.0

def _set_single(name: str, frame: int):
    """Mute all shape keys then set the target to 1.0."""
    for sk in kb:
        sk.value = 0.0
        sk.keyframe_insert(data_path="value", frame=frame)
    if name in kb:
        kb[name].value = 1.0
        kb[name].keyframe_insert(data_path="value", frame=frame)

for frame, key_name in zip(frames, key_seq):
    _set_single(key_name, frame)

# ── HDRI-style environment lighting ───────────────────────────────────────────
world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background") or world.node_tree.nodes.new("ShaderNodeBackground")
bg.inputs["Strength"].default_value = 0.6

# ── Material with KP_Height attribute → Cobalt-Amber gradient ─────────────────
mat = bpy.data.materials.new("KP_WebSoliton_Mat")
mat.use_nodes = True
nt = mat.node_tree
nt.nodes.clear()

out   = nt.nodes.new("ShaderNodeOutputMaterial")
bsdf  = nt.nodes.new("ShaderNodeBsdfPrincipled")
attr  = nt.nodes.new("ShaderNodeAttribute")
ramp  = nt.nodes.new("ShaderNodeValToRGB")

attr.attribute_name = "KP_Height"
ramp.color_ramp.elements[0].color = (0.030, 0.120, 0.750, 1.0)   # cobalt
ramp.color_ramp.elements[1].color = (0.960, 0.600, 0.020, 1.0)   # amber
bsdf.inputs["Metallic"].default_value  = 0.35
bsdf.inputs["Roughness"].default_value = 0.40

nt.links.new(attr.outputs["Color"],        ramp.inputs["Fac"])
nt.links.new(ramp.outputs["Color"],        bsdf.inputs["Base Color"])
nt.links.new(bsdf.outputs["BSDF"],         out.inputs["Surface"])

ob.data.materials.clear()
ob.data.materials.append(mat)

# ── Render ─────────────────────────────────────────────────────────────────────
bpy.ops.render.render(animation=True)
print(f"Saved viewport animation → {scene.render.filepath}")
