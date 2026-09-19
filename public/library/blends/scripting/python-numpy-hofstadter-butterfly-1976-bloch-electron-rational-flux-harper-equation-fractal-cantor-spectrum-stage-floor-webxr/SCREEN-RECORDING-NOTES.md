# Screen Recording Notes — Hofstadter Butterfly

**Target file**: `public/library/videos/scripting/python-numpy-hofstadter-butterfly-1976-bloch-electron-rational-flux-harper-equation-fractal-cantor-spectrum-stage-floor-webxr/screen.mp4`

---

## OBS / Windows Game Bar setup

| Setting | Value |
|---|---|
| Source | Window capture — Blender |
| Resolution | 1920 × 1080 |
| Frame rate | 30 fps |
| Audio | Off (mute mic + desktop) |
| Output format | MP4 (H.264) |
| Bit rate | 8 000 kbps |

---

## Recording steps

1. Open `hofstadter_butterfly_floor.blend` in Blender 5.1.
2. Maximise the 3D Viewport (hover, press **Space** → drag, or **Ctrl+Space**).
3. Set shading to **Material Preview** (Z → 5 or click the sphere icon).
4. Position the view: **Numpad 5** (orthographic off), then orbit to a
   slightly elevated angle so the butterfly's wing structure is clear.
5. Open the **N-panel → Shape Keys**: you will manually scrub between keys
   during the recording.
6. Start OBS / Game Bar recording.
7. Record this sequence (5 – 10 seconds per state, smooth slider drags):
   - **Basis** (Q_MAX=100 full butterfly) — pause to let the shape register
   - Slowly drag slider to **SK_Coarse** — watch the fine branches dissolve
   - Slowly drag slider back and across to **SK_Dense** — sub-bands emerge
   - Slowly drag slider to **SK_Central** — zoom reveals Cantor-set gaps
   - Return to **Basis**
8. Total clip length: 60 – 90 seconds.
9. Stop OBS recording.

---

## What to capture in the commentary track (optional voice-over)

- "Each wing is an energy band of electrons in a magnetic field."
- "Gaps between wings are topological insulators — each gap has a Chern number."
- "Zooming into the centre reveals a fractal: the butterfly repeats inside itself."
- "This structure is why the quantum Hall effect has integer steps."

---

## Notes for the viewport render (automated)

`record.py` produces a 10-second automated render at 1920×1080 using
EEVEE NEXT. Run it after `blueprint.py` to generate `viewport.mp4` without
needing OBS.
