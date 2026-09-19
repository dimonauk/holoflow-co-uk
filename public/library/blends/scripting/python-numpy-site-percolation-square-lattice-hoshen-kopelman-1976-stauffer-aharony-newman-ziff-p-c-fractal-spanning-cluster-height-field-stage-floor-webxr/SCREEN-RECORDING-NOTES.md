# Screen-Recording Notes — Site Percolation Stage Floor

## Goal
Capture a 1920 × 1080, 30 fps screen recording of the percolation height-field
transitioning through four phases of the phase diagram: sub-critical,
critical, super-critical, and bond percolation at threshold.

---

## Software

| Tool       | Platform | Notes                                         |
|------------|----------|-----------------------------------------------|
| OBS Studio | Windows / macOS / Linux | Window capture + Blender window |
| Xbox Game Bar | Windows | Win + G, good fallback                   |
| QuickTime  | macOS    | Built-in, lossless                            |

---

## OBS Setup

1. **New Scene** → name it `perc-floor`.
2. **Add Source** → Window Capture → select the Blender window.
3. **Resolution**: 1920 × 1080 (match Blender viewport).
4. **FPS**: 30.
5. **Audio**: **off** — no commentary needed for the viewport animation.
6. **Output format**: MP4 (H.264 CRF 18).
7. **Output path**: `public/library/videos/scripting/<slug>/screen.mp4`

---

## Blender Viewport Settings

Before recording, configure the 3-D viewport:

```
Viewport Shading: Material Preview  (or Rendered for full lighting)
Overlay: Wireframe OFF
Viewport colour management: Filmic, Medium High Contrast
Camera: Numpad 0 (RecordCam placed by record.py)
Playback: Space bar → plays the 300-frame animation
```

---

## Recording Sequence

1. Open Blender with the `.blend` file saved after running `blueprint.py`.
2. Run `record.py` once to bake keyframes and create `RecordCam`.
3. Press **Numpad 0** to enter camera view.
4. Start OBS recording.
5. Press **Space** in the Blender timeline to play.
6. Stop recording after one full loop (≈ 10 s).

---

## Post-Processing (optional)

```bash
# Trim to exact 10 s and normalise to 1920×1080
ffmpeg -i screen_raw.mp4 -t 10 -vf scale=1920:1080 -c:v libx264 -crf 18 screen.mp4
```

---

## Expected Output

| File         | Duration | Resolution  | Audio |
|--------------|----------|-------------|-------|
| `viewport.mp4` | 10 s   | 1920 × 1080 | none  |
| `screen.mp4`   | 10 s   | 1920 × 1080 | none  |
