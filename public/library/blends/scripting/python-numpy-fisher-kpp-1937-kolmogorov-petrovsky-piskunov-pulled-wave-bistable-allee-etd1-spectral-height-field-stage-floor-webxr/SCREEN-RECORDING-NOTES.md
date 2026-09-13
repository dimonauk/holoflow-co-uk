# Screen Recording Notes — Fisher-KPP Wavefront

## OBS / Game Bar Setup

| Setting | Value |
|---------|-------|
| Source  | Window capture → Blender 5.1 |
| Resolution | 1920 × 1080 |
| Frame rate | 30 fps |
| Bitrate | 8 000 kbps (CQP 20 if available) |
| Audio | OFF |
| Output | `screen.mp4` |

## Suggested Blender workspace before recording

1. Open `fisher_kpp_floor.blend`.
2. Switch to the **Scripting** workspace; paste and run `blueprint.py`
   (or use the `.blend` already containing the mesh).
3. In a 3-D viewport, select `Fisher_KPP_Floor`, set Viewport Shading
   to **Rendered** (EEVEE).
4. In the **Object Data → Shape Keys** panel, scrub the three shape-key
   value sliders — the viewer should see the wavefront expand, sharpen,
   and flip from monostable to bistable.

## Shot list (≈ 2 min total)

| Segment | Action | Duration |
|---------|--------|----------|
| Opening | Show Scripting workspace; briefly scroll through blueprint.py | 20 s |
| Run | Execute script; Python console shows progress lines | 30 s |
| Viewport inspection | Orbit around floor in Rendered mode; cobalt→amber ring visible | 25 s |
| Shape-key demo | Drag SK_FastR → 1.0 (sharper, faster ring); drag back | 15 s |
| Shape-key demo | Drag SK_LowD → 1.0 (narrower front, slower); drag back | 15 s |
| Bistable demo | Drag SK_Bistable → 1.0 (pushed wave, distinct interior pattern) | 15 s |
| Export | Run `_export_glb` from Python console; show file size in OS explorer | 20 s |
| Closing | Switch to Layout workspace; press Numpad-0 for camera view | 20 s |

## Post-processing (optional)

```
ffmpeg -i screen.mp4 -vf "scale=1920:1080" -c:v libx264 -crf 20 \
  -preset slow -an screen_final.mp4
```

Save as `public/library/videos/scripting/<slug>/screen.mp4`.
