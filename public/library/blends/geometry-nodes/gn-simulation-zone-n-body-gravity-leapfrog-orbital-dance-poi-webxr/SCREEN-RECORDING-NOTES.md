# Screen Recording Notes — N-Body Gravity Leapfrog Orbital Dance

**Target file:** `public/library/videos/geometry-nodes/gn-simulation-zone-n-body-gravity-leapfrog-orbital-dance-poi-webxr/screen.mp4`

## OBS / Game Bar settings

| Setting | Value |
|---|---|
| Source | Window Capture → Blender 5.1 |
| Resolution | 1920 × 1080 |
| Frame rate | 30 fps |
| Audio | Off (no microphone) |
| Output format | MP4 |
| Encoder | x264 · CRF 20 (or GPU equivalent) |
| Duration | ~35 s total (see cues below) |

## Recording cues

1. **0 s** — Open `blueprint.py` in the Scripting workspace. Camera should already be in position facing the cluster's initial orbit.
2. **5 s** — Press **Run Script**. The terminal output prints the GLB path once export completes (~5–10 s on modern hardware).
3. **15 s** — Switch to **Timeline** view (drag the bottom panel). Press **Space** to play. The 8 neon trails grow from tiny dots outward over 300 frames (10 s).
4. **25 s** — Scrub back to frame 1. Press **Space** again so the full playback loops — shows the orbital dance repeating.
5. **35 s** — Stop recording.

## Viewport shading

- **Rendered** mode (Z → Rendered, or click the sphere icon in the header).
- World background must be **pure black** — confirmed by blueprint.py.
- EEVEE Bloom visible in Rendered mode only.

## Post-processing (optional)

Trim the first 3 s of script-loading pause in DaVinci Resolve or ffmpeg:

```bash
ffmpeg -i screen.mp4 -ss 00:00:03 -t 00:00:30 -c copy screen_trimmed.mp4
```
