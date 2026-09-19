"""
record.py — viewport animation render for N-body orbital dance
Run AFTER blueprint.py in the same Blender 5.1 session.

Outputs: public/library/videos/geometry-nodes/
         gn-simulation-zone-n-body-gravity-leapfrog-orbital-dance-poi-webxr/
         viewport.mp4

Settings: EEVEE Next · 1920×1080 · 30 fps · frames 1–300 (~10 s)
          H.264 / MP4 via FFmpeg
"""

import bpy

scene = bpy.context.scene

scene.render.engine = "BLENDER_EEVEE_NEXT"
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.render.fps = 30
scene.frame_start = 1
scene.frame_end = 300

scene.render.image_settings.file_format = "FFMPEG"
scene.render.ffmpeg.format = "MPEG4"
scene.render.ffmpeg.codec = "H264"
scene.render.ffmpeg.constant_rate_factor = "MEDIUM"
scene.render.ffmpeg.ffmpeg_preset = "GOOD"

out = bpy.path.abspath(
    "//../../../../videos/geometry-nodes/"
    "gn-simulation-zone-n-body-gravity-leapfrog-orbital-dance-poi-webxr/"
    "viewport.mp4"
)
scene.render.filepath = out

bpy.ops.render.render(animation=True)
print(f"[record] viewport render complete → {out}")
