"""
Viewport animation recorder for the DLA blueprint.
Run AFTER blueprint.py has created dla_cluster_floor in the scene.

Records a 10-second (300-frame) EEVEE NEXT render that:
  1. Starts top-down; camera slowly tilts to a 40° overhead angle.
  2. Shape keys animate: Basis → SK_Small → SK_Mid → Basis → SK_Inverse.
     Each transition reveals a growth stage of the fractal cluster.
Output:
  public/library/videos/scripting/
  python-numpy-dla-diffusion-limited-aggregation-witten-sander-1981-fractal-growth-dendritic-crystal-height-field-stage-floor-webxr/
  viewport.mp4
"""

import bpy
import math

FPS        = 30
DURATION_S = 10
N_FRAMES   = FPS * DURATION_S   # 300

_SLUG = (
    "python-numpy-dla-diffusion-limited-aggregation-witten-sander-1981-"
    "fractal-growth-dendritic-crystal-height-field-stage-floor-webxr"
)
OUT_PATH = f"//../../videos/scripting/{_SLUG}/viewport"

# Shape-key morph schedule: (frame, Basis, SK_Small, SK_Mid, SK_Inverse)
KEY_SCHEDULE = [
    (1,   1.0, 0.0, 0.0, 0.0),   # Basis full cluster
    (70,  0.0, 1.0, 0.0, 0.0),   # SK_Small: early sparse growth
    (140, 0.0, 0.0, 1.0, 0.0),   # SK_Mid: mid-growth dendrites
    (210, 1.0, 0.0, 0.0, 0.0),   # back to Basis (full)
    (270, 0.0, 0.0, 0.0, 1.0),   # SK_Inverse: core-high view
    (300, 1.0, 0.0, 0.0, 0.0),   # return to Basis
]


def setup_camera() -> bpy.types.Object:
    """Orbital rig: pivot empty + camera child; tilts from top-down to 40°."""
    cam_data = bpy.data.cameras.new("RecordCam")
    cam_obj  = bpy.data.objects.new("RecordCam", cam_data)
    bpy.context.collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj
    cam_data.lens = 28

    pivot = bpy.data.objects.new("CamPivot", None)
    bpy.context.collection.objects.link(pivot)
    pivot.location = (0.0, 0.0, 0.0)

    cam_obj.parent   = pivot
    cam_obj.location = (0.0, -3.8, 5.2)
    cam_obj.rotation_euler = (math.radians(36), 0.0, 0.0)

    # Slowly orbit 30° over the clip
    pivot.rotation_euler = (0.0, 0.0, 0.0)
    pivot.keyframe_insert("rotation_euler", frame=1)
    pivot.rotation_euler = (0.0, 0.0, math.radians(30))
    pivot.keyframe_insert("rotation_euler", frame=N_FRAMES)

    return cam_obj


def animate_shape_keys(obj: bpy.types.Object) -> None:
    """Insert keyframes for each shape key according to KEY_SCHEDULE."""
    sks = obj.data.shape_keys
    if sks is None:
        return
    key_names = ["Basis", "SK_Small", "SK_Mid", "SK_Inverse"]
    blocks = {n: sks.key_blocks.get(n) for n in key_names}

    for frame, *vals in KEY_SCHEDULE:
        bpy.context.scene.frame_set(frame)
        for name, val in zip(key_names, vals):
            blk = blocks.get(name)
            if blk:
                blk.value = val
                blk.keyframe_insert("value", frame=frame)


def add_world_light() -> None:
    """Simple HDRI-less world for EEVEE: warm overhead area light."""
    world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs["Color"].default_value   = (0.04, 0.06, 0.12, 1.0)
        bg.inputs["Strength"].default_value = 0.6

    lamp_data = bpy.data.lights.new("KeyLight", type="AREA")
    lamp_data.energy = 800
    lamp_data.size   = 3.0
    lamp_obj = bpy.data.objects.new("KeyLight", lamp_data)
    bpy.context.collection.objects.link(lamp_obj)
    lamp_obj.location = (2.0, -1.0, 5.0)
    lamp_obj.rotation_euler = (math.radians(30), math.radians(15), 0.0)


def configure_render() -> None:
    """EEVEE NEXT, 1920×1080, H.264 MP4 output."""
    scene = bpy.context.scene
    scene.render.engine          = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x    = 1920
    scene.render.resolution_y    = 1080
    scene.render.fps             = FPS
    scene.frame_start            = 1
    scene.frame_end              = N_FRAMES

    scene.render.image_settings.file_format      = "FFMPEG"
    scene.render.ffmpeg.format                   = "MPEG4"
    scene.render.ffmpeg.codec                    = "H264"
    scene.render.ffmpeg.constant_rate_factor     = "HIGH"
    scene.render.filepath = OUT_PATH


def main() -> None:
    obj = bpy.data.objects.get("dla_cluster_floor")
    if obj is None:
        raise RuntimeError("Run blueprint.py first to create dla_cluster_floor.")

    add_world_light()
    setup_camera()
    animate_shape_keys(obj)
    configure_render()

    print("[record.py] Rendering 300 frames — this may take a few minutes …")
    bpy.ops.render.render(animation=True)
    print(f"[record.py] Done → {OUT_PATH}.mp4")


if __name__ == "__main__":
    main()
