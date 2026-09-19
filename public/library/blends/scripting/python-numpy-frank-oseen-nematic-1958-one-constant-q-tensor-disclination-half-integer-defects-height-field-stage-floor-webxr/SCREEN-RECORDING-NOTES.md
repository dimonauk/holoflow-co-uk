# Screen-Recording Notes — Frank-Oseen Nematic LC Director Field

## Goal

Capture a 1920 × 1080, 30 fps screen recording of the nematic director
height-field morphing through four defect configurations: quadrupole →
single +½ comet → hedgehog +1 → annihilating ±½ pair.

---

## Software

| Tool          | Platform              | Notes                              |
|---------------|-----------------------|------------------------------------|
| OBS Studio    | Windows / macOS / Linux | Window capture, Blender window   |
| Xbox Game Bar | Windows               | Win + G, good fallback             |
| QuickTime     | macOS                 | Built-in, lossless                 |

---

## OBS Setup

1. **New Scene** → name it `lc-nematic-floor`.
2. **Add Source** → Window Capture → select the Blender window.
3. **Resolution**: 1920 × 1080.
4. **FPS**: 30.
5. **Audio**: **off**.
6. **Output format**: MP4 (H.264 CRF 18).
7. **Output path**: `public/library/videos/scripting/<slug>/screen.mp4`

---

## Blender Viewport Settings

```
Viewport Shading : Material Preview
Overlay          : Wireframe OFF
Colour management: Filmic, Medium High Contrast
Camera           : Numpad 0  (RecordCam placed by record.py)
Playback         : Space bar → plays the 300-frame animation
```

---

## Recording Sequence

1. Open Blender with the `.blend` saved after `blueprint.py`.
2. Run `record.py` once to bake shape-key keyframes and create `RecordCam`.
3. Press **Numpad 0** to enter camera view.
4. Start OBS recording.
5. Press **Space** in the Blender timeline to play.
6. Stop recording after one full loop (≈ 10 s).

---

## Post-Processing (optional)

```bash
ffmpeg -i screen_raw.mp4 -t 10 -vf scale=1920:1080 -c:v libx264 -crf 18 screen.mp4
```

---

## Expected Output

| File           | Duration | Resolution  | Audio |
|----------------|----------|-------------|-------|
| `viewport.mp4` | 10 s     | 1920 × 1080 | none  |
| `screen.mp4`   | 10 s     | 1920 × 1080 | none  |
