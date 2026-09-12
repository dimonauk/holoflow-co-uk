"""
Holoflow Studio — viewport.mp4 recorder for Allen–Cahn Stage Floor.
Run AFTER blueprint.py in the same Blender session (or re-open the .blend).
Outputs: public/library/videos/scripting/<slug>/viewport.mp4
Duration: 10 s · 30 fps (300 frames)
Content: morphs Basis → SK_Coarsened to show domain coarsening in action.
"""
import bpy, os, math

SLUG = (
    "python-numpy-allen-cahn-phase-field-mean-curvature-motion-"
    "allen-cahn-1979-stage-floor-webxr"
)
OBJ_NAME = "allen_cahn_floor"
FPS      = 30
FRAMES   = 300   # 10 s total


def setup_render():
    scene = bpy.context.scene
    scene.render.engine       = 'BLENDER_EEVEE_NEXT'
    scene.render.fps          = FPS
    scene.frame_start         = 1
    scene.frame_end           = FRAMES
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format              = 'MPEG4'
    scene.render.ffmpeg.codec               = 'H264'
    scene.render.ffmpeg.constant_rate_factor = 'HIGH'

    repo_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../../../")
    )
    out_dir = os.path.join(
        repo_root, "public", "library", "videos", "scripting", SLUG
    )
    os.makedirs(out_dir, exist_ok=True)
    scene.render.filepath = os.path.join(out_dir, "viewport.mp4")


def keyframe_morph():
    """
    Animate SK_Coarsened value 0 → 1 over FRAMES frames.
    This morphs from the Basis (t=10, fine blobs) to SK_Coarsened (t=70,
    fewer larger domains), visually demonstrating curvature-driven coarsening.
    """
    ob = bpy.data.objects.get(OBJ_NAME)
    if ob is None:
        raise RuntimeError("Run blueprint.py first to create the mesh.")
    keys  = ob.data.shape_keys.key_blocks
    coarse = keys.get("SK_Coarsened")
    if coarse is None:
        raise RuntimeError("SK_Coarsened shape key not found.")
    # Start fully Basis
    coarse.value = 0.0
    coarse.keyframe_insert("value", frame=1)
    # Hold at start for 1 s (allow viewer to see fine-scale state)
    coarse.keyframe_insert("value", frame=30)
    # Morph to coarsened over frames 30 → 270
    coarse.value = 1.0
    coarse.keyframe_insert("value", frame=270)
    # Hold at end for 1 s
    coarse.keyframe_insert("value", frame=300)


def setup_camera():
    """
    Bird's-eye orthographic camera, tilted 15° from vertical.
    Orthographic shows the domain structure without perspective distortion.
    """
    scene = bpy.context.scene
    cam_data           = bpy.data.cameras.new("RecordCam")
    cam_data.type      = 'ORTHO'
    cam_data.ortho_scale = 10.0
    cam_obj = bpy.data.objects.new("RecordCam", cam_data)
    bpy.context.collection.objects.link(cam_obj)
    cam_obj.location       = (0.0, -6.0, 10.0)
    cam_obj.rotation_euler = (math.radians(75), 0.0, 0.0)
    scene.camera           = cam_obj


def setup_lighting():
    """Area light from above-left for gentle shadow on domain edges."""
    light_data          = bpy.data.lights.new("RecordLight", 'AREA')
    light_data.energy   = 400
    light_data.size     = 6.0
    light_obj = bpy.data.objects.new("RecordLight", light_data)
    bpy.context.collection.objects.link(light_obj)
    light_obj.location       = (-3.0, -2.0, 8.0)
    light_obj.rotation_euler = (math.radians(45), 0.0, math.radians(-30))

    # World: dark background so cobalt–amber colouring pops
    bpy.context.scene.world.use_nodes = True
    bg = bpy.context.scene.world.node_tree.nodes.get('Background')
    if bg:
        bg.inputs['Color'].default_value    = (0.02, 0.02, 0.04, 1.0)
        bg.inputs['Strength'].default_value = 0.1


def main():
    setup_render()
    keyframe_morph()
    setup_camera()
    setup_lighting()
    bpy.ops.render.render(animation=True)
    print(f"[Allen–Cahn record] Saved → {bpy.context.scene.render.filepath}")


main()
