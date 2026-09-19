# Screen Recording Notes — BTW Abelian Sandpile

Target file: `public/library/videos/scripting/<slug>/screen.mp4`

## Software

| Platform | Recommended |
|---|---|
| Windows 11 | Xbox Game Bar (Win + G) or OBS Studio |
| macOS | OBS Studio or built-in Screenshot.app video |
| Linux | OBS Studio |

## OBS Settings

| Setting | Value |
|---|---|
| Source | Window Capture → Blender |
| Base resolution | 1920 × 1080 |
| Output resolution | 1920 × 1080 |
| FPS | 30 |
| Audio | Disabled (no mic, no desktop audio) |
| Output format | MP4 |
| Video encoder | x264 (CRF 18) or NVENC (quality preset) |

## What to record (approx. 4 minutes)

1. **Open Blender** (Blender 5.1). New General file.
2. **Script Editor** — switch one pane to Scripting workspace.
3. Open `blueprint.py`. Walk through the physics docstring while the
   viewer reads: explain the BTW threshold (h ≥ 4), open boundaries,
   and why no parameter tuning is needed.
4. **Show parameters** at the top of the file: N=128, CRITICAL_HEIGHT=4,
   N_GRAIN_SETTLE=1 200 000. Explain the settling criterion (>> 5×N²).
5. **Run the script** (Alt+P or the Run Script ▶ button).
   - Console shows progress lines ("running to criticality …",
     "hunting small avalanche …", etc.)
   - While it runs (~1–3 min), narrate the Abelian property: all unstable
     sites topple simultaneously and the final state is order-independent.
6. **After completion** — switch to 3-D Viewport. Orbit the mesh.
   - Point out the cobalt (h=0) → amber (h=3) gradient across the surface.
   - Open Properties → Mesh Data → Shape Keys. Drag SK_SmallAval to 1.0
     and show the small fractal island rising out of the surface.
   - Reset to 0.0, drag SK_LargeAval to 1.0 — a larger system-spanning
     footprint appears.
   - Explain D_f ≈ 2.75 by eye: the cluster has holes inside it and
     intricate boundary tendrils — a fractal, not a smooth disc.
   - Reset, drag SK_Maximal — the whole surface becomes uniformly amber
     and raised (all h=3).
7. **Material** — mention the FLOAT_COLOR attribute drives colour and
   emission in the shader without any UV maps.
8. **GLB export** — open the File → Export menu and show the Draco + WebP
   settings, or note that blueprint.py already exported it.

## File naming

Rename OBS output to `screen.mp4` and place alongside `viewport.mp4`
in `public/library/videos/scripting/<slug>/`.
