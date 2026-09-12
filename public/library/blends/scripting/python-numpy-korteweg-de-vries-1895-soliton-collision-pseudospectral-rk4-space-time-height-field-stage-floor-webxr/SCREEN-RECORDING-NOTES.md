# Screen-Recording Notes — KdV Soliton Collision Stage Floor

**OBS Studio / Windows Game Bar setup for `screen.mp4`**

## Before you start

1. Open Blender 5.1.
2. Load `kdv_soliton_floor.blend` (built by `blueprint.py`).
3. Switch to the **Layout** workspace; select `kdv_soliton_floor`.
4. Set viewport shading to **Material Preview** (Z → Material Preview).
5. Enable **Bloom** in Viewport Overlays → Render Properties → EEVEE bloom.

## OBS settings

| Setting | Value |
|---------|-------|
| Source | Window Capture → Blender |
| Resolution | 1920 × 1080 |
| Frame rate | 30 fps |
| Encoder | H.264 (software) |
| Bitrate | 8000 kbps |
| Audio | **Off** |
| Output file | `screen.mp4` |

## Shot list (≈ 60 seconds total)

| Time | Action |
|------|--------|
| 0–10 s | Top-down view of the floor in **Basis** (2-soliton). Pan slowly to show diagonal soliton ridges crossing. |
| 10–20 s | Tilt to a low-angle view (Numpad 1 + scroll wheel). Orbit 90° to show the space-time structure. |
| 20–30 s | In the shape-key panel (Properties → Object Data → Shape Keys), fade from **Basis** to **SK_Single**. Show how one ridge replaces two. |
| 30–40 s | Fade to **SK_Three** — three colliding ridges; pause on the triple-interaction region. |
| 40–50 s | Fade to **SK_Slow** — two slower solitons, longer interaction window. |
| 50–60 s | Return to **Basis**; zoom to the collision region and trace the phase shift with the cursor. |

## Narration cues (for tutorial voiceover)

- **0–10 s**: "Each diagonal ridge is a soliton — a localised wave travelling at constant speed. Taller means faster."
- **20–30 s**: "With a single soliton there is one clean stripe. The KdV equation reduces to a pure drift."
- **30–40 s**: "Three solitons interact sequentially. Notice each pair of ridges bends slightly at the crossing — that is the phase shift."
- **40–50 s**: "Slower solitons have lower amplitude and a wider profile — the KdV amplitude–speed relation A = c/2."

## Output destination

Save the recording as:
```
public/library/videos/scripting/
  python-numpy-korteweg-de-vries-1895-soliton-collision-pseudospectral-rk4-space-time-height-field-stage-floor-webxr/
    screen.mp4
```
