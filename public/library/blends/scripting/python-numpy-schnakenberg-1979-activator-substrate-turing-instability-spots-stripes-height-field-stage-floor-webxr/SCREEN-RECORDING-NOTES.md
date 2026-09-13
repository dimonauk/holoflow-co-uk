# Screen Recording Notes — Schnakenberg Turing Floor

Target file: `public/library/videos/scripting/
python-numpy-schnakenberg-1979-activator-substrate-turing-instability-
spots-stripes-height-field-stage-floor-webxr/screen.mp4`

## OBS / Game Bar setup

| Setting | Value |
|---------|-------|
| Source | Window Capture → Blender 5.1 |
| Resolution | 1920 × 1080 |
| Frame rate | 30 fps |
| Audio | OFF |
| Output format | MP4 (H.264) |
| Encoder quality | CRF 23 |

## What to capture

1. **Open Blender 5.1** (fresh scene, Scripting workspace visible).
2. Paste / open `blueprint.py`.  Briefly scroll through the parameter block so viewers
   can read the Turing-condition verification output area.
3. Press **Run Script**.  Keep the Info / System Console docked so the Turing
   check table and "Running BASIS …" progress lines are visible.
4. Once the script finishes, switch to **3D Viewport** (Solid shading).
   Orbit around the height-field spotty surface for 5 – 8 seconds.
5. Open the **Properties → Object Data → Shape Keys** panel.
   Drag each shape-key value slider from 0 → 1 → 0 in turn:
   SK_Coarse (coarser spots), SK_Fine (finer spots), SK_Bloom (dense array).
   This shows the pattern continuously morphing between regimes.
6. Switch to **Material Preview** shading to show the cobalt-to-amber
   SC_Activator vertex colour.
7. End recording. Total duration: 60 – 90 s is ideal.

## Key visual beats

- **Spot formation** is not visible live (simulation runs offline), but the
  height-field RESULT clearly shows the Turing pattern.
- **Shape key morphing** (step 5) is the main visual payoff — smooth interpolation
  between four distinct pattern wavelengths.
- Mention briefly (voice or on-screen text) that these are the SAME chemistry,
  different rate constants.

## File delivery

Place the rendered `.mp4` at the path shown above (create the directory if needed).
`record.py` renders `viewport.mp4` automatically; `screen.mp4` is the manual capture.
