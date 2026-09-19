# Screen Recording Notes — DLA Fractal Growth

**Target file**:
`public/library/videos/scripting/python-numpy-dla-diffusion-limited-aggregation-witten-sander-1981-fractal-growth-dendritic-crystal-height-field-stage-floor-webxr/screen.mp4`

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

1. Open `dla_cluster_floor.blend` in Blender 5.1.
2. Maximise the 3D Viewport (**Ctrl+Space**).
3. Set shading to **Material Preview** (Z → 5, or click the sphere icon in the
   viewport header).
4. Position the view: hold **Middle Mouse** and orbit to a 40° overhead angle
   so the dendritic arms radiate clearly from the centre.
5. Open the **Properties panel → Object Data → Shape Keys** (or N-panel).
6. Start OBS / Game Bar recording.
7. Record this sequence (hold each state 10–15 s, drag sliders slowly):
   - **Basis** — full 2 000-particle DLA cluster. Blue core, amber tips.
     Orbit slowly so the fractal branching is visible from multiple angles.
   - Drag to **SK_Small** — first 400 particles. Watch the outer dendrites
     disappear, leaving only the dense inner core. The cluster looks like
     a simple cross.
   - Drag to **SK_Mid** — first 1 200 particles. Secondary branches begin
     to appear; the fractal nature becomes apparent.
   - Return to **Basis** — full cluster again.
   - Drag to **SK_Inverse** — same cluster, but height is inverted:
     the seed becomes the peak and the tips taper to the floor. This gives
     a mountain-shaped silhouette that reads like a coral or lightning tree.
8. Total clip length: 90 – 120 seconds.
9. Stop OBS recording.

---

## Camera angles that work well

- **Top-down orthographic** (Numpad 7): shows the 2D fractal geometry cleanly;
  use this for the opening 5 seconds.
- **40° overhead perspective** (Numpad 5 to toggle orthographic off; orbit to
  taste): shows the height variation between core and tips.
- **Side profile** (Numpad 1): reveals the mountain silhouette of SK_Inverse.

---

## Optional commentary

- "Each arm grew independently — no instructions, only stick-or-walk."
- "The fractal dimension is 1.71, halfway between a line and a filled area."
- "Real-world examples: snowflakes, mineral dendrites, electrodeposition."
- "The colour encodes time: cobalt is oldest, amber is newest."

---

## Notes for the viewport render (automated)

`record.py` produces a 10-second automated EEVEE NEXT render at 1920×1080.
Run it inside Blender after `blueprint.py` to generate `viewport.mp4` without
needing OBS.
