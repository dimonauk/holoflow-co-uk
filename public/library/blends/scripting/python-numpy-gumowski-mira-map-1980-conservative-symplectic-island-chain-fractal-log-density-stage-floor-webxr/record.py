"""
record.py — Viewport animation for the Gumowski–Mira Map tutorial
==================================================================
Outputs to:
  public/library/videos/scripting/
    python-numpy-gumowski-mira-map-1980-conservative-symplectic-island-chain-fractal-log-density-stage-floor-webxr/
      viewport.mp4

Run AFTER blueprint.py has created the GumowskiMira_Floor object in the scene.
Duration: 12 seconds at 24 fps = 288 frames.

WHY 12 s and not 10 s: the shape-key sweep (Basis→SK_Ring→SK_Web→SK_Fish→Basis)
needs ~8 frames per transition to be legible, and we want a full orbit before
the first cut — 12 s gives comfortable pacing at 24 fps.
"""

import bpy, math, os

OBJ_NAME   = "GumowskiMira_Floor"
CAM_NAME   = "GM_BirdCam"
FPS        = 24
DURATION_S = 12
N_FRAMES   = FPS * DURATION_S   # 288

OUTPUT_PATH = (
    "public/library/videos/scripting/"
    "python-numpy-gumowski-mira-map-1980-conservative-symplectic-island-chain-"
    "fractal-log-density-stage-floor-webxr/viewport.mp4"
)


def _clear_anim(obj: bpy.types.Object) -> None:
    if obj.animation_data:
        obj.animation_data_clear()


def setup_camera() -> bpy.types.Object:
    """
    Orbit camera 40° above the XY plane, radius 10 m.
    WHY 40°: shows both the flat sea (zero-density cells) and the island
    ridges — less steep than 90° top-down (loses height), more informative
    than near-horizon which hides the fractal structure.
    """
    if CAM_NAME in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[CAM_NAME], do_unlink=True)

    cam_data      = bpy.data.cameras.new(CAM_NAME)
    cam_data.type = "PERSP"
    cam_data.lens = 35.0   # 35 mm gives a wide enough FOV to show full floor
    cam           = bpy.data.objects.new(CAM_NAME, cam_data)
    bpy.context.scene.collection.objects.link(cam)
    bpy.context.scene.camera = cam
    return cam


def keyframe_camera(cam: bpy.types.Object) -> None:
    """
    360° orbit over 288 frames.  Slow rotation lets the viewer trace island
    chains around the edge; the oblique angle shows height variation.
    """
    radius = 10.0
    elev   = 5.5    # height above floor (≈ 29° elevation)

    for frame in range(1, N_FRAMES + 1):
        t     = (frame - 1) / N_FRAMES
        angle = 2.0 * math.pi * t

        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        z = elev

        cam.location = (x, y, z)

        # Face origin
        dx, dy, dz = -x, -y, -z
        dist  = math.sqrt(dx**2 + dy**2 + dz**2)
        pitch = math.asin(-dz / dist)      # look-down
        yaw   = math.atan2(dy, dx)

        cam.rotation_euler = (
            math.pi / 2 + pitch,
            0.0,
            yaw + math.pi / 2,
        )
        cam.keyframe_insert("location",       frame=frame)
        cam.keyframe_insert("rotation_euler", frame=frame)


def keyframe_shape_keys(obj: bpy.types.Object) -> None:
    """
    Animate through the four shape keys with smooth in-out transitions.
    Schedule:
      frame   1–72   : Basis       (3 s) — galactic island chains
      frame  73–144  : SK_Ring     (3 s) — concentric rings emerge
      frame 145–216  : SK_Web      (3 s) — web geometry
      frame 217–288  : SK_Fish     (3 s) — large elliptic island
    Each key fades in over 12 frames (0.5 s) and holds until the next transition.
    """
    if obj.data.shape_keys is None:
        return

    kb = obj.data.shape_keys.key_blocks
    key_names   = ["Basis", "SK_Ring", "SK_Web", "SK_Fish"]
    start_frames = [1, 73, 145, 217]
    FADE         = 12   # blend frames

    for key_name in key_names:
        if key_name in kb:
            kb[key_name].value = 0.0
            kb[key_name].keyframe_insert("value", frame=1)

    for idx, (kname, start) in enumerate(zip(key_names, start_frames)):
        if kname not in kb:
            continue
        # Fade in
        kb[kname].value = 0.0
        kb[kname].keyframe_insert("value", frame=max(1, start - FADE))
        kb[kname].value = 1.0
        kb[kname].keyframe_insert("value", frame=start)
        # Hold until end of segment
        end_frame = start_frames[idx + 1] - FADE if idx + 1 < len(start_frames) else N_FRAMES
        kb[kname].keyframe_insert("value", frame=end_frame)
        # Fade out
        kb[kname].value = 0.0
        kb[kname].keyframe_insert("value", frame=min(N_FRAMES, end_frame + FADE))


def render() -> None:
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end   = N_FRAMES
    scene.render.fps  = FPS

    # Output settings
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    scene.render.filepath   = OUTPUT_PATH
    scene.render.image_settings.file_format = "FFMPEG"
    scene.render.ffmpeg.format              = "MPEG4"
    scene.render.ffmpeg.codec               = "H264"
    scene.render.ffmpeg.constant_rate_factor = "MEDIUM"
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080

    # Viewport shading (SOLID with vertex colour)
    for area in bpy.context.screen.areas:
        if area.type == "VIEW_3D":
            for space in area.spaces:
                if space.type == "VIEW_3D":
                    space.shading.type          = "MATERIAL"
                    space.shading.use_scene_lights = True
            break

    bpy.ops.render.opengl(animation=True)
    print(f"[record.py] Viewport animation written to {OUTPUT_PATH}")


def main() -> None:
    obj = bpy.data.objects.get(OBJ_NAME)
    if obj is None:
        raise RuntimeError(
            f"Object '{OBJ_NAME}' not found.  Run blueprint.py first."
        )

    _clear_anim(obj)
    cam = setup_camera()
    _clear_anim(cam)

    keyframe_camera(cam)
    keyframe_shape_keys(obj)
    render()


main()
