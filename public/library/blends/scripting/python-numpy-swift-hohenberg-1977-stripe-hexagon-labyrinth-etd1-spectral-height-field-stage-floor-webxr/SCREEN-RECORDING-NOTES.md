# Screen Recording Notes — Swift-Hohenberg Pattern Floor

**Target file:** `public/library/videos/scripting/python-numpy-swift-hohenberg-1977-stripe-hexagon-labyrinth-etd1-spectral-height-field-stage-floor-webxr/screen.mp4`

## OBS / Game Bar setup

| Setting | Value |
|---|---|
| Capture source | Window → Blender (title: `Blender`) |
| Resolution | 1920 × 1080 |
| Frame rate | 30 fps |
| Audio | Off |
| Encoder | Software H.264 (x264), CRF 23 |
| Output format | MP4 |

## Recording script (what to show)

1. **Open Blender 5.1** — new General file.
2. **Open Scripting workspace** — paste `blueprint.py`, press **Run Script**.
   - The terminal shows `[SH] Basis … SK_Hex … SK_Labyrinth … SK_Inverted … Exported`.
   - 4 simulations run sequentially; total time ≈ 15–25 s on a modern CPU.
3. **Switch to 3D Viewport** — switch to Material Preview (Z → Material Preview).
   - The cobalt-amber stripes (Basis shape key) are visible.
4. **Shape Keys panel** (Properties → Data → Shape Keys):
   - Scrub `SK_Hex` value from 0 → 1: stripes morph to hexagonal lattice.
   - Scrub `SK_Labyrinth` value from 0 → 1: hexagons morph to labyrinthine chaos.
   - Scrub `SK_Inverted` value from 0 → 1: labyrinths invert to spotted topology.
5. **NumPy / ETD1 explanation** (optional screen text overlay):
   - *"The operator (1+∇²)² selects exactly one wavelength — ETD1 integrates
     the linear part exactly, allowing a 10 000× larger time step than
     explicit Euler."*
6. **Orbit the viewport** slowly while SK_Hex is active — shows 3-D depth of
   the hexagonal lattice and the cobalt-valley / amber-peak colour coding.
7. **Stop recording.**

## Post-production notes

- Trim to ≤ 60 seconds.
- Add a title card: `"Swift-Hohenberg Equation (1977) · Blender 5.1 bpy"`.
- No background music required; ambient Blender UI sounds are fine.
- Upload to `public/library/videos/scripting/<slug>/screen.mp4`.
