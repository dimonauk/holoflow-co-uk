# Screen Recording Notes — Wigner Quasi-Probability Floor

## Software
- OBS Studio 30+ or Windows Game Bar (Win+G)
- Source: Window Capture → Blender 5.1

## Settings
| Setting | Value |
|---|---|
| Resolution | 1920 × 1080 |
| Frame rate | 30 fps |
| Encoder | H.264 (NVENC or x264) |
| CRF / Quality | 18–22 |
| Audio | Off (no audio needed) |
| Output | `screen.mp4` |

## What to record

### Scene overview (0:00–0:20)
- Open Blender 5.1 with this blend file
- Switch viewport to **Vertex Paint** colour mode so the cobalt/amber colouring is visible
- Rotate the view to show the floor at a 45° angle from above

### Running the blueprint (0:20–1:00)
- Open the **Scripting** workspace
- Load and run `blueprint.py`
- The console should print: `[Wigner] mesh: 16384V 16129F` and shape key list
- Switch back to 3D viewport and show the resulting mesh

### Shape key morphing (1:00–2:30)
Demonstrate each shape key by manually setting its value from 0→1 in the Properties panel:

1. **Basis (Fock |0⟩)** — circular Gaussian hill, pure cobalt, no amber
2. **SK_Fock1 (Fock |1⟩)** — depression at centre (amber) with cobalt ring: the W < 0 region
3. **SK_Fock5 (Fock |5⟩)** — five concentric alternating rings, striking cobalt/amber pattern
4. **SK_Cat** — two raised peaks at q = ±2 (the two locations of the coherent states)
   plus a dense set of oscillating fringes between them along p — pure quantum interference
5. **SK_Squeezed** — narrow ellipse along q, spread wide along p: squeezed vacuum

### GLB export (2:30–3:00)
- Show the GLB export dialogue with Draco compression enabled
- Note the `export_morph=True` flag so shape keys come through

## Tips
- Set Viewport Shading → **Solid → Attribute** colour display before recording
- Pause shape key slider briefly at each extreme (0.0 and 1.0) for clean cuts
- The interference fringes in SK_Cat are very fine — zoom in to the centre region
  to show them clearly before zooming back out

## Output location
Place finished `screen.mp4` in:
```
public/library/videos/scripting/python-numpy-wigner-quasi-probability-distribution-1932-quantum-phase-space-fock-state-cat-state-squeezed-vacuum-stage-floor-webxr/screen.mp4
```
